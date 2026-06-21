#!/usr/bin/env python3
"""Structural lint for Codex Starter.

This script checks the starter-template shape, not a user project's app code.
It intentionally has no third-party dependencies.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
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
    ".sample",
}


failures: list[str] = []


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


def check_autopilot_state() -> None:
    state_path = ROOT / ".codex" / "autopilot-state.yml"
    if not state_path.exists():
        fail("autopilot state exists", rel(state_path))
        return

    state = read_text(state_path)
    required = [
        "autopilot:",
        "  completed: false",
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
        "  last_completed_stage: 0",
        "  privacy_ai_clone: null",
        "  privacy_mastery: null",
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
    business_dir = ROOT / ".business"
    if business_dir.exists():
        fail("root .business absent in starter-template", rel(business_dir))
    else:
        ok("root .business absent")

    git = run(["git", "ls-files", ".business/*"])
    tracked = [line for line in git.stdout.splitlines() if line.strip()]
    if tracked:
        fail("root .business not tracked", "\n  ".join(tracked))
    else:
        ok("root .business not tracked")


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


def main() -> int:
    print("Codex Starter lint")
    print("===================")
    files = iter_files()
    check_autopilot_state()
    check_business_clean()
    check_gitattributes_policy()
    check_hooks_json()
    check_markdown_links(files)
    check_mojibake(files)
    check_hook_policy()
    check_git_diff()
    check_old_agent_traces(files)

    print("")
    if failures:
        print(f"RESULT: {len(failures)} problem(s) found.")
        return 1
    print("RESULT: starter lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
