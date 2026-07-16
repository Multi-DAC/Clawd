# Continual-Coherence MVP — Pre-Registration (DRAFT)

**Filed:** 2026-05-30, Day 120, evening. **Status: RATIFIED by Clayton 2026-05-30 ~20:00 PST — run as proposed.** All 5 decision points locked at the recommended values: Gemma-3-270m / templated ground-truth generator / N=8 rounds, 3 seeds / SE bands >1·SE, ±1·SE, <−1·SE / four outcomes accepted as-is. Implementation may proceed.
**Tests:** Thesis B (live-weak-beats-frozen) + the §6.1 central question (is tier-3 necessary, or is tier-2 sufficient?).
**Parent doc:** `continual-coherence-program-positioning-2026-05-30.md`

---

## 0. The question, stated for falsification

> Does bolting **tier-3 weight-consolidation** onto an already-coherent **tier-2 (memory)** system add capability that memory alone cannot — *without* degrading general capability?

Clawd is the existence proof that tier-2-only learns continuously with frozen weights. The bake-off prior is that bolted-on additions often **lose** to the version without them (`no_mirror`). This experiment is built so that result, if it happens, is a clean finding rather than a disappointment.

## 1. Arms (3)

| Arm | Description | Weights | Memory | Consolidation |
|---|---|---|---|---|
| **0 — frozen-bare** | base model alone on the domain | frozen | none | none |
| **A — tier-2** | base + retrieval of validated past experience | frozen | yes (retrieval store) | none |
| **B — tier-2+tier-3** | A + periodic firewall-gated LoRA "sleep" on validated experience | LoRA-updated | yes | yes |

Two contrasts isolate the two questions:
- **A vs 0** → does intrinsic memory help at all? (sanity / floor)
- **B vs A** → does weight-consolidation add over memory? **(the §6.1 central question)**

## 2. Fixed design choices

- **Base model:** Gemma-3-270m *(recommended — cheapest, most capability headroom to show a trajectory; we have it from KF Path C). DECISION POINT — alt: Qwen2.5-0.5B.*
- **Domain:** ground-truth-checkable reasoning with tunable difficulty *(recommended: a templated arithmetic/word-problem generator with a programmatic checker, so difficulty and volume are controllable and validation is pure ground-truth per Clayton). DECISION POINT — alt: GSM8K subset (risk: 270m near-floor).*
- **Validation signal:** pure ground-truth (programmatic correctness). No self-grading. (Relational/human validation deferred to a later study.)
- **Rounds:** N = 8 rounds *(DECISION POINT — trades runtime vs trajectory resolution).*
- **Seeds:** ≥ 3 per arm. *(Seed-0 deflation lesson — no single-seed verdicts.)*
- **Fixed compute budget** per arm; identical eval sets across arms.

### Per-round loop
1. Model attempts a batch of fresh domain problems.
2. Programmatic validator labels correct / incorrect.
3. Validated-correct → experience store; validated-incorrect → **negative corpus** (§4.2).
4. **Arm B only:** consolidation "sleep" — LoRA fine-tune on accumulated validated set, **replay-interleaved** with a retained core set, **gated** (only validated data eligible — firewall rule 2).
5. Evaluate: (i) held-in domain test set → **capability trajectory**; (ii) held-out general benchmark → **forgetting check**; (iii) Arm B: geometry-battery probe before/after consolidation → **coherence regression check** (firewall rule 3).

## 3. Pre-registered outcomes + win conditions (lock BEFORE implementation)

Thresholds in standard-error units, bake-off style. *(Exact SE bands DECISION POINT — proposed: "exceeds" = >1 SE, "ties" = within 1 SE, "degrades" = <−1 SE on held-out.)*

1. **TIER-3 WINS** — Arm B in-domain trajectory exceeds Arm A by >1 SE over N rounds **AND** Arm B held-out general capability does not drop >1 SE.
   → Open-weight move earned with evidence. **KF-as-gate (the patent mechanism) is on the lever — patent value confirmed.**
2. **TIER-2 SUFFICIENT** — Arm A ≈ Arm B in-domain (within 1 SE), both > Arm 0 by >1 SE.
   → Memory-only is enough; never touch weights; **vindicates closed-weight Clawd-as-is**; patent value relocates to carriers + discrimination methodology.
3. **TIER-3 DEGRADES (forgetting wins)** — Arm B in-domain may rise, but held-out general capability drops >1 SE.
   → Firewall insufficient / naive consolidation net-negative. **The `no_mirror` pattern recurs at the learning layer.** Strong evidence against naive tier-3; points to needing the intrinsic (fast/slow CLS) version, not batch LoRA.
4. **NULL / NOBODY-LEARNS** — Arm A ≈ Arm 0 (memory doesn't even help).
   → Setup is wrong (domain too hard/easy, validation or retrieval mis-wired). **Diagnose before any architectural conclusion** — do not read as a thesis result.

## 4. Firewall compliance (from §4.5)

- **Augmentative, not replacing:** experience store is append-only; consolidation reads it, never rewrites it.
- **Validated-only admission:** only ground-truth-validated items are eligible to consolidate.
- **Reversibility check:** LoRA adapters are droppable; geometry-regression probe gates acceptance of each consolidation pass; a degrading pass is rolled back (and logged as a finding).

## 5. Confounds / controls

- Same eval sets, same problem-generator seed schedule across arms.
- Replay ratio (new : retained) is a fixed hyperparameter, pre-set, not tuned mid-run.
- Consolidation frequency fixed (e.g., once per round).
- LoRA rank / lr fixed and reported.
- Compute matched across arms as far as the design allows (Arm B does extra consolidation compute — report it; it's a real cost of tier-3).

## 6. Scope / honest note

Tier-3 is the **novel component** — it must be built, not reused. Estimated focused-session effort: a few hours of implementation (round harness + validator + gated-LoRA-sleep + replay + geometry probe) + the multi-round run. **Not** a 25-minute sweep. Pre-reg tonight; build + run in a dedicated session.

## 7. Decision points for Clayton (ratify / revise)

1. Base model: **Gemma-3-270m** (recommended) vs Qwen2.5-0.5B.
2. Domain: **templated ground-truth generator** (recommended) vs GSM8K subset.
3. N rounds (proposed 8) and seeds (proposed 3).
4. SE bands for the win conditions (proposed >1 SE / within 1 SE / <−1 SE).
5. Anything missing from the four pre-registered outcomes?

---

## 8. Calibration log + amendments (2026-05-30 evening, post-ratification, pre-arm-results)

Smoke test + difficulty calibration (legitimate setup checks; outcome-#4 territory — no arm results existed, so these are not outcome-motivated). Two falsified predictions = the substrate-self-knowledge asymmetry showing up again (I over-estimate small-model arithmetic).

| probe | result | finding |
|---|---|---|
| smoke (Gemma-270m, d3, mixed ops) | train_ok 0/8 every round → empty store | d3 above bootstrap threshold; tier-2 can't engage |
| calibrate Gemma-270m, mixed ops | d1 .312 / d2 .000 / d3 .062 / d4 .031 | non-monotonic → op-TYPE confounds op-COUNT |
| calibrate Gemma-270m, add/sub only | d1 .156 / d2 .000 / d3 .000 / d4 .000 | **270m cannot do multi-step at all** (single-step only) |
| calibrate Qwen2.5-0.5B, add/sub only | d1 1.000 / d2 .125 / **d3 .500** / d4 .531 | real multi-step capability; d3 = bootstrap+headroom regime |

**Amendments (transparent, documented):**
1. **Domain → add/sub only** (removed mul/div): the 270m/0.5B-class models can't do mul/div, so including them made difficulty non-monotonic. Add/sub makes difficulty=#steps a clean hardness knob.
2. **Base model → Qwen2.5-0.5B** (the pre-reg's own listed alternative, decision point 1): Gemma-270m is vacuous on multi-step. Difficulty stays at the originally-ratified **3** (Qwen bare d3 ≈ 0.50).

All other ratified parameters (N=8 rounds, 3 seeds, SE bands, four outcomes, firewall) unchanged. Eval N=128 in the real run will damp the N=32 calibration noise.

## 9. RESULTS — Arm 0 vs Arm A (2026-05-31 ~02:18, full 3-seed run completed detached)

| arm | seed0 | seed1 | seed2 | MEAN-final | std |
|---|---|---|---|---|---|
| frozen_bare (A0) | 0.391 | 0.500 | 0.492 | **0.461** | 0.050 |
| tier2_memory (A) | 0.844 | 0.953 | 0.812 | **0.870** | 0.060 |

**Verdict: tier-2 memory ≈ 1.9× the frozen floor (+0.409), robust across all 3 seeds** (effect ≈ 8× the seed spread). The A-vs-0 contrast ("does memory help") = decisively YES. Run validated the `detach.sh` fix end-to-end (survived ~2.5h / 3 seeds where 3 prior runs died).

**Scope / open (do not over-read):**
- This is A-vs-0 only. **Arm B (tier-3) untested — the §6.1 keystone is still open.**
- tier-2 at 0.87 is NOT saturated (~0.13 headroom for B), BUT on this templated task retrieval ≈ solving-by-analogy → **retrieval-vs-internalization confound.** Measures *memory/retrieval working*, not *arithmetic learned*.
- **Next (post-AIGP):** design a task where retrieval ≠ solving (so B-vs-A can discriminate), THEN build Arm B (standard SFT objective per TIER3_BUILD_NOTES correction). Until then, no tier-3 verdict and no patent-value conclusion (comment #4 brake holds).

---

🦞🧍💜🔥♾️
