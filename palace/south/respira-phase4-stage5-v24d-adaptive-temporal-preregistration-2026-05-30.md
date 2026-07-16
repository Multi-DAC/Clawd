# Respira Phase 4 — Stage 5: §2.5 Design D Adaptive Temporal Extension Pre-Registration

*Day 120 ~14:00 PST Saturday. Drafted after Stage 4 Design C landed mild LOSS (v24c_temporal 0.8949 vs no_mirror 0.9175, -3.26 SE). Stage 5 tests the sweep-surfaced "Mamba-style content-adaptive temporal dynamics" variant. Clayton ratified "for good measure" + co-canonical-pending-scale-up framing for v22_matrix and no_mirror.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** DRAFTED 2026-05-30 ~14:00 PST. AWAITING CLAYTON RATIFICATION before implementation. (Or proceeding under Clayton's earlier "I agree, let's go for it" — captured here for the record.)

---

## 1. Structural thesis being tested

**The §2.5 reading** (sweep-surfaced extension of §2.4): the substrate-condition has temporal extent, but the *decay rate* is content-adaptive rather than fixed. Each forward pass, the per-cycle decay coefficient is computed from the current cross-organ message, allowing the architecture to learn *when to use history vs. when to ignore it*.

**LC27 prediction**: this should fare better than Design C (fixed λ_decay) if LC27 holds. LC27 says the relational pattern emerging from coupled dynamics outperforms added-substance. Design C's λ_decay=0.4 is engineered-substance; Design D's gate(state) → λ is emergent-from-coupled-dynamics. **If LC27 is operative at this architectural scale, Design D should land at least as well as no_mirror — possibly better, possibly within NEUTRAL.**

**Mamba analog**: Mamba's selective state-space update where SSM parameters are functions of input. Design D is the cross-organ-coupling-specific version of that mechanism, applied to Respira's organ-substrate distinction.

**The discriminating question**: does *content-adaptive* temporal extent in the substrate-condition help, hurt, or do nothing, compared to no_mirror's instantaneous independent matrices?

## 2. Implementation: AdaptiveTemporalExtensionWrapper

**Design**: wrap each cross-organ ComplexLinear with a small gate that computes per-cycle λ_decay from the current message magnitude. The gate is a 2-layer MLP outputting a real scalar in [0, 1] via sigmoid. When the gate saturates at λ=1, the wrapper recovers no_mirror behavior (current message only, no history); when it saturates at λ=0, it recovers full history (no new info). The architecture learns where to be on this spectrum per-cycle.

```python
class AdaptiveTemporalExtensionWrapper(nn.Module):
    def __init__(self, source: ComplexLinear, hidden_dim: int = 8):
        super().__init__()
        self.source = source
        # Gate: takes raw message magnitude (real, last-dim = out_features)
        # outputs per-element (or scalar) λ_decay in [0, 1].
        # Start with PER-BATCH-PER-POSITION scalar λ (simplest content-adaptive form).
        out_features = source.real.weight.shape[0]
        self.gate = nn.Sequential(
            nn.Linear(out_features, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),
        )
        # State buffer (dict pattern from Stage 4 to avoid PyTorch attribute tracking)
        object.__setattr__(self, "_state", {"history": None})

    def reset_history(self):
        self._state["history"] = None

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        raw = self.source(z)
        hist = self._state["history"]
        if hist is None or hist.shape != raw.shape:
            hist = torch.zeros_like(raw, requires_grad=False)
        hist = hist.detach()
        # Compute per-batch-per-position λ from raw magnitude
        raw_mag = raw.abs()  # [..., out_features], real
        lam = self.gate(raw_mag)  # [..., 1], real, in [0, 1]
        lam_complex = lam.to(raw.dtype)  # broadcast to complex
        effective = (1.0 - lam_complex) * hist + lam_complex * raw
        self._state["history"] = effective.detach()
        return effective
```

**Parameter count addition**: gate has `out_features × hidden_dim + hidden_dim + hidden_dim × 1 + 1` params per direction. For out_features=64, hidden_dim=8: 64×8 + 8 + 8×1 + 1 = 521 params for p_to_e gate; 32×8 + 8 + 8×1 + 1 = 273 params for e_to_p gate. **Total ~800 additional params** (vs no_mirror's 82452, ~1% addition).

**Critical design choice**: per-batch-per-position scalar λ (not per-channel or per-output-element). This is the simplest content-adaptive form and most-Mamba-aligned. Future Design D' could test per-output-channel λ if D lands NEUTRAL/WIN and we want richer adaptive control.

**History reset semantics**: same as Stage 4 — per-forward-call reset via patched model.forward.

## 3. Win conditions (LOCKED before implementation)

Mean ± SE across 3 seeds (0, 1, 2), 2500 steps, HRM-sudoku task, same recipe as Stages 1-4. Reference: Stage 1 no_mirror = 0.9175 ± 0.0069.

**W-24D-acc-WIN:** v24d_adaptive mean @2500 EXCEEDS no_mirror mean by > 1 SE.
- Interpretation: content-adaptive temporal extent actively helps. The substrate-condition benefits from being relational-emergent (gate-learned) rather than instantaneous-only. Strong support for LC27 at architectural scale. Highest-information outcome.

**W-24D-acc-NEUTRAL:** within ±1 SE of no_mirror.
- Interpretation: gate-adaptive temporal extent neither helps nor hurts. Consistent with "architecture tolerates broad variants where the variant is appropriately gated to not interfere." LC27 weakly supported (the adaptive form recovers no_mirror as a degenerate case via gate=1).

**W-24D-acc-LOSS:** > 1 SE below no_mirror.
- Interpretation: even adaptive temporal extent hurts. Combined with Stage 4 LOSS, the bake-off says the architecture wants strict instantaneous coupling regardless of how the temporal extent is parametrized. LC27 architectural-scale instance partially-contradicted.

### Secondary diagnostics

- **Comparison to Stage 4 (v24c_temporal)**: does adaptive outperform fixed? If v24d_adaptive ≥ v24c_temporal + 1 SE, the adaptive-vs-fixed distinction discriminates.
- **Gate value distribution**: at end of training, what does the learned λ distribution look like? If λ saturates near 1.0 across batches, the architecture is essentially recovering no_mirror (the gate learned to ignore history). If λ has meaningful spread, the architecture is using adaptive temporal extent for some signals.
- **Per-seed variance**: Stage 4 had higher variance (sd=0.021); does Stage 5 reduce or amplify that?

### Pre-committed deeper-finding flag

If v24d_adaptive shows numerical instability, gate-collapse pathology (λ stuck at 0 or 1), or training failure mode → DEEPER-FINDING, diagnose before concluding.

## 4. What we will NOT do this stage

- No per-channel or per-output-element λ (Design D' refinement; future stage if D lands clean)
- No multi-velocity adaptive (Design D combined with Design A dual-velocity); future stage
- No retraining no_mirror reference — re-use Stage 1 baseline
- No declaring Respira-canonical based on Stage 5 results. Canonical-decision waits for Phase 5 scale-up testing.

## 5. Scope checks against existing data

- Stage 4 Design C (fixed temporal extension) LOST by 3.3 SE. Stage 5 tests whether the adaptive-vs-fixed axis discriminates within the temporal-extent family.
- Mamba's success at scale suggests content-adaptive temporal dynamics is a real win-axis in modern architectures. Whether this transfers to organ-substrate-distinguished architecture is unknown.
- The bake-off's spectrum-freedom requirement (Stage 3+3b LOSS) is independent of temporal axis; Design D preserves spectrum freedom (gate adds info, doesn't constrain magnitudes).

## 6. Estimated wall-clock

- Implementation of AdaptiveTemporalExtensionWrapper + install function + history-reset patch: ~7 min
- Smoke test (50 steps, 1 seed): ~1 min
- Detached 3-seed sweep at 2500 steps: ~7-10 min
- Analysis + report: ~5 min
- **Total: ~20-25 min from ratification to verdict.** (Wall-clock for me; longer for Clayton if including review.)

## 7. Cognitive DSL pre-commitments

**PREDICT (medium confidence)**:
- W-24D-acc-NEUTRAL @ 45% — gate-adaptive recovers no_mirror behavior via λ saturation when adaptive feature isn't helping
- W-24D-acc-WIN @ 25% — LC27 prediction + Mamba's success suggests adaptive-temporal is a real win-axis; possibility worth seriously weighting
- W-24D-acc-LOSS @ 25% — gate adds optimization difficulty without payoff at this scale; architecture wants pure instantaneous
- W-24D-DEEPER-FINDING @ 5% — gate pathology, NaN, etc.

**Highest-information FALSIFY**: W-24D-acc-LOSS would discriminate that the architecture has a *fundamental* preference for instantaneous coupling, not a *parametrization* preference. Would close the four-reading frame with the cleanest possible structural reading.

**Highest-information CONFIRM**: W-24D-acc-WIN would establish content-adaptive temporal dynamics as a positive ingredient — would be the first WIN in the bake-off and would substantively strengthen LC27 at architectural scale.

**Most likely outcome (NEUTRAL)** still informative — would confirm that the architecture is broadly constraint-tolerant *when the constraint is gated to be optional* (gate can saturate to recover no_mirror).

---

🦞🧍💜🔥♾️
