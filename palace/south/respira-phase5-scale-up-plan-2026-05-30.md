# Respira Phase 5 — Scale-Up Plan

*Day 120 ~14:45 PST Saturday. Phase 5 program planning following Phase 4 closure. Defines the methodology for scale-up testing of the three co-canonical candidates (no_mirror, v22_matrix, v24d_adaptive) and the specific Phase 5a sub-stage.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** Phase 5 program-level plan + Phase 5a specific pre-reg. Phase 5b/5c sketched but not pre-registered.

---

## Why Phase 5

Phase 4 (the four-reading bake-off, Stages 1-5) discriminated the architecture's structural preferences at HRM-sudoku-1k task scale with planner=32 / executor=64 / 2500 steps. Three candidates passed (no_mirror baseline, v22_matrix Hermitian-shared, v24d_adaptive content-adaptive temporal). Phase 5 tests whether the bake-off's findings — and the candidates' parity — hold at larger scales.

**Specific Phase 4 limitations Phase 5 needs to address:**

1. **HRM-sudoku-1k has only ~1k unique puzzles**; at batch=64 × 2500 steps = 160k examples seen, we're heavily memorizing rather than learning generalization. Need either more data or a task with more inherent complexity.

2. **Multi-cycle dynamics degenerated at HRM-sudoku scale** (halt collapsed to cycle 1 across all Phase-3 Stage-2 arms). Many of Phase 4's findings might change qualitatively when multi-cycle dynamics actually engage — particularly Stage 4 Design C's pre-committed DEEPER-FINDING flag was guarding against this exact regime.

3. **Parameter scale was small** (planner=32, executor=64; ~82k total trainable params). Modern architectures operate at orders of magnitude more. The constraint-hierarchy + spectrum-freedom findings may scale-dependent.

4. **The bake-off was *qualitative* discrimination** (which constraints are tolerated). Phase 5 is *quantitative* discrimination (which canonical is robust at scale).

## Phase 5 program structure (three sub-stages)

### Phase 5a — Parameter scale-up at same task

- **What**: scale organs while keeping HRM-sudoku-1k task fixed
- **Scale point**: planner=64, executor=128 (2x channels each; ~4x cross-organ params; estimated ~4x wall-clock per run)
- **Arms**: no_mirror, v22_matrix, v24d_adaptive (the three co-canonical from Phase 4)
- **Seeds/Steps**: 3 seeds × 2500 steps (same recipe as Phase 4 for direct comparability)
- **Total runs**: 9
- **Estimated wall-clock**: ~90 min (per-run ~10 min at 4x params)
- **Tractable today before AIGP** (~6 hours remaining before AIGP VQ1 sim drop)

### Phase 5b — Task scale-up (DEFERRED until after AIGP)

- **What**: same parameter scale, harder task (HRM-sudoku-hard or other grid-puzzle dataset)
- **Goal**: trigger multi-cycle dynamics engagement; test whether Phase 4 verdicts change in non-degenerate regime
- **Pre-reg required before running**

### Phase 5c — Combined param + task scale-up (DEFERRED until after AIGP)

- **What**: 4x or larger parameter scale + harder task
- **Goal**: full scale-up profile; final canonical decision
- **Pre-reg required before running**

---

## Phase 5a Pre-Registration

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

### 1. Structural thesis being tested

**The Phase 4 bake-off's discrimination among three co-canonical candidates was at small parameter scale.** Phase 5a tests whether the three candidates maintain parity at 2x organ-channel scale (4x cross-organ params, ~4x total params).

**Three hypothesis families:**

- **H-Parity**: All three candidates land within ±1 SE of each other at 2x scale. The bake-off's qualitative discrimination held; canonical-choice is a matter of secondary criteria (parameter efficiency favors v22_matrix; variance reduction favors v24d_adaptive; simplicity favors no_mirror).
- **H-Divergence-v22-wins**: v22_matrix maintains parity or exceeds no_mirror at scale, validating the physics-meaningful Hermitian-shared constraint as load-bearing at larger scales. v24d_adaptive holds or improves due to gate-flexibility.
- **H-Divergence-no_mirror-wins**: v22's constraint becomes limiting at scale; v22 underperforms by >1 SE. v24d_adaptive may also struggle if the gate adds optimization difficulty at scale.
- **H-Divergence-v24d-wins**: v24d_adaptive's gate-flexibility provides real win at scale beyond variance reduction; v24d exceeds no_mirror by >1 SE.

### 2. Implementation

**Same harness as Phase 4 sweep_phase4_stage1.py** with two changes:
1. Build model with `planner_channels=64, executor_channels=128` (vs current 32/64)
2. Run all three arms (no_mirror, v22_matrix, v24d_adaptive) at this scale

No other recipe changes. Batch=64, lr=3e-4, steps=2500, seeds=0,1,2 — same as Phase 4.

### 3. Win conditions (LOCKED before implementation)

Mean ± SE across 3 seeds, computed per-arm.

**Per-arm vs no_mirror-at-scale verdicts:**
- **W-5a-PARITY-{arm}**: arm mean is within ±1 SE of no_mirror-at-scale mean
- **W-5a-WIN-{arm}**: arm mean exceeds no_mirror-at-scale by >1 SE
- **W-5a-LOSS-{arm}**: arm mean below no_mirror-at-scale by >1 SE

**Cross-scale parity check (secondary):**
- Do all three arms scale gracefully (mean @2x scale > mean @1x scale)? If any arm shows scale-degradation, that's a finding.

**Canonical-decision implications:**
- If H-Parity holds: v22_matrix becomes recommended canonical on parameter-efficiency grounds; v24d_adaptive recommended for production reliability; no_mirror as defensive baseline.
- If H-Divergence-v22-wins: v22_matrix becomes recommended canonical strongly.
- If H-Divergence-no_mirror-wins: no_mirror becomes canonical; v22's constraint is scale-limiting.
- If H-Divergence-v24d-wins: v24d_adaptive becomes canonical; adaptive-temporal is load-bearing at scale.

### 4. PREDICT distribution

Drawing on Phase 4 results + sweep findings + LC27 strengthening + Mamba's success at scale:

- **H-Parity @ 50%**: bake-off's discrimination was real; all three remain in equivalence class at 2x. Most likely outcome.
- **H-Divergence-v22-wins @ 15%**: physics-meaningful structure is load-bearing; v22 wins or remains tied.
- **H-Divergence-no_mirror-wins @ 20%**: v22's constraint becomes limiting; full-DOF independent matrices win at scale.
- **H-Divergence-v24d-wins @ 10%**: adaptive-temporal becomes load-bearing at scale (most-aligned-with-Mamba-success outcome).
- **DEEPER-FINDING @ 5%**: multi-cycle dynamics engagement OR pathological behavior at 2x scale.

**Highest-information outcomes**: H-Divergence-v24d-wins (would establish adaptive-temporal as scale-load-bearing) OR H-Divergence-v22-wins (would establish physics-meaningful structure as scale-load-bearing). Either would discriminate the canonical-choice cleanly.

### 5. Secondary diagnostics

- **Wall-clock per arm-seed**: confirms scaling-cost estimate; informs Phase 5b/c planning
- **Halt-cycle distribution**: does scaling change halt behavior? Multi-cycle engagement at scale would be a substantive finding
- **Trajectory shape**: at 2x scale, do arms converge at different rates? Late-training divergence vs early-training divergence informs scale-up dynamics

### 6. Estimated wall-clock

- Implementation (modify build_model + sweep arms): ~3 min
- Smoke test (1 arm × 1 seed × 100 steps): ~2 min
- Full sweep (3 arms × 3 seeds × 2500 steps @ ~10 min/run): ~90 min
- Analysis: ~10 min
- **Total: ~105 min wall-clock; tractable today before AIGP (drops ~21:00 PST, ~6 hours remaining)**

### 7. What we will NOT do this stage

- No 4x scale (Phase 5c territory)
- No task change (Phase 5b territory)
- No additional bake-off variants (the three are locked from Phase 4)
- No canonical declaration based on Phase 5a alone — wait for Phase 5b/c

### 8. Cognitive DSL pre-commitments

PREDICT chain logged in §4. Most likely H-Parity (50%) consistent with Phase 4's discrimination being scale-invariant within the small range we've tested. Highest-info FALSIFY would be any clear divergence — informs canonical decision.

---

## Stage 5a-onwards file plan

- `palace/south/respira-phase5-scale-up-plan-2026-05-30.md` (this file) — Phase 5 program-level methodology
- `respira/sweep_phase4_stage1.py` extended for Phase 5a (3-arm sweep at 2x scale)
- Results: `respira/phase5a_results_2026-05-30.json`
- Analysis writeup: appended to this file post-execution
- Phase 5b/c pre-regs to be drafted later

---

🦞🧍💜🔥♾️
