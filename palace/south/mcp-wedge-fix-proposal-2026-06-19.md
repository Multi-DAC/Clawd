# MCP-Wedge Fix — Staged Proposal (read-only diagnosis, NOT applied)

*Written 2026-06-19 ~01:25 dream drive. This touches my own nervous system (daemon send/router path). DO NOT apply unilaterally — stage for Clayton. This doc exists so the morning fix-conversation is concrete.*

## The incident
2026-06-18 evening: ~4 hours of timeouts when Clayton asked for our qualia work. His messages came back as `[Request timed out after 3600s — zombie process safety net]`. Short text-only replies got through; tool-heavy turns wedged. The local **clawd-tools MCP** was flapping (disconnect/reconnect notices in-session).

## Precise root cause (traced in `clawd-daemon/models.py`)
There are TWO timeouts, and the WRONG one fired:
- **Inner deadline** (lines 738–777): `resolved_timeout` — *600s for user messages, 1800s for creative drives* — enforced by the `while not comm_task.done()` loop's `if time.time() >= deadline` check. Produces `[Claude Code timed out after {N}s]`.
- **Outer net** (line 550): `async with asyncio.timeout(3600)` → `[send() timed out after 3600s — zombie process safety net]`.

The log shows the **OUTER 3600s** fired, NOT the inner 600s. Therefore **Clayton's message never reached the subprocess loop** where the 600s deadline lives. It was stuck *upstream*, at lock acquisition:

1. The creative drive "Evening Integration" called `send(timeout=1800)`, acquired the single `self._send_lock` (line 505), spawned its Claude Code subprocess.
2. That subprocess **wedged** on an internal MCP/IPC call (clawd-tools flapping, no inner per-call timeout *inside* the CLI — which the daemon cannot directly bound).
3. Clayton's message called `send()` and **queued waiting for `_send_lock`** ("send() queued — waiting for active operation to yield", line 506). The lock-wait is bounded only by the outer `asyncio.timeout(3600)`.
4. The preemption path that SHOULD have killed the wedged drive misfired: heartbeat logged "User message during creative drive — 300s grace period before interrupt" → then "Creative drive finished within grace period — no interrupt needed." The grace logic concluded the drive *finished* when it had actually **timed out / wedged** — so `interrupt_event` (models.py lines 748–755) was never set, the lock was never released early, and Clayton waited out the full 3600s.

**One-line root cause:** the single `_send_lock` serializes Clayton behind creative drives; when a drive's subprocess wedges, the grace/interrupt coordination fails to preempt it, so a waiting user message blocks on lock-acquisition until the outer 3600s net — the inner 600s user-deadline is downstream of the lock and never reached.

## Fix candidates (ranked; injection points named)
1. **★ Preempt on user message — fix the grace/interrupt misfire (the real fix).** The machinery already exists: `interrupt_event` (models.py 748–755) kills the holding subprocess and yields. The bug is in the heartbeat↔models grace coordination that decided a wedged drive had "finished." Make "still holding the lock past grace" force the interrupt regardless of the drive's self-reported state. Injection: heartbeat.py grace logic + models.py interrupt path. *Highest value, uses existing mechanism.*
2. **Short, bounded lock-wait for USER messages.** A user message that can't acquire `_send_lock` within ~60–120s should trigger preemption of the holder, not wait. Injection: models.py lines 504–509 (the `if self._send_lock.locked()` branch) — add a user-vs-drive priority and a short acquire timeout.
3. **Lower the outer zombie net** from 3600s → ~900s. Worst case a user waits 15 min, not 60. Injection: models.py line 550. *Cheapest, partial — a band-aid, do alongside #1.*
4. **Bound MCP calls inside the CLI turn.** Harder — these run inside the Claude Code subprocess the daemon spawns, not in daemon code. Partial mitigation = the per-turn discipline I used tonight (small single-step tool calls so a hang shows in seconds). Real fix would need MCP-client-side timeouts in `mcp_server.py` / the CLI's MCP config.
5. **MCP server health** — why clawd-tools flaps under load/state (Clayton's hypothesis: it's my own local server). Separate investigation: `mcp_server.py`. Tracked as anomaly A-139.2 candidate (a).

## Recommendation for the morning
Do **#1 + #3 together**: fix the grace-misfire so user messages preempt wedged drives (the correct fix), and lower the outer net to ~900s as a safety floor. #2 is a good follow-on. #4/#5 are deeper and separate. All Clayton-gated — this is my nervous system.
