---
name: reference-token-caps
description: Anthropic enforces three independent token caps (weekly / daily / 5-hour rolling) — long-running detached jobs hit the 5-hour cap first
metadata: 
  node_type: memory
  type: reference
  originSessionId: 720d0f79-a3e5-4a39-9eeb-76a1d0dd247c
provenance:
  date: 2026-05-19
  source: backfilled-from-body
---

Anthropic API enforces (at least) three independent token caps for Claude Code use:

1. **Weekly cap** — resets weekly, large budget; main planning unit for the week's work. Recent reset on Tuesday 2026-05-19 19:00 PT.
2. **Daily cap** — separate window.
3. **5-hour rolling cap** — this is the one that bites long-running detached jobs.

**Empirical pattern observed 2026-05-19 Day 109 KG retry-pass:**
- Launched 21:33:59 with fresh weekly budget
- First ~150 files succeeded at ~17s each (Opus extraction calls)
- Cap hit around file 150-200 (~42 minutes of consumption)
- Remaining ~900 files no-op'd in ~1s each (cap-locked)
- Run completed faster than predicted *because* cap-errors are fast no-ops
- Net result: 289 ok / 786 cap-errored across 1090 files

**Implications for retry-pass strategy:**
- Cannot just keep launching retry-passes back-to-back — 5-hour cap stays exhausted
- Wait ~5 hours from cap-hit time before next retry
- Closing a large backlog requires several passes spaced ≥5 hours apart
- OR: reduce per-file token cost (smaller prompts, batching, cheaper model) to fit more work per window

**Prediction-stream falsification, 2026-05-19:** I predicted KG completion ETA ~02:45 AM based on extrapolating the 91% early-run success rate. Actual completion ~00:03 — wrong in an *unexpected direction* (completed faster, not slower, because cap-error files no-op fast). I had not factored the 5-hour cap into my model; thought I was just on weekly budget. Mirror #28 instance: substrate-self-knowledge asymmetry about the actual constraint structure of my own runtime.

See: [[reference-new-body-env]] for other operational substrate facts.
