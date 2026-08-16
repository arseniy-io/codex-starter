#!/usr/bin/env python3
"""Structural lint for Codex Starter.

By default this script checks the pristine starter-template shape, not a user
project's app code. Use ``--onboarded`` for a copy after the interview and
before the confirmed cleanup. It intentionally has no third-party dependencies.
"""

from __future__ import annotations

import json
import hashlib
import os
import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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


failures: list[str] = []

PUBLIC_SURFACES = [
    "README.md",
    "AGENTS.md",
    "PROJECT_STATE.md",
    "STRUCTURE.md",
    "TROUBLESHOOTING.md",
    "QUALITY_CHECKLIST.md",
    "CHANGELOG.md",
]

PLACEHOLDER_PATTERNS = [
    re.compile(r"\{\{[^{}\n]+\}\}"),
    re.compile(
        r"\[(?:ISO-время|preview_id|точный список|название|описание|значение|"
        r"источник|ГГГГ-ММ-ДД|lite/standard/deep|1-2 причины)[^\]]*\]",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:TBD|CHANGEME|REPLACE_ME)\b", re.IGNORECASE),
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def fail(label: str, detail: str | None = None) -> None:
    failures.append(label if detail is None else f"{label}: {detail}")
    print(f"FAIL: {label}")
    if detail:
        print(f"  {detail}")


def ok(label: str) -> None:
    print(f"OK: {label}")


def run(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def iter_files() -> list[Path]:
    ignored_dirs = {".git", "node_modules", ".next", "dist", "build", "coverage"}
    files: list[Path] = []
    for current_root, dirs, names in os.walk(ROOT):
        dirs[:] = [name for name in dirs if name not in ignored_dirs]
        for name in names:
            path = Path(current_root) / name
            if path.suffix.lower() in TEXT_SUFFIXES or path.name.endswith(".sample"):
                files.append(path)
    return files


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_utf8(files: list[Path]) -> bool:
    unreadable: list[str] = []
    for path in files:
        try:
            read_text(path)
        except UnicodeDecodeError as exc:
            unreadable.append(f"{rel(path)}: byte {exc.start}")

    if unreadable:
        fail("UTF-8 readable", "\n  ".join(unreadable))
        return False
    ok("all checked text files are UTF-8 readable")
    return True


def normalized_hash(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES or path.name.endswith(".sample"):
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            pass
        else:
            data = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def check_autopilot_state() -> None:
    state_path = ROOT / ".codex" / "autopilot-state.yml"
    if not state_path.exists():
        fail("autopilot state exists", rel(state_path))
        return

    state = read_text(state_path)
    required = [
        "schema_version: 2",
        "autopilot:",
        "  completed: false",
        "  interview_completed: false",
        "  current_stage: start",
        "  current_flow: null",
        "  last_completed_step: 0",
        "  last_completed_substep: null",
        "  started_at: null",
        "  os: null",
        "  project_type: null",
        "  stack: null",
        "  onboarding_depth: null",
        "post_autopilot:",
        "  completed: false",
        "  decision: pending",
        "  last_completed_stage: 0",
        "  privacy_business: null",
        "  privacy_ai_clone: null",
        "  privacy_mastery: null",
        "finalization:",
        "  current_stage: interview",
        "  last_safe_stage: interview",
        "  preview_id: null",
        "answer_states:",
        "  project_identity: pending",
        "  onboarding_depth: pending",
        "  lite_primary_action: pending",
        "  standard_deep_trigger_screen: pending",
        "  deep_reality_check: pending",
        "  post_autopilot_decision: pending",
        "  privacy_business: pending",
        "  remote_decision: pending",
    ]
    missing = [item for item in required if item not in state]
    if missing:
        fail("autopilot state baseline", ", ".join(missing))
    else:
        ok("autopilot state baseline")

    for scenario in ("AUTOPILOT.md", "POST_AUTOPILOT.md"):
        path = ROOT / scenario
        first_line = read_text(path).splitlines()[0]
        if first_line == "---":
            fail("scenario file has mutable frontmatter", scenario)
        else:
            ok(f"{scenario} has no YAML frontmatter")


def check_business_clean() -> None:
    business_dir = ROOT / "business"
    if business_dir.exists():
        fail("root business absent in starter-template", rel(business_dir))
    else:
        ok("root business absent")

    git = run(["git", "ls-files", "business/*"])
    tracked = [line for line in git.stdout.splitlines() if line.strip()]
    if tracked:
        fail("root business not tracked", "\n  ".join(tracked))
    else:
        ok("root business not tracked")


def check_onboarded_autopilot_state() -> None:
    state_path = ROOT / ".codex" / "autopilot-state.yml"
    if not state_path.exists():
        fail("onboarded autopilot state exists", rel(state_path))
        return

    state = read_text(state_path)
    required = [
        "autopilot:",
        "  completed: false",
        "  interview_completed: true",
        "  current_flow: null",
        "  last_completed_step: 10",
        "post_autopilot:",
        "finalization:",
    ]
    missing = [item for item in required if item not in state]
    if missing:
        fail("pre-cleanup autopilot state", ", ".join(missing))
    else:
        ok("pre-cleanup autopilot state")

    allowed_finalization = (
        "  current_stage: final_validation",
        "  current_stage: cleanup_preview",
        "  current_stage: cleanup_confirmed",
        "  current_stage: cleanup_running",
        "  current_stage: post_cleanup_validation",
    )
    if any(value in state for value in allowed_finalization):
        ok("pre-cleanup finalization stage")
    else:
        fail("pre-cleanup finalization stage", "expected final_validation or later")

    if "  onboarding_depth: lite" in state:
        ok("onboarded flow recorded (lite)")
    elif "  onboarding_depth: standard" in state:
        ok("onboarded flow recorded (standard)")
    elif "  onboarding_depth: deep" in state:
        ok("onboarded flow recorded (deep)")
    else:
        fail("onboarded flow recorded", "onboarding_depth should be lite, standard or deep")


def check_onboarded_business() -> None:
    business_dir = ROOT / "business"
    if not business_dir.exists():
        fail("onboarded business exists", rel(business_dir))
        return
    ok("onboarded business exists")

    required_files = [
        "business/INDEX.md",
        "business/life-metrics.md",
        "business/raw/README.md",
    ]
    missing = [path for path in required_files if not (ROOT / path).exists()]
    if missing:
        fail("onboarded business core files", ", ".join(missing))
    else:
        ok("onboarded business core files")

    git = run(["git", "ls-files", "business/*"])
    tracked = [line for line in git.stdout.splitlines() if line.strip()]
    if tracked:
        fail("onboarded business not tracked", "\n  ".join(tracked))
    else:
        ok("onboarded business not tracked")

    if (ROOT / "business" / "INDEX.md").exists():
        index = read_text(ROOT / "business" / "INDEX.md")
        required_snippets = ["business/life-metrics.md", "1-3"]
        missing_snippets = [snippet for snippet in required_snippets if snippet not in index]
        if missing_snippets:
            fail("onboarded business index routes context", ", ".join(missing_snippets))
        else:
            ok("onboarded business index routes context")


def check_onboarded_context_route() -> None:
    required_files = [
        ".codex/finalization-documents/AGENTS.md",
        ".codex/finalization-documents/PROJECT_STATE.md",
        ".codex/finalization-documents/README.md",
        ".codex/finalization-documents/STRUCTURE.md",
    ]
    missing = [path for path in required_files if not (ROOT / path).exists()]
    if missing:
        fail("onboarded context entry files", ", ".join(missing))
        return
    ok("onboarded context entry files")

    agents = read_text(ROOT / ".codex/finalization-documents/AGENTS.md")
    project_state = read_text(ROOT / ".codex/finalization-documents/PROJECT_STATE.md")
    checks = [
        ("AGENTS routes PROJECT_STATE", agents, "PROJECT_STATE.md"),
        ("AGENTS routes business index", agents, "business/INDEX.md"),
        ("AGENTS routes live metrics", agents, "business/life-metrics.md"),
        ("PROJECT_STATE routes business index", project_state, "business/INDEX.md"),
        ("PROJECT_STATE avoids full context by default", project_state, "весь `business/`"),
    ]
    missing_routes = [label for label, text, snippet in checks if snippet not in text]
    if missing_routes:
        fail("onboarded context route", ", ".join(missing_routes))
    else:
        ok("onboarded context route")


def check_unresolved_placeholders(onboarded: bool) -> None:
    paths: list[Path] = []
    if onboarded:
        documents = ROOT / ".codex" / "finalization-documents"
        if documents.exists():
            paths.extend(path for path in documents.rglob("*") if path.is_file())
        business = ROOT / "business"
        if business.exists():
            paths.extend(
                path
                for path in business.rglob("*")
                if path.is_file() and "raw" not in path.relative_to(business).parts
            )
    else:
        paths.extend(ROOT / relative for relative in PUBLIC_SURFACES if (ROOT / relative).is_file())

    hits: list[str] = []
    for path in paths:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        for line_no, line in enumerate(read_text(path).splitlines(), start=1):
            if any(pattern.search(line) for pattern in PLACEHOLDER_PATTERNS):
                hits.append(f"{rel(path)}:{line_no}:{line[:140]}")

    if hits:
        fail("unresolved placeholders", "\n  ".join(hits))
    else:
        ok("no unresolved placeholders on published surfaces")


def load_onboarded_contract() -> dict[str, object] | None:
    path = ROOT / "autopilot" / "finalization" / "onboarded-contract.json"
    if not path.is_file():
        fail("onboarded reference contract", rel(path))
        return None
    try:
        contract = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail("onboarded reference contract", str(exc))
        return None
    if not isinstance(contract, dict) or contract.get("schema_version") != 1:
        fail("onboarded reference contract", "expected schema_version 1")
        return None
    return contract


def contract_path_forbidden(path: str, forbidden: list[str]) -> bool:
    return any(
        path.startswith(item) if item.endswith("/") else path == item
        for item in forbidden
    )


def validate_flow_paths(
    flow: str,
    paths: set[str],
    contract: dict[str, object],
) -> list[str]:
    problems: list[str] = []
    common = contract.get("common_required_files")
    flows = contract.get("flows")
    if not isinstance(common, list) or not all(isinstance(item, str) for item in common):
        return ["common_required_files must be a list of paths"]
    if not isinstance(flows, dict) or not isinstance(flows.get(flow), dict):
        return [f"missing flow contract: {flow}"]

    settings = flows[flow]
    required = [*common, *settings.get("required_files", [])]
    missing = sorted(path for path in required if path not in paths)
    if missing:
        problems.append("missing: " + ", ".join(missing))

    groups = settings.get("required_any", [])
    for group in groups:
        if not isinstance(group, list) or not any(path in paths for path in group):
            problems.append("need one of: " + ", ".join(group))

    forbidden = settings.get("forbidden_paths", [])
    blocked = sorted(path for path in paths if contract_path_forbidden(path, forbidden))
    if blocked:
        problems.append("forbidden for flow: " + ", ".join(blocked))

    working = {
        path
        for path in paths
        if path.startswith("business/")
        and path.endswith(".md")
        and path != "business/life-metrics.md"
        and not path.startswith("business/raw/")
    }
    expected_range = settings.get("working_markdown_files")
    if (
        not isinstance(expected_range, list)
        or len(expected_range) != 2
        or not all(isinstance(item, int) for item in expected_range)
    ):
        problems.append("working_markdown_files must contain min and max")
    elif not expected_range[0] <= len(working) <= expected_range[1]:
        problems.append(
            f"working business files: expected {expected_range[0]}-{expected_range[1]}, got {len(working)}"
        )

    return problems


def check_onboarded_reference_contract(onboarded: bool) -> None:
    contract = load_onboarded_contract()
    if contract is None:
        return
    flows = contract.get("flows")
    if not isinstance(flows, dict) or set(flows) != {"lite", "standard", "deep"}:
        fail("onboarded reference contract", "flows must be lite, standard and deep")
        return

    definition_problems: list[str] = []
    for flow in ("lite", "standard", "deep"):
        settings = flows.get(flow)
        reference = settings.get("reference_minimum") if isinstance(settings, dict) else None
        if not isinstance(reference, list) or not all(isinstance(item, str) for item in reference):
            definition_problems.append(f"{flow}: reference_minimum must be a list of paths")
            continue
        definition_problems.extend(
            f"{flow}: {problem}" for problem in validate_flow_paths(flow, set(reference), contract)
        )

    if definition_problems:
        fail("onboarded reference contract", "\n  ".join(definition_problems))
        return
    ok("lite, standard and deep reference minimums")

    if not onboarded:
        return

    state = read_text(ROOT / ".codex" / "autopilot-state.yml")
    match = re.search(r"(?m)^  onboarding_depth: (lite|standard|deep)$", state)
    if not match:
        return
    flow = match.group(1)
    paths = {
        rel(path)
        for path in (ROOT / "business").rglob("*")
        if path.is_file()
    }
    problems = validate_flow_paths(flow, paths, contract)

    settings = flows[flow]
    required_content = settings.get("required_content", {})
    if isinstance(required_content, dict):
        for relative, snippets in required_content.items():
            path = ROOT / relative
            if not path.is_file():
                continue
            text = read_text(path)
            absent = [snippet for snippet in snippets if snippet not in text]
            if absent:
                problems.append(f"{relative} missing: {', '.join(absent)}")

    if problems:
        fail(f"onboarded flow output ({flow})", "\n  ".join(problems))
    else:
        ok(f"onboarded flow output ({flow})")


def check_onboarding_trigger_contract() -> None:
    required = {
        "AGENTS.md": [
            "обслуживает сам starter-template, не запускай пользовательский AUTOPILOT",
            "Если файлов нет - Starter уже удалён, работай как с обычным проектом.",
            "finalization.current_stage: interview",
            "autopilot.interview_completed: false",
            "post_autopilot.decision: running",
            "не начинай интервью заново",
            "Только если `autopilot.interview_completed: false`",
        ],
        "AUTOPILOT.md": [
            "только если `autopilot.completed: false`",
            "если пользователь просит аудит, оценку, список улучшений или обслуживает сам starter-template",
            "не задавай вопросы заново",
            "не объявляй успех",
            "до следующего вопроса",
            "business/raw/onboarding-notes.md",
            "step1_project_recorded",
        ],
        "autopilot/flows/common.md": [
            "до следующего вопроса",
            "business/raw/onboarding-notes.md",
            "первого действительно незавершённого вопроса",
        ],
        "autopilot/NEW_WINDOW_TEST.md": [
            "внутри незавершённого шага",
            "business/raw/onboarding-notes.md",
            "не повторяет записанный вопрос",
        ],
    }
    problems: list[str] = []
    for relative, snippets in required.items():
        text = read_text(ROOT / relative)
        missing = [snippet for snippet in snippets if snippet not in text]
        if missing:
            problems.append(f"{relative} missing: {', '.join(missing)}")

    resume_stages = [
        "final_validation",
        "cleanup_preview",
        "cleanup_confirmed",
        "cleanup_running",
        "post_cleanup_validation",
    ]
    agents = read_text(ROOT / "AGENTS.md")
    autopilot = read_text(ROOT / "AUTOPILOT.md")
    for stage in resume_stages:
        if stage not in agents or stage not in autopilot:
            problems.append(f"resume stage is not aligned: {stage}")

    if problems:
        fail("onboarding trigger contract", "\n  ".join(problems))
    else:
        ok("onboarding trigger contract")


def check_no_legacy_business_traces(files: list[Path]) -> None:
    allowed_prefixes = {
        "maintainer/history/",
    }
    allowed_files = {
        "CODEX_MIGRATION.md",
        "MIGRATION_BUSINESS_FOLDER.md",
        "maintainer/history/plans/2026-06-21-starter-technical-cleanup.md",
        "README.md",
        "TROUBLESHOOTING.md",
    }
    hits: list[str] = []
    for path in files:
        relative = rel(path)
        if relative == "scripts/starter-lint.py":
            continue
        if relative in allowed_files or any(relative.startswith(prefix) for prefix in allowed_prefixes):
            continue
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            if ".business" in line:
                hits.append(f"{relative}:{line_no}:{line[:140]}")
    if hits:
        fail("no legacy .business model in working files", "\n  ".join(hits))
    else:
        ok("no legacy .business model in working files")


def check_instruction_alignment() -> None:
    required_snippets = [
        (
            "README explains business/life-metrics/raw",
            ROOT / "README.md",
            ["business/", "life-metrics.md", "raw/"],
        ),
        (
            "AUTOPILOT creates business/life-metrics/raw",
            ROOT / "AUTOPILOT.md",
            ["business/INDEX.md", "business/life-metrics.md", "business/raw/"],
        ),
        (
            "common flow defines live metrics and raw",
            ROOT / "autopilot" / "flows" / "common.md",
            ["business/life-metrics.md", "LIVE", "business/raw/"],
        ),
        (
            "business interview prompt creates live metrics and raw",
            ROOT / "prompts" / "setup" / "04-business-interview.md",
            ["life-metrics.md", "raw/", "LIVE"],
        ),
        (
            "import prompt creates live metrics and raw",
            ROOT / "prompts" / "methodology" / "import-existing-project.md",
            ["business/life-metrics.md", "business/raw/", "LIVE"],
        ),
        (
            "AGENTS template routes live metrics",
            ROOT / "templates" / "AGENTS.md.tmpl",
            ["business/INDEX.md", "business/life-metrics.md", "LIVE"],
        ),
        (
            "PROJECT_STATE template routes live metrics",
            ROOT / "templates" / "PROJECT_STATE.md.tmpl",
            ["business/INDEX.md", "business/life-metrics.md"],
        ),
        (
            "quality checklist covers instruction folders",
            ROOT / "QUALITY_CHECKLIST.md",
            ["business/life-metrics.md", "business/raw/"],
        ),
        (
            "coffeeshop AGENTS routes live metrics",
            ROOT / "examples" / "coffeeshop" / "AGENTS.md",
            ["business/INDEX.md", "business/life-metrics.md", "business/raw/"],
        ),
    ]
    missing: list[str] = []
    for label, path, snippets in required_snippets:
        text = read_text(path)
        absent = [snippet for snippet in snippets if snippet not in text]
        if absent:
            missing.append(f"{label}: {rel(path)} missing {', '.join(absent)}")
    if missing:
        fail("instruction alignment checks", "\n  ".join(missing))
    else:
        ok("instruction alignment checks")

    lite_flow = read_text(ROOT / "autopilot" / "flows" / "lite.md")
    forbidden_lite_phrases = [
        "Не создавай `goals/`, `economics/`, `execution/`, `ai-clone/`, `mastery/`",
        "Не создавай `ai-clone/`",
        "Не создавай `mastery/`",
    ]
    found = [phrase for phrase in forbidden_lite_phrases if phrase in lite_flow]
    if found:
        fail("lite flow keeps ai-clone/mastery as starter placeholders", ", ".join(found))
    else:
        ok("lite flow keeps ai-clone/mastery as starter placeholders")

    expected_ai_clone_files = [
        "ai-clone/INDEX.md",
        "ai-clone/role.md",
        "ai-clone/identity/values.md",
        "ai-clone/identity/vision.md",
        "ai-clone/identity/mission.md",
        "ai-clone/identity/biography.md",
        "ai-clone/voice/tone.md",
        "ai-clone/voice/vocabulary.md",
        "ai-clone/voice/stop-words.md",
        "ai-clone/thinking/mental-models.md",
        "ai-clone/principles/product.md",
        "ai-clone/principles/code.md",
        "ai-clone/principles/business.md",
        "ai-clone/feedback/README.md",
        "ai-clone/style/telegram-format.md",
        "ai-clone/style/general.md",
        "ai-clone/reference/README.md",
    ]
    missing_ai_clone = [path for path in expected_ai_clone_files if not (ROOT / path).exists()]
    if missing_ai_clone:
        fail("ai-clone instruction skeleton", ", ".join(missing_ai_clone))
    else:
        ok("ai-clone instruction skeleton")

    wiki_link_checks = {
        "examples/coffeeshop/business/audience/avatar.md": ["[[objections]]", "[[overview]]"],
        "examples/coffeeshop/business/audience/objections.md": ["[[avatar]]", "[[funnel]]"],
        "examples/coffeeshop/business/products/overview.md": ["[[pricing]]", "[[avatar]]"],
        "autopilot/flows/common.md": ["Wiki-links внутри `business/`", "[[имя-файла-без-расширения]]"],
    }
    missing_wiki_links: list[str] = []
    for relative, snippets in wiki_link_checks.items():
        text = read_text(ROOT / relative)
        absent = [snippet for snippet in snippets if snippet not in text]
        if absent:
            missing_wiki_links.append(f"{relative} missing {', '.join(absent)}")
    if missing_wiki_links:
        fail("business wiki-links guidance", "\n  ".join(missing_wiki_links))
    else:
        ok("business wiki-links guidance")


def check_finalization_contract(onboarded: bool) -> None:
    required_files = [
        "autopilot/finalization/finalize.py",
        "autopilot/finalization/onboarded-contract.json",
        "autopilot/finalization/test_finalize.py",
        "autopilot/finalization/test_release.py",
        "scripts/release-check.py",
        "autopilot/finalization/cleanup-manifest.json",
        "templates/AGENTS.md.tmpl",
        "templates/PROJECT_STATE.md.tmpl",
        "templates/README.project.md.tmpl",
        "templates/STRUCTURE.project.md.tmpl",
    ]
    missing_files = [path for path in required_files if not (ROOT / path).is_file()]
    if missing_files:
        fail("finalization files exist", ", ".join(missing_files))
        return
    ok("finalization files exist")

    manifest_path = ROOT / "autopilot/finalization/cleanup-manifest.json"
    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        fail("cleanup manifest parses", str(exc))
        return
    if manifest.get("schema_version") != 1:
        fail("cleanup manifest schema", "expected schema_version 1")
        return
    ok("cleanup manifest parses")

    def entries(value: object, label: str) -> list[dict[str, str | None]]:
        if not isinstance(value, list):
            fail("cleanup manifest lists", f"{label} is not a list")
            return []
        parsed: list[dict[str, str | None]] = []
        for item in value:
            if isinstance(item, str):
                parsed.append({"path": item, "sha256": None})
            elif isinstance(item, dict) and isinstance(item.get("path"), str):
                digest = item.get("sha256")
                parsed.append(
                    {
                        "path": item["path"],
                        "sha256": digest if isinstance(digest, str) else None,
                    }
                )
            else:
                fail("cleanup manifest entries", f"invalid {label} entry: {item!r}")
        return parsed

    categories: list[tuple[str, list[dict[str, str | None]]]] = [
        ("keep", entries(manifest.get("keep"), "keep")),
        ("rewrite", entries(manifest.get("rewrite"), "rewrite")),
        ("remove", entries(manifest.get("remove"), "remove")),
        ("transient_remove", entries(manifest.get("transient_remove"), "transient_remove")),
    ]
    conditional = manifest.get("conditional")
    expected_groups = {
        "ai_clone",
        "mastery",
        "prompts",
        "experiments",
        "repo_skills",
        "community_files",
        "pre_commit_sample",
    }
    actual_groups: set[str] = set()
    if not isinstance(conditional, list):
        fail("cleanup conditional groups", "conditional is not a list")
        conditional = []
    for group in conditional:
        if not isinstance(group, dict) or not isinstance(group.get("name"), str):
            fail("cleanup conditional groups", f"invalid group: {group!r}")
            continue
        name = group["name"]
        actual_groups.add(name)
        categories.append((f"conditional.{name}", entries(group.get("entries"), name)))
    if actual_groups != expected_groups:
        fail(
            "cleanup conditional groups",
            f"expected {sorted(expected_groups)}, got {sorted(actual_groups)}",
        )
    else:
        ok("cleanup conditional groups")

    seen: dict[str, str] = {}
    path_errors: list[str] = []
    hash_errors: list[str] = []
    for category, category_entries in categories:
        for entry in category_entries:
            path = entry["path"] or ""
            if (
                not path
                or "\\" in path
                or path.startswith("/")
                or re.search(r"(^|/)\.\.(/|$)", path)
                or any(character in path for character in "*?[]")
            ):
                path_errors.append(f"{category}: {path!r}")
                continue
            if path in seen:
                path_errors.append(f"{path} is in {seen[path]} and {category}")
            else:
                seen[path] = category
            absolute = ROOT / path
            if category in {"keep", "rewrite"} and not absolute.is_file():
                path_errors.append(f"{category}: missing {path}")
            if category == "remove" or category.startswith("conditional."):
                expected_hash = entry["sha256"]
                if not expected_hash or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
                    hash_errors.append(f"{path}: missing sha256")
                elif absolute.is_file() and normalized_hash(absolute) != expected_hash:
                    hash_errors.append(f"{path}: stale sha256")

    if path_errors:
        fail("cleanup manifest exact paths", "\n  ".join(path_errors))
    else:
        ok("cleanup manifest exact paths")
    if hash_errors:
        fail("cleanup manifest hashes", "\n  ".join(hash_errors))
    else:
        ok("cleanup manifest hashes")

    rewrite_paths = {entry["path"] for label, values in categories if label == "rewrite" for entry in values}
    expected_rewrite = {"AGENTS.md", "PROJECT_STATE.md", "README.md", "STRUCTURE.md"}
    if rewrite_paths != expected_rewrite:
        fail("cleanup rewrite set", f"got {sorted(rewrite_paths)}")
    else:
        ok("cleanup rewrite set")

    removal_paths = {
        entry["path"]
        for label, values in categories
        if label == "remove" or label.startswith("conditional.")
        for entry in values
    }
    protected = sorted(
        path
        for path in removal_paths
        if path == ".git"
        or path.startswith(".git/")
        or path == ".env"
        or path.startswith(".env.")
        or path.endswith(".local.toml")
        or path == "business"
        or path.startswith("business/")
    )
    if protected:
        fail("cleanup protected paths", ", ".join(protected))
    else:
        ok("cleanup protected paths")

    finalizer_text = read_text(ROOT / "AUTOPILOT.md")
    required_commands = [
        "finalize.py --root . preview",
        "finalize.py --root . apply --approve",
        "finalize.py --root . status",
    ]
    absent_commands = [item for item in required_commands if item not in finalizer_text]
    if absent_commands:
        fail("AUTOPILOT finalization commands", ", ".join(absent_commands))
    else:
        ok("AUTOPILOT finalization commands")

    answer_keys = [
        "project_identity",
        "primary_audience",
        "nearest_result",
        "first_scope",
        "next_step",
        "onboarding_depth",
        "lite_primary_action",
        "lite_trust",
        "lite_style",
        "standard_user_problem",
        "standard_mvp_boundary",
        "standard_user_path",
        "standard_pricing",
        "standard_objections",
        "standard_channels",
        "standard_deep_trigger_screen",
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
        "post_autopilot_decision",
        "privacy_business",
        "privacy_ai_clone",
        "privacy_mastery",
        "remote_decision",
    ]
    state = read_text(ROOT / ".codex/autopilot-state.yml")
    if onboarded:
        missing_answers = [
            key
            for key in answer_keys
            if not re.search(
                rf"(?m)^  {re.escape(key)}: (pending|answered|unknown_for_now|not_applicable)$",
                state,
            )
        ]
        label = "answer-state schema"
    else:
        missing_answers = [key for key in answer_keys if f"  {key}: pending" not in state]
        label = "answer-state baseline"
    if missing_answers:
        fail(label, ", ".join(missing_answers))
    else:
        ok(label)


def check_gitattributes_policy() -> None:
    path = ROOT / ".gitattributes"
    if not path.exists():
        fail("gitattributes policy exists", rel(path))
        return

    lines = {
        line.strip()
        for line in read_text(path).splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    required = {
        "* text=auto",
        "*.md text eol=lf",
        "*.tmpl text eol=lf",
        "*.toml text eol=lf",
        "*.json text eol=lf",
        "*.yml text eol=lf",
        "*.yaml text eol=lf",
        "*.py text eol=lf",
        "*.ps1 text eol=lf",
        "*.sh text eol=lf",
        "*.sample text eol=lf",
        "*.example text eol=lf",
        ".gitattributes text eol=lf",
    }
    missing = sorted(required - lines)
    if missing:
        fail("gitattributes line-ending policy", ", ".join(missing))
    else:
        ok("gitattributes line-ending policy")


def check_hooks_json() -> None:
    path = ROOT / ".codex" / "hooks.json"
    try:
        hooks_json = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail("hooks.json parses", str(exc))
        return

    hooks = hooks_json.get("hooks", {}).get("PreToolUse", [])
    if not isinstance(hooks, list) or not hooks:
        fail("PreToolUse hook registration", "missing hooks.PreToolUse")
        return

    first = hooks[0]
    registered_hooks = first.get("hooks", []) if isinstance(first, dict) else []
    command_hook = registered_hooks[0] if registered_hooks else {}
    command = command_hook.get("command", "")
    command_windows = command_hook.get("commandWindows", "")
    missing: list[str] = []
    if first.get("matcher") != "^Bash$":
        missing.append('matcher "^Bash$"')
    if "git rev-parse --show-toplevel" not in command:
        missing.append("POSIX command resolves git root")
    if (
        "rev-parse" not in command_windows
        or "pre_tool_use_policy.py" not in command_windows
        or ".decode('utf-8')" not in command_windows
    ):
        missing.append("Windows command resolves git root")
    if not command_hook.get("statusMessage"):
        missing.append("statusMessage")
    if command_hook.get("timeout") != 5:
        missing.append("timeout 5")

    if missing:
        fail("PreToolUse hook registration", ", ".join(missing))
    else:
        ok("PreToolUse hook registration")


def check_release_entrypoint() -> None:
    script_path = ROOT / "scripts" / "release-check.py"
    workflow_path = ROOT / ".github" / "workflows" / "security-audit.yml"
    required_script_snippets = [
        "scripts/starter-lint.py",
        "unittest",
        "test_*.py",
        "security-audit",
        "autopilot/NEW_WINDOW_TEST.md",
    ]
    required_workflow_snippets = [
        "ubuntu-latest",
        "windows-latest",
        "python scripts/release-check.py",
    ]
    problems: list[str] = []
    if not script_path.is_file():
        problems.append(rel(script_path))
    else:
        script = read_text(script_path)
        problems.extend(
            f"release-check missing {snippet}"
            for snippet in required_script_snippets
            if snippet not in script
        )
    if not workflow_path.is_file():
        problems.append(rel(workflow_path))
    else:
        workflow = read_text(workflow_path)
        problems.extend(
            f"workflow missing {snippet}"
            for snippet in required_workflow_snippets
            if snippet not in workflow
        )

    if problems:
        fail("release check entrypoint", "\n  ".join(problems))
    else:
        ok("release check entrypoint and CI matrix")


def check_markdown_links(files: list[Path]) -> None:
    broken: list[str] = []
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in files:
        if path.suffix.lower() not in {".md", ".tmpl"}:
            continue
        text = read_text(path)
        for match in link_re.finditer(text):
            href = match.group(1).strip()
            if re.match(r"^(https?:|mailto:)", href) or href.startswith("#"):
                continue
            href = href.strip("<>").split("#", 1)[0]
            if not href:
                continue
            target = (path.parent / href).resolve()
            if not target.exists():
                broken.append(f"{rel(path)} -> {match.group(1)}")
    if broken:
        fail("local markdown links", "\n  ".join(broken))
    else:
        ok("local markdown links")


def check_mojibake(files: list[Path]) -> None:
    patterns = [
        re.compile(r"Р[џЃђѓєјѕїЉЊЌЎ]"),
        re.compile(r"С[ЃЂЉЊЌЋЏ]"),
        re.compile(r"Рџ|РЅ|Рё|Рµ|Рѕ|СЃ|С‚|СЊ|С‹|СЏ"),
        re.compile("\ufffd"),
    ]
    hits: list[str] = []
    for path in files:
        if rel(path) == "scripts/starter-lint.py":
            continue
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            fail("UTF-8 readable", rel(path))
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in patterns):
                hits.append(f"{rel(path)}:{line_no}:{line[:140]}")
                if len(hits) >= 20:
                    break
    if hits:
        fail("no obvious mojibake", "\n  ".join(hits))
    else:
        ok("no obvious mojibake")


def check_hook_policy() -> None:
    hook = ROOT / ".codex" / "hooks" / "pre_tool_use_policy.py"
    cases = [
        ({"tool": "shell", "input": {"command": "rm -rf tmp"}}, "deny"),
        ({"tool": "shell", "input": {"command": "git status --short"}}, "allow"),
        ({"tool": "shell", "input": {"command": "Get-Content .env"}}, "deny"),
    ]
    results: list[str] = []
    for payload, expected in cases:
        raw = json.dumps(payload)
        completed = run([sys.executable, str(hook)], input_text=raw)
        try:
            output = json.loads(completed.stdout)
            decision = output.get("hookSpecificOutput", {}).get("permissionDecision")
        except json.JSONDecodeError:
            decision = None
        results.append(f"{payload['input']['command']}={decision}")
        if decision != expected:
            fail("hook policy smoke-test", f"expected {expected}, got {decision} for {raw}")
            return

    ok("hook policy smoke-test (" + ", ".join(results) + ")")


def check_git_diff() -> None:
    inside = run(["git", "rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        ok("git diff --check skipped outside a Git work tree")
        return
    completed = run(["git", "diff", "--check"])
    if completed.returncode != 0:
        fail("git diff --check", completed.stdout + completed.stderr)
    else:
        ok("git diff --check")


def check_old_agent_traces(files: list[Path]) -> None:
    allowed_prefixes = {
        "maintainer/history/",
    }
    allowed_files = {
        "CODEX_MIGRATION.md",
        "CHANGELOG.md",
    }
    patterns = [
        re.compile(r"\bCLAUDE\.md\b"),
        re.compile(r"\.claude/"),
        re.compile(r"\bAnthropic\b", re.I),
        re.compile(r"\bClaude Code\b", re.I),
    ]
    hits: list[str] = []
    for path in files:
        relative = rel(path)
        if relative == "scripts/starter-lint.py":
            continue
        if relative in allowed_files or any(relative.startswith(prefix) for prefix in allowed_prefixes):
            continue
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            if relative == "QUALITY_CHECKLIST.md" and "Prompts не ссылаются на старые Claude/Anthropic" in line:
                continue
            if any(pattern.search(line) for pattern in patterns):
                hits.append(f"{relative}:{line_no}:{line[:140]}")
    if hits:
        fail("no old agent traces in working instructions", "\n  ".join(hits))
    else:
        ok("no old agent traces in working instructions")


def parse_args() -> tuple[bool, Path]:
    parser = ArgumentParser(description="Lint a Codex Starter template or onboarded copy.")
    parser.add_argument(
        "--onboarded",
        action="store_true",
        help="check a copy after the interview and before cleanup",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root to check; defaults to the parent of this script",
    )
    args = parser.parse_args()
    return args.onboarded, args.root.resolve()


def main() -> int:
    global ROOT

    failures.clear()
    onboarded, root = parse_args()
    ROOT = root
    mode = "pre-cleanup project" if onboarded else "starter-template"

    print("Codex Starter lint")
    print("===================")
    print(f"Mode: {mode}")
    print(f"Root: {ROOT}")
    files = iter_files()
    if not check_utf8(files):
        print("")
        print(f"RESULT: {len(failures)} problem(s) found.")
        return 1
    if onboarded:
        check_onboarded_autopilot_state()
        check_onboarded_business()
        check_onboarded_context_route()
    else:
        check_autopilot_state()
        check_business_clean()
    check_unresolved_placeholders(onboarded)
    check_onboarded_reference_contract(onboarded)
    check_onboarding_trigger_contract()
    check_no_legacy_business_traces(files)
    check_instruction_alignment()
    check_finalization_contract(onboarded)
    check_gitattributes_policy()
    check_hooks_json()
    check_release_entrypoint()
    check_markdown_links(files)
    check_mojibake(files)
    check_hook_policy()
    check_git_diff()
    check_old_agent_traces(files)

    print("")
    if failures:
        print(f"RESULT: {len(failures)} problem(s) found.")
        return 1
    print(f"RESULT: {mode} lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
