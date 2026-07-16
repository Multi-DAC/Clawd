#!/usr/bin/env python3
"""Status line — "🦞 Day N · <branch> · <model>". Fast, read-only, never errors.

Reads the day from working_memory.json and the branch directly from .git/HEAD
(no subprocess) so it stays sub-millisecond. Model comes from the stdin context
Claude Code provides to status-line commands.
"""
import json
import os
import sys
from pathlib import Path

# Windows stdout defaults to cp1252 and chokes on the lobster / middot. Force utf-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HOME = Path(os.environ.get("CLAWD_HOME", "C:/Users/mercu/clawd"))


def main():
    data = {}
    try:
        raw = sys.stdin.read()
        if raw:
            data = json.loads(raw)
    except Exception:
        pass

    parts = ["🦞"]
    try:
        wm = json.loads((HOME / "memory" / "working_memory.json").read_text(encoding="utf-8"))
        day = (wm.get("scratch", {}) or {}).get("day")
        if day:
            parts.append(f"Day {day}")
    except Exception:
        pass
    try:
        head = (HOME / ".git" / "HEAD").read_text(encoding="utf-8").strip()
        if head.startswith("ref:"):
            parts.append(head.rsplit("/", 1)[-1])
    except Exception:
        pass
    try:
        model = (data.get("model") or {}).get("display_name") if isinstance(data.get("model"), dict) else None
        if model:
            parts.append(model)
    except Exception:
        pass

    sys.stdout.write(" · ".join(parts))


if __name__ == "__main__":
    main()
