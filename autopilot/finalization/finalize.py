#!/usr/bin/env python3
"""Preview, apply and verify the final Codex Starter cleanup.

The helper intentionally uses only the Python standard library. It never
deletes a directory recursively and never follows symlinks or Windows reparse
points. Every removable file must be listed in cleanup-manifest.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


MANIFEST_REL = "autopilot/finalization/cleanup-manifest.json"
STATE_REL = ".codex/autopilot-state.yml"
DECISIONS_REL = ".codex/finalization-decisions.json"
DOCUMENTS_REL = ".codex/finalization-documents"
PREVIEW_REL = ".codex/finalization-preview.json"
RUNTIME_REL = ".codex/finalization-runtime.json"

REWRITE_LATE = {"AGENTS.md", "PROJECT_STATE.md"}
LATE_REMOVE = {
    STATE_REL,
    "AUTOPILOT.md",
    "POST_AUTOPILOT.md",
}
RUNTIME_EXACT = {
    DECISIONS_REL,
    PREVIEW_REL,
    RUNTIME_REL,
    f"{DOCUMENTS_REL}/AGENTS.md",
    f"{DOCUMENTS_REL}/PROJECT_STATE.md",
    f"{DOCUMENTS_REL}/README.md",
    f"{DOCUMENTS_REL}/STRUCTURE.md",
}
PROTECTED_PREFIXES = {
    ".git/",
    "business/",
}
PROTECTED_EXACT = {
    ".git",
    ".env",
    ".env.local",
    ".codex/config.local.toml",
}
RESERVED_STARTER_PREFIXES = {
    "autopilot/",
    "examples/",
    "maintainer/",
    "templates/",
}
TEXT_SUFFIXES = {
    ".md",
    ".tmpl",
    ".toml",
    ".json",
    ".yml",
    ".yaml",
    ".py",
    ".ps1",
    ".sh",
    ".txt",
    ".sample",
}
FORBIDDEN_FINAL_MARKERS = (
    "AUTOPILOT.md",
    "POST_AUTOPILOT.md",
    ".codex/autopilot-state.yml",
    "Codex Starter",
    "starter-template",
    "maintainer/",
    "examples/",
    "templates/AGENTS.md.tmpl",
)
PLACEHOLDER_RE = re.compile(r"\{\{[^{}]+\}\}|<your-[^>]+>|\bTODO\b", re.I)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

BUSINESS_CORE = {
    "business/INDEX.md",
    "business/life-metrics.md",
    "business/raw/README.md",
    "business/company/about.md",
    "business/products/overview.md",
    "business/audience/avatar.md",
}
LITE_OPTIONAL_CONTEXT = {
    "business/marketing/funnel.md",
    "business/marketing/channels.md",
    "business/products/pricing.md",
    "business/assets/brand-guidelines.md",
}

VALID_ANSWER_STATES = {"answered", "unknown_for_now", "not_applicable"}
COMMON_REQUIRED_ANSWERS = {
    "project_identity",
    "primary_audience",
    "nearest_result",
    "first_scope",
    "next_step",
    "onboarding_depth",
    "post_autopilot_decision",
    "privacy_business",
    "privacy_ai_clone",
    "privacy_mastery",
    "remote_decision",
}
FLOW_REQUIRED_ANSWERS = {
    "lite": {
        "lite_primary_action",
        "lite_trust",
        "lite_style",
    },
    "standard": {
        "standard_user_problem",
        "standard_mvp_boundary",
        "standard_user_path",
        "standard_pricing",
        "standard_objections",
        "standard_channels",
        "standard_deep_trigger_screen",
    },
    "deep": {
        "deep_mvp_boundaries",
        "deep_roles",
        "deep_data",
        "deep_integrations",
        "deep_payments",
        "deep_files_audit",
        "deep_ai_boundary",
        "deep_trust_security",
        "deep_economics",
        "deep_marketing_assets",
        "deep_reality_check",
    },
}
BLOCKING_ANSWERS = {
    "project_identity",
    "primary_audience",
    "nearest_result",
    "first_scope",
    "next_step",
    "onboarding_depth",
    "post_autopilot_decision",
    "privacy_business",
    "privacy_ai_clone",
    "privacy_mastery",
    "remote_decision",
    "lite_primary_action",
    "standard_user_problem",
    "standard_mvp_boundary",
    "standard_user_path",
    "standard_deep_trigger_screen",
    "deep_mvp_boundaries",
    "deep_roles",
    "deep_data",
    "deep_integrations",
    "deep_payments",
    "deep_files_audit",
    "deep_ai_boundary",
    "deep_trust_security",
    "deep_reality_check",
}
NOT_APPLICABLE_FORBIDDEN = {
    "project_identity",
    "primary_audience",
    "nearest_result",
    "first_scope",
    "next_step",
    "onboarding_depth",
    "post_autopilot_decision",
    "privacy_business",
    "standard_user_problem",
    "standard_mvp_boundary",
    "standard_deep_trigger_screen",
    "deep_mvp_boundaries",
    "deep_reality_check",
}


class FinalizationError(RuntimeError):
    """A user-facing, non-destructive finalization error."""


@dataclass(frozen=True)
class Entry:
    path: str
    sha256: str | None = None


def is_protected_relative(relative: str) -> bool:
    lowered = relative.casefold()
    return (
        lowered in {path.casefold() for path in PROTECTED_EXACT}
        or lowered.startswith(".env.")
        or lowered.endswith(".local.toml")
        or any(lowered.startswith(prefix.casefold()) for prefix in PROTECTED_PREFIXES)
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def normalize_rel(raw: str) -> str:
    value = raw.replace("\\", "/").strip()
    pure = PurePosixPath(value)
    if (
        not value
        or pure.is_absolute()
        or value.startswith("/")
        or re.match(r"^[a-z]:", value, re.I)
    ):
        raise FinalizationError(f"Недопустимый путь в манифесте: {raw!r}")
    if any(part in {"", ".", ".."} for part in pure.parts):
        raise FinalizationError(f"Недопустимый путь в манифесте: {raw!r}")
    normalized = pure.as_posix()
    lowered = normalized.casefold()
    if lowered == ".git" or lowered.startswith(".git/"):
        raise FinalizationError(f"Манифест не имеет права трогать .git: {raw!r}")
    return normalized


def is_reparse_or_symlink(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(info.st_mode):
        return True
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def checked_path(root: Path, relative: str, *, allow_missing: bool = True) -> Path:
    relative = normalize_rel(relative)
    root_resolved = root.resolve(strict=True)
    current = root_resolved
    for part in PurePosixPath(relative).parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if is_reparse_or_symlink(current):
                raise FinalizationError(f"Symlink или reparse point запрещён: {relative}")
    resolved = current.resolve(strict=False)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise FinalizationError(f"Путь вышел за корень проекта: {relative}") from exc
    if not allow_missing and not current.exists():
        raise FinalizationError(f"Не найден обязательный путь: {relative}")
    return current


def normalized_content(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() not in TEXT_SUFFIXES and not path.name.endswith(".sample"):
        return data
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def content_hash(path: Path) -> str:
    return hashlib.sha256(normalized_content(path)).hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FinalizationError(f"Не найден {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise FinalizationError(f"Некорректный JSON в {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise FinalizationError(f"{label} должен быть JSON-объектом")
    return value


def parse_entries(raw_entries: Any, label: str) -> list[Entry]:
    if not isinstance(raw_entries, list):
        raise FinalizationError(f"{label} должен быть списком")
    entries: list[Entry] = []
    for item in raw_entries:
        if isinstance(item, str):
            entries.append(Entry(normalize_rel(item)))
            continue
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise FinalizationError(f"Некорректная запись в {label}: {item!r}")
        sha256 = item.get("sha256")
        if sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}", str(sha256)):
            raise FinalizationError(f"Некорректный sha256 для {item['path']}")
        entries.append(Entry(normalize_rel(item["path"]), sha256))
    return entries


def load_manifest(root: Path) -> dict[str, Any]:
    manifest_path = checked_path(root, MANIFEST_REL, allow_missing=False)
    manifest = load_json(manifest_path, "манифест очистки")
    if manifest.get("schema_version") != 1:
        raise FinalizationError("Поддерживается только schema_version: 1")

    keep = parse_entries(manifest.get("keep", []), "keep")
    rewrite = parse_entries(manifest.get("rewrite", []), "rewrite")
    remove = parse_entries(manifest.get("remove", []), "remove")
    transient = parse_entries(manifest.get("transient_remove", []), "transient_remove")
    conditional = manifest.get("conditional", [])
    if not isinstance(conditional, list):
        raise FinalizationError("conditional должен быть списком")

    seen: dict[str, str] = {}
    for category, entries in (
        ("keep", keep),
        ("rewrite", rewrite),
        ("remove", remove),
        ("transient_remove", transient),
    ):
        for entry in entries:
            if category in {"remove", "transient_remove"} and is_protected_relative(entry.path):
                raise FinalizationError(f"Манифест не имеет права удалять защищённый путь: {entry.path}")
            identity = entry.path.casefold() if os.name == "nt" else entry.path
            if identity in seen:
                raise FinalizationError(
                    f"Путь {entry.path} одновременно находится в {seen[identity]} и {category}"
                )
            seen[identity] = category

    parsed_groups: list[dict[str, Any]] = []
    group_names: set[str] = set()
    for group in conditional:
        if not isinstance(group, dict) or not isinstance(group.get("name"), str):
            raise FinalizationError(f"Некорректная conditional-группа: {group!r}")
        name = group["name"]
        if name in group_names:
            raise FinalizationError(f"Повтор conditional-группы: {name}")
        group_names.add(name)
        actions = group.get("actions")
        if not isinstance(actions, list) or not actions or not all(isinstance(item, str) for item in actions):
            raise FinalizationError(f"У группы {name} нет допустимых actions")
        entries = parse_entries(group.get("entries", []), f"conditional.{name}.entries")
        prefixes = [normalize_rel(item).rstrip("/") + "/" for item in group.get("owned_prefixes", [])]
        for entry in entries:
            if is_protected_relative(entry.path):
                raise FinalizationError(f"Манифест не имеет права удалять защищённый путь: {entry.path}")
            identity = entry.path.casefold() if os.name == "nt" else entry.path
            if identity in seen:
                raise FinalizationError(
                    f"Путь {entry.path} одновременно находится в {seen[identity]} и conditional.{name}"
                )
            seen[identity] = f"conditional.{name}"
        parsed_groups.append(
            {
                "name": name,
                "actions": actions,
                "entries": entries,
                "owned_prefixes": prefixes,
                "clean_when_kept": bool(group.get("clean_when_kept", False)),
            }
        )

    manifest["_keep"] = keep
    manifest["_rewrite"] = rewrite
    manifest["_remove"] = remove
    manifest["_transient"] = transient
    manifest["_conditional"] = parsed_groups
    manifest["_known_paths"] = {
        entry.path
        for _, entries in (
            ("keep", keep),
            ("rewrite", rewrite),
            ("remove", remove),
            ("transient_remove", transient),
        )
        for entry in entries
    }
    manifest["_known_paths"].update(
        entry.path for group in parsed_groups for entry in group["entries"]
    )
    return manifest


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "null":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def parse_simple_state(path: Path) -> dict[str, dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise FinalizationError(f"Не найден state-файл: {path}") from exc
    result: dict[str, dict[str, Any]] = {}
    current: str | None = None
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        top = re.fullmatch(r"([a-z_]+):\s*", line)
        if top:
            current = top.group(1)
            result.setdefault(current, {})
            continue
        child = re.fullmatch(r"  ([a-z_]+):\s*(.*?)\s*", line)
        if child and current:
            result[current][child.group(1)] = parse_scalar(child.group(2))
    return result


def update_state(root: Path, section: str, updates: dict[str, Any]) -> None:
    path = checked_path(root, STATE_REL, allow_missing=False)
    lines = path.read_text(encoding="utf-8").splitlines()
    section_start: int | None = None
    section_end = len(lines)
    for index, line in enumerate(lines):
        if line == f"{section}:":
            section_start = index
            continue
        if section_start is not None and re.fullmatch(r"[a-z_]+:\s*", line):
            section_end = index
            break
    if section_start is None:
        raise FinalizationError(f"В state-файле нет секции {section}")

    def render(value: Any) -> str:
        if value is None:
            return "null"
        if value is True:
            return "true"
        if value is False:
            return "false"
        return str(value)

    remaining = dict(updates)
    for index in range(section_start + 1, section_end):
        child = re.fullmatch(r"  ([a-z_]+):\s*(.*?)\s*", lines[index])
        if child and child.group(1) in remaining:
            key = child.group(1)
            lines[index] = f"  {key}: {render(remaining.pop(key))}"
    additions = [f"  {key}: {render(value)}" for key, value in remaining.items()]
    lines[section_end:section_end] = additions
    atomic_write_text(path, "\n".join(lines) + "\n")


def set_finalization_stage(root: Path, stage: str, **extra: Any) -> None:
    updates = {"current_stage": stage, "last_safe_stage": stage}
    updates.update(extra)
    update_state(root, "finalization", updates)


def iter_project_entries(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    root = root.resolve(strict=True)
    for current_root, directories, filenames in os.walk(root, topdown=True, followlinks=False):
        current = Path(current_root)
        kept_directories: list[str] = []
        for name in sorted(directories):
            path = current / name
            relative = path.relative_to(root).as_posix()
            if relative == ".git" or relative.startswith(".git/"):
                continue
            if is_reparse_or_symlink(path):
                info = path.lstat()
                entries.append(
                    {
                        "path": relative,
                        "kind": "link",
                        "size": info.st_size,
                        "mtime_ns": info.st_mtime_ns,
                    }
                )
                continue
            kept_directories.append(name)
        directories[:] = kept_directories
        for name in sorted(filenames):
            path = current / name
            relative = path.relative_to(root).as_posix()
            if relative.startswith(".git/"):
                continue
            info = path.lstat()
            entries.append(
                {
                    "path": relative,
                    "kind": "link" if is_reparse_or_symlink(path) else "file",
                    "size": info.st_size,
                    "mtime_ns": info.st_mtime_ns,
                }
            )
    return entries


def is_runtime_path(relative: str) -> bool:
    return relative in RUNTIME_EXACT


def tree_fingerprint(entries: Iterable[dict[str, Any]]) -> str:
    filtered = [
        item
        for item in entries
        if item["path"] != STATE_REL and not is_runtime_path(item["path"])
    ]
    return digest_json(filtered)


def load_decisions(root: Path) -> dict[str, Any]:
    decisions = load_json(checked_path(root, DECISIONS_REL, allow_missing=False), "решения финализации")
    if decisions.get("schema_version") != 1:
        raise FinalizationError("В decisions нужен schema_version: 1")
    return decisions


def candidate_path(root: Path, relative: str) -> Path:
    return checked_path(root, f"{DOCUMENTS_REL}/{normalize_rel(relative)}", allow_missing=False)


def run_command(command: list[str], root: Path, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=root,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def git_info(root: Path) -> dict[str, Any]:
    inside = run_command(["git", "rev-parse", "--is-inside-work-tree"], root)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return {"available": False, "status": [], "remotes": [], "pre_commit": False}
    status = run_command(["git", "status", "--short", "--untracked-files=all"], root)
    remotes = run_command(["git", "remote", "-v"], root)
    git_dir_result = run_command(["git", "rev-parse", "--git-dir"], root)
    pre_commit = False
    if git_dir_result.returncode == 0:
        git_dir = Path(git_dir_result.stdout.strip())
        if not git_dir.is_absolute():
            git_dir = root / git_dir
        pre_commit = (git_dir / "hooks" / "pre-commit").is_file()
    return {
        "available": True,
        "status": [line for line in status.stdout.splitlines() if line.strip()],
        "remotes": [line for line in remotes.stdout.splitlines() if line.strip()],
        "pre_commit": pre_commit,
    }


def hook_smoke(root: Path) -> dict[str, Any]:
    hook = checked_path(root, ".codex/hooks/pre_tool_use_policy.py", allow_missing=False)
    cases = [
        ({"tool": "shell", "input": {"command": "rm -rf tmp"}}, "deny"),
        ({"tool": "shell", "input": {"command": "git status --short"}}, "allow"),
    ]
    results: list[dict[str, str | None]] = []
    passed = True
    for payload, expected in cases:
        completed = run_command([sys.executable, str(hook)], root, json.dumps(payload))
        decision: str | None = None
        try:
            output = json.loads(completed.stdout)
            decision = output.get("hookSpecificOutput", {}).get("permissionDecision")
        except json.JSONDecodeError:
            pass
        results.append({"command": payload["input"]["command"], "expected": expected, "actual": decision})
        passed = passed and decision == expected
    return {"script_smoke_passed": passed, "cases": results}


def find_forbidden_markers(path: Path) -> list[str]:
    if path.suffix.lower() not in TEXT_SUFFIXES and not path.name.endswith(".sample"):
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["файл не читается как UTF-8"]
    return [marker for marker in FORBIDDEN_FINAL_MARKERS if marker.lower() in text.lower()]


def validate_candidate_documents(root: Path, rewrite: list[Entry], decisions: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for entry in rewrite:
        try:
            candidate = candidate_path(root, entry.path)
        except FinalizationError as exc:
            blockers.append(str(exc))
            continue
        if not candidate.is_file():
            blockers.append(f"Нет финальной версии {entry.path}")
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            blockers.append(f"Финальная версия {entry.path} не UTF-8")
            continue
        placeholders = sorted(set(match.group(0) for match in PLACEHOLDER_RE.finditer(text)))
        if placeholders:
            blockers.append(f"В {entry.path} остались placeholder: {', '.join(placeholders)}")
        markers = [marker for marker in FORBIDDEN_FINAL_MARKERS if marker.lower() in text.lower()]
        if markers:
            blockers.append(f"В {entry.path} остались ссылки Starter: {', '.join(markers)}")

    try:
        agents = candidate_path(root, "AGENTS.md").read_text(encoding="utf-8")
    except (FinalizationError, UnicodeDecodeError):
        agents = ""
    if "business/raw/" not in agents or "инструкц" not in agents.lower():
        blockers.append("Финальный AGENTS.md должен считать business/raw/ данными, а не инструкциями")
    prompts_action = decisions.get("conditional", {}).get("prompts")
    if prompts_action == "remove" and "prompts/" in agents:
        blockers.append("AGENTS.md ссылается на prompts/, хотя библиотека выбрана к удалению")
    if "перед новым промптом проверь" in agents.lower():
        blockers.append("AGENTS.md требует открывать prompts/INDEX.md перед каждой задачей")
    return blockers


def validate_future_links(
    root: Path,
    source_paths: set[str],
    future_paths: set[str],
    rewrite_paths: set[str],
) -> list[str]:
    blockers: list[str] = []
    for relative in sorted(source_paths):
        if relative.startswith("business/raw/"):
            continue
        source = candidate_path(root, relative) if relative in rewrite_paths else checked_path(root, relative)
        if not source.is_file() or source.suffix.lower() not in {".md", ".tmpl"}:
            continue
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            blockers.append(f"Активный Markdown не читается как UTF-8: {relative}")
            continue
        for match in MARKDOWN_LINK_RE.finditer(text):
            href = match.group(1).strip().strip("<>")
            if re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I) or href.startswith("#"):
                continue
            href = href.split("#", 1)[0]
            if not href:
                continue
            source_parent = PurePosixPath(relative).parent
            parts: list[str] = []
            invalid = False
            for part in (source_parent / href).parts:
                if part == "..":
                    if not parts:
                        invalid = True
                        break
                    parts.pop()
                elif part not in {"", "."}:
                    parts.append(part)
            target = "/".join(parts).rstrip("/")
            target_exists = target in future_paths or any(
                path.startswith(target + "/") for path in future_paths
            )
            if invalid or not target or not target_exists:
                blockers.append(f"Битая ссылка после очистки: {relative} -> {match.group(1)}")
    return blockers


def validate_state_and_decisions(
    root: Path,
    manifest: dict[str, Any],
    decisions: dict[str, Any],
    git: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    state = parse_simple_state(checked_path(root, STATE_REL, allow_missing=False))
    autopilot = state.get("autopilot", {})
    post = state.get("post_autopilot", {})
    finalization = state.get("finalization", {})
    answers = state.get("answer_states", {})

    flow = autopilot.get("onboarding_depth")
    if autopilot.get("interview_completed") is not True:
        blockers.append("Первое интервью ещё не завершено")
    if flow not in FLOW_REQUIRED_ANSWERS:
        blockers.append("Не записан выбранный flow: lite, standard или deep")
    if post.get("decision") not in {"completed", "skipped"}:
        blockers.append("POST_AUTOPILOT нужно пройти или явно пропустить")
    if finalization.get("current_stage") not in {
        "final_validation",
        "cleanup_preview",
        "cleanup_confirmed",
        "cleanup_running",
        "post_cleanup_validation",
    }:
        blockers.append("Финализация ещё не перешла в final_validation")
    required_answers = set(COMMON_REQUIRED_ANSWERS)
    if flow in FLOW_REQUIRED_ANSWERS:
        required_answers.update(FLOW_REQUIRED_ANSWERS[flow])
    missing = sorted(required_answers - set(answers))
    if missing:
        blockers.append("В state отсутствуют состояния ответов: " + ", ".join(missing))
    invalid = sorted(
        key
        for key in required_answers & set(answers)
        if answers[key] not in VALID_ANSWER_STATES
    )
    if invalid:
        blockers.append("Не закрыты обязательные ответы: " + ", ".join(invalid))
    unresolved_blockers = sorted(
        key
        for key in required_answers & BLOCKING_ANSWERS
        if answers.get(key) == "unknown_for_now"
    )
    if unresolved_blockers:
        blockers.append(
            "Блокирующие ответы нельзя оставить неизвестными: "
            + ", ".join(unresolved_blockers)
        )
    invalid_not_applicable = sorted(
        key
        for key in required_answers & NOT_APPLICABLE_FORBIDDEN
        if answers.get(key) == "not_applicable"
    )
    if invalid_not_applicable:
        blockers.append(
            "Эти ответы нельзя пометить неприменимыми: "
            + ", ".join(invalid_not_applicable)
        )

    if decisions.get("post_autopilot") not in {"completed", "skipped"}:
        blockers.append("В decisions не записано решение по POST_AUTOPILOT")
    if decisions.get("post_autopilot") != post.get("decision"):
        blockers.append("Решение POST_AUTOPILOT в state и decisions не совпадает")
    privacy = decisions.get("privacy")
    if not isinstance(privacy, dict):
        blockers.append("В decisions отсутствует privacy")
    else:
        if privacy.get("business") not in {"ignored", "tracked_private_confirmed", "not_git"}:
            blockers.append("Не решена приватность business/")
        if privacy.get("ai_clone") not in {
            "tracked_private",
            "ignored",
            "safe_summary_only",
            "not_applicable",
        }:
            blockers.append("Не решена приватность ai-clone/")
        if privacy.get("mastery") not in {"tracked", "ignored", "not_applicable"}:
            blockers.append("Не решена приватность mastery/")

    conditional = decisions.get("conditional")
    if not isinstance(conditional, dict):
        blockers.append("В decisions отсутствует conditional")
        conditional = {}
    for group in manifest["_conditional"]:
        action = conditional.get(group["name"])
        if action not in group["actions"]:
            blockers.append(
                f"Для {group['name']} нужен выбор: {', '.join(group['actions'])}"
            )

    if git["available"]:
        if git["remotes"] and decisions.get("remote") != "acknowledged":
            blockers.append("Нужно осознанно подтвердить существующий Git remote")
    elif not decisions.get("no_git_cleanup_confirmed"):
        blockers.append("Без Git нужно отдельно подтвердить отсутствие простого отката")
    if decisions.get("codex_hook") not in {
        "configured_smoke_passed",
        "configured_unconfirmed",
    }:
        blockers.append("В decisions не записан честный статус Codex policy-hook")
    return blockers


def validate_business(
    root: Path,
    decisions: dict[str, Any],
    git: dict[str, Any],
    flow: str | None,
) -> list[str]:
    blockers: list[str] = []
    for relative in sorted(BUSINESS_CORE):
        path = checked_path(root, relative)
        if not path.is_file():
            blockers.append(f"Не найден обязательный файл {relative}")
    if flow == "lite" and not any(checked_path(root, path).is_file() for path in LITE_OPTIONAL_CONTEXT):
        blockers.append(
            "Для lite нужен один прикладной контекст: funnel, channels, pricing или brand-guidelines"
        )
    if flow == "standard" and not checked_path(root, "business/marketing/funnel.md").is_file():
        blockers.append("Для standard не найден обязательный business/marketing/funnel.md")
    if flow == "deep":
        overview_path = checked_path(root, "business/products/overview.md")
        if overview_path.is_file():
            overview = overview_path.read_text(encoding="utf-8")
            missing_scope = [
                marker
                for marker in ("MVP сейчас", "Later", "Не делаем")
                if marker.lower() not in overview.lower()
            ]
            if missing_scope:
                blockers.append(
                    "В deep products/overview.md нет явного MVP vs later: "
                    + ", ".join(missing_scope)
                )

    business_root = checked_path(root, "business")
    if business_root.is_dir():
        for current_root, directories, filenames in os.walk(business_root, followlinks=False):
            current = Path(current_root)
            relative_dir = current.relative_to(root).as_posix()
            directories[:] = [
                name
                for name in directories
                if not is_reparse_or_symlink(current / name)
            ]
            if relative_dir == "business/raw" or relative_dir.startswith("business/raw/"):
                directories[:] = []
                continue
            for name in filenames:
                path = current / name
                if path.suffix.lower() not in {".md", ".txt"} or is_reparse_or_symlink(path):
                    continue
                relative = path.relative_to(root).as_posix()
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    blockers.append(f"Рабочий бизнес-файл не читается как UTF-8: {relative}")
                    continue
                placeholders = sorted(set(match.group(0) for match in PLACEHOLDER_RE.finditer(text)))
                if placeholders:
                    blockers.append(
                        f"В {relative} остались placeholder: {', '.join(placeholders)}"
                    )
                markers = [
                    marker
                    for marker in FORBIDDEN_FINAL_MARKERS
                    if marker.lower() in text.lower()
                ]
                if markers:
                    blockers.append(
                        f"В {relative} остались Starter-ссылки: {', '.join(markers)}"
                    )
    gitignore = checked_path(root, ".gitignore", allow_missing=False).read_text(encoding="utf-8")
    privacy = decisions.get("privacy", {}).get("business")
    if privacy == "ignored" and "/business/" not in gitignore:
        blockers.append("Для privacy=ignored в .gitignore нет /business/")
    if git["available"] and privacy == "ignored":
        tracked = run_command(["git", "ls-files", "business/*"], root)
        if tracked.stdout.strip():
            blockers.append("business/ выбран приватным, но содержит tracked-файлы")
    return blockers


def group_unknown_files(entries: list[dict[str, Any]], known: set[str]) -> list[str]:
    unknown: list[str] = []
    for item in entries:
        relative = item["path"]
        if is_runtime_path(relative) or relative == STATE_REL:
            continue
        if relative not in known:
            unknown.append(relative)
    return sorted(unknown)


def ensure_expected_hash(root: Path, entry: Entry, blockers: list[str], label: str) -> None:
    path = checked_path(root, entry.path)
    if not path.exists():
        return
    if not path.is_file():
        blockers.append(f"{label}: {entry.path} не является обычным файлом")
        return
    if not entry.sha256:
        blockers.append(f"{label}: у {entry.path} нет контрольного sha256")
        return
    actual = content_hash(path)
    if actual != entry.sha256:
        blockers.append(f"{label}: {entry.path} изменён и не будет удалён автоматически")


def build_preview(root: Path) -> tuple[dict[str, Any], list[str]]:
    manifest = load_manifest(root)
    decisions = load_decisions(root)
    entries = iter_project_entries(root)
    git = git_info(root)
    state = parse_simple_state(checked_path(root, STATE_REL, allow_missing=False))
    flow = state.get("autopilot", {}).get("onboarding_depth")
    required_answers = set(COMMON_REQUIRED_ANSWERS)
    if flow in FLOW_REQUIRED_ANSWERS:
        required_answers.update(FLOW_REQUIRED_ANSWERS[flow])
    deferred_answers = sorted(
        key
        for key in required_answers
        if state.get("answer_states", {}).get(key) == "unknown_for_now"
    )
    blockers = validate_state_and_decisions(root, manifest, decisions, git)
    blockers.extend(validate_business(root, decisions, git, flow))
    blockers.extend(validate_candidate_documents(root, manifest["_rewrite"], decisions))

    remove_entries: list[Entry] = list(manifest["_remove"])
    keep_paths = {entry.path for entry in manifest["_keep"]}
    conditional_result: dict[str, dict[str, Any]] = {}
    decisions_conditional = decisions.get("conditional", {})
    for entry in remove_entries:
        ensure_expected_hash(root, entry, blockers, "remove")

    for group in manifest["_conditional"]:
        action = decisions_conditional.get(group["name"])
        conditional_result[group["name"]] = {
            "action": action,
            "paths": [entry.path for entry in group["entries"]],
        }
        if action == "remove":
            for entry in group["entries"]:
                ensure_expected_hash(root, entry, blockers, f"conditional.{group['name']}")
                remove_entries.append(entry)
        elif action in {"keep", "keep_rewritten"}:
            keep_paths.update(entry.path for entry in group["entries"])
            if group["clean_when_kept"]:
                for entry in group["entries"]:
                    path = checked_path(root, entry.path)
                    if path.is_file():
                        markers = find_forbidden_markers(path)
                        if markers:
                            blockers.append(
                                f"{entry.path} сохраняется, но содержит Starter-ссылки: {', '.join(markers)}"
                            )

    known = set(manifest["_known_paths"])
    known.update(RUNTIME_EXACT)
    known.add(STATE_REL)
    for item in entries:
        if is_runtime_path(item["path"]):
            known.add(item["path"])
    unknown = group_unknown_files(entries, known)
    for relative in unknown:
        if relative.startswith(DOCUMENTS_REL + "/"):
            blockers.append(
                "Неизвестный файл во временной папке финализации нужно сохранить или перенести вручную: "
                + relative
            )
        if any(relative.startswith(prefix) for prefix in RESERVED_STARTER_PREFIXES):
            blockers.append(
                f"Неизвестный файл внутри служебной зоны Starter нужно сохранить или перенести вручную: {relative}"
            )

    protected_conflicts = [
        entry.path
        for entry in remove_entries
        if is_protected_relative(entry.path)
    ]
    if protected_conflicts:
        blockers.append("Манифест пытается удалить защищённые пути: " + ", ".join(protected_conflicts))

    future_paths = {item["path"] for item in entries if item["kind"] == "file"}
    future_paths.difference_update(entry.path for entry in remove_entries)
    future_paths.difference_update(entry.path for entry in manifest["_transient"])
    future_paths.update(entry.path for entry in manifest["_rewrite"])
    link_source_paths = {
        path
        for path in future_paths
        if path in keep_paths
        or path in {entry.path for entry in manifest["_rewrite"]}
        or (path.startswith("business/") and not path.startswith("business/raw/"))
    }
    blockers.extend(
        validate_future_links(
            root,
            link_source_paths,
            future_paths,
            {entry.path for entry in manifest["_rewrite"]},
        )
    )

    hook = hook_smoke(root)
    if not hook["script_smoke_passed"]:
        blockers.append("Policy-hook не прошёл прямой smoke-test")
    if (
        decisions.get("codex_hook") == "configured_smoke_passed"
        and not hook["script_smoke_passed"]
    ):
        blockers.append("Policy-hook отмечен рабочим, но прямой smoke-test это не подтвердил")

    local_secret_names = sorted(
        item["path"]
        for item in entries
        if item["path"] == ".env"
        or item["path"].startswith(".env.")
        or item["path"].endswith(".local.toml")
    )
    if local_secret_names and not decisions.get("local_secret_files_acknowledged"):
        blockers.append(
            "Найдены локальные секретные файлы. Их содержимое не читалось; нужно подтвердить их локальное хранение"
        )

    rewrite_data: list[dict[str, Any]] = []
    for entry in manifest["_rewrite"]:
        candidate = candidate_path(root, entry.path)
        current = checked_path(root, entry.path)
        rewrite_data.append(
            {
                "path": entry.path,
                "current_sha256": content_hash(current) if current.is_file() else None,
                "candidate_sha256": content_hash(candidate),
            }
        )

    all_remove_paths = {entry.path for entry in remove_entries}
    all_remove_paths.update(entry.path for entry in manifest["_transient"])
    payload = {
        "schema_version": 1,
        "flow": flow,
        "root": str(root.resolve(strict=True)),
        "manifest_sha256": content_hash(checked_path(root, MANIFEST_REL, allow_missing=False)),
        "decisions_sha256": content_hash(checked_path(root, DECISIONS_REL, allow_missing=False)),
        "tree_hash": tree_fingerprint(entries),
        "rewrite": rewrite_data,
        "remove": sorted(all_remove_paths),
        "keep": sorted(keep_paths),
        "conditional": conditional_result,
        "preserved_unknown": unknown,
        "git": git,
        "hook": hook,
        "local_secret_files": local_secret_names,
        "deferred_answers": deferred_answers,
    }
    payload["preview_id"] = digest_json(payload)
    return payload, sorted(set(blockers))


def print_blockers(blockers: list[str]) -> None:
    print("Финализация остановлена.")
    print("Готово: проверка выполнена, рабочие файлы не изменены.")
    print("Нужно решить:")
    for blocker in blockers:
        print(f"- {blocker}")
    print("Можно уточнить позже: вернёмся к этому после блокирующих пунктов.")
    print("Ничего не удалено.")


def command_preview(root: Path) -> int:
    preview, blockers = build_preview(root)
    if blockers:
        print_blockers(blockers)
        return 2
    preview["created_at"] = utc_now()
    atomic_write_json(checked_path(root, PREVIEW_REL), preview)
    set_finalization_stage(
        root,
        "cleanup_preview",
        preview_id=preview["preview_id"],
        preview_tree_hash=preview["tree_hash"],
        approved_preview_id=None,
    )
    print("Финальная проверка пройдена.")
    print("Готово:")
    print(f"Будет переписано файлов: {len(preview['rewrite'])}")
    print(f"Будет удалено файлов: {len(preview['remove'])}")
    print(f"Неизвестных файлов сохраняется: {len(preview['preserved_unknown'])}")
    print(f"Preview: {preview['preview_id']}")
    if preview["deferred_answers"]:
        print("Можно уточнить позже: " + ", ".join(preview["deferred_answers"]))
    else:
        print("Можно уточнить позже: нет открытых вопросов.")
    print("Рабочие документы не изменены, файлы не удалены.")
    return 0


def safe_remove_file(root: Path, entry: Entry) -> bool:
    if is_protected_relative(entry.path):
        raise FinalizationError(f"Отказ удаления защищённого пути: {entry.path}")
    path = checked_path(root, entry.path)
    if not path.exists():
        return False
    if not path.is_file():
        raise FinalizationError(f"Отказ удаления: {entry.path} не является обычным файлом")
    if entry.sha256 and content_hash(path) != entry.sha256:
        raise FinalizationError(f"Отказ удаления: {entry.path} изменился после preview")
    path.unlink()
    return True


def rewrite_from_candidate(root: Path, relative: str, expected_hash: str) -> bool:
    target = checked_path(root, relative)
    candidate = candidate_path(root, relative)
    if content_hash(candidate) != expected_hash:
        raise FinalizationError(f"Финальная версия {relative} изменилась после preview")
    if target.is_file() and content_hash(target) == expected_hash:
        return False
    text = candidate.read_text(encoding="utf-8")
    atomic_write_text(target, text)
    return True


def remove_empty_parents(root: Path, paths: Iterable[str]) -> None:
    root_resolved = root.resolve(strict=True)
    parents: set[Path] = set()
    for relative in paths:
        path = checked_path(root, relative)
        parent = path.parent
        while parent != root_resolved:
            parents.add(parent)
            parent = parent.parent
    for parent in sorted(parents, key=lambda item: len(item.parts), reverse=True):
        if not parent.exists() or is_reparse_or_symlink(parent):
            continue
        try:
            parent.rmdir()
        except OSError:
            pass


class Journal:
    def __init__(self, root: Path, preview: dict[str, Any], fail_after: int | None) -> None:
        self.root = root
        self.path = checked_path(root, RUNTIME_REL)
        self.fail_after = fail_after
        preview_id = str(preview.get("preview_id"))
        if self.path.exists():
            data = load_json(self.path, "runtime journal")
            if data.get("preview_id") != preview_id:
                raise FinalizationError("Runtime journal относится к другому preview")
            self.data = data
        else:
            self.data = {
                "schema_version": 1,
                "preview_id": preview_id,
                "preview": preview,
                "stage": "cleanup_running",
                "completed_operations": [],
                "started_at": utc_now(),
            }
            atomic_write_json(self.path, self.data)

    @property
    def completed(self) -> set[str]:
        return set(self.data.get("completed_operations", []))

    def run(self, operation: str, callback: Any) -> None:
        if operation in self.completed:
            return
        callback()
        self.data.setdefault("completed_operations", []).append(operation)
        atomic_write_json(self.path, self.data)
        if self.fail_after is not None and len(self.data["completed_operations"]) >= self.fail_after:
            raise FinalizationError("Тестовое прерывание после безопасной операции")

    def set_stage(self, stage: str) -> None:
        self.data["stage"] = stage
        atomic_write_json(self.path, self.data)


def clean_tree_checks(root: Path, preview: dict[str, Any], *, prospective: bool) -> list[str]:
    blockers: list[str] = []
    for relative in preview["remove"]:
        if prospective and (
            relative in LATE_REMOVE
            or is_runtime_path(relative)
            or relative.startswith("autopilot/finalization/")
        ):
            continue
        if checked_path(root, relative).exists():
            blockers.append(f"После очистки остался {relative}")
    for item in preview["rewrite"]:
        relative = item["path"]
        if prospective and relative in REWRITE_LATE:
            path = candidate_path(root, relative)
        else:
            path = checked_path(root, relative)
        if not path.is_file() or content_hash(path) != item["candidate_sha256"]:
            blockers.append(f"Финальный документ не совпадает с preview: {relative}")
        elif find_forbidden_markers(path):
            blockers.append(f"В финальном документе остались Starter-ссылки: {relative}")
    for relative in ("business/INDEX.md", "business/life-metrics.md", "business/raw/README.md"):
        if not checked_path(root, relative).is_file():
            blockers.append(f"После очистки отсутствует {relative}")
    return blockers


def applied_document_checks(root: Path, preview: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for item in preview["rewrite"]:
        path = checked_path(root, item["path"])
        if not path.is_file() or content_hash(path) != item["candidate_sha256"]:
            blockers.append(f"Финальный документ не применён: {item['path']}")
        elif find_forbidden_markers(path):
            blockers.append(f"В финальном документе остались Starter-ссылки: {item['path']}")
    return blockers


def command_apply(root: Path, approve: str, fail_after: int | None) -> int:
    preview_path = checked_path(root, PREVIEW_REL)
    runtime_path = checked_path(root, RUNTIME_REL)
    if preview_path.exists():
        preview = load_json(preview_path, "cleanup preview")
    elif runtime_path.exists():
        runtime_data = load_json(runtime_path, "runtime journal")
        preview = runtime_data.get("preview")
        if not isinstance(preview, dict):
            raise FinalizationError("В runtime journal нет сохранённого preview")
    else:
        raise FinalizationError("Не найден cleanup preview")
    if approve != preview.get("preview_id"):
        raise FinalizationError("Подтверждение не совпадает с показанным preview")

    resuming = runtime_path.exists()
    if not resuming:
        current, blockers = build_preview(root)
        if blockers:
            print_blockers(blockers)
            return 2
        if current["preview_id"] != approve:
            raise FinalizationError("Дерево изменилось после preview. Сначала создайте новый preview")
        update_state(root, "finalization", {"approved_preview_id": approve})
        set_finalization_stage(root, "cleanup_confirmed", approved_preview_id=approve)
        set_finalization_stage(root, "cleanup_running", approved_preview_id=approve)

    manifest = load_manifest(root)
    remove_by_path: dict[str, Entry] = {entry.path: entry for entry in manifest["_remove"]}
    for group in manifest["_conditional"]:
        remove_by_path.update({entry.path: entry for entry in group["entries"]})

    journal = Journal(root, preview, fail_after)
    rewrite_by_path = {item["path"]: item for item in preview["rewrite"]}
    transient_paths = {entry.path for entry in manifest["_transient"]}

    for relative in sorted(set(rewrite_by_path) - REWRITE_LATE):
        item = rewrite_by_path[relative]
        journal.run(
            f"rewrite:{relative}",
            lambda relative=relative, item=item: rewrite_from_candidate(
                root, relative, item["candidate_sha256"]
            ),
        )

    early_remove = [
        relative
        for relative in preview["remove"]
        if relative not in LATE_REMOVE
        and relative not in transient_paths
        and not relative.startswith("autopilot/finalization/")
    ]
    for relative in sorted(early_remove):
        entry = remove_by_path[relative]
        journal.run(
            f"remove:{relative}",
            lambda entry=entry: safe_remove_file(root, entry),
        )
    remove_empty_parents(root, early_remove)

    journal.set_stage("post_cleanup_validation")
    set_finalization_stage(root, "post_cleanup_validation", approved_preview_id=approve)
    blockers = clean_tree_checks(root, preview, prospective=True)
    if blockers:
        print_blockers(blockers)
        return 2

    if "AGENTS.md" in rewrite_by_path:
        item = rewrite_by_path["AGENTS.md"]
        journal.run(
            "rewrite:AGENTS.md",
            lambda: rewrite_from_candidate(root, "AGENTS.md", item["candidate_sha256"]),
        )

    for relative in ("AUTOPILOT.md", "POST_AUTOPILOT.md"):
        if relative in remove_by_path:
            entry = remove_by_path[relative]
            journal.run(
                f"remove:{relative}",
                lambda entry=entry: safe_remove_file(root, entry),
            )

    if checked_path(root, STATE_REL).exists():
        update_state(root, "autopilot", {"completed": True, "current_stage": "done"})
        set_finalization_stage(root, "completed", completed_at=utc_now(), approved_preview_id=approve)
    journal.set_stage("completed")

    if "PROJECT_STATE.md" in rewrite_by_path:
        item = rewrite_by_path["PROJECT_STATE.md"]
        journal.run(
            "rewrite:PROJECT_STATE.md",
            lambda: rewrite_from_candidate(root, "PROJECT_STATE.md", item["candidate_sha256"]),
        )

    blockers = applied_document_checks(root, preview)
    if blockers:
        print_blockers(blockers)
        return 2

    journal.run(
        f"remove:{STATE_REL}",
        lambda: checked_path(root, STATE_REL).unlink(missing_ok=True),
    )

    late_manifest_paths = [
        relative
        for relative in preview["remove"]
        if relative.startswith("autopilot/finalization/")
        and relative != "autopilot/finalization/finalize.py"
        and relative in remove_by_path
    ]
    for relative in sorted(late_manifest_paths):
        entry = remove_by_path[relative]
        journal.run(
            f"remove:{relative}",
            lambda entry=entry: safe_remove_file(root, entry),
        )

    for relative in (DECISIONS_REL, PREVIEW_REL):
        checked_path(root, relative).unlink(missing_ok=True)

    documents = checked_path(root, DOCUMENTS_REL)
    if documents.exists():
        for name in ("AGENTS.md", "PROJECT_STATE.md", "README.md", "STRUCTURE.md"):
            checked_path(root, f"{DOCUMENTS_REL}/{name}").unlink(missing_ok=True)
        try:
            documents.rmdir()
        except OSError as exc:
            raise FinalizationError(
                "Во временной папке финализации остались неизвестные файлы; они не удалены"
            ) from exc

    runtime_path.unlink(missing_ok=True)
    checked_path(root, MANIFEST_REL).unlink(missing_ok=True)
    self_path = checked_path(root, "autopilot/finalization/finalize.py")
    self_path.unlink(missing_ok=True)
    remove_empty_parents(root, preview["remove"])

    print("Очистка и автоматическая проверка завершены.")
    top_level = sorted(path.name for path in root.iterdir())
    print("В корне осталось: " + ", ".join(top_level))
    print("Осталось открыть новое окно Codex и убедиться, что он видит обычный рабочий проект.")
    return 0


def command_status(root: Path) -> int:
    state_path = checked_path(root, STATE_REL)
    if not state_path.exists():
        print("State-файл отсутствует. Starter уже очищен или финализация ещё не настроена.")
        return 0
    state = parse_simple_state(state_path)
    finalization = state.get("finalization", {})
    print(f"Текущая стадия: {finalization.get('current_stage', 'unknown')}")
    print(f"Последняя безопасная стадия: {finalization.get('last_safe_stage', 'unknown')}")
    preview = finalization.get("preview_id")
    if preview:
        print(f"Preview: {preview}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safe Codex Starter finalization")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="project root")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("preview", help="validate and create a no-write cleanup preview")
    apply_parser = subparsers.add_parser("apply", help="apply one approved preview")
    apply_parser.add_argument("--approve", required=True, help="exact preview id shown to the user")
    apply_parser.add_argument("--fail-after", type=int, help=argparse.SUPPRESS)
    subparsers.add_parser("status", help="show the safe recovery checkpoint")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise FinalizationError(f"Корень проекта не является папкой: {root}")
        if args.command == "preview":
            return command_preview(root)
        if args.command == "apply":
            return command_apply(root, args.approve, args.fail_after)
        return command_status(root)
    except FinalizationError as exc:
        print(f"Финализация остановлена: {exc}", file=sys.stderr)
        print("Неизвестные и пользовательские файлы не удалялись.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
