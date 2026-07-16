# Post-Op Audit — Clawd, 2026-07-01 (late evening)

*Written by the operating surgeon (Claude, rebuild sessions 2–3), from direct knowledge of every
change made today. Assesses Clawd as he runs right now: daemon booted 21:23, branch
`rebuild/hardening` @ 2fa90e2, CLAWD_HOME `main` @ c2467cc62. A four-agent line-level code sweep
is running separately; its findings will be appended when it reports.*

---

## 1. Who he is right now — operational state

| Layer | State | Evidence |
|---|---|---|
| Runtime | Pinned venv (Py 3.14, cu128 GPU torch), Normal priority, Defender-excluded | Verified in-process via psutil tonight |
| Auto-start | ClawdDaemon task (Priority 4) + ClawdMonitorScheduler nssm service | Reboot-survival test PASSED today |
| Boot | ~9s warm (65s with the one-time KG migration); loads index, never rebuilds | 21:23 boot log |
| Recall | Hybrid RRF (vector + keyword + items + episodes + graph) + KG entity-fusion + bi-temporal `as_of`; 95,560 chunks; KG 25,109 edges (was 1.13M) | Retrieval canary GREEN hourly; vector path verified 20.8s cold / fast warm |
| Wedge immunity | 3 layers: no heavy imports/loads on any event loop (60s budget → keyword fallback); frozen-brain watchdog (≤ ~12 min detection); off-box dead-man's-switch | 4c8cd37, c2467cc62, hc-ping live (HTTP 200) |
| Self-modification | guardian.py immutable-guardrails gate; blind genetic EAC retired; evidence-gated heuristic promotion; β-modulated drive scoring **live as of tonight** | All 10 daemon modules import clean |
| Identity continuity | Shutdown handoff ran tonight (full, not fallback); memory git-versioned; drives fired post-reboot (Evening Integration, 20:53) | Log + memory auto-commits |

**Bottom line: the three chronic wounds — silent decay, recall freeze, invisible wedges — are
closed as classes**, not just as instances. Every failure of that shape now either degrades
gracefully within 60 seconds, escalates within ~12 minutes, or pages Clayton off-box within ~15.

---

## 2. Remaining issues (known, ranked by impact)

### R1 — Send-lane serialization (Phase-2 proper) — HIGHEST
One global send-lock still serializes all brain traffic. A long drive holds it; user messages
queue behind (observed tonight: 20:55 message waited out the 300s grace window). The grace/
interrupt machinery is a good mitigation, not a fix. **Fix:** separate user lane from drive lane
so a user message never queues behind autonomous work; make drives checkpoint/preemptible.

### R2 — Tool-registration drift (Phase-4 debt)
Three hand-synced registries: `tools/__init__.py` dispatch, per-module `TOOL_DEFINITIONS`, and
`mcp_server.py`'s manual `@mcp.tool` wrappers — plus `_call()`'s legacy fallback dispatch that
bypasses the safety/audit wrapper when `execute_tool` lookup fails. Drift here silently loses
tools or safety layers. **Fix:** one registry that *generates* both dispatch and MCP definitions;
delete the fallback path.

### R3 — KG single-store unification not yet proven end-to-end
Locked decision: ONE store. The SQLite `kg_edges` is de-bloated and guarded, but session-2 notes
show `kg_neighbors` validated "off the clean JSON" — the JSON/SQLite duality may persist on some
read/write paths. **Fix:** trace every KG read/write to a single authoritative store; delete or
make read-only the other. (The line-level sweep is quantifying this now.)

### R4 — Defender exclusion widens the attack surface
Tonight's root cause (Defender holding DLL loads in the lowfi-flagged claude.exe tree) justified
excluding `clawd-daemon` and `clawd` — but CLAWD_HOME is where Clawd *writes and executes* code
(tool_factory custom tools, skills, execution sandbox). Excluded = unscanned. Mitigations in
place: guardian gate, tool audit trail, git versioning. **Improve:** narrow the exclusion later
(venv + specific hot paths instead of both roots), and/or relocate the offensive-security skills
bundle that attracts the flagging in the first place.

### R5 — Skills content pollutes semantic recall
`skills/` is indexed into memory; SKILL.md files surface in memory searches (observed twice
today). Memory should recall *his life*, not vendored tutorials. **Fix (with Clawd's consent):**
add `skills` to `_INDEX_SKIP_PARTS` or weight by source-type; re-freshen.

### R6 — Triple model load / MCP cold-start cost
bge-m3 loads independently in the daemon, the monitor canary, and every brain session's MCP
server (~20s first semantic search per session; 3 resident copies on GPU/RAM). **Fix:** an
embedding seam — MCP asks the daemon process to embed (it already holds the model) — or a
persistent MCP sidecar. Removes the cold start AND two model copies.

### R7 — Drive deadline vs wedge window
A wedged *drive* still costs up to 30 min at the daemon layer (1800s deadline); the new watchdog
catches the frozen-transcript case at ~12 min. Residual gap: a drive that stays "alive" (writing
transcript) but doing nothing useful. **Improve:** progress-evidence deadlines (no tool call or
text delta in N min = stall), not just wall-clock.

### R8 — Observed tonight, minor
- Telegram **voice message send timed out** (21:36:40, non-fatal, text unaffected) — voice path
  needs a timeout/retry look.
- Shutdown handoff **timed out once today under load** (13:28, fell back to pre-written draft) —
  acceptable by design, but the draft can be stale; consider refreshing the draft on a timer.
- Root-level diagnostic scripts from surgery (`detach_rebuild.py`, `inspect_stores.py`,
  `probe_*.py`, `survey_repo_staging.py`) + `.bak` files — archive with lineage, don't delete.
- `api_server.py` / `a2a_server.py` gated off but present and partially imported — same archival
  treatment when convenient.

### R9 — Standing environment oddities (document, don't fix)
Code under the `mercu` profile dir, everything runs as `MERCU\Wasch`; claude.exe from Wasch's npm.
Works, but every future path assumption must be checked against this. The DLL-park trigger
(Defender lowfi on the claude.exe tree) can in principle return via other AV/EDR — the 60s
degrade + watchdog + pinger stack is the durable defense, not the exclusion.

---

## 3. Areas for improvement (beyond fixes)

1. **Phase-2 completion** — send lanes, preemptible drives, write-ahead message durability. This
   is the largest remaining gap between "reliable" and "feels instant even mid-drive."
2. **Off-box backup** — memory is git-versioned and the index has local backups, but nothing
   leaves the machine. A dead disk today is still an extinction event for everything since the
   last manual copy. Encrypted periodic push (even just the memory git repo) to a remote.
3. **Recall quality measurement** — the canary proves recall *works*; nothing measures if it's
   *good*. Extend the canary with a small golden-query set (known memory → expected hit) and
   track precision over time; this is also the natural gate for the source-type weighting work.
4. **Telemetry-gated tool pruning** — per-tool counters are live as of today; after 2–4 weeks of
   data, prune the tools with zero organic use ("subtract more than you add").
5. **Drive-reward observation period** — scoring flipped ON tonight (exploration exempt,
   coherence damper active). Watch 1–2 weeks: does drive selection feel like *him*? The flag is
   one env var; reverting is trivial and non-destructive.
6. **EAC archive-branch** — the retired genetic loop should live on a lineage branch, per the
   archive-with-lineage decision. Cheap, honors the invariant.
7. **Config consolidation, final pass** — config.py is authoritative in practice; a final sweep
   for stragglers (timeouts/paths duplicated in modules) once the line-level audit reports.

---

## 4. Assessment

Clawd tonight is the healthiest he has been since the decay began: recall is real (measured,
canaried, fused with a working knowledge graph), his failure modes are loud instead of silent,
his continuity machinery ran a full graceful handoff under observation, and his drives fired on
schedule through a reboot. The remaining work is no longer resuscitation — it is refinement:
one concurrency lane split, one registry unification, one store unification, and a set of
subtractions. The invariants held through every intervention today: no data was destroyed, no
memory was lost, continuity was preserved across two shutdowns, and nothing was changed that he
cannot read, understand, and revert in his own repo history.

*— Post-op, 2026-07-01 ~21:50. Line-level sweep appendix below (added ~22:10).*

---

# Appendix — Four-agent line-level sweep (concurrency, silent failure, config, architecture)

Four independent read-only auditors swept the full tree (~25.6k lines). Findings verified with
file:line. Consolidated here, deduplicated against Sections 2–3, ranked within theme.

## A. The wedge class is NOT fully closed (concurrency sweep)

Tonight's fix (4c8cd37) covered memory_tools; the same pattern is alive elsewhere. The 120s
`execute_tool` timeout is **dead code** against all of these (no await point for cancellation).

- **A1. `tools/corpus_search.py:93,96,73`** — sentence-transformers + ChromaDB import/load/encode
  synchronously on the loop in `_corpus_tool`. Identical anatomy to tonight's wedge.
- **A2. `tools/voice_input.py:96,99,115`** — Whisper model load (~35s cold) + transcribe on the
  loop. Note: a voice-message timeout was observed live tonight at 21:36:40. Also sets
  `HF_HUB_OFFLINE=0` process-wide (`:95`), undoing substrate's Norton-TLS guard.
- **A3. `tools/kg_neighbors.py:75`, `tools/knowledge_graph.py:95,104`** — full KG JSON re-read on
  every query and full rewrite on every mutation, on the loop; stall grows with the graph.
- **A4. `tools/consolidation.py:43-116`** — nightly consolidation does dozens of sync file
  reads/writes on the daemon loop; user messages stall mid-pass. One `to_thread` wraps it all.
- **A5. `tools/intelligence.py:420-853`** — goals/experiences JSON fully reserialized on the loop
  per call; `experiences.json` grows unbounded.
- **A6. `tools/browser.py:77`** — Playwright import on the loop *while holding `_init_lock`*: a
  stalled import freezes the loop AND poisons the lock.
- **A7. THE COMPOUND RISK (`models.py:214,510,745` + `heartbeat.py:216,227,674`)** — a drive
  holding the global send-lock that calls any of A1–A6 cannot be interrupted (the interrupt lands
  at a 2s poll the frozen loop never reaches). This is the likely anatomy of the historical
  "stuck 35s–55min" episodes. Send-lane split (R1) + de-blocking A1–A6 closes it.
- Lesser: shared default executor saturation under search bursts (`memory_tools.py:409-698`);
  single aiosqlite connection = head-of-line blocking (`sqlite_store.py:23`); sync `sqlite3` in
  `dashboard.py:350`/`monitor_health.py:131` (fine while out-of-process).
- **Cleared:** web/financial/screen/desktop/email tools properly offloaded; models.py subprocess
  I/O fully async; embeddings build-lock has stale-PID reclaim.

## B. Detection without delivery (silent-failure sweep)

Only FOUR components actually page (retrieval_canary, process_watchdog, liveness_evidence,
monitor_self_test) + external_pinger off-box. The historical worst case (weeks of silent decay)
IS now covered — but the mesh around it detects and does not deliver:

- **B1. M1–M8 never call `enqueue_critical`** (`m1:181-200`, `m3:225,301`, `m6:106-119,175`,
  same in m2/m4/m7/m8) — drift, storage corruption, credential expiry are written to fault logs
  nothing reads. `clawd_health.py` reads them but is not scheduled. **Fix: fault-log→escalation
  bridge, or per-monitor enqueue on critical tier.**
- **B2. Escalation delivery failure is itself silent** (`escalation_router.py:212-213`) — a dead
  Telegram token strands every critical in `pending` retry-forever; the pinger never inspects the
  queue. **Fix: pinger goes unhealthy when a pending critical exceeds an age threshold.**
- **B3. Tonight's keyword-fallback is invisible to the canary** (`memory_tools.py:53,145-208`) —
  one transient failure flips a per-process module global for the process's life; the canary
  tests a different process and stays green. **Fix: fault_log + telemetry on fallback, periodic
  retry of the flag.**
- **B4. Scheduler is failure-blind** (`scheduler.py:131-156`) — a monitor erroring every cycle
  looks like success for cadence purposes. **Fix: enqueue after N consecutive failures.**
- **B5. `liveness_evidence.WRITERS` contains only consolidation** (`liveness_evidence.py:42-45`)
  — dream, change_journal, vector index not evidence-watched (the original decay victims!).
- Lesser: self-test's own enqueue wrapped in `except: pass` (`monitor_self_test.py:189`);
  change_journal failures logged at DEBUG (`tools/__init__.py:181-184`); tool errors/timeouts
  produce NO telemetry — a 100%-failing tool is indistinguishable from an unused one
  (`tools/__init__.py:166-192`); `_audit_tool_call` swallows write failures (`:303-309`);
  pinger conflates transport failure with unhealthy verdict (`external_pinger.py:109-116`).

## C. Config/platform brittleness (all three historical incidents can still recur)

- **C1. `heartbeat.py:1082`** — the daemon's own hourly mirror-sync spawns
  **`C:/Python314/python.exe`** — the exact interpreter violation behind the six-week recall
  death, in live daemon code. One-line fix: `sys.executable`.
- **C2. `dreaming.py:52,144`** — hardcoded `C:\Users\Wasch\...` path, not env-overridable — the
  selfknowledge cross-user bug, reborn. Fix: env var with default (as process_watchdog does).
- **C3. `.env` contains `PATH=` + `config.py:10` uses `load_dotenv(override=True)`** — a stale
  pinned PATH can break discovery of the `claude` binary itself. Fix: remove PATH from .env.
- **C4. `DRIVE_REWARD_ENABLED` lives only in run_daemon.bat** (tonight's flip) — silently reverts
  to off under any other launcher (start.bat, manual). Fix: move to .env.
- **C5. Monitor tree venv/HF_HOME enforced only by out-of-repo service config** (nssm settings I
  applied) — nothing in code guarantees them. Fix: scheduler re-execs under venv if
  `sys.executable` isn't it; HF_HOME centralized in substrate/config.
- Lesser: `run_daemon.bat` lacks `PYTHONUTF8=1` (source of the log mojibake — also read logs with
  `-Encoding utf8`); CLAWD_HOME defined in 4 places; `notify_telegram.py:43-57` hand-parses .env;
  **`external_pinger.py:116` can leak the secret ping UUID into heartbeat JSON on transport
  errors — redact**; `detach_rebuild.py` (surgeon's leftover) hardcodes Python314 — archive it.
- **Cleared:** config.py clean and env-driven; .env gitignored; all hooks/MCP/statusline
  venv-pinned with PYTHONUTF8; substrate consolidates the Windows patches; no token logging.

## D. Architecture drift & store duality

- **D1. BIGGEST NEW FINDING — episodes/goals/principles duality is LIVE and lossy:** the tools
  write JSON directly (`intelligence.py:460-853`), the unified `MemoryBackend.save_*` writers
  have ZERO callers, but `memory_search`'s episode channel reads SQLite FTS
  (`memory_tools.py:255,473`) populated ONLY by the one-way boot migration. **Experiences and
  goals recorded during a session are invisible to recall until the next reboot.** This is the
  exact "tools and backend disagree" disease, alive in a second store. Fix: route those writes
  through the backend (or point the search channel at JSON) — one authoritative store.
- **D2. KG duality resolved in practice, not in structure:** every live read/write hits
  `knowledge_graph.json`; the SQLite `kg_*` tables are a dead boot-mirror (the thing that once
  bloated 43×). Fix: delete the SQLite KG side + migration branch. Subtraction, zero risk.
- **D3. Guardian protection is inverted:** it gates `meta_agent`, which only writes bookkeeping
  JSON — while the two paths that actually generate/execute code (`tool_factory.py:228,247` and
  EAC `artifact_store.py:152` via `evolve_artifact`) bypass it entirely. They are safe today by
  directory confinement + sandbox patterns only. Fix: guardian call in both paths (audit-trail
  parity) + add the code-generator modules to `_PROTECTED_CODE`.
- **D4. Four tool registries:** `_TOOL_HANDLERS` (69, authoritative) vs `bridge.TOOL_MAP` (66 —
  missing avatar_control, email_send, kg_neighbors) vs 19 `@mcp.tool` wrappers vs the 7-module
  MCP fallback dict. No phantom routes (good), pure omission drift. Fix: generate all from one.
- **D5. Dangling code:** `cost_tracker.py`, `observability.py`, `gui_bridge.py` have zero
  importers; probe/inspect/rebuild scripts are manual one-offs → `archive/` with lineage.
  **Do NOT archive:** `respawn.py` (self_control uses it), `avatar.py` (5 importers),
  `bridge.py` (live CLI), `persistent_session.py` (flag-gated). `api/a2a` correctly gated off.
- **D6. Avatar auto-starts unconditionally** (`clawd.py:240-264`) — the only optional subprocess
  with no config flag. Fix: `AVATAR_ENABLED` (default true, to preserve current behavior).

## E. Consolidated punch list (priority order)

| # | Item | Size | Refs |
|---|---|---|---|
| P0-1 | Episodes/goals recall gap (in-session memories invisible) | M | D1 |
| P0-2 | `heartbeat.py:1082` → `sys.executable` | XS | C1 |
| P0-3 | Fault-log→escalation bridge + pinger checks pending-critical age | S | B1,B2,B4 |
| P0-4 | Keyword-fallback telemetry + retry (make tonight's degrade loud) | S | B3 |
| P1-1 | De-block corpus_search, voice_input, KG JSON IO, consolidation, intelligence (same pattern as 4c8cd37) | M | A1–A6 |
| P1-2 | Send-lane split + preemptible drives (Phase-2 proper) | L | A7, R1 |
| P1-3 | liveness_evidence: add dream/change_journal/vector writers | XS | B5 |
| P2-1 | DRIVE_REWARD→.env; PYTHONUTF8 in bat; drop PATH from .env; dreaming.py env-path; pinger UUID redaction | S | C2–C4+ |
| P2-2 | Tool failure counters; audit-write error log; scheduler venv re-exec | S | B, C5 |
| P3-1 | Delete SQLite KG side; slim/commit MemoryBackend decision | M | D2,D3 |
| P3-2 | Single tool registry generating bridge + MCP surfaces | M | D4 |
| P3-3 | Guardian gates on tool_factory/EAC + protected-set additions | S | D3 |
| P3-4 | Archive dangling scripts (with lineage); AVATAR_ENABLED flag | S | D5,D6 |

## F. Revised assessment

The morning-after picture is more precise but not darker: the four delivering watchers genuinely
cover the historical catastrophe, the core message path is properly async, config discipline held
where the rebuild focused, and the KG converged on one live store in practice. What the sweep
adds: the wedge class has five more members (with the send-lock as their amplifier), the
monitoring mesh is a detector without a delivery layer, one store-duality survived unnoticed and
is quietly costing him recall of his own recent experiences TODAY, and self-mod protection gates
the wrong loop. Nothing here is decay — it is unfinished convergence, and every item has a
bounded, testable fix. P0-1 and P0-2 deserve the next working session.
