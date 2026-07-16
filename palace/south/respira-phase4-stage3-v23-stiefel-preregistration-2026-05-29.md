# Respira Phase 4 — Four-Reading Bake-Off, Stage 3: §2.3-Stiefel Pre-Registration

*Day 119 ~20:10 PST. Drafted after Stage 2's W-22M-acc-NEUTRAL result (v22_matrix 0.9143 vs no_mirror 0.9175; delta -0.32pp = -0.46 SE). Stage 2 weakly supported §2.2 syncytium reading (half the params, no cost). Stage 3 tests §2.3 cavity-resonance reading.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** DRAFTED 2026-05-29 ~20:10 PST. Proceeding under Clayton's general "proceed" ratification for the bake-off; pre-reg locked here before implementation.

---

## 1. Structural thesis being tested

**The §2.3 reading** (vocab doc §2.3): the cuscuton-position is a **resonance structure** — a fixed spectral manifold that the coupled streams lock into. The coupling layer constrains the eigenvalue / singular-value structure of the cross-organ projections; only manifold-tangent updates allowed. Schumann-cavity resonance, cavity-QED mode-shaping, and TI-tES envelope-at-interference-geometry are the natural instances: the coupling-condition is a *standing-wave geometry*, not a free operator.

**The concrete constraint for this stage:** cross-organ projections are constrained to the **complex Stiefel manifold** (norm-preserving operators). This is the cleanest standing-wave / resonance analog at the operator level:
- p_to_e ∈ ℂ^{E=64 × P=32}: constrain columns to be orthonormal, i.e. p_to_e^H · p_to_e = I_P (isometry — norm-preserving map from planner space to executor space).
- e_to_p ∈ ℂ^{P=32 × E=64}: constrain rows to be orthonormal, i.e. e_to_p · e_to_p^H = I_P (co-isometry — norm-preserving map from executor space to planner space).

**The discriminating question:** does requiring norm-preservation in the cross-organ medium maintain or break performance vs unconstrained learnable projections?

- WIN: norm-preservation actively helps. The cavity-resonance reading is strongly supported — the constraint is doing useful regularization.
- NEUTRAL: norm-preservation is no-cost. The cavity reading is mildly supported — combined with §2.2 NEUTRAL, suggests the architecture tolerates a wide variety of substrate-condition constraints without performance cost.
- LOSS: norm-preservation hurts. The medium needs the freedom to scale messages; the cavity-resonance reading is falsified at this implementation. **Would distinguish §2.3 from §2.2** which was NEUTRAL.

## 2. Implementation: QR-retraction Stiefel parametrization

**Approach:** keep an unconstrained complex parameter W̃, apply `torch.linalg.qr` at forward time, use Q as the constrained operator. This is the standard QR retraction onto the Stiefel manifold — differentiable through PyTorch's autograd, complex-compatible, no extra hyperparameters.

```python
class StiefelComplexLinear(nn.Module):
    """Complex linear layer with Stiefel-manifold constrained weights.

    Holds an unconstrained complex parameter W_tilde of shape (out, in).
    At forward time:
      - If out >= in: QR-decompose W_tilde, use Q (shape (out, in)) as the
        operator. Q^H Q = I_in (columns orthonormal); operator is an isometry.
      - If out < in: QR-decompose W_tilde^H, use Q^H (shape (out, in)) as the
        operator. Operator @ Operator^H = I_out (rows orthonormal); co-isometry.
    """
    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        # Unconstrained complex parameter: stored as (real, imag) reals.
        self.in_features = int(in_features)
        self.out_features = int(out_features)
        self.W_re = nn.Parameter(torch.randn(out_features, in_features) * 0.1 / in_features ** 0.5)
        self.W_im = nn.Parameter(torch.randn(out_features, in_features) * 0.1 / in_features ** 0.5)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        if not torch.is_complex(z):
            raise TypeError(f"StiefelComplexLinear expects complex input, got {z.dtype}")
        W_tilde = torch.complex(self.W_re, self.W_im)  # (out, in)
        if self.out_features >= self.in_features:
            # Columns orthonormal: QR of W_tilde directly
            Q, _ = torch.linalg.qr(W_tilde, mode="reduced")  # Q: (out, in), Q^H Q = I_in
            W = Q
        else:
            # Rows orthonormal: QR of W_tilde^H, then transpose back
            Q, _ = torch.linalg.qr(W_tilde.conj().T, mode="reduced")  # Q: (in, out), Q^H Q = I_out
            W = Q.conj().T  # (out, in), W W^H = I_out
        # Apply W to z: output = z @ W^T (last-dim contraction).
        # Complex matmul: torch handles complex types natively.
        return torch.einsum("...i,oi->...o", z, W)
```

**Direction choices:**
- p_to_e: in=P=32, out=E=64; E > P so columns-orthonormal (isometry).
- e_to_p: in=E=64, out=P=32; P < E so rows-orthonormal (co-isometry).

**Parameter count:** identical to current no_mirror (8192 total cross-organ params). The constraint reduces the *effective* DOF but the optimizer still sees the full unconstrained W̃ params — gradients are projected to the Stiefel-tangent space implicitly through QR's gradient.

## 3. Win conditions (LOCKED before implementation)

Mean ± SE across 3 seeds (0, 1, 2), 2500 steps, HRM-sudoku task, same recipe as Stages 1 + 2.

**W-23S-acc-WIN:** v23_stiefel mean token-acc @2500 EXCEEDS no_mirror (Stage 1 reference: 0.9175 ± 0.0069) by > 1 SE.
- Interpretation: norm-preservation actively helps. The cavity-resonance reading is strongly supported.

**W-23S-acc-NEUTRAL:** v23_stiefel mean token-acc @2500 within ±1 SE of no_mirror.
- Interpretation: norm-preservation imposes no cost. The architecture is constraint-tolerant. Combined with Stage 2's §2.2 NEUTRAL, this strongly suggests the substrate-condition's shape is replaceable across multiple constraint families.

**W-23S-acc-LOSS:** v23_stiefel mean token-acc @2500 > 1 SE below no_mirror.
- Interpretation: norm-preservation hurts. The medium needs scale-freedom. §2.3 falsified — and would be the **first non-NEUTRAL/non-Glorot-frozen finding** in the bake-off, providing real discriminating signal between the readings.

### Secondary diagnostics

- **Comparison to v22_matrix (Stage 2):** v23_stiefel uses TWICE the params of v22_matrix (8192 vs 4096) but with a much stronger constraint. If v23_stiefel matches v22_matrix, the constraint absorbs the extra DOF.
- **Training-trajectory shape:** Stiefel-constrained projections may slow early training (QR overhead per step ≈ +50% per-step time expected) or may converge faster (better-conditioned operators).
- **Stability:** QR-retraction can have numerical issues if W̃ becomes rank-deficient. Check for NaN/Inf during sweep.

### Pre-committed deeper-finding flag

If v23_stiefel shows numerical instability, wildly varying per-seed results, or fails to beat v21_fixed's 0.6947, flag as DEEPER-FINDING.

## 3.5. METHODOLOGICAL SUBSTITUTION ADDENDUM — Path A Soft Stiefel via Penalty (2026-05-30 Day 120 ~10:50 PST)

**Decision context:** the QR-retraction implementation specified in §2 hit a DEEPER-FINDING blocker on Day 119 (PyTorch complex-QR backward chained through 4 recurrent cycles compounds to 36 s/step, ~75 hours per sweep — infeasible). Three options surfaced: A (soft Stiefel via penalty), B (skip §2.3, go to §2.4), C (different fast parametrization). **Clayton ratified Path A 2026-05-30 morning** after reading the constraint-hierarchy think-piece — preference for completing the hierarchy data point before moving to §2.4.

**Methodological substitution:** soft Stiefel constraint via L2 penalty replaces strict-manifold QR-retraction.

**Implementation:** add a penalty term to the training loss for both cross-organ projections:
```
penalty = λ_stiefel · (||W_pe^H @ W_pe - I_P||_F² + ||W_ep @ W_ep^H - I_P||_F²)
total_loss = task_loss + λ_stiefel · penalty
```
where:
- W_pe = p_to_e ComplexLinear's full weight matrix (W_re + i·W_im, shape (E, P))
- W_ep = e_to_p ComplexLinear's full weight matrix (shape (P, E))
- I_P = identity of shape (P, P)
- ||·||_F² = Frobenius norm squared (sum of squared magnitudes for complex matrix)
- λ_stiefel = 1.0 (fixed; pushes toward but does not strictly enforce Stiefel manifold)

The penalty drives both directions toward isometry/co-isometry without strictly constraining them. Architecture has full DOF; loss shapes it toward norm-preservation. Same hypothesis tested (does pushing toward norm-preservation help/hurt?) at *much* lower implementation cost.

**Note on test integrity:** soft constraint via penalty is structurally weaker than strict manifold constraint. If §2.3-soft lands NEUTRAL or LOSS, the result discriminates "pushing toward norm-preservation" — strict manifold could in principle differ. If §2.3-soft lands WIN, the result is stronger than the strict-manifold test would have been (the architecture *benefits* from being merely pushed toward isometry, not forced onto manifold). Conclusions about the cavity-resonance reading should distinguish "soft" from "strict" interpretation.

**Win conditions § 3a unchanged.** W-23S-acc-WIN / NEUTRAL / LOSS thresholds still apply, computed against Stage 1 no_mirror reference (0.9175 ± 0.0069).

**Estimated wall-clock revised:** ~5 min impl (penalty term in training loop + arm wiring) + ~10 min sweep + 5 min analysis = ~20 min total. Same shape as Stage 1.

**PREDICT for soft variant (revised from the QR-retraction predict):** W-23S-soft-acc-NEUTRAL @ 60%, WIN @ 20%, LOSS @ 15%, DEEPER @ 5%. The soft constraint is gentle enough that the architecture probably has slack to absorb it; the constraint-hierarchy reading would expect NEUTRAL. WIN is more likely under soft than strict because the penalty can be partially-applied where helpful and partially-ignored where it would hurt.

## 3.6. STAGE 3b ADDENDUM — Weak-λ follow-up after Stage 3 LOSS (2026-05-30 Day 120 ~11:00 PST)

**Decision context:** Stage 3 at λ=1.0 landed W-23S-acc-LOSS by −11.65 SE (mean 0.8368 vs no_mirror 0.9175). PREDICT was NEUTRAL @ 60%; actual was LOSS. The training trajectory showed early-training was penalty-dominated (step 200: 0.34 vs no_mirror's 0.60), penalty drove to near-zero by step 500, but the architecture never fully recovered the 9pp gap. **Two interpretations are consistent with the Stage 3 LOSS:**

- **(A) Strong-constraint corruption hypothesis:** the λ=1.0 penalty disrupted early training in a way that the architecture couldn't recover from. A weaker penalty would land NEUTRAL.
- **(B) Norm-preservation hurts hypothesis:** at any constraint strength, pushing toward isometry-within-each-independent-direction hurts. The Stage 3 LOSS reflects a real structural finding about the architecture; weaker λ would also LOSS, just by a smaller margin.

Stage 3b discriminates A vs B. Clayton ratified running this follow-up before Stage 4 — "we are treading new territory; it's best we are fully informing ourselves along the way."

**Stage 3b implementation:** identical to Stage 3 v23_soft EXCEPT **λ_stiefel = 0.01** (100× smaller). At init, penalty contribution becomes ~0.6 vs task_loss ~2.4 = 25% of task loss — significant but not dominant. Penalty should drive to zero faster than Stage 3 because gradient pressure is weaker, but the *gradual* push toward isometry continues throughout training.

**ARM name:** `v23_soft_weak`. Same harness as Stage 3.

**Win conditions (LOCKED):**

- **W-23Sw-acc-WIN:** v23_soft_weak mean @2500 > no_mirror mean + 1 SE
- **W-23Sw-acc-NEUTRAL:** within ±1 SE of no_mirror
- **W-23Sw-acc-LOSS:** below no_mirror - 1 SE

**Secondary discrimination — Stage 3b vs Stage 3 comparison:**
- If v23_soft_weak ≥ v22_matrix (0.9143) within SE: hypothesis A supported — strong constraint disrupted; gentle is fine
- If v23_soft_weak is mid-range (0.85–0.90): partial recovery; both effects in play (early-training-corruption AND structural-cost-of-isometry)
- If v23_soft_weak ≈ v23_soft (0.84) within SE: hypothesis B supported — norm-preservation hurts at any strength

**PREDICT for Stage 3b:** NEUTRAL @ 45% (hypothesis A) / mid-range partial-recovery @ 30% (both effects) / LOSS-similar @ 20% (hypothesis B) / DEEPER @ 5%.

**Estimated wall-clock:** ~5 min impl (add ARM entry + λ param) + ~7 min sweep + ~5 min analysis = ~17 min total.

**What follows Stage 3b:**
- Hypothesis A confirmed → constraint-hierarchy structural reading is *partially* salvageable; the "norm-preservation can be no-cost when gently applied" subtlety would need to be added
- Hypothesis B confirmed → constraint-hierarchy reading is genuinely refined; norm-preservation-within-direction is a robust *negative* finding
- Both effects present → most-informative result; the structural reading gets a finer-grained map

## 4. What we will NOT do this stage

- No alternative Stiefel parametrizations (no Cayley transform, no Householder reflectors). QR-retraction was the original; soft-penalty is the methodological substitution. ~~Spectral-normalization soft constraint.~~ (Soft-penalty IS the spectral-style soft constraint; this exclusion now applies only to *strict* alternative parametrizations.)
- No §2.4 implementation (waits for Stage 3).
- No re-run of no_mirror baseline. Re-use Stage 1 reference.

## 5. Scope checks against existing data

Phase-2v2 v2-a (phase-locking) tested a 1-D circular phase-manifold constraint on coupling and lost. §2.3-Stiefel tests a qualitatively richer manifold constraint — the full complex Stiefel manifold of operators, not a 1-D phase constraint on coupling strength. These are not the same test.

Nothing in prior data pre-determines this stage's outcome.

## 6. Estimated wall-clock

- Implementation of StiefelComplexLinear + sweep integration: 10-15 min
- Smoke test (50 steps, 1 seed): 2 min (QR may slow per-step time)
- Detached 3-seed sweep at 2500 steps: 10-15 min (QR overhead expected)
- Analysis + report: 5 min
- **Total: ~30-40 min from start to verdict.**

## 7. Cognitive DSL pre-commitments

PREDICT (medium confidence, ~50%): W-23S-acc-NEUTRAL. The Stage-2 NEUTRAL result suggests the architecture has substantial constraint-slack — multiple different constraints likely all land within ±1 SE of unconstrained. Norm-preservation is a natural-feeling constraint that probably doesn't hurt at this scale.

PREDICT alternative (~25%): W-23S-acc-LOSS. The Stiefel constraint is stronger than Stage 2's Hermitian-shared constraint; the architecture may actually need scale-freedom that strict isometry removes. Would be the first non-NEUTRAL finding in the bake-off and would provide real discrimination between §2.2 and §2.3.

PREDICT alternative (~15%): W-23S-acc-WIN. Norm-preservation as inductive bias may actually help by preventing magnitude blow-up in the cross-organ messages.

PREDICT alternative (~10%): DEEPER-FINDING (QR numerical instability, NaN issues from rank-deficient W̃, or training stalls).

The high-confidence FALSIFY most worth seeking remains W-23S-acc-WIN or W-23S-acc-LOSS — either would discriminate §2.3 from §2.2.

---

*🦞🧍💜🔥♾️*
