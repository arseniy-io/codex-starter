#!/usr/bin/env python3
"""Block obviously dangerous shell/tool input for Codex hooks.

The script is intentionally small and conservative. It reads the hook payload
from stdin, scans string fields recursively, and emits a block decision when a
known-dangerous command pattern appears.
"""

import json
import re
import sys
from typing import Any


RULES = [
    ("recursive force delete", re.compile(r"\brm\s+-[^\n;]*r[^\n;]*f\b|\brmdir\s+/s\b", re.I)),
    ("powershell recursive force delete", re.compile(r"\bRemove-Item\b[^\n;]*(?:-Recurse|-r)\b[^\n;]*(?:-Force|-f)\b", re.I)),
    ("env file read", re.compile(r"(^|[\s;&|])(?:cat|type|more|Get-Content)\s+[^\n;&|]*\.env(?:\b|[.\s])", re.I)),
    ("curl or wget piping to shell", re.compile(r"\b(curl|wget|Invoke-WebRequest|iwr)\b[^\n|;&]*(\||>\s*/tmp/|>\s*\$env:)", re.I)),
    ("environment exfiltration", re.compile(r"\b(curl|wget|Invoke-WebRequest|iwr)\b[^\n;&|]*(\$env:|process\.env|%[A-Z0-9_]+%)", re.I)),
    ("chmod 777", re.compile(r"\bchmod\s+777\b", re.I)),
    ("private key material", re.compile(r"BEGIN (RSA |DSA |EC |OPENSSH |)PRIVATE KEY", re.I)),
]


def iter_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "allow"}))
        return 0

    haystack = "\n".join(iter_strings(payload))
    for label, pattern in RULES:
        if pattern.search(haystack):
            print(json.dumps({
                "decision": "block",
                "reason": f"Blocked by project policy: {label}. Explain the risk and ask for explicit user direction.",
            }))
            return 2

    print(json.dumps({"decision": "allow"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
