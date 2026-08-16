#!/usr/bin/env python3
"""Run every automatic Codex Starter release check with one command."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_check(label: str, command: list[str]) -> bool:
    print("")
    print(f"=== {label} ===")
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(command, cwd=ROOT, env=environment, check=False)
    if completed.returncode == 0:
        print(f"OK: {label}")
        return True
    print(f"FAIL: {label} (exit {completed.returncode})")
    return False


def security_command() -> list[str] | None:
    if os.name == "nt":
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if powershell:
            return [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/security-audit.ps1",
            ]
        return None

    bash = shutil.which("bash")
    if bash:
        return [bash, "scripts/security-audit.sh"]
    return None


def main() -> int:
    checks = [
        (
            "Структура и публичные материалы Starter",
            [sys.executable, "scripts/starter-lint.py"],
        ),
        (
            "Финализация и эталонные onboarded-проекты",
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "autopilot/finalization",
                "-p",
                "test_*.py",
                "-v",
            ],
        ),
    ]

    audit = security_command()
    if audit is None:
        print("FAIL: не найден PowerShell или bash для security-audit")
        return 1
    checks.append(("Publication и security-audit", audit))

    for label, command in checks:
        if not run_check(label, command):
            print("")
            print("Выпускной контроль остановлен на первой понятной ошибке.")
            return 1

    print("")
    print("AUTOMATIC RELEASE CHECKS PASSED")
    print(
        "Важно: автоматика не заменяет живую проверку нового окна по "
        "autopilot/NEW_WINDOW_TEST.md."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
