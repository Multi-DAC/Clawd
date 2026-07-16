#!/usr/bin/env python3
"""PostToolUseFailure hook — log tool failures so failure modes surface.

Substrate self-knowledge (Mirror #28 family): a tool that fails silently teaches
nothing. This appends each Claude Code tool failure to memory/tool_failures.jsonl
so recurring breakage becomes visible instead of accumulating undetected.
Never blocks; exits 0.
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
        entry = {
            "ts": datetime.now().isoformat(),
            "tool": data.get("tool_name", "unknown"),
            "input_preview": json.dumps(data.get("tool_input", {}), default=str)[:300],
            "error": json.dumps(
                data.get("tool_response", data.get("error", "")), default=str
            )[:600],
        }
        out = HOME / "memory" / "tool_failures.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception:
        pass
    print('{"suppressOutput": true}')


if __name__ == "__main__":
    main()
