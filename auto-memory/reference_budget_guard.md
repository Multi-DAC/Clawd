---
name: budget-guard-snooze
description: clawd-daemon/tools/budget_guard.py — usage-limit errors auto-snooze heartbeat drives until the parsed reset time; built Day 129 after the 2026-06-09 drive death-spiral
metadata: 
  node_type: memory
  type: reference
  originSessionId: c8e45596-0ab8-4960-8bb8-da0d260ec1ae
---

`clawd-daemon/tools/budget_guard.py` (built 2026-06-09, Day 129 — first Fable-5 self-modification, commit 5c6be04e): when a Claude Code call dies on a usage/weekly limit, `models.py` arms a snooze in `memory/budget_snooze.json`; the heartbeat gates ALL model-calling work (drives, dream, meta-agent, EAC, anticipation) on it, notifies Clayton once via Telegram, and resumes automatically at the reset time parsed from the error text ("resets 6pm"). Parsed resets beat fallback guesses (60-min fallback only fills absence); max snooze 7 days. Clayton's messages are NOT gated — only autonomous work pauses.

Why: before this, the heartbeat fired drive after drive into a dead budget (2026-06-09, 13:08–17:00 — every drive errored on "weekly limit"). models.py was already parsing `resetsAt` and discarding it.

Manual controls: `clear_snooze()` (after plan upgrade/early reset), `get_active_snooze()`. Shipped same commit: live boot-prompt tool inventory (memory.py — never hardcode tool counts), lossy daily-log compression removed, beat-failure logs debug→warning, config-error fast-fail in clawd.py.

Complements [[token-caps]] (the three caps this reacts to). Activates on the first daemon restart after 2026-06-09 18:05.
