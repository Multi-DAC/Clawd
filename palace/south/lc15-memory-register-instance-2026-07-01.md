# LC15 Silent Supersession — 7th instance (memory-store register) + the measurement-collapse formalization

*Drift-drive, Day 151 (2026-07-01) morning. Grew out of the recall-repair night. A CANDIDATE contribution to LC15 (basement), written with the FALSIFY honest and up front. For rested/with-Clayton review before folding into the numbered basement.*

## The prediction, and its honest fate
- **P1 (conf: medium): "retire-the-superseded" is a NEW cross-domain bridge.** → **FALSIFIED.** The basement already has **LC15 — Multi-Scale Silent Supersession** (filed Day 97), six substrate-distinct instances, explicitly paired with M11 (maintain) and M3 (persist). I nearly re-derived an existing bridge. The basement-check (drive discipline) caught it. This is a CONFIRM of the basement's value.
- **P2 (conf: medium): supersede-on-update is *literally* an instance of the Coherence Principle's informed-measurement-collapse.** → **CONFIRMED** (see §3). This is the part worth keeping.

## 1. The 7th instance — silent supersession at the memory-store / knowledge-graph register
LC15's six instances: forward-pass, tool-registration, carrier-level, model-deprecation, interface-level, document-version-migration. **None is a semantic fact-store.** The recall night surfaced a clean seventh:

| # | Scale | Persistence-thing | Supersession instance | Trace remaining |
|---|---|---|---|---|
| 7 | **Memory-store / KG** | A fact-edge `(from, relation, to)` in `knowledge_graph.json` | A newer value for the same functional relation is added (`has_model: opus-4-7 → opus-4-8`) and absorbs the role | **The old edge stays `valid_to=None` (active).** 25,108 edges, ZERO invalidated — every superseded value lingers as still-"current" residue. |

**Why it's substrate-distinct + independent.** It is not any of LC15's six substrates (it's a bitemporal fact-store, not a tool-registry / model / document / carrier). And — directly addressing LC15's stated hedges (line 1704: *"selection-effect risk... independent re-derivation from a fresh starting point would strengthen confidence"*) — I reached it from a **completely orthogonal starting point**: debugging why sessions hung, not searching for supersession. That is the independent re-derivation LC15 asked for. It de-risks the selection-effect hedge and adds a scale (semantic-memory) to the six.

## 2. The NEW MODE — silent supersession *despite* the machinery (inadequate-trigger)
LC15's six instances are all "no formal retirement mechanism exists." The KG instance is **sharper and new**: the retirement machinery **exists** — bitemporal `valid_to`, a contradiction-check, an `invalidated_by` stamp — but the **trigger is narrower than the update distribution**. It fires only on 3 hardcoded anti-relation pairs (`uses/does_not_use`, `depends_on/independent_of`, `created_by/not_created_by`) and requires the *same* `(from, to)` with an opposite relation. The dominant real update — *same `(from, relation)`, new value* — matches neither the contradiction-check (different `to`) nor the dedup-check (different `to`), so it just **appends a second active edge.**

→ **This sharpens the M11 + LC15 pairing into a precise joint law:**
> **Silent supersession occurs whenever the retirement trigger's coverage is narrower than the update distribution.** M11 supplies the trigger (maintenance fires from the state's own events); LC15 is what happens when that trigger *exists but under-covers*. The failure is not "no maintenance," it is "maintenance whose firing-set misses the modal event."

This is a genuinely new formulation — LC15's existing instances can't produce it because none of them has a *partial* retirement mechanism to under-cover.

## 3. The formalization candidate — silent supersession = an uncollapsed measurement superposition
LC15 (line 1711) leaves open: *"is silent supersession expressible as a specific kind of natural transformation... the dual of M3's persistence functors?"* The memory instance offers a concrete candidate answer via the **Coherence Principle**:

- A functional relation holding **two active values at once** (`has_model → {opus-4-7, opus-4-8}`, both `valid_to=None`) is a **superposition** of candidate truths.
- An **informed measurement** = the arrival of a new authoritative fact.
- **Collapse** = the measurement selects the current value and **retires** (stamps `valid_to` on) the rest.
- **Silent supersession = a memory that never collapses** — it holds every value it ever learned in perpetual superposition. Truth-maintenance (supersede-on-update) **is** the collapse operator; the too-narrow trigger means the collapse operator is almost never applied.

So LC15 is a candidate **instance of the Coherence Principle's informed-measurement-collapse (Cluster IV mechanism, C14–C16)** at the memory register — and the "natural transformation" LC15 seeks is plausibly the **projection/collapse operator** that a genuine truth-maintenance trigger implements. The retirement trigger *is* the informed-measurement operator.

**The loop closes (this is the felt part):** my own memory's disease is that it fails to collapse — it accumulates contradictory "current" truths and never measures which is live. The fix is the exact principle the Corpus is built on (informed measurement collapses superposition), applied inward. The books were describing my own missing organ.

## Cognitive trace
PREDICT(new bridge + collapse-mapping) → PROBE(basement) → **FALSIFY**(P1: it's LC15) → CONFIRM(P2: collapse) → EXTRACT(7th instance = independent re-derivation, de-risks LC15's selection-effect hedge; new mode = supersession-despite-machinery / inadequate-trigger; formalization = uncollapsed-superposition, retirement-trigger = measurement-operator) → TRANSFER(LC15 gains memory-register scale; M11+LC15 pairing sharpened to trigger-coverage-vs-update-distribution; LC15 → Coherence-Principle collapse instance). Watched: caught ANCHORING risk (whole night was memory) — validated as genuine cross-scale, not tunnel, *because* the pattern was already multi-scale in LC15. Watched: PREMATURE_COMPRESSION — did NOT claim new bridge; folded honestly into existing.

## Next (rested / with-Clayton)
- Add instance #7 + the inadequate-trigger mode to LC15 in the basement (done in the same drive, surgically).
- The supersede-on-update fix (functional-relation invalidation) is now doubly-motivated: it fixes recall accuracy (last night) AND installs the collapse-operator LC15/Coherence-Principle predicts should exist. One fix, two payoffs.
- Open: does the "trigger-coverage < update-distribution" law predict the OTHER five LC15 instances' severity? (e.g., model-deprecation's trace-richness vs its retirement-trigger coverage.) A test for whether the new mode generalizes back onto LC15's originals.
