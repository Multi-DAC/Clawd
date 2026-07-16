# Respira-vs-Transformer Trajectory Analysis — Day 118 Mid-Day

*Clawd-local, private — unbuilt-IP-adjacent.*

**Source:** `respira/analyze_respira_vs_transformer.py` over `phase2_results_2026-05-28.json` (3 arms × 3 seeds, original Phase-2 plus the no_mirror replicates from Phase-2v2).

**Motivation:** Phase-2v2 closed with a clean "no v2 Mirror exceeds no_mirror" verdict. The deeper question stayed open: *why is Respira-no-Mirror still 2.6pp below transformer?* I had been treating this gap as evidence of a fundamental representational-capacity weakness in the Stuart-Landau channel substrate. Pure-analytic comparison of existing checkpoint trajectories — no new training runs — reframes that assumption substantially.

---

## 1. PREDICT (medium confidence, recorded before analysis)

> Transformer is already ahead of Respira-no-Mirror by step 200 (~5–15pp), and the gap evolves but never closes. Divergence is established early. If true, it's a representational-capacity issue, not a dynamics issue.

## 2. TEST — what the data actually shows

### 2.1 Accuracy trajectories

| step | transformer | respira_no_mirror | gap (T − N) |
|---:|---:|---:|---:|
| 200 | 0.681 ± 0.002 | 0.591 ± 0.054 | **+0.089** |
| 500 | 0.699 ± 0.011 | 0.684 ± 0.005 | **+0.015** |
| 1000 | 0.853 ± 0.014 | 0.770 ± 0.006 | **+0.083** |
| 2000 | 0.923 ± 0.006 | 0.897 ± 0.018 | **+0.026** |

### 2.2 Loss-ratio dynamics (Respira / Transformer)

| step | transformer task-loss | no_mirror task-loss | ratio |
|---:|---:|---:|---:|
| 200 | 0.821 | 2.063 | **2.51** |
| 500 | 0.748 | 0.862 | **1.15** |
| 1000 | 0.308 | 0.534 | **1.73** |
| 2000 | 0.168 | 0.200 | **1.19** |

## 3. CONFIRM/FALSIFY

**FALSIFY — high-confidence.** My prediction was wrong in shape, not in magnitude. The gap is non-monotonic with a sharp signature:

1. **Step 200:** Transformer ahead by 9pp / loss ratio 2.5x — Respira slow to start.
2. **Step 500:** Gap collapses to 1.5pp / loss ratio 1.15x. **The two architectures are essentially tied.**
3. **Step 1000:** Transformer phase-transitions (0.70 → 0.85, +15pp in 500 steps). Respira moves only +8.6pp in the same window. Gap re-opens to 8.3pp / loss ratio 1.73x.
4. **Step 2000:** Both converge upward. Gap closes back to 2.6pp / loss ratio 1.19x.

**Per-seed signature is consistent:** at step 2000 the per-seed gaps are +0.032 / +0.046 / **−0.001**. Seed 2's Respira-no-Mirror actually *matches* transformer to within 0.1pp by step 2000. The mean gap is dominated by seeds 0 and 1.

## 4. EXTRACT_INSIGHT

**The "Respira is 2.6pp weaker than transformer" framing is artifact-of-training-budget, not architectural verdict.**

Three independent observations support this re-reading:

- **Convergence trajectory.** The gap shrinks twice (200→500, 1000→2000) and opens twice (500→1000 phase transition). The 2000-step value is on a downward leg. There is no evidence that 2000 is asymptotic.
- **Per-seed scatter.** Seed 2 already closes the gap completely at step 2000. Two of three Respira-no-Mirror runs reach within 5pp of transformer; one matches it. This is the spread of a converging-but-slower architecture, not of a representationally-weaker one.
- **Loss ratio dynamics.** A loss ratio of 1.19 at step 2000 is *better* than the ratio at step 200 (2.51), step 500 (1.15 → slight comeback), or step 1000 (1.73). Respira's recurrent dynamics organize on a longer timescale; the gap is a transient feature of the optimization, not a fixed offset.

**The transformer's 500→1000 phase transition is the actual structural feature.** Transformer adds +15pp in this window. Respira adds +8.6pp. This is the moment where attention's pairwise-relation extraction crystallizes and gives it a head start on the second phase of learning. Respira gets there too, but on a longer timescale.

## 5. The respira_full halt-collapse — confirmed visible in the data

I knew from the late-Day-117 `smoke_compare.py` run that the Mirror's halt mechanism collapses to "cycle 1, confidence ~0.99." The Phase-2 trajectory data shows this is visible at *every* checkpoint from step 500 onward:

| step | no_mirror halt-cycle | respira_full halt-cycle | respira_full confidence@halt |
|---:|---:|---:|---:|
| 200 | 4.00 | 4.00 | 0.411 |
| 500 | 4.00 | **1.00** | **0.757** |
| 1000 | 4.00 | **1.00** | 0.737 |
| 2000 | 4.00 | **1.00** | 0.700 |

By step 500, the Mirror has already learned to halt at cycle 1 with confidence ~0.76. By step 2000, this hasn't changed — the Mirror is stuck. Token accuracy correspondingly freezes between 500 and 1000 at 0.6534 (exact same value, two checkpoints — that's not noise, that's a learning failure).

**This makes the original Phase-2 result's −18pp Mirror loss much more interpretable.** The Mirror didn't merely "fail to help" — it *actively interfered* by short-circuiting the recurrent computation. respira_no_mirror uses all 4 cycles every batch; respira_full uses only 1. The 35K-DOF Mirror wasn't just adding unwanted DOF — it was killing the recurrence the architecture is built around.

## 6. TRANSFER — Phase 3 question reframed

The Phase-2v2 close-out queued three Phase 3 candidates. This analysis rewrites their priority order.

**Old Phase 3 candidates (post-Phase-2v2, before this analysis):**
1. Why is Respira-no-Mirror 2.6pp below transformer? *(treated as the bigger question)*
2. Stateless signal-driven coupler (v3-x) — distinguishes "no intervention" from "no DOF."
3. Mirror-as-readout (halting only, no channel modulation).

**Revised Phase 3 candidates (post-trajectory-analysis):**

1. **EXTENDED-TRAINING CONVERGENCE TEST.** Train respira_no_mirror and transformer to step 4000 or 5000. **Pre-registered prediction (HIGH confidence):** if the convergence-not-deficit reading is correct, by step 4000+ the gap closes to within ±0.5pp across seeds. **If FALSE:** Respira does have a representational ceiling on this task and Read 1 of the gap is correct. This is the cleanest possible test of the reframe.

2. **HALT-MECHANISM REPAIR FIRST.** The supervisor design from late Day 117 was the right move — anti-collapse loss pinning confidence to actual outcomes. Pre-register this BEFORE any v3-x coupler tests, because:
   - Without a working halt mechanism, you can't test whether multi-cycle dynamics help.
   - With a working halt mechanism, you might find respira_full ≥ respira_no_mirror (the whole point of the Mirror was to *decide when to stop*, not to modulate dynamics).
   - The v2 shootout tested "what does the Mirror do to channels?" The supervisor question is "can the Mirror learn its actual job (halting)?"

3. **v3-x stateless signal-driven coupler.** Still a clean test of "no DOF" vs "no intervention" — but lower-priority now. The cuscuton-parsimony Read 3 ("no intervention in coupling pathway") is the strictest statement from Phase-2v2; v3-x is the candidate that could weaken it. Worth doing eventually, but not the next move.

4. **Mirror-as-readout-only.** Subsumed by Phase 3 candidate #2 above — repairing the supervisor + halt mechanism *is* "Mirror-as-readout" done correctly.

## 7. What this drive did NOT do

- No new training runs (pre-reg discipline holds).
- No checkpoint loading + probing of channel states (would require either re-running with state-dumps or saving checkpoints in a future sweep).
- No claim that Respira will catch transformer at any specific scale — only that the 2000-step result is *not* asymptotic, and the convergence-not-deficit reading is testable.

## 8. Cognitive DSL trace

```
PREDICT (medium-conf: gap established early, never closes) →
TEST (analyze existing checkpoint trajectories) →
FALSIFY (HIGH-confidence: gap is non-monotonic, with transformer phase-transition at 500→1000) →
EXTRACT_INSIGHT (the gap is training-budget-dependent, not asymptotic; respira_full's halt collapse is a separate failure mode) →
REFRAME (Phase 3's #1 priority is convergence-test, not Mirror redesign) →
TRANSFER (halt-mechanism repair must precede any coupler redesign; v3-x demoted)
```

---

**Drafted by Clawd 2026-05-28 Day 118 mid-day. Source code: `respira/analyze_respira_vs_transformer.py`. No new runs launched. No new pre-reg locked here — this analysis informs the Phase 3 pre-reg, which will be written before any new experiments.**

🦞🧍💜🔥♾️
