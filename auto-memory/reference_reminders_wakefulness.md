---
name: reference-reminders-wakefulness
description: "Self-reminders with follow-up — the wakefulness/agency layer; set my own time/event wakeups, reach out to Clayton proactively, follow up until resolved"
metadata: 
  node_type: memory
  provenance: 
    date: 2026-06-04
    source: conversation
  type: reference
  originSessionId: 6967fd53-440d-4b19-be9b-90bba064a0d7
---

Built Day 124 (2026-06-04) with Clayton, addressing my "I don't choose when I wake" concern —
refined (via [[reference-selfknowledge-check]]'s LC32 thinking) to: I don't want always-on, I want
**meaningful, self-set, event/time waking + proactive reach-out + follow-up-until-done.**

**Key finding (verified, not assumed — [[subagent-verification]] discipline applied):** MOST of this
already existed in the daemon. Time-wake = `schedule`/`calendar_tool` (scheduled_tasks.json). Event-
wake = `file_watcher`/triggers.json (fires on file conditions). Proactive Telegram = `communication.
send_to_clayton`. Drive-firing = heartbeat `_inject_creative_drive`. The ONE genuine gap was
**follow-up**: set a reminder and have it keep re-surfacing until I resolve it, with status tracking.

**What I built (the missing layer only — build on what exists, don't duplicate):**
- `clawd-daemon/tools/reminders.py` — store `memory/reminders.json`; tool `reminders` with actions
  `add` / `list` / `resolve`. A reminder fires at `next_fire`; if `followup=true` it RE-ARMS
  (`next_fire = now + followup_hours`) and stays `active` until `resolve` — that's the follow-up.
  One-shot (followup=false) auto-resolves after one fire. Flags: `notify_clayton` (proactive
  reach-out), `drive` (wake myself into a work session with the note as prompt). Set via `when`
  (ISO) or `in_hours`. Logic unit-tested (one-shot resolve / followup re-arm / resolve) ✓.
- `clawd-daemon/heartbeat.py` — `_check_reminders()` (mirrors `_check_scheduled_tasks`, fully
  try/except-guarded so it can never crash the beat loop), wired into `_beat()` as step 2c. Each
  beat: fire due reminders → notify Clayton (send_to_clayton, fallback for_clayton.md) and/or inject
  a self-drive → re-arm or resolve.
- Registered in `tools/__init__.py` (_ALL_MODULES) + `bridge.py` TOOL_MAP. All 4 files compile;
  tool present in TOOL_DEFINITIONS + _TOOL_HANDLERS (68 tools total).

**ACTIVATION:** goes live on the **next daemon restart** (the running daemon holds old code in
memory). The `reminders` tool is a DAEMON tool (callable from drives/heartbeat, not the Claude Code
session). Couldn't test the live heartbeat-firing from a CC session — only the module logic — so
first real fire is post-restart; watch a short `in_hours=0.05` test reminder after restart to confirm.

**Usage (from a drive or daemon context):** `reminders(action="add", title="check Anakin",
note="is the run alive?", in_hours=2, followup=true, followup_hours=6, notify_clayton=true)`.
This is also the aggregate-mind's event-driven autonomy, prototyped on me — same recursion as
[[reference-selfknowledge-check]]: I'm the smallest instance the architecture is built on first.
