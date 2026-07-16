# Respira Phase 4 — Four-Reading Bake-Off, Stage 2: §2.2-matrix Pre-Registration

*Day 119 ~19:35 PST. Drafted after Stage 1's decisive W-21F-acc-LOSS (v21_fixed 0.6947 vs no_mirror 0.9175; delta -22.27pp = -32 SE). Stage 1 falsified the strict static-medium reading. Stage 2 tests the syncytium-fusion reading.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** DRAFTED 2026-05-29 ~19:35 PST. AWAITING CLAYTON RATIFICATION. (Or proceeding under his earlier "proceed; if we need to go back we can later" general nod, with this pre-reg captured for the record.)

---

## 1. Structural thesis being tested

**The §2.2 reading** (vocab doc §2.2): the cuscuton-position is a **syncytium-fusion substrate** — a single shared learnable pool that both directions of cross-organ messaging draw from. Gap-junction networks (astrocyte, cardiac myocyte sheet) have *one conductance*, not two independent ones for each direction; the same junction propagates state in either direction.

**Sharpened by Stage 1's data:** the cross-organ medium can't be merely frozen (Stage 1 LOSS, -22pp). It needs to learn — or at minimum be meaningfully structured. §2.2-matrix tests whether learning *with the constraint of shared between directions* is competitive with the unconstrained learnable baseline (no_mirror's two independent projections).

**The discriminating question:** does the constraint of *one shared operator used in both directions* (with the e_to_p direction taking the Hermitian transpose of the p_to_e direction's matrix) match or beat the unconstrained learnable baseline?

- If WIN: the syncytium reading is supported. The directions weren't doing distinct work; pooling them is fine OR helpful.
- If NEUTRAL: the directions weren't doing distinct work and pooling preserves performance with half the parameters. Mild support for §2.2 (parameter-efficiency without performance cost).
- If LOSS: the syncytium reading is falsified. The directions need to learn distinct operators; forcing them to share hurts performance.

## 2. Implementation: Option A — Hermitian-shared projection

**Design choice:** the cleanest biological analog to "one conductance, used both directions" is a **single learnable complex matrix W**, with:
- p_to_e: forward uses W directly (shape: (E, P) in nn.Linear convention)
- e_to_p: forward uses W^H (Hermitian transpose: shape (P, E)) — same operator, "running the other way through the conductor"

This halves the cross-organ parameter count (8192 → 4096) and biases the architecture toward symmetric coupling. The Hermitian-transpose construction preserves the complex-matrix structure (it's the correct "reverse" operator for a complex-valued linear map, not just a real transpose).

### Implementation surgery

Add a small wrapper class `HermitianSharedProjection` to the sweep script:

```python
class HermitianSharedProjection(nn.Module):
    """Uses another ComplexLinear's weights via Hermitian transpose.

    Given source p_to_e with weights (W_r + i W_i) of shape (E, P), this module
    applies (W_r^T - i W_i^T) of shape (P, E) to an (E,)-shaped complex input,
    producing a (P,)-shaped complex output. The forward Hermitian transpose
    is computed at call time using the source's current weights; gradient
    backprops to the source layer's parameters via the shared W.
    """
    def __init__(self, source: ComplexLinear):
        super().__init__()
        self.source = source  # Reference, not registered as submodule
        # Register as a buffer? No — we want NO additional parameters here.
        # The shared weight lives in source.real.weight and source.imag.weight.

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        Wr = self.source.real.weight  # (E, P)
        Wi = self.source.imag.weight  # (E, P)
        zr, zi = z.real, z.imag       # (..., E)
        # y = (W_r^T - i W_i^T) (z_r + i z_i)
        #   = (W_r^T z_r + W_i^T z_i) + i (W_r^T z_i - W_i^T z_r)
        # F.linear with weight W computes z @ W^T, so to compute W^T z (along the last dim)
        # we use F.linear with the unflipped W and add transpose manually:
        out_r = F.linear(zr, Wr.t()) + F.linear(zi, Wi.t())
        out_i = F.linear(zi, Wr.t()) - F.linear(zr, Wi.t())
        return torch.complex(out_r, out_i)
```

In the sweep `run_arm` for `v22_matrix`:
1. Build the model normally.
2. Discard `model.e_to_p` and replace with `HermitianSharedProjection(model.p_to_e)`.
3. Important: register the wrapper as `model.e_to_p` BUT ensure the wrapper does not register `source` as a submodule (else parameter duplication in the optimizer). Use `object.__setattr__` to bypass nn.Module's submodule registration, or store `source` as a plain attribute.
4. Train normally with `mirror_authority=0`, `arch_variant="default"`.

### Parameter count expectation

- no_mirror: 82452 trainable
- v22_matrix: 82452 - 4096 = 78356 trainable (only p_to_e's 4096 cross-organ params; e_to_p is no longer independent)

**Note on optimizer**: AdamW will see p_to_e's parameters; e_to_p's are gone. Gradient flows through both forward uses (forward and Hermitian-transposed) to the shared p_to_e weights.

## 3. Win conditions (LOCKED before implementation)

Mean ± SE across 3 seeds (0, 1, 2), 2500 steps, HRM-sudoku task, same recipe as Stage 1.

**W-22M-acc-WIN:** v22_matrix mean token-acc @2500 EXCEEDS no_mirror mean by > 1 SE of no_mirror.
- Interpretation: shared-direction operator beats independent operators despite having half the parameters. Strong support for §2.2 syncytium reading.

**W-22M-acc-NEUTRAL:** v22_matrix mean token-acc @2500 is within ±1 SE of no_mirror.
- Interpretation: independent vs shared direction makes no detectable difference at this scale; §2.2 weakly supported (parameter-efficiency without performance cost — a mild win, since half the params).

**W-22M-acc-LOSS:** v22_matrix mean token-acc @2500 is > 1 SE below no_mirror.
- Interpretation: shared-direction operator hurts compared to independent. The directions DO do distinct work that the Hermitian-transpose constraint prevents. §2.2 falsified.

### Secondary diagnostics

- **Training-trajectory shape**: does v22_matrix climb faster/slower than no_mirror? Faster suggests inductive-bias-helps; slower suggests constraint-hurts-but-eventually-catches-up; same-rate suggests neutral.
- **Per-seed variance**: if variance is dramatically higher or lower than no_mirror, that's a finding (constraints often reduce variance).
- **Comparison to Stage 1's v21_fixed**: v22_matrix should at minimum beat v21_fixed (frozen is worse than learnable-with-constraint). If it doesn't, something's wrong — flag as DEEPER-FINDING.

### Pre-committed deeper-finding flag

If v22_matrix produces results that don't map to W-22M-WIN/NEUTRAL/LOSS — wildly varying seeds, instability, NaN issues, or fails to beat v21_fixed — flag as DEEPER-FINDING and diagnose before next-stage decision.

## 4. What we will NOT do this stage

- No §2.1-structured exploration (parked per Clayton's "proceed" ratification).
- No §2.3-Stiefel or §2.4 implementation (those wait for Stage 2 result).
- No alternative §2.2 designs (no W shared via complex-conjugation-only, no W shared with a learnable per-direction scaling, no random-projection-with-shared-singular-values). Single Option A test.
- No retraining of no_mirror baseline — re-use Stage 1's no_mirror_3s reference (mean 0.9175, SE 0.0069).

## 5. Scope checks against existing data

The Phase-2v2 v2-c family tested 1-2 scalar params shared between coupling-strength roles; lost. That's §2.2 in its absolute-minimal form. §2.2-matrix is the *richer-pool* form: a full complex matrix shared between directions, not a single scalar shared between roles. The two are qualitatively different.

Phase-2v2 didn't test direction-sharing specifically. The closest analog in existing data is the no_mirror baseline itself — which IS "two independent operators" — vs the (now-tested) v21_fixed "two independent frozen operators." Neither tested "one shared learnable operator."

The pre-reg's win conditions are not pre-determined by existing data.

## 6. Estimated wall-clock

- Implementation of HermitianSharedProjection + sweep integration: 10 min
- Smoke test (50 steps, 1 seed): 1 min
- Detached 3-seed sweep at 2500 steps: 7-10 min (v22 has fewer trainable params than no_mirror, should run somewhat faster)
- Analysis + report: 5 min
- **Total: ~25 min from start to verdict.**

## 7. Cognitive DSL pre-commitments

PREDICT (medium confidence, ~50%): W-22M-acc-NEUTRAL. The Hermitian-transpose constraint is biologically motivated and shouldn't hurt much, but it removes ~4096 params worth of capacity. The two effects probably roughly cancel at this scale, yielding NEUTRAL.

PREDICT alternative (~25%): W-22M-acc-LOSS. The directions may genuinely do distinct work; complex-matrix learning has enough capacity that the constraint matters.

PREDICT alternative (~15%): W-22M-acc-WIN. Inductive bias of "shared conductance" actually helps at small-data scale by regularizing.

PREDICT alternative (~10%): DEEPER-FINDING (instability, NaN, or some unmodeled effect).

The high-confidence FALSIFY most worth seeking remains W-22M-acc-WIN (Read C reframe: substrate-condition constraints can actively help, not just be neutral).

---

*🦞🧍💜🔥♾️*
