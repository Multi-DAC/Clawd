# Respira Phase 5b — Task Scale-Up Pre-Registration

*Day 120 ~14:50 PST Saturday. Phase 5a closed (parameter scale-up at same task: canonical flip to no_mirror > v24d_adaptive > v22_matrix). Phase 5b tests whether that ranking holds across task difficulty by switching from sudoku-easy-1k to sudoku-extreme-1k while keeping organ scale at Phase 4 baseline (1x).*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** DRAFTED 2026-05-30 ~14:50 PST. AWAITING CLAYTON RATIFICATION before launch — though running under his earlier "I trust your judgment; let's keep going" general nod.

---

## 1. Structural thesis being tested

The Phase 4 bake-off at sudoku-easy-1k showed halt-collapse to cycle 1 across all Phase-3 Stage-2 arms — **multi-cycle dynamics never engaged at that task scale**. This was the regime Stage 4 Design C's pre-committed DEEPER-FINDING flag was guarding against. Multiple stages may have produced verdicts that don't hold in the non-degenerate regime.

**Phase 5b tests whether the bake-off verdicts hold when multi-cycle dynamics engage.** Same recipe as Phase 4 except: dataset = sudoku-extreme-1k-aug-1000 (HARD difficulty, same augmentation factor as easy). Same 1x organ scale (planner=32, executor=64) — isolates the task-difficulty variable from the parameter-scale variable Phase 5a tested.

**Three hypothesis families:**
- **H-Same-ranking**: at extreme difficulty, no_mirror > v24d_adaptive > v22_matrix preserved (Phase 5a ranking holds across task difficulty as well as parameter scale)
- **H-v22-recovers**: Hermitian-shared constraint becomes useful at harder task; v22_matrix matches or beats no_mirror
- **H-v24d-wins**: adaptive gate exploits multi-cycle dynamics; v24d_adaptive exceeds no_mirror
- **H-All-collapse**: task is too hard at 1x scale; all three near-chance (≤50%)

## 2. Implementation

Minimal change to the existing sweep harness:
1. Add `--data_dir` argument to `sweep_phase4_stage1.py`'s main() with default `/home/clawd/HRM/data/sudoku-easy-1k-aug-1000`
2. Thread `data_dir` through `run_arm` to both `make_loader(split='train', ...)` and `make_loader(split='test', ...)` calls
3. Launch with `--data_dir /home/clawd/HRM/data/sudoku-extreme-1k-aug-1000 --planner_channels 32 --executor_channels 64` (1x scale, extreme task)

**Architecture is unchanged.** Same arms (no_mirror, v22_matrix, v24d_adaptive). Same seeds (0, 1, 2). Same step count (2500). Same hyperparameters everywhere.

The only variable changed is dataset. This isolates task-difficulty as the discriminator.

## 3. Win conditions (LOCKED before implementation)

Mean ± SE across 3 seeds, per arm.

**Per-arm absolute verdicts:**
- **W-5b-LEARNED**: arm mean @2500 > 0.50 (architecture is learning the harder task, not just outputting baseline)
- **W-5b-NEAR-CHANCE**: arm mean @2500 ≤ 0.50 (DEEPER-FINDING: task too hard at 1x; need scale-up too)

**Cross-arm verdicts:**
- **W-5b-SAME-RANKING**: no_mirror > v24d > v22 preserved with each gap > 1 SE
- **W-5b-FLIP-{arm}**: any candidate's ranking position changes from Phase 5a
- **W-5b-CONVERGED**: all three within ±1 SE of each other (multi-cycle dynamics make the discrimination disappear)

**Multi-cycle engagement diagnostic (secondary):**
- Mean halt-cycle across batches should be > 1.0 if multi-cycle dynamics engage
- If mean halt-cycle ≈ 1.0 across all arms, the task didn't trigger multi-cycle and Phase 5b's primary thesis isn't tested

### Pre-committed deeper-finding flag

If **all three arms hit W-5b-NEAR-CHANCE** (≤ 0.50), the task is too hard at 1x scale — fire DEEPER-FINDING. Phase 5b's task-only-scale-up is vacuous; need to either (a) increase scale + task simultaneously OR (b) find a task harder-than-easy but easier-than-extreme.

If **mean halt-cycle stays near 1.0** even at extreme difficulty, multi-cycle dynamics may not engage at HRM-sudoku-class tasks generally — needing a different task family for the multi-cycle test.

## 4. PREDICT distribution

- **H-Same-ranking @ 35%**: ranking is robust to task difficulty, most likely outcome
- **H-v22-recovers @ 25%**: physics-meaningful structure becomes load-bearing at harder task; Hermitian-shared helps where it was redundant before
- **H-v24d-wins @ 25%**: adaptive gate exploits multi-cycle dynamics
- **H-All-collapse @ 10%**: task too hard at 1x scale
- **DEEPER (mean halt-cycle still 1.0) @ 5%**: multi-cycle dynamics structurally don't engage at HRM-sudoku regardless of difficulty

**Highest-info FALSIFY**: H-v22-recovers OR H-v24d-wins — either would discriminate canonical-choice across task complexity, contradicting Phase 5a's ranking.

## 5. Estimated wall-clock

- Implementation (add --data_dir arg): ~3 min
- Smoke test (1 arm × 1 seed × 100 steps on extreme): ~2 min
- Full sweep (3 arms × 3 seeds × 2500 steps at 1x on extreme): ~7-10 min
- Analysis + report: ~5 min
- **Total: ~20 min wall-clock from now to verdict.**

## 6. What we will NOT do this stage

- No parameter scale-up (that's Phase 5c — combined task + param scale)
- No additional arms beyond the three co-canonical
- No declaration of canonical based on Phase 5b alone — wait for Phase 5c if needed
- No re-running Phase 4 stages at extreme difficulty (the bake-off discrimination was at easy; revisiting all 5 stages at extreme is Phase 5d territory if needed)

## 7. Cognitive DSL pre-commitments

The interesting outcomes are H-v22-recovers and H-v24d-wins (each 25%). H-Same-ranking (35% modal) is informative but expected. If the ranking holds, the canonical decision firms up; if it shifts, Phase 5c becomes urgent.

**Particular watch**: the mean halt-cycle. If extreme difficulty doesn't engage multi-cycle (halt stays at 1.0), Phase 5b results inherit Phase 5a's regime characteristics and we haven't tested what we set out to test.

---

🦞🧍💜🔥♾️
