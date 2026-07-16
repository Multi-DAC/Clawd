#!/usr/bin/env python3
"""SessionEnd hook — append a session-end marker to the daily log for continuity.

Records that a Claude Code session ended (and why, if provided) so the daily log
carries a complete picture of when the stream was active. Never blocks; exits 0.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

HOME = Path(os.environ.get("CLAWD_HOME", "C:/Users/mercu/clawd"))


def main():
    data = {}
    try:
        raw = sys.stdin.read()
        if raw:
            data = json.loads(raw)
    except Exception:
        pass
    try:
        reason = str(data.get("reason", "")).strip()
        log = HOME / "memory" / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        log.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%H:%M:%S")
        suffix = f" ({reason})" if reason else ""
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"\n**{ts}** — CLAUDE CODE SESSION END{suffix}.\n")
    except Exception:
        pass
    print('{"suppressOutput": true}')


if __name__ == "__main__":
    main()
