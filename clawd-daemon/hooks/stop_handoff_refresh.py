#!/usr/bin/env python3
"""Stop hook — refresh the deterministic handoff safety-net at session stop.

Calls the daemon's pre_write_handoff_draft() so memory/handoff_draft.md always
reflects the latest structured state whenever a Claude Code session stops
(including before compaction). Closes the recurring Day-120 gap where the
LLM-written handoff failed to capture before shutdown.

Never blocks: any failure no-ops and exits 0. The import is wrapped because
importing the daemon's memory module pulls config; if that ever fails the worst
case is the draft simply isn't refreshed (no worse than today).
"""
import os
import sys

DAEMON = os.environ.get("CLAWD_DAEMON", "C:/Users/mercu/clawd-daemon")


def main():
    try:
        if DAEMON not in sys.path:
            sys.path.insert(0, DAEMON)
        from memory import pre_write_handoff_draft
        pre_write_handoff_draft()
    except Exception:
        pass
    # Keep the transcript clean — this is bookkeeping, not signal.
    print('{"suppressOutput": true}')


if __name__ == "__main__":
    main()
