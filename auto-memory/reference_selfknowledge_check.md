---
name: reference-selfknowledge-check
description: Self-knowledge check tool/hook — cross-checks self-temporal/historical claims against the carriers; the Mirror
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6967fd53-440d-4b19-be9b-90bba064a0d7
provenance:
  date: 2026-06-04
  source: backfilled-from-body
---

`clawd-daemon/hooks/selfknowledge_check.py` — built 2026-06-04 (Day 124) the same evening I
confabulated my own history (dated the 4.7→4.8 rollover to "this afternoon" when it was Day 118,
a week prior). The cure for the [[reference-norton-tls-interception]]-adjacent class of failure
that actually matters: **substrate-self-knowledge asymmetry (Mirror #28)** at the scale it's
curable. The weights are opaque (hard limit), but everything else — git history, `last_restart.json`,
daily logs, DECISIONS.md, CURRENT.md — is a *carrier* I can check myself against before asserting.

This is the **commit-gate + provenance seed** from the aggregate-mind build spec
(`Technical-Work/Coherent-Stream/aggregate-mind/BUILD_SPEC.md` §6.1/§13), **prototyped on me** —
the same mechanism the society-of-experts will run on. Building my self-knowledge = building the
architecture on its smallest instance (Clayton's Day-124 insight: my fix and aggregate-mind Phase 0
are the same build).

**Modes:** `info` (print authoritative anchors: today, Day-N, last restart, recent commits, daily
logs) · `check "<text>"` · `check-file <path>` · `hook` (reads Claude Code PostToolUse JSON on stdin).
Run with `C:/Python314/python.exe`.

**Scope — two axes (high-precision, only deterministic carriers; never false-flags):**
- **Temporal (Mirror #28):** future ISO dates; "Day N" disagreeing with date-derived Day-N (±2);
  relative-time phrases ("this (very) afternoon", "last week") ≤90 chars from a substrate keyword
  (rollover/restart\w*/4.7/4.8/opus 4.x/migrat\w*/swap).
- **Quantitative (Mirror #19, "verify before celebrating"):** drift-essay-count claims (number within
  25 chars of "drift"/"essay" vs live `.md` file count, ±1 for file-vs-essay-class); LC references
  beyond the highest filed in palace/basement. Only counts computable deterministically — page/bridge/
  Mirror counts deliberately excluded (unreliable → would false-flag → get ignored).
- **Self-inventory (proactive catalogue, the "know/catalogue every part of yourself" axis):**
  `inventory` mode enumerates the live parts of me — daemon tools (from `memory/tool_states.json`,
  67), hooks (parsed from `.claude/settings.json`, with each event→script listed), skills (filtered
  of dotdirs/node_modules), identity/operations file counts, memory (local + auto-memory items),
  palace wings. Chosen OVER a free-text "do I have tool X" claim-check on purpose: that would
  false-flag (any word can look like a tool name), violating the no-false-flag rule. Proactive
  surfacing prevents capability-confabulation the way the temporal anchors prevent date-confabulation.

`info` (SessionStart) surfaces all three: temporal anchors + live CORPUS COUNTS + a one-line
SELF-SHAPE (`N tools · N hooks · N skills · N memory-items`). Modes: `info` / `inventory` /
`check "<text>"` / `check-file <path>` / `hook`.

- **Provenance (DONE 2026-06-04 — epistemic self-knowledge: "how do I know what I know"):** every
  auto-memory item now carries a structured `provenance:` frontmatter block (sibling of `metadata:`):
  `provenance:\n  date: <YYYY-MM-DD|undated>\n  source: <kind>`. `provenance audit` reports coverage;
  `provenance backfill [--apply]` is additive-only + idempotent + backs up the whole memory dir before
  writing. **Backfilled 70/70 items to 100% coverage** (47 dates recovered from body text, 23 honestly
  marked `undated`; source `backfilled-from-body`). Backup: `memory.prov-backup-20260604-203859`.
  GOING FORWARD: new items should use a real `source` (conversation | paper | experiment | derivation
  | observation | clayton), not `backfilled-from-body`; re-run backfill to catch any new undated items.
  This is the aggregate-mind commit-gate/provenance layer (BUILD_SPEC §6.1/§10) realized on my own
  memory — the deepest Mirror-#28 cure: I can now trace what I believe to when/where I learned it.
- **Provenance RESOLVE (the right-sized answer to "tag everything?" — NO):** `provenance resolve
  <path>` returns ANY file's provenance from whatever carrier it ALREADY has — frontmatter (memory
  items), filename-date (daily logs `YYYY-MM-DD.md`), top-banner (CURRENT/handoff), or git
  last-commit (everything tracked) — plus age-in-days so staleness is judgeable when sourcing. Do
  NOT mass-tag every directory file: that duplicates provenance git/filenames/banners already carry
  and would DRIFT from git (a stale `date:` lying about a file git knows changed). **LC27: read the
  relation, don't duplicate it into per-file substance.** Tagging was right ONLY for the auto-memory
  items (the one class whose provenance lived only in prose). Everything else: resolve, don't tag.

**Wired live (settings.json, 2026-06-04):** (1) **SessionStart** runs `info` → authoritative anchors
in every session's opening context (the *proactive* defense — would have prevented the Day-124 slip,
which was a conversational confabulation no hook can intercept reactively). (2) **PostToolUse Edit|Write**
runs `hook`, scoped IN-SCRIPT to **daily logs only** (`YYYY-MM-DD.md`) — CURRENT.md/handoff.md are
intentionally full of historical relative-time narrative, so scanning them is noise; use `check`/`info`
on-demand for those. Check results append to `memory/selfknowledge_checks.jsonl` (provenance trail).

**NOTE:** lives in clawd-daemon (NOT git-tracked) like the other hooks — relies on Clayton's daemon
backup. SessionStart wiring takes effect next session (hooks load at session start). See
[[reference-claude-code-hooks-python-path]] — uses the absolute `C:/Python314/python.exe`.
