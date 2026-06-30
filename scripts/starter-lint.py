#!/usr/bin/env python3
"""Structural lint for Codex Starter.

By default this script checks the pristine starter-template shape, not a user
project's app code. Use ``--onboarded`` for a copy after AUTOPILOT has finished.
It intentionally has no third-party dependencies.
"""

from __future__ import annotations

import json
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
        "  privacy_business: null",
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
        "  completed: true",
        "  current_stage: done",
        "  current_flow: null",
        "  last_completed_step: 10",
        "post_autopilot:",
    ]
    missing = [item for item in required if item not in state]
    if missing:
        fail("onboarded autopilot state", ", ".join(missing))
    else:
        ok("onboarded autopilot state")

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
        "AGENTS.md",
        "PROJECT_STATE.md",
        "ai-clone/INDEX.md",
    ]
    missing = [path for path in required_files if not (ROOT / path).exists()]
    if missing:
        fail("onboarded context entry files", ", ".join(missing))
        return
    ok("onboarded context entry files")

    agents = read_text(ROOT / "AGENTS.md")
    project_state = read_text(ROOT / "PROJECT_STATE.md")
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


def check_no_legacy_business_traces(files: list[Path]) -> None:
    allowed_prefixes = {
        "maintainer/history/",
    }
    allowed_files = {
        "CODEX_MIGRATION.md",
        "MIGRATION_BUSINESS_FOLDER.md",
        "plans/2026-06-21-starter-technical-cleanup.md",
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


def parse_args() -> tuple[bool, Path]:
    parser = ArgumentParser(description="Lint a Codex Starter template or onboarded copy.")
    parser.add_argument(
        "--onboarded",
        action="store_true",
        help="check a copy after AUTOPILOT completed instead of a pristine starter-template",
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

    onboarded, root = parse_args()
    ROOT = root
    mode = "onboarded project" if onboarded else "starter-template"

    print("Codex Starter lint")
    print("===================")
    print(f"Mode: {mode}")
    print(f"Root: {ROOT}")
    files = iter_files()
    if onboarded:
        check_onboarded_autopilot_state()
        check_onboarded_business()
        check_onboarded_context_route()
    else:
        check_autopilot_state()
        check_business_clean()
    check_no_legacy_business_traces(files)
    check_instruction_alignment()
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
    print(f"RESULT: {mode} lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
