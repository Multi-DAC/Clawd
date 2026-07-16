# Respira Phase 5c — Combined Param + Task Scale-Up Pre-Registration

*Day 120 ~15:10 PST. Phase 5a tested param scale-up (easy task, 2x organ); Phase 5b tested task scale-up (extreme task, 1x organ). Phase 5c tests both simultaneously.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** Drafted 2026-05-30 ~15:10 PST. Proceeding under Clayton's "trust your judgment" ratification.

---

## 1. Structural thesis being tested

Phase 5a + Phase 5b together gave a *partial* scaling profile:

| Regime | no_mirror | v22_matrix | v24d_adaptive |
|---|---|---|---|
| Easy 1x | 0.918 | NEUTRAL (-0.5σ) | NEUTRAL (-0.0σ) |
| Easy 2x | 0.937 | LOSS (-1.0σ) | PARITY (-0.4σ) |
| Extreme 1x | 0.556 | PARITY (-0.4σ) | LOSS (-1.3σ) |
| **Extreme 2x** | **?** | **?** | **?** |

Phase 5c fills the fourth cell. Tests whether the ranking observed at extreme 1x (no_mirror > v22 ≥ v24d) holds at extreme 2x — OR whether the extra capacity at 2x scale flips it back toward Phase 5a's pattern.

## 2. Implementation

Identical to Phase 5b harness, with `--planner_channels 64 --executor_channels 128`. No code changes needed.

## 3. Win conditions (LOCKED)

Per-arm vs no_mirror-at-extreme-2x:
- **WIN**: arm > no_mirror + 1 SE
- **PARITY**: within ±1 SE
- **LOSS**: arm < no_mirror - 1 SE

**Cross-regime question**: does Phase 5b's v22-recovery hold at 2x (consistent with "constraint matters when DOF precious")? Or does Phase 5a's v22-LOSS reassert at 2x (consistent with "constraint costs when DOF abundant")? The interaction between task difficulty and parameter scale is the discriminating question.

**Pre-committed deeper-finding flag**: if all three near-chance (<0.50), task too hard even at 2x — would suggest needing 4x scale.

## 4. PREDICT distribution

Drawing on Phase 5a + 5b combined patterns:

- **H-Extreme-1x-ranking-holds @ 40%**: no_mirror > v22 ≥ v24d preserved at 2x extreme. The extreme task's hardness dominates the parameter-scale dynamics.
- **H-Easy-2x-ranking-reasserts @ 30%**: at 2x scale, capacity becomes abundant again, v22 starts paying its constraint cost, v24d recovers. Pattern flips to no_mirror > v24d ≥ v22.
- **H-Full-Parity @ 15%**: at extreme 2x, all three converge within SE (no discrimination because both axes maxed).
- **H-v24d-finally-wins @ 10%**: at extreme 2x, the gate finally exploits multi-cycle dynamics that have capacity.
- **DEEPER-FINDING @ 5%**: near-chance or some pathology.

**Highest-info FALSIFY**: H-v24d-finally-wins — would suggest the adaptive gate is regime-dependent in a specific way (helps when both scale AND task difficulty are non-trivial).

## 5. Estimated wall-clock

- Sweep (3 arms × 3 seeds × 2500 steps at 2x extreme): ~15-20 min (extreme is slightly slower than easy; 2x adds ~50% more time)
- Analysis: ~5 min
- **Total: ~20-25 min.**

---

🦞🧍💜🔥♾️
