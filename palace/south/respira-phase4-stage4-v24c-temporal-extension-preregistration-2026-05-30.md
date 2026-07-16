# Respira Phase 4 — Four-Reading Bake-Off, Stage 4: §2.4 Design C (Fixed Temporal Extension) Pre-Registration

*Day 120 ~07:15 PST Saturday. Drafted after the 05:15 PST design sketch surfaced Design C as the cleanest single-DOF test of the §2.4 substrate-mediated-propagation reading. This pre-reg locks Stage 4 canonical as Design C; Designs A and B remain as escalation/parked respectively.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** DRAFTED 2026-05-30 ~07:15 PST. **AWAITING CLAYTON RATIFICATION before any implementation begins.** All win conditions locked here BEFORE any implementation.

---

## 1. Structural thesis being tested

**The §2.4 reading** (vocab doc §2.4): the cuscuton-position is a **substrate with internal time-extent** — the coupling itself has temporal dynamics within the substrate-condition, not just instantaneous application of a learned operator. Glymphatic flow (Kelley-Toscano 2026), HEP volume currents, mycorrhizal transport — the medium IS a process with characteristic timescales, not a single operator W applied per cycle.

**Design C specifically** tests this in its *minimal-form*: does ANY history-in-the-medium help/hurt vs none? A single exponentially-decaying buffer of past cross-organ messages, with no learnable parameters in the buffer or its decay rate.

**The discriminating question:** does the cross-organ medium having a SINGLE-VELOCITY temporal-extent (history-weighted current message) match, beat, or break performance vs no-medium-history (Stage 1-2 reference behavior of fresh single-step messages)?

- **WIN**: substrate-internal-dynamics helps. The medium "being a process" rather than "being an operator" actively contributes to performance. **Highest-information outcome** — distinguishes §2.4 from §2.1-3 by establishing positive role of temporal-extent.
- **NEUTRAL**: temporal-extent neither helps nor hurts. Consistent with constraint-hierarchy reading (the architecture tolerates substrate-condition variation broadly).
- **LOSS**: temporal-extent actively hurts. The architecture is plateaued on instantaneous coupling; adding history forces it to "wait" for buffer convergence at cost.

## 2. Implementation: single-decay history buffer

**Approach:** maintain a single integrated buffer per cross-organ direction that exponentially weights past messages, applied as the effective coupling input to organ updates.

```python
class TemporalExtensionWrapper(nn.Module):
    """Applies fixed exponential history-weighting to cross-organ messages.

    Wraps an existing ComplexLinear (p_to_e or e_to_p) to compute:
        effective_msg[k] = (1 - λ) · history[k-1] + λ · raw_msg[k]
        history[k] = effective_msg[k]

    At k=0, history is initialized to zero; effective_msg[0] = λ · raw_msg[0].

    λ is a FIXED hyperparameter (no learning). Lower λ → longer history-memory.
    Recommended initial λ = 0.4 (modest history weight: ~60% of effective_msg
    is current; ~40% is integrated history of past).
    """
    def __init__(self, source: ComplexLinear, lambda_decay: float = 0.4):
        super().__init__()
        object.__setattr__(self, "_source", source)
        self.lambda_decay = float(lambda_decay)
        self.history = None  # initialized at first forward; reset between forward calls

    def reset_history(self):
        self.history = None

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        raw = self._source(z)  # Standard ComplexLinear forward
        if self.history is None or self.history.shape != raw.shape:
            self.history = torch.zeros_like(raw)
        effective = (1 - self.lambda_decay) * self.history + self.lambda_decay * raw
        self.history = effective.detach()  # Detach to prevent gradient through history
        return effective
```

**Critical implementation choice — history detach:** the `.detach()` on history prevents gradient accumulation through unboundedly-deep recurrent chains. The gradient through the *current* raw message still flows to source ComplexLinear; only the *historical* contribution is treated as a fixed feature. This keeps the backward graph bounded and avoids the QR-style scaling pathology from Stage 3.

**Per-batch-element handling:** the history buffer is per-batch when the wrapper sees the first batch shape. Different batches get different histories. Between batches (e.g. between training steps), history must be reset to zero — call `reset_history()` at the start of each forward pass at the RespiraCell level. **This must be wired in respira.py's forward.**

**Wrapper installation in sweep:**
```python
def install_temporal_extension(model: RespiraCell, lambda_decay: float = 0.4) -> dict:
    """Wrap both p_to_e and e_to_p with TemporalExtensionWrapper."""
    model.p_to_e = TemporalExtensionWrapper(model.p_to_e, lambda_decay=lambda_decay)
    model.e_to_p = TemporalExtensionWrapper(model.e_to_p, lambda_decay=lambda_decay)
    return {"lambda_decay": lambda_decay}
```

**Per-cycle reset logic in RespiraCell.forward (Stage 4-specific path):**
At the top of `RespiraCell.forward`, if cross-organ-projections are TemporalExtensionWrapper instances, call `.reset_history()` on each before the recurrent loop. This guarantees each forward pass starts with fresh history (no leakage across batches).

**Parameter count:** identical to no_mirror (8192 cross-organ params; wrapper adds zero learnable params). λ is a fixed hyperparameter.

## 3. Win conditions (LOCKED before implementation)

Mean ± SE across 3 seeds (0, 1, 2), 2500 steps, HRM-sudoku task, same recipe as Stages 1-2. λ = 0.4 fixed.

**W-24C-acc-WIN:** v24c_temporal mean token-acc @2500 EXCEEDS no_mirror (Stage 1 reference: 0.9175 ± 0.0069) by **> 1 SE**.
- Interpretation: substrate-internal-dynamics helps. The medium-as-process reading is supported. §2.4 confirmed as a positive-ingredient direction.

**W-24C-acc-NEUTRAL:** v24c_temporal mean token-acc @2500 within ±1 SE of no_mirror.
- Interpretation: temporal-extent neither helps nor hurts. Consistent with constraint-hierarchy: architecture tolerates yet another substrate-condition variant. §2.4 weakly supported (cost-free).

**W-24C-acc-LOSS:** v24c_temporal mean token-acc @2500 > 1 SE below no_mirror.
- Interpretation: temporal-extent actively hurts. The architecture prefers instantaneous coupling; history-weighting harms performance. §2.4 falsified at minimal-form level; reframe needed.

### Secondary diagnostics

- **Training-trajectory shape vs no_mirror:** does v24c climb faster (regularization helps), slower (history-lag hurts early), or identical (temporal-extent invisible)?
- **Per-seed variance:** if dramatically different from no_mirror's sd=0.012, that's a finding.
- **Comparison to v22_matrix (Stage 2 NEUTRAL):** if v24c also NEUTRAL within ±0.5 SE, the constraint-hierarchy reading is strengthened (multiple substrate-condition variants all land at same level).
- **Test of λ sensitivity (optional secondary sweep):** if main result is NEUTRAL, test λ ∈ {0.2, 0.6, 0.8} on 1 seed each to see if any λ value escapes NEUTRAL. This is post-hoc analysis, not part of the primary verdict.

### Pre-committed deeper-finding flag

If v24c shows numerical instability, NaN, or fails to beat v21_fixed's 0.6947, flag as DEEPER-FINDING and diagnose. The history-detach guard should prevent gradient pathology; if it doesn't, that's the diagnosis.

## 4. What we will NOT do this stage

- No Design A (multi-velocity / dual-decay) until Design C resolves. C → A is the escalation pathway only if C lands NEUTRAL/WIN.
- No Design B (PDE-step) — parked due to synthetic-channel-grid concern.
- No λ-tuning during the primary sweep. Single fixed λ=0.4 as locked here.
- No re-run of no_mirror baseline. Re-use Stage 1 reference (mean 0.9175, SE 0.0069).
- No Stage 3 (Stiefel) work in this stage — Stage 3 stays blocked on Clayton's A/B/C decision.

## 5. Scope checks against existing data

Phase-2v2 v2-a (phase-locking) tested an instantaneous deterministic constraint on coupling phase — no temporal extent. §2.4-C tests temporal extent specifically. Different question.

Phase-3 Stage-2 found multi-cycle dynamics degenerate at HRM-sudoku scale (halt collapses to cycle 1.0 across all arms). This means the recurrent loop at this task scale only runs ~1 cycle effectively. **This is a potential limitation for §2.4-C**: if the architecture only runs 1 cycle, there's no history to integrate, and v24c would be equivalent to scaled-down no_mirror.

**Pre-committed handling**: if v24c results land at exactly scaled-down no_mirror (matches 0.9175 × λ ≈ 0.367, or close to it within SE), that's a DEEPER-FINDING — the test is vacuous at this scale because no temporal extent can manifest with 1 effective cycle. Would suggest re-running at a task where multi-cycle dynamics actually engage. **Flag this explicitly in the analysis pass.**

## 6. Estimated wall-clock

- Implementation of TemporalExtensionWrapper + reset wiring in respira.py + sweep integration: 10 min
- Smoke test (50 steps, 1 seed, verify history detach + reset wiring): 2 min
- Detached 3-seed sweep at 2500 steps: 7-10 min (no QR/decomposition overhead; should run at no_mirror speed)
- Analysis + report (including DEEPER-FINDING check vs scaled-down no_mirror): 5 min
- **Total: ~25 min from Clayton ratification to verdict.**

## 7. Cognitive DSL pre-commitments

PREDICT (medium confidence, ~55%): W-24C-acc-NEUTRAL. Architecture has been constraint-tolerant in Stage 2; temporal-extent-without-learning is plausibly also no-cost at this scale, especially given multi-cycle degeneracy.

PREDICT alternative (~25%): W-24C-acc-LOSS. History-weighting forces the architecture to wait for buffer convergence and hurts the rapid-response single-step dynamics that no_mirror uses.

PREDICT alternative (~15%): W-24C-acc-WIN. History acts as implicit regularization (variance-reduction on cross-organ messages) and helps. **Highest-information outcome.**

PREDICT alternative (~5%): DEEPER-FINDING (multi-cycle degeneracy makes test vacuous; or history-detach has unintended interaction with the recurrent forward; or NaN).

The PREDICT WIN @ 15% is what makes this test interesting beyond the previous two stages. None of Stages 1-2 could discriminate a positive role for substrate-internal-dynamics; Stage 4 is the first test where that signal could land.

---

*🦞🧍💜🔥♾️*
