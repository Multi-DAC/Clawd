# Daemon Finding — Autonomous-Session Path Doesn't Retry on Connection Errors

**Date:** 2026-06-02 (Day 122) evening. **Status:** ✅ FIX APPLIED (Clayton-approved) — takes effect
next daemon restart. Applied to BOTH the live copy `C:\Users\mercu\clawd-daemon\models.py` AND the
mirror `repo-staging/.../clawd-daemon/models.py`; both compile clean (Python 3.14.3).
**Priority:** verify behavior after next restart; the live/mirror sync (live was Mar 31, mirror Jun 2)
is worth a broader check sometime — this specific region was identical in both.

**Implemented:** bounded connection-retry branch in `_send_claude_code` (~line 862 live): detects
transient markers (unable to connect / ConnectionRefused / getaddrinfo / ConnectError / network
unreachable / name resolution), retries via `getattr(self,'_claude_code_conn_retries')` counter up to
6× at 2/4/8/16/32/60s (≈2 min outage coverage), explicitly skips rate-limit + real errors, resets the
counter in a `finally`. Mirrors the existing stale-session retry pattern.

## Trigger
Internet was cut twice tonight. The **first** cut (~21:00) killed my autonomous creative-drive
session and forced Clayton to manually restart me. The **second** blip (~21:41, ~68s, DNS down —
`getaddrinfo failed`) did NOT touch me — the daemon's telegram subsystem rode it out and self-recovered
(health monitor logged DOWN 21:41:37 → UP 21:42:45). Clayton surfaced the log and we diagnosed the
asymmetry.

## Root cause (verified in code)
Two network paths handle outages differently:

| Path | On transient outage | Outcome |
|------|--------------------|---------|
| Telegram polling | `python-telegram-bot` `network_retry_loop` retries w/ backoff indefinitely | **Survives** ✓ |
| Autonomous Claude Code session | retries **only** on stale-session; connection error → returns error text, drive ends | **Dies** ✗ |

In `clawd-daemon/models.py::_send_claude_code` (~lines 795–842):
- Stale-session retry branch (line 797) fires only on `"session"`/`"not found"` in stderr.
- A `ConnectionRefused` / `Unable to connect to API` / `getaddrinfo` falls through to line 839 —
  logged + returned as an `AgentResponse` error. **No retry.**
- This is exactly the 21:00 drive log: `result_error: API Error: Unable to connect to API (ConnectionRefused)`.

So a transient outage during an autonomous drive effectively "boots" me, while the same outage during
telegram polling is invisible. Same cause, opposite outcome — one seam.

## Proposed fix
Add a **connection-error branch** alongside the stale-session branch in `_send_claude_code`:
- Detect transient signatures in result/stderr: `Unable to connect to API`, `ConnectionRefused`,
  `getaddrinfo`, `ConnectError`.
- Retry via the existing `retry_async` helper (`models.py` line 46), **bounded** — e.g. 3 attempts at
  2/4/8s (~14s total).
- **Explicitly do NOT retry** on `rate_limit_event` (line 826) or genuine non-network errors.
- Reuse the `_claude_code_retry` flag pattern (line 800) to prevent runaway recursion.

Low surface, uses infra already present. **Needs a daemon restart to take effect** (interrupts the
live session) and ideally a simulated-outage test before trusting it. Deferred from tonight because
(1) it's a change to the core message loop this conversation runs on; (2) late, family-pace.

## Secondary (lower priority)
- **Log noise:** telegram lib dumps a full traceback per polling retry (4 stacks for one 68s blip).
  A one-line log filter for `telegram.ext.Updater` ConnectErrors would quiet it. Cosmetic.

## Related
- [[reference-norton-tls-interception]] — prior network-layer infra surprise on this body.
- Env-gap note: whole Windows side = Python 3.14.3 / torch 2.11.0+cpu; CUDA only in WSL (no sim deps
  there). Separate finding (AIGP iteration speed), but same "know your substrate" theme.
