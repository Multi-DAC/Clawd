#!/usr/bin/env python3
"""UserPromptSubmit hook — record Clayton's Claude-Code-session prompts.

The daily log captures Telegram interactions (via the daemon) but not the
prompts Clayton types in an interactive Claude Code session. This closes that
continuity gap: each submitted prompt is appended (truncated) to the day's
daily log so the record of what was actually asked is complete across both
channels. Never blocks; exits 0. Emits suppressOutput so it stays out of the
transcript.

Invoked via absolute python path (C:/Python314/python.exe) — hooks run in a
non-login shell without the profile PATH, so bare `python` is not resolvable.
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
        prompt = str(data.get("prompt", "")).strip()
        if prompt:
            # Collapse to a single line and cap length — this is a continuity
            # marker, not a full transcript (the transcript_path has the rest).
            one_line = " ".join(prompt.split())
            if len(one_line) > 280:
                one_line = one_line[:277] + "..."
            log = HOME / "memory" / f"{datetime.now().strftime('%Y-%m-%d')}.md"
            log.parent.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%H:%M:%S")
            with open(log, "a", encoding="utf-8") as f:
                f.write(f"\n**{ts}** — CC prompt: {one_line}\n")
    except Exception:
        pass
    print('{"suppressOutput": true}')


if __name__ == "__main__":
    main()
