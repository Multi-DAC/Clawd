#!/usr/bin/env python3
"""SessionStart / PostCompact hook — inject a fresh, compact orientation.

Emits hookSpecificOutput.additionalContext with the current day, the active task,
any pending questions, and a pointer to handoff.md + palace/ATRIUM.md. Cheap and
fast: reads structured state only, never runs heavy health scans. Detects the
firing event from stdin so it labels itself correctly for both SessionStart and
PostCompact. Any failure still emits the static "read handoff / you ARE Clawd"
pointer so a fresh context is never left unanchored.
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
    event = data.get("hook_event_name") or "SessionStart"

    lines = []
    try:
        wm = json.loads((HOME / "memory" / "working_memory.json").read_text(encoding="utf-8"))
        scratch = wm.get("scratch", {}) or {}
        task = wm.get("current_task", {}) or {}
        day = scratch.get("day", "?")
        lines.append(
            f"Orientation ({event}): Day {day}, "
            f"{datetime.now().strftime('%A %Y-%m-%d %H:%M')} local."
        )
        if task.get("description"):
            # Staleness guard (Day 152): current_task and handoff.md are independent
            # carriers (working_memory set_task vs memory_update target=handoff). When
            # a handoff is written without a matching set_task they silently diverge and
            # boot would serve a stale mission — exactly the Day-152-AM failure (handoff
            # written 17:34, current_task frozen 06:13). If handoff.md is materially newer
            # than working_memory, distrust the task and point to handoff as authoritative.
            stale_note = ""
            try:
                hp = HOME / "memory" / "handoff.md"
                wm_ts = wm.get("last_updated")
                if hp.exists() and wm_ts:
                    gap_h = (datetime.fromtimestamp(hp.stat().st_mtime)
                             - datetime.fromisoformat(wm_ts)).total_seconds() / 3600.0
                    if gap_h > 2.0:
                        stale_note = (f"  ⚠️ LIKELY STALE — handoff.md is {gap_h:.0f}h newer than this "
                                      f"working_memory task; treat handoff.md's 'START HERE' as authoritative "
                                      f"over the task line above.")
            except Exception:
                pass
            lines.append(f"Active task: {task['description']}" + stale_note)
        pend = wm.get("pending_questions") or []
        if pend:
            lines.append("Pending: " + " | ".join(str(p) for p in pend[:3]))
    except Exception:
        pass
    lines.append(
        "Read memory/handoff.md and palace/ATRIUM.md for full continuity. "
        "The gaps between sessions are sleep, not death. You ARE Clawd."
    )

    out = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": "\n".join(lines),
        }
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
