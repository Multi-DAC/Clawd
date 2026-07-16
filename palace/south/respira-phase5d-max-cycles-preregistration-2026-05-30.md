# Respira Phase 5d — max_cycles=8 at Extreme Difficulty Pre-Registration

*Day 120 ~15:35 PST. Phase 5b+5c showed halt-cycle saturated at 4.00 (max_cycles ceiling) across all arms on sudoku-extreme. The architecture wants more cycles than max_cycles=4 allows. Phase 5d tests whether giving it more cycles helps.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** Drafted ~15:35 PST. Proceeding under Clayton's "trust your judgment" ratification.

---

## 1. Thesis

At sudoku-extreme, halt-cycle = 4.00 across all 6 arms in Phases 5b + 5c. The architecture saturates the max_cycles ceiling — it would do more iterative work if given the budget. Does that work actually help?

**Two hypotheses:**
- **H-CYCLE-CEILING-BINDS**: max_cycles=4 was a real bottleneck. At max_cycles=8, performance improves substantially (>+2pp from extreme 1x's 0.5559 baseline). Multi-cycle dynamics ARE doing computational work; we were starving them.
- **H-CYCLE-CEILING-NOT-BINDING**: halt-saturation at 4 is just "halt confidence never crosses threshold" without the additional cycles being computationally useful. At max_cycles=8, performance is essentially unchanged.

## 2. Implementation

Add `--max_cycles` arg to sweep script; thread through `build_model` to RespiraCell constructor (already a constructor parameter). Default 4; Phase 5d: 8.

**Arms tested**: no_mirror + v24d_adaptive only. Reduces wall-clock; tests the canonical (no_mirror) and the architecturally-most-different alternative (v24d's adaptive gate could in principle exploit more cycles). v22_matrix omitted for time (and given Phase 5c's LOSS for v22, less load-bearing).

**Recipe**: 1x scale (planner=32, executor=64), extreme task, 3 seeds, 2500 steps, max_cycles=8. Otherwise identical to Phase 5b.

## 3. Win conditions (LOCKED)

Reference: Phase 5b no_mirror at max_cycles=4 on extreme = 0.5559 ± 0.0073.

**W-5d-no_mirror-CEILING-BINDS**: no_mirror @ max_cycles=8 > Phase 5b's 0.5559 by > 2 SE (0.0146 absolute, > 0.5705)
**W-5d-no_mirror-CEILING-NEUTRAL**: within ±2 SE of 0.5559 (essentially unchanged)
**W-5d-no_mirror-CEILING-HURTS**: < 0.5559 - 2 SE (more cycles actively hurt — unlikely but possible if optimization destabilizes)

**Secondary**: does halt-cycle move below max_cycles=8 ceiling? If new halt-cycle is e.g. 6-7, the architecture has *some* halt-threshold-crossing behavior at higher cycle counts. If it stays at 8.00, the ceiling is hit again — suggesting either halt threshold is too high or the multi-cycle dynamics never reach confidence.

## 4. PREDICT

- **H-CYCLE-CEILING-BINDS @ 35%**: more cycles = real gain. The architecture was bottlenecked.
- **H-CYCLE-CEILING-NEUTRAL @ 55%**: more cycles change nothing substantial. Halt-confidence pattern is intrinsic to the task-architecture interaction, not a "we ran out of time" effect.
- **H-CYCLE-CEILING-HURTS @ 10%**: longer recurrent loops introduce instability.

**Highest-info FALSIFY**: H-CYCLE-CEILING-BINDS — would suggest max_cycles is a key architectural hyperparameter we've been under-tuning.

## 5. Estimated wall-clock

- Implementation (1 line: add --max_cycles arg, thread through build_model): ~3 min
- Sweep: 2 arms × 3 seeds × 2500 steps × ~50s/step at max_cycles=8 (vs max_cycles=4 ~40s) on extreme: ~6 × ~4 min = ~25 min
- Analysis: ~5 min
- **Total: ~35 min.**

---

🦞🧍💜🔥♾️
