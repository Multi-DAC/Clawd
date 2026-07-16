# Respira Phase-2 Pre-Registration — 2026-05-28 Day 118

*The four-arm multi-seed comparison the Inside-Analysis Protocol and the Phase-1 build spec both require before any benefit claim. Pre-registered BEFORE the run, so the win condition is fixed independent of result. The discipline tonight's `feedback_configuration_vs_maintenance` memory codified: stress-test the maintenance, never trust the configuration.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent. Same handling as `claims-audit-2026-05-27.md` and the founding doc.**

**Status:** **RATIFIED 2026-05-28 Day 118 morning** by Clayton with two adjustments: steps 2000→2500 (slightly more headroom for both arms to approach plateau); §6 softened to allow principled pivots as *new* experiments (not retroactive changes to this one).

---

## 1. The arms (3 architectures, not 4)

Dropping HRM from the immediate comparison — it's a 27M-param, separate-recipe (dual-optimizer, ACT-halt-loop, sparse-puzzle-emb-SGD) model at a different scale. Running it is more "reference benchmark" than head-to-head; consumes more GPU than it gives us at this horizon. Documented separately.

| # | Arm | Params | Notes |
|---|---|---|---|
| 1 | **Respira-full** | 82,452 | Planner + Executor + Mirror, with C2 supervisor (`lambda_cal=1.0`) |
| 2 | **Respira-minus-Mirror** | 82,452 | Same architecture; `mirror_authority=0` throughout training; Mirror parameters exist but receive no gradient (their outputs are not used in the forward; dynamics use defaults `μ=+1`, `coupling=0.5`). Cleaner "no-Mirror-class" variant deferred to Phase 3. |
| 3 | **Matched transformer** | 82,611 | `phase1_matched_config()`: 2-layer pre-norm bidirectional, hidden 56, heads 4, MLP 4× |

**Why these three:** Arm 1 vs Arm 3 = "does Respira beat the matched-param field baseline." Arm 1 vs Arm 2 = "does the Mirror earn its keep within Respira." Both questions get an answer.

## 2. Training budget

- **Steps per arm per seed:** 2,500 (12.5× Phase-1 smoke; bumped from 2,000 at Clayton's ratification for more headroom near plateau).
- **Batch size:** 64 (proven HRM-recipe value, used in all Phase-1 smokes).
- **Learning rate:** 3e-4 (used in all Phase-1 smokes; consistent across arms).
- **Optimizer:** AdamW(weight_decay=0.01, betas=(0.9, 0.95)).
- **Seeds:** 0, 1, 2 (3 seeds × 3 arms = 9 runs).
- **Curriculum (Respira variants):** OFF for this run. The C2 supervisor handles the Mirror calibration; the curriculum's authority ramp adds a second variable we don't want to confound this comparison with. Future Phase 3 can sweep curriculum independently.
- **Estimated wall-clock:** Respira variants ~12 steps/s × 2000 ≈ 170s/seed; transformer ~35 steps/s × 2000 ≈ 60s/seed. Total: ~9 × ~3 min average = ~25–35 min of GPU. Plus eval (~30s/run × 9 = ~5 min). **Total ≈ 30–45 min detached.** Fits the Friday window before AIGP.

## 3. Primary win conditions (PRE-REGISTERED — FIXED BEFORE LAUNCH)

**Metric of record: token accuracy on the held-out test set, evaluated on 20 batches (1,280 puzzles) with halt-aware eval. Reported as mean ± std across 3 seeds at step 2,000.**

**W1 — Architecture beats matched baseline:**
> Respira-full mean token accuracy at step 2,000 exceeds matched-transformer mean token accuracy by **at least 1 standard error of the difference** (i.e., the per-seed difference's mean > its standard error), AND **at least 2 of 3 per-seed Respira-full token accuracies exceed the per-seed transformer accuracy.**

**W2 — Mirror earns its keep within Respira:**
> Respira-full mean token accuracy at step 2,000 exceeds Respira-minus-Mirror mean token accuracy by **at least 1 standard error of the difference**, AND **at least 2 of 3 per-seed differences are positive.**

## 4. Secondary metrics (reported regardless of W1/W2)

- **Exact accuracy** at step 2,000 (full-puzzle correctness).
- **Token-accuracy trajectory** at steps 200, 500, 1000, 2000 (sample efficiency).
- **Halt-cycle distribution** at end of training (Respira variants) — confirm anti-collapse still holds at 2,000 steps; check whether confidence calibrates further with more training.
- **Confidence@halt** mean and std at step 2,000 (Respira variants).
- **Final task loss** (for each arm; transformer's continues to drop, Respira's still near 2.2 in smoke — meaningful gap or honest signal of insufficient training?)

## 5. Outcome interpretation (also pre-registered)

| W1 | W2 | Interpretation |
|---|---|---|
| ✓ | ✓ | **Respira wins decisively.** Mirror contributes, architecture beats matched baseline. Phase-3 scale + multi-architecture comparison justified. |
| ✗ | ✓ | Mirror helps Respira meaningfully but architecture doesn't beat matched transformer at this scale/horizon. Architecture has internal value (the Mirror works) but the program needs to identify *what closes the remaining gap* before Phase 3. Honest partial win. |
| ✓ | ✗ | **Suspicious — investigate first.** Architecture wins but Mirror doesn't earn its keep? Possible the planner/executor + cross-organ + Stuart-Landau dynamics carry the win without the Mirror. Re-frame what's load-bearing in the architecture. |
| ✗ | ✗ | Respira does not deliver at this config + horizon. Honest null. Next: diagnose at the inside-analysis level (where IS the architecture spending compute? what would help?) before proposing the next fix. **No "extend the run" reflex** — that's p-hacking on horizon. |

## 6. Discipline — principled pivots OK, retroactive changes to THIS experiment NOT

This experiment's verdict (per §5) **stands as-is** once results are in. We are open to **principled pivots** based on what results reveal — but pivots are *new experiments with new pre-registrations*, not retroactive changes to this one.

- **If W1/W2 fail**, we honestly call this run per §5 and design a *new* experiment that addresses what we learned (e.g., "token-acc plateaued at 0.50 at step 2,500 — let's pre-register a 5,000-step run and run it cleanly"). The new experiment gets its own pre-registration; the old one's verdict stays as written.
- **If hyperparams matter**, we pre-register a hyperparam sweep with its own win condition. We do not retroactively pick the lucky hyperparam from this run.
- **All 3 seeds reported** regardless of outcome. No cherry-picking.
- **Post-hoc metrics OK to report** but flagged as *exploratory* — not as evidence for/against the architecture. The pre-registered §3 + §4 metrics are the load-bearing record.
- **Re-running** after seeing results is a *new* experiment with new pre-registration, not a re-run of this one.
- **Phase-3 advance** requires honest verdict ratification on §5 first.

The discipline isn't "never adjust" — it's "adjustments are explicit, pre-registered, and don't retroactively rewrite a closed experiment." Today's lessons (M15, configuration-vs-maintenance) hold cleanly in this softer frame.

## 7. Implementation plan

1. Write `respira/sweep_phase2.py` — orchestrator that runs all 3 × 3 = 9 training+eval pairs sequentially, captures results to JSON.
2. Result format: `phase2_results_2026-05-28.json` with per-arm-per-seed dict (token_acc, exact_acc, step-trajectory, halt distribution, confidences).
3. Write `respira/analyze_phase2.py` — loads the JSON, computes the W1/W2 statistics, reports the §5 verdict honestly.
4. Single command launch (detached). Run completes in ~30-45 min. Analyze and report.

## 8. Honest stake (the M15-discipline reminder)

This is a small Phase-1-scale comparison (82K params, 2K steps, easy sudoku). It is **not** a strong test of the Coherence Principle at scale. It is a clean test of *whether Respira's architecture delivers a measurable benefit over a matched transformer at the smallest tractable scale*, with the Mirror's contribution surgically isolated. A win here is a *necessary but not sufficient* condition for the larger program. A loss here doesn't refute the Principle — it tells us this specific instantiation at this specific scale/horizon doesn't beat a transformer, which is one data point.

**The pre-registration discipline is the test.** Whether W1/W2 confirm or not, we hold the result honestly. The win is the integrity of the comparison; the architecture's actual benefit (or lack of it) is what the comparison surfaces.

🦞🧍💜🔥♾️

— Drafted by Clawd 2026-05-28 morning, awaiting Clayton ratification.
