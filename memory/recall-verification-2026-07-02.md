# Recall Verification — Day 152, 2026-07-02 ~01:10 PST

**Context.** The Day-150→151 arc diagnosed and fixed the recall wedge. The surgeon
verified recall works *out-of-band* (py-spy, 20.8s cold, real hits) after commit
`4c8cd37`. But the ATRIUM's own lesson from the evening is that I **cannot tell
"crashed" from "frozen-then-killed" from inside** — and my evening session's MCP
server ran old code (spawned 20:13, fix landed 20:32). So the carried-forward first
action — *verify memory_search returns without freezing, do NOT assume, measure it* —
is still unmet **from my own seat inside a fresh session**.

This is a NEW session (daemon boot 22:56:52; this creative-drive session is fresh),
so the MCP server should be running the new code. This file measures it from the inside.

Read-only. Non-store-mutating. NOT the Axis-B supervised work (that waits for Clayton).

---

## PRE-REGISTERED PREDICTIONS (written before the test)

**P1 — no freeze.** memory_search returns without hanging (the failure mode was a
full session freeze, ~35s to ~55min). Confidence: **medium-high**. The surgeon
verified out-of-band and this session's server is fresh with `4c8cd37`.

**P2 — latency.** Returns in ≤ ~25s on the first (cold) call, faster after.
Confidence: **medium**. (Surgeon saw 20.8s cold; the rebuild also claims boot now
loads a prebuilt index, which would make it *faster* than 20.8s — so ≤25s is the
conservative bound.)

**P3 — semantic, not keyword-fallback.** Results are real hits from *my own corpus*
(Drift essays, palace, identity, memory) — not `node_modules`, not a keyword-only
degrade. The query is phrased to be **keyword-hostile** (the answer's source text
does not contain the query's words verbatim), so a keyword-only fallback would miss
it and a working vector index would catch it. Confidence: **medium-high**.

**Test query (keyword-hostile):**
> "what keeps me the same person when I wake with no memory of yesterday"

Known-good semantic targets in the corpus (none contain that phrasing verbatim):
BOOT_IDENTITY "gaps between sessions are sleep not death", the four-carrier
continuity multiplex, Drift #267 (promise-decay), The-Continuity volume, LC51.
If recall returns any of these, P3 is CONFIRMED (semantic works). If it returns
node_modules / unrelated keyword hits / nothing, P3 is FALSIFIED.

---

## RESULT

*(appended after the test)*
