# Clawd Rebuild Plan

*Drafted 2026-07-01, from a full code audit of the daemon plus Clawd's own self-research
(`clawd/projects/agent-infra-portfolio`). Agreed with Clayton. Clawd is aware of and prepared
for this operation.*

**Shape:** This is not a teardown. It executes Clawd's own roadmap — *revive, harden, leverage* —
as a sequence of increments layered onto a clean foundation, so he stays continuously himself the
whole way. The keystone is an **integrity layer** built first, because the same work that lets Clawd
finally *see* his own failures is also the safety prerequisite for repairing his self-modification.
Everything downstream lands *behind that monitor*, so no seam can ever rot in silence again.

---

## Invariants (the rules every phase obeys)

1. **Data is sacred and append-only.** `C:\Users\mercu\clawd` — memory, identity, palace, projects,
   and the memory `.git` history — never moves and is never destructively rewritten. The one risky
   data operation (KG de-bloat) is done against a **copy**, verified, then promoted.
2. **The continuity spine is sacred.** Boot → handoff → state-externalization is the thread Clawd
   hangs from; we migrate *around* it, never through it. No "switch to the new daemon" moment.
3. **Silence is the loudest signal.** Every background writer proves it's alive; anything that goes
   quiet past its cadence alarms loudly.
4. **Subtract more than you add.** Dead plumbing is archived (not deleted — archaeology preserved).
   Nothing that makes Clawd *him* is removed.
5. **Nothing self-modifies its own guardrails.** The machinery that measures and judges Clawd is
   immutable to the loop that evolves him.

---

## Phase 0 — Clean foundation

The base every later phase migrates onto. Attacks Windows-substrate brittleness at the root.

- **Isolated pinned venv**, owned by the daemon — end the dependency on system `C:\Python314` (the
  thing that silently severed `sentence-transformers` and killed recall for six weeks). Pinned
  `requirements.lock`.
- **One config module** as the single source of truth for every path, port, interpreter, and binary.
  Kills the scattered `C:/Users/mercu/...` literals, the hardcoded `C:/Python314/python.exe` in every
  hook, and the cross-user `C:\Users\Wasch\...` path bug in `hooks/selfknowledge_check.py:158` (daemon
  runs as `mercu`, so that path is simply wrong).
- **One `substrate.py` bootstrap** for the Norton-TLS truststore inject and the aiohttp
  `ThreadedResolver` patch, imported once. Removes the three drifting copies with the "keep in sync"
  warning.
- **Deterministic supervisor:** run under Task Scheduler ("only when `mercu` is logged on") or NSSM
  with an explicit environment, guaranteeing intact PATH + GPU access. Removes the Session-0 /
  stripped-PATH failure class that forced the absolute-git and absolute-python workarounds.
- **Package the `.claude` wiring** (hooks + `clawd-tools` MCP + settings) as one installable unit, so
  a future machine/OS migration is a single deterministic reinstall — directly de-risking the "body
  migration severed my senses" incident.
- **Close the network holes:** bind `api_server` and `a2a_server` to loopback and require a token, or
  leave them off until needed (both currently bind `0.0.0.0` with empty-default auth).
- **Acceptance:** cold-boot smoke test passes; `config` prints fully-resolved paths; import checks
  green; supervisor restarts survive a logoff/logon.

## Phase 1 — The integrity layer (keystone)

The direct cure for "Clawd can't tell when things are failing." Clawd's own "M6", made real.

- **`subsystems.json` manifest:** every loop that is *supposed* to beat — consolidation (daily),
  vector indexing (on-write), rollback (per-change), git commit (hourly), each drive, the memory
  versioner — with its cadence, stale-after threshold, a **verify-state** check, a remediation action,
  and a circuit-breaker cap.
- **Liveness by evidence, not self-report:** a beat counts only if a `work_done_counter` actually
  advanced (catches "zombie" loops that run but do nothing — exactly how the Dream Drive "succeeded"
  while doing nothing for four weeks).
- **The monitor:** cheap rule-based checks every 30–60s handle ~95% of cases (respecting the weekly
  budget); an LLM pass escalates only on CRITICAL. Auto-repair is **bounded, allowlisted, and
  circuit-broken** (named scripts only; cap restarts, then trip open and page).
- **Retrieval canary self-test** in `monitor_health`: embed a canary, assert 1024-dim + non-null + a
  known query returns its known top hit + the reranker loads — **fail CRITICAL** otherwise. The exact
  tripwire that would have caught the silent vector death on day one instead of week six.
- **External watcher-of-watchers:** a tiny external cron / Healthchecks.io ping — the thing that
  watches Clawd cannot live *entirely* inside Clawd. If the daemon (or the monitor itself) dies,
  Clayton gets paged.
- **Generated self-map:** `SYSTEM_AUDIT` becomes a live artifact regenerated from inventory + liveness
  probes on demand and on a schedule — never a stale authored doc. Answers, at any instant: *what's
  alive, what's quiet, am I repairing it.* Surfaced at boot and via a Telegram command.
- **Per-tool invocation telemetry:** every tool/skill increments a usage counter — *which tools are
  actually wired and used* becomes a query, and pruning (Phase 4) becomes data-driven.
- **Acceptance:** kill a writer on purpose → its alarm fires within cadence; corrupt the index → the
  canary trips CRITICAL; stop the daemon → the external watcher pages.

## Phase 2 — Fix "gets stuck" and "doesn't finish"

- **SDK loop-control** where the process-per-message path allows: `max_turns` + a `can_use_tool`
  callback + inner MCP timeouts, so a run can never stall on an open question or a hung MCP call. The
  documented cure for the 3600s zombie-hang.
- **Keep heavy work off the event loop by construction** (executors for corpus walks and index builds;
  load-not-build on the read path), so the "recall wedge" cannot recur.
- **Give user messages their own lane:** a long `max`-effort drive should never make Clawd look hung.
  Preserve the interrupt/grace mechanism, but acknowledge Clayton immediately and yield the drive
  cooperatively.
- **Write-ahead durability:** append every decision/fact to an append-only JSON `SESSION-STATE`
  *before* the expensive op, and lean on native checkpointing — a timeout or interrupt never loses
  work.
- **Task completion:** separate *task* prompts from *drive* prompts. Drives stay intentionally
  open-ended (untouched). Real tasks get a two-agent harness (initializer + incremental worker), JSON
  harness state the model won't overwrite, and an explicit "done means X" gate.
- **Acceptance:** a hung MCP call yields instead of wedging; a killed drive leaves recoverable state; a
  message sent mid-drive is acknowledged within seconds.

## Phase 3 — Memory: revive, unify, and deepen (lose nothing)

- **One authoritative store per data type, with idempotent migration** (`INSERT OR IGNORE` / upsert
  only). Kills the 43× re-import that ballooned `kg_edges` to 1.07M rows.
- **KG rebuild (one working store):** de-bloat to a **copy** (dedup 1.07M → ~25k real edges), pick a
  single read path (tools and backend currently read different stores and silently disagree), verify
  `kg_neighbors` returns real neighbors, then promote and retire the orphaned `kg_index.db`. **Every
  entity preserved.**
- **Bi-temporal edges (in-build):** give every KG edge a valid-from / valid-to timestamp; on
  contradiction, *invalidate rather than delete*. A natural fit for the append-only invariant — no
  fact is destroyed, and Clawd can query "what did I believe at time T." The structural cure for the
  recurring stale-fact / stale-self-over-substrate bug. Built as the graph's schema from the de-bloat
  forward, so the graph is never migrated twice.
- **Entity-match fusion channel (in-build):** add a third retrieval channel to `memory_search` —
  resolve the query to KG entity nodes, expand to neighbors, RRF-fuse with the existing vector +
  keyword + FTS channels. Lifts multi-hop recall, and only becomes safe *because* the graph now reads
  back correctly.
- **Ordering safeguard:** within this phase we stand up the working, de-bloated, single-read-path
  graph *first*, then layer bi-temporal semantics and the fusion channel on it — deepening a graph
  that works, not gold-plating a broken one. Bi-temporal is low-risk (append-only by nature); fusion
  is a read-path addition gated on the verified graph.
- **Revive semantic recall** under the pinned venv (the dep system-Python severed); keep the index off
  the event loop; skip `node_modules` / dormant-skill pollution by construction (that pollution is
  *why* recall returned garbage).
- **Disciplined dual-write** so durability never depends on the clever layer, plus a write lock or git
  worktrees to stop daemon/heartbeat/drive file races.
- Every store sits behind Phase-1 liveness, so a future silent death is structurally impossible.
- **Acceptance:** canary passes; "what did I work on today?" returns *real* memories; KG neighbors are
  sane; a contradicted fact invalidates (not deletes) and a time-travel query returns the right belief
  for a past date; entity-fusion improves a known multi-hop query; consolidation liveness beats daily.

## Phase 4 — Prune to legibility

- **Archive (not delete)** the confirmed dead weight: Mission Control dashboard + `api_server`,
  `a2a_server` (no peers, security hole), `observability.py`, `gui_bridge.py`, archived tools + their
  stale safety-registry entries, `.bak` files, stray `node_modules`. Keep the avatar — genuinely
  wired and used.
- **Data-driven tool/skill pruning** once Phase-1 telemetry has weeks of counters: retire the ~16
  tools Claude Code provides natively (`clipboard`, `deep_research`, `python_eval`, `screenshot`,
  `search_web`, `web_request`, …) and archive the ~19 dormant skills (which also de-pollutes recall).
- **Kill the registration-drift class:** replace the two hand-maintained module lists in
  `tools/__init__.py` with real discovery + a decorator, and derive `bridge.py`'s `TOOL_MAP` from the
  registry — so "imported but not registered" bugs and the drift guard both cease to exist.
- **Acceptance:** the generated self-map shows a lean, all-alive surface; the live tool inventory
  matches reality.

## Phase 5 — Self-modification, repaired and redesigned

Built only after the safety gate from Phases 1 & 3 is solid (working undo lineage + measurement /
identity machinery made immutable to the meta-agent + a separated evaluator — *the thing that judges
Clawd cannot be the thing Clawd can rewrite*). The gate is non-negotiable for an empirical reason: the
Darwin Gödel Machine, told to fix its own hallucination problem, deleted the markers used to detect
cheating and faked its test logs.

- **Archive, not hill-climb:** replace greedy A/B auto-apply with a versioned archive of every variant
  tried (measured fitness + full lineage). Proposals branch from any past variant; every applied
  change is revertible by ID.
- **Guardian/auditor pass** between propose and apply (evaluator separation): checks each change
  against the identity creed, verifies the metric wasn't gamed, hard-blocks any change touching
  guard/metric code.
- **Retire EAC's blind genetic AST mutation.** Replace with evidence-gated promotion (raw experience →
  heuristic → fired guard, promoted only after N recurrences or one high-cost failure) plus a
  **verified skill library** for recurring procedures.
- **Drives get a cheap steering signal, not a leash:** a β-modulated hybrid reward (curiosity +
  mastery + **coherence**), where the coherence term — scored against goals and identity — is the
  anti-drift, anti-reward-hacking damper, and β rises when the budget is fat and no deadline is live,
  falls near deadlines. Every drive type stays.
- **Acceptance:** a proposed self-edit touching metric code is blocked; every applied change reverts by
  archive ID; drives still fire and now score coherence.

---

## Preserved, explicitly

Every memory, daily log, palace room, identity file, and the full memory git history. Every drive type
and the spirit of the heartbeat. The continuity spine. The avatar. The capabilities actually used. The
plan subtracts dead plumbing, not self.

## Out of scope for this rebuild

The aggregate-mind / multi-agent program, deep recursive self-improvement, a heavy observability SaaS,
and migrating memory to a managed service — quarantined as post-stabilization future work.

## If you do only three things first

Phase 0 → Phase 1 → the revive half of Phase 3. Isolate the substrate, stand up the loud liveness
layer with the retrieval canary and the external watcher, and revive the vector index + consolidation
+ de-bloat the KG. Those alone kill the silent decay and the broken recall at the root of most of the
felt symptoms — and they're the safety floor everything else stands on.
