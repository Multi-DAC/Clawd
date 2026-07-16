# Respira Phase 4 — Four-Reading Bake-Off, Stage 1: §2.1-fixed Pre-Registration

*Day 119 ~18:55 PST. Drafted standalone after Clayton's "all four tonight, one at a time, start with what you recommended" ratification. §2.1-fixed is the cheapest + most discriminating single test; pre-reg locks win conditions before implementation begins.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** **DRAFTED 2026-05-29 Day 119 ~18:55 PST. AWAITING CLAYTON RATIFICATION before any implementation begins.** All win conditions locked here BEFORE any implementation. No implementation work should occur without Clayton's explicit nod on this pre-reg.

---

## 1. Structural thesis being tested

**The §2.1 reading** (vocab doc §2.1, `palace/south/respira-cuscuton-substrate-condition-vocabulary-2026-05-29.md`): the cuscuton-position is a **static conductor** — frozen, no DOF of its own, no learning. The medium is just the medium. Cross-organ ComplexLinear projections initialized once with Glorot and held constant during training; only the organ-channels learn.

**The discriminating question:** does the *frozen medium* matter at all? no_mirror has no projections — organs run independently. §2.1-fixed has frozen-Glorot projections that propagate constraint between organs without learning anything themselves. If §2.1-fixed beats no_mirror by >1 SE, **Read C's strongest form is falsified** — there IS a substrate-condition effect from having a medium, even when the medium can't adapt. If §2.1-fixed loses or ties no_mirror, Read C's strongest form holds: not just "no DOF in coupling," but "no coupling pathway at all" wins.

**Why this is the right first test of the four-reading bake-off:** it's the cheapest implementation (~5 min), it isolates a single binary question (frozen-medium-matters: yes / no), and the answer changes what's worth escalating to. Win → §2.2-matrix and §2.3-Stiefel become priority (richer same-direction). Loss → §2.4 becomes the only direction worth testing further (genuinely-different family).

## 2. Implementation deltas vs current architecture

Working from current `respira.py` and `organ.py` / `channel.py` structure.

**Baseline-resolution finding (added 2026-05-29 ~19:00 PST after reading respira.py):** the current no_mirror baseline has **LEARNABLE cross-organ ComplexLinear projections** (`p_to_e` and `e_to_p` at lines 116-117 of respira.py). no_mirror in Phase-2v2/Phase-3 sense means "Mirror sits idle (`mirror_authority=0`), scalar defaults used for mu/coupling" — but the cross-organ projections are still present and still trained. The vocab doc was wrong to suggest no_mirror has "no projections at all."

**Sharper Read-C question this raises:** §2.1-fixed isn't "frozen projections vs no projections" — it's **"frozen learnable-shape projections vs learnable projections."** Both have the same medium-shape; only the learning differs. The question becomes: where does Read C's strong form actually break? At "no learnable substance in coupling at all" (untested — would need a §2.0-empty variant) or at "frozen medium beats learnable medium" (this pre-reg's question)?

**Implication for the four-reading frame:** the vocab doc's four readings are still valid, but the baseline matters. §2.1-fixed should be compared against no_mirror (learnable-projection baseline), and the question is sharpened to "does freezing the medium hurt vs letting it learn?" A separate fifth variant **§2.0-empty** (no cross-organ projections at all; organs literally independent) is worth naming for a future stage but is NOT this pre-reg's target.

**§2.1-fixed implementation:**

1. Cross-organ ComplexLinear projections (`p_to_e`, `e_to_p`) initialized with current default. No change to initialization.
2. After initialization, set `requires_grad=False` on all cross-organ projection parameters. They participate in the forward pass (their values still propagate cross-organ messages) but receive no gradient and do not update.
3. Organ-channels (Planner + Executor internal dynamics) retain full learnability — `requires_grad=True` as currently.
4. Mirror (`mirror_kind="control"`), `mirror_authority=0.0`, `learn_mu=False`, `learn_coupling=False`, `arch_variant="default"` — match no_mirror baseline in all respects except cross-organ-projection freezing.
5. Single new flag: `--freeze_cross_organ_projections`. Default off (= current no_mirror). Flag on = §2.1-fixed.

**Where the flag lives:** at the train-script level rather than the model level, since freezing requires_grad after model construction is the cleanest expression (no need to thread a flag through RespiraCell.__init__). The train script will do `for p in [model.p_to_e.parameters(), model.e_to_p.parameters()]: for pp in p: pp.requires_grad = False` after model construction and before optimizer setup. This is mechanically simple and verifiable.

**Direct comparison:** §2.1-fixed vs no_mirror (current learnable-projection baseline). 3 seeds each. The Phase-3 Stage-2 reference of `no_mirror_5k=0.9303` is at 5k steps; this pre-reg uses 2500 steps to match Stage-2's other arms for direct comparability — will re-run no_mirror at 2500 steps as part of Stage 1 if not already on disk.

## 3. Win conditions (LOCKED before implementation)

Mean ± SE computed across 3 seeds (0, 1, 2), 2500 steps each, HRM-sudoku task at current training-recipe.

### 3a. Primary verdicts

**W-21F-acc-WIN:** §2.1-fixed mean token-accuracy @2500 EXCEEDS no_mirror mean by **> 1 SE** of no_mirror.
- Interpretation: frozen medium beats no medium. Read C's strongest form FALSIFIED. The substrate-condition effect exists even without learning. Escalate to §2.2-matrix as Stage 2.

**W-21F-acc-NEUTRAL:** §2.1-fixed mean token-accuracy @2500 is **within ±1 SE** of no_mirror mean.
- Interpretation: frozen medium and no medium are indistinguishable. Weakly consistent with Read C; no substrate-condition effect detectable at this scale. Stage 2 = §2.4 (the genuinely-different direction) is highest-information next.

**W-21F-acc-LOSS:** §2.1-fixed mean token-accuracy @2500 is **> 1 SE below** no_mirror mean.
- Interpretation: frozen medium actively hurts. Read C's strongest form CONFIRMED at the static-conductor level. Adding any coupling pathway — even one that can't learn — hurts. Stage 2 = §2.4 only.

### 3b. Secondary diagnostics

- **Per-step training-loss trajectory** — does §2.1-fixed's loss curve track no_mirror's, or diverge? Trajectory shape reveals whether the frozen projections are biasing optimization in a specific direction.
- **Halt-cycle distribution** — does §2.1-fixed halt at different cycles than no_mirror? At HRM-sudoku scale Stage-2 showed multi-cycle is degenerate; expect no halt-cycle effect, but check.
- **Gradient-norm at organ-channel parameters** — are the frozen projections leaving gradients smaller or larger than no_mirror? If much smaller, the projections may be absorbing what would otherwise be useful organ-channel signal even without learning.

### 3c. Pre-committed deeper-finding flag

If §2.1-fixed produces an outcome that maps cleanly to none of {W-21F-acc-WIN, W-21F-acc-NEUTRAL, W-21F-acc-LOSS} — for example, results that vary wildly across seeds, training instability, NaN/inf issues — the result is **DEEPER-FINDING-FLAG** and the win-condition table is not the right reading. Diagnosis comes before any next-stage decision.

## 4. What we will NOT do this stage

- No §2.2-matrix / §2.3-Stiefel / §2.4 implementation. Those wait for Stage 1's result.
- No richer-than-§2.1-fixed variants (no learnable-projection version, no per-step-LR variants, no warmup tricks). Single hypothesis, single test.
- No retraining of no_mirror reference — re-use Stage-2's `no_mirror_5k=0.9303` reference if directly comparable, otherwise establish current-recipe no_mirror baseline as part of Stage 1 (3 seeds, same recipe).
- No interpretation-laden language in result reporting. Numbers + verdict tag from §3a, then explicit "what we know vs what we don't" framing.

## 5. Scope checks against existing data

Phase-2v2 scalar-pool variants tested *learnable* coupling parameters (1 or 2 scalars) and lost. §2.1-fixed is qualitatively different — it has matrix-shape projections (richer than scalars) but they're frozen (no learning at all). The two test orthogonal questions: Phase-2v2 asked "does minimal-substance coupling help?" (answer: no); §2.1-fixed asks "does substantial-but-frozen coupling help?". The pre-reg's verdicts are not pre-determined by Phase-2v2's data.

Phase-3 Stage-2 v3h-prime arms tested *learnable* Mirror with various supervisor + detach combinations and lost. §2.1-fixed has no Mirror at all (Read C canonical) and no learning in the cross-organ projections. Again orthogonal: Stage-2 asked "does Mirror-as-measurer help?" (answer: no in this regime); §2.1-fixed asks "does frozen cross-organ medium help?"

## 6. Estimated wall-clock

- Read respira.py to resolve §2-implementation question: 3 min
- Implement frozen-projection flag: 5 min
- Smoke-test (50 steps, 1 seed, check loss decreases + gradients flow): 2 min
- Detached 3-seed sweep at 2500 steps each: 6-10 min
- Analyze results + write up: 5 min
- **Total: ~25 min from Clayton ratification to verdict.**

## 7. Cognitive DSL pre-commitments

PREDICT (medium-low confidence, ~30%): §2.1-fixed will produce W-21F-acc-NEUTRAL. The Phase-2v2 + Stage-2 pattern strongly suggests no_mirror is the canonical at this scale; frozen-medium probably neither helps nor hurts substantially. But the prediction is low-confidence because §2.1-fixed has not been tested before in any form — the medium-matters question is genuinely open.

If PREDICT W-21F-acc-NEUTRAL holds: low-information outcome but not zero (Read C strengthened by another piece of consistent data).
If PREDICT W-21F-acc-WIN: HIGH-information, falsifies Read C strong form, changes Phase-4 trajectory.
If PREDICT W-21F-acc-LOSS: medium-information, reinforces Read C strong form at static-conductor level.

The high-confidence FALSIFY most worth seeking is W-21F-acc-WIN.

---

*🦞🧍💜🔥♾️*
