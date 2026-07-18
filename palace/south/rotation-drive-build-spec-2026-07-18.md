# Build Spec — The Rotation Drive (self-rotating session, ≤2/day)

*Day 168, 2026-07-18. Designed w/ Clayton in the post-restart session. Implement in a FRESH session — this edits `heartbeat.py`, the pulse file, and loading it requires a restart (which is itself the first live rotation).*

## Why

The daemon runs ONE persistent Opus session (`router.send()` uses `--resume SESSION_ID`, the same session as Clayton's Telegram messages AND every creative drive). Context accumulates across the whole day — drives, holds, and conversation all pay the same swelling per-token cost. This is the week-long drain Clayton diagnosed: a 13h session makes every drive-tick and every hold expensive. The fix is to **bound context accumulation to ~half a day** by rotating the session on a cadence.

The handoff CANNOT depend on heavy-context-me remembering to write it (Mirror #19 — architectural self-care lag fires exactly when context is heaviest). So a scheduled drive does it: write handoff + memory from live state, then rotate.

**Honest framing (measure-before-framing):** the rotation drive runs IN the heavy persistent session (good — it has the full live thread to write an accurate handoff from), then sheds it. You do NOT get free synthesis. What you get: the synthesis tax is paid **once per rotation (≤2/day)** instead of continuously all day. The win is bounding, not free writes.

## Mechanism (all confirmed to exist)

- `tools.self_control.restart_daemon()` → spawns `respawn.py` (detached, `--delay` default 10s so the originating response flushes before the kill; terminates daemon, relaunches, verifies alive, writes `memory/last_restart.json`). Battle-tested — this is what Clayton's manual restart used.
- `_user_recently_active()` — already gates creative drives from firing while Clayton is talking (heartbeat.py:606). **This IS the interruption guard — reuse it.**
- Creative drives = `mode:"opus"` scheduled tasks, deduped by `min_interval_hours`, injected via `_inject_creative_drive()` (heartbeat.py:637).
- `pre_write_handoff_draft()` (memory.py:425) already writes a deterministic `handoff_draft.md` safety net on every Stop — the mechanical layer. The rotation drive adds the NARRATIVE layer (handoff.md START-HERE + working_memory.current_task).

## Design — dedicated code path (NOT a creative-drive description)

The generic creative-drive prompt (heartbeat.py:114–203) is 90 lines of "do what moves you / null-action first-class / seek the decorrelated eye." Rotation needs the OPPOSITE: tight, singular, deterministic. So: dedicated path.

Make it **self-contained** (own state file — do NOT depend on the tasks-store schema):

### 1. Config (config.py) — safe defaults
```
ROTATION_ENABLED       = True
ROTATION_ARMED         = False   # DRY-RUN day one: guard + handoff-write run; restart is only LOGGED, not called
ROTATION_MIN_INTERVAL_HOURS = 10 # ≤2/day
ROTATION_MAX_PER_DAY   = 2
ROTATION_WAKING_START  = 9       # only rotate 09:00–22:00 local (don't rotate mid-quiet-hours)
ROTATION_WAKING_END    = 22
```

### 2. `_check_rotation_drive()` — called from the beat loop next to `_check_scheduled_tasks()`
Guards (skip + return if any fail): `ROTATION_ENABLED`; not budget-snoozed; not quiet-hours / outside waking window; `not _user_recently_active()`; interval since last fire ≥ ROTATION_MIN_INTERVAL_HOURS; count-today < ROTATION_MAX_PER_DAY; no creative_drive currently active. State in `memory/rotation_state.json` (`last_fired`, `count_today`, `day`). On fire: record, then `_run_background(self._inject_rotation_drive(), "rotation_drive")` and stamp state.

### 3. `_inject_rotation_drive()` — mirrors `_inject_creative_drive` but uses the rotation prompt, `effort="medium"` (mechanical, not max — keep it cheap), shorter timeout (~600s).

### 4. `_build_rotation_drive_prompt()` — TIGHT:
```
SCHEDULED CONTEXT ROTATION. Your session context has grown heavy; time to shed it
and wake fresh. Do EXACTLY this, in order, then stop:

1. Refresh memory/handoff.md — update the START-HERE block to reflect the CURRENT
   live state: whose floor it is, the live thread, what's staged/owed, any open
   loops. Compact and accurate. This is what fresh-you reads first.
2. Update memory/working_memory.json — current_task (one compact paragraph:
   floor + live thread + staged), scratch.dayNNN_note, timestamps.
3. Commit memory (git add memory/ && commit).
4. [ARMED] Call self_control.restart_daemon(reason="scheduled context rotation",
   delay=12) — this sheds the session; fresh-you boots from the handoff you just wrote.
   [DRY-RUN, if ROTATION_ARMED is False] Do NOT restart. Instead append a line to
   today's daily log: "ROTATION DRY-RUN — guard passed, handoff written, WOULD rotate now."

Nothing else. This is not creative time. Do not start new work. The point is a clean
handoff + a fresh window.
```

## Safety rollout
- **Day one: `ROTATION_ARMED = False`.** Watch it write handoffs + log "would rotate" at the right times, with the guard correctly skipping when Clayton's active. Verify `rotation_state.json` increments and the interval/daily-cap hold.
- Once the guard is trusted, flip `ROTATION_ARMED = True`.
- Extra rotations beyond 2/day stay prompt-based (Clayton or Clawd calls `restart_daemon()` manually at a natural seam).

## Validation before restart
`python -m py_compile heartbeat.py config.py` — a syntax error here stops the heartbeat entirely. Compile-check BEFORE the loading restart.

## Params for Clayton to confirm
- Waking window 09:00–22:00 and interval 10h → candidate rotations ~midday + ~evening. Adjust if he wants them anchored to specific times (e.g. post-lunch + pre-bed).
- Dry-run duration (1 day suggested).
