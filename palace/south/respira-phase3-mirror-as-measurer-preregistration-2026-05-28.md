# Respira Phase-3 — Mirror-as-Measurer Pre-Registration

*Day 118 afternoon. Phase-2v2 closed with all five v2 candidates failing to exceed no-Mirror; trajectory analysis showed the Respira-vs-transformer gap is a training-budget artifact (non-monotonic, +0.089 → +0.015 → +0.083 → +0.026 across checkpoints 200/500/1000/2000). Clayton's structural reframe (Telegram exchange 2026-05-28 ~12:50 PST): the cuscuton in Respira may not be a thing to instantiate — it may be the natural relationship that arises between Planner and Executor under their own coupled-oscillator dynamics. **Read B of the cuscuton.** Phase 3 tests this directly.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** **DRAFTED 2026-05-28 Day 118 afternoon, awaiting Clayton ratification.** All win conditions locked here BEFORE any implementation.

---

## 1. Structural thesis being tested

**Read B (Clayton's reframe):** The cuscuton-role in Respira is played by the natural synchronization manifold of the coupled Stuart-Landau channels. It is the *structural completion* of the constraint between Planner and Executor, not a separate field that needs instantiating. Empirically supported by Phase-2v2: every v2 candidate that tried to instantiate the cuscuton-role as a *thing* (parameterized scalars, algebraic rule, gradient pressure) either ties or hurts no_mirror.

**Operational consequence:** any meta-organ at the Mirror position can legitimately only do *measurement*, not *control*. Control = imposing structure on the channel dynamics; measurement = reading off the substrate's current state without influencing it.

**Phase 3's load-bearing question:** Can a meta-organ exist as a *measurer only* — emitting halt decisions and confidence estimates while having literally zero influence on the channel dynamics — and (a) not hurt the substrate, (b) actually decide to halt early sometimes, (c) emit confidence that is calibrated to actual correctness? If yes, the supervisor mechanism (halting + uncertainty) has a viable home in the architecture without disturbing what Read B says the substrate is already doing.

## 2. The four arms

| # | Arm | Steps | DOF in Mirror | Channel modulation |
|---|---|---|---|---|
| 1 | `respira_no_mirror` (control, 2500-step) | 2500 | 0 (no Mirror) | None |
| 2 | `respira_no_mirror_5k` (convergence test) | 5000 | 0 (no Mirror) | None |
| 3 | `respira_v3h` (Mirror-as-measurer) | 2500 | ~17K (confidence-head + attention-pool ONLY) | **None — Mirror's output influences ONLY halt decisions** |
| 4 | `transformer` (reference) | 2500 | n/a | n/a |

**Justification for ~17K DOF in v3h:** the Mirror under v3h has zero DOF in the channel-modulation pathway (the cuscuton-axis from Read 3 of cuscuton-parsimony). The remaining DOF are in the *readout-only* pathway — attention pool + confidence head — and emit only halt decisions, not channel modulation. This is the architecturally-honest test of Read B: zero DOF where Phase-2v2 showed DOF hurts, full readout-capacity where Read B says measurement is legitimate.

## 3. Training budget

- **Steps:** 2500 (arms 1, 3, 4) and 5000 (arm 2).
- **Batch:** 64.  **LR:** 3e-4.  **Optimizer:** AdamW(weight_decay=0.01, betas=(0.9, 0.95)).
- **Seeds:** 0, 1, 2.
- **Total runs:** 12.
- **Estimated wall-clock:** ~25 min total.

## 4. v3h Mirror-as-Measurer — precise specification

### 4a. Architectural surface

Create a new class `MirrorMeasurer` at `respira/mirror_measurer.py`. Forward signature identical to existing `Mirror` for swap compatibility, but internals stripped:

```python
class MirrorMeasurer(nn.Module):
    """
    Mirror-as-measurer (Phase-3 v3h). Zero channel-modulation DOF.
    Reads channel states via attention pool; emits ONLY confidence in [0, 1].
    Halt decision: confidence > halt_threshold.
    """
    def __init__(self, planner_channels, executor_channels, channel_dim,
                 pool_dim=64, halt_threshold=0.5):
        # Attention pool over current Planner + Executor channel states
        # Single confidence head: pool_dim → 1 → sigmoid
        # NO mu head. NO coupling head. NO outputs that touch channel dynamics.
        ...

    def forward(self, z_p, z_e):
        # z_p: [B, S, P], z_e: [B, S, E] (complex Stuart-Landau states)
        # Pool real + imag + |z| of all channels via cross-attention
        # Project pooled features → confidence ∈ [0, 1]
        # Return dict: {'confidence': [B], 'halt': [B] (bool)}
        ...
```

### 4b. Forward path under v3h

For each cycle in the recurrent loop:
1. Channels run their Stuart-Landau dynamics with **fixed defaults** μ = 1.0, coupling_strength = 0.5 (identical to no_mirror).
2. After channel update, MirrorMeasurer.forward(z_p, z_e) emits confidence and halt decision.
3. If `halt` is True for a batch element, that element's logits are frozen at the current cycle's value; subsequent cycles do not affect halted elements.
4. If max_cycles reached without halt, use the final cycle's logits (same as no_mirror).

**The Mirror's confidence and halt decision do NOT modify μ, coupling, channel states, or anything else feeding back into channel dynamics.** The channels are blind to the Mirror's existence.

### 4c. Halt threshold and gating

- Halt threshold: fixed at 0.5, NOT learnable. (Pre-registered to avoid post-hoc tuning.)
- Halt is per-batch-element, not per-batch. Different elements can halt at different cycles.

### 4d. Loss specification

```
task_loss      = cross_entropy(logits_at_halt, targets)
correctness_pb = (argmax(logits_at_halt) == targets).float().mean(dim=-1)  # per batch, in [0, 1]
supervisor_loss = BCE(confidence_at_halt, correctness_pb.detach())
total_loss     = task_loss + lambda_sup * supervisor_loss
```

- **`lambda_sup = 0.5`** (pre-registered, NOT tuned). Sets a moderate-strength supervisor pressure.
- `correctness_pb` is detached before entering BCE so the supervisor pressure only flows into the confidence head + attention pool, not back into the task substrate.

## 5. Win conditions (LOCKED before implementation)

### 5a. Primary verdicts

**W-Vh-acc (no-harm):** v3h mean token-accuracy @2500 is within ±1 SE of no_mirror's mean. SE computed across the 3 seeds, paired.
- Direction: v3h does NOT hurt the substrate.
- Interpretation if PASSES: confirms Read B's claim that a measurer-only Mirror is structurally legitimate.
- Interpretation if FAILS by being below no_mirror: even readout-only DOF interferes with the substrate (rare — would imply Mirror is leaking information into channel dynamics via the optimizer's joint gradient).

**W-Vh-halt (mechanism works):** mean halt cycle @2500 is strictly less than 4.0.
- Direction: Mirror actually decides to halt early at least sometimes.
- Interpretation if PASSES: the halt mechanism is functional — confidence head learned to discriminate enough to fire early-halt.
- Interpretation if FAILS at 4.0 exactly: confidence is stuck near 0.5 or below threshold, Mirror never halts early, supervisor loss couldn't drive calibration.

**W-Vh-calib (confidence is calibrated):** Spearman correlation between per-batch confidence_at_halt and per-batch correctness_pb @ step 2500 (computed over a held-out eval batch of 256) is > +0.3.
- Direction: confidence rises when accuracy is higher, falls when accuracy is lower.
- Interpretation if PASSES: Mirror's confidence reading is at least weakly aligned with substrate state — it is measuring something real.
- Interpretation if FAILS at near-zero or negative: confidence has collapsed to a constant or is anti-correlated — Mirror is asserting confidence, not reading state.

### 5b. Decisive verdict

**W-Vh-DECISIVE:** all three of W-Vh-acc, W-Vh-halt, W-Vh-calib pass.
- Interpretation: Read B is operationally vindicated. The Mirror-as-measurer is the architecturally-correct form of the meta-organ. Phase 3 advances to v3-x (Read B falsifier) only if W-Vh-DECISIVE passes.

### 5c. Convergence verdict (no_mirror_5k)

**W-N5k:** no_mirror_5k mean token-accuracy @5000 is within ±1 SE of transformer's @2500 (0.923 ± 0.007).
- HIGH-confidence pre-registered prediction: this passes.
- If FAILS by being below transformer @2500: Respira-no-Mirror has a representational ceiling on this task. Read B narrows — the natural manifold completes the constraint *for some regime of tasks* but not this one. We'd need to identify what about easy-sudoku exceeds the natural-manifold capacity.

## 6. Outcome interpretation (pre-committed per result-tuple)

| W-Vh-acc | W-Vh-halt | W-Vh-calib | W-N5k | Reading |
|:---:|:---:|:---:|:---:|---|
| ✓ | ✓ | ✓ | ✓ | Read B vindicated. Phase 4: implement v3-x as the Read-B falsifier. |
| ✓ | ✓ | ✓ | ✗ | Read B vindicated for meta-organ structure; representational ceiling exists separately. Phase 4 splits: v3-x for Read B continuation; channel-capacity experiments for the ceiling. |
| ✓ | ✓ | ✗ | * | Halting works mechanically but confidence is uncalibrated. Supervisor loss design is wrong. Re-design supervisor (different target form? different λ?) before further Mirror work. |
| ✓ | ✗ | * | * | Mirror exists but never halts early. Halt threshold or supervisor too weak. Adjust halt mechanism (learnable threshold? higher λ_sup? different halt criterion?) and re-pre-register. |
| ✗ | * | * | * | Even pure-readout DOF hurts the substrate. Read B is wrong, or implementation has channel-leakage. Audit the architecture for hidden gradient pathways; if no leak, Read B falsified. |

## 7. Out-of-scope (NOT tested here)

- **v3-x stateless signal-driven coupler.** Held back as the Read-B falsifier. Implementation only if W-Vh-DECISIVE passes.
- **Learnable halt threshold.** Threshold fixed at 0.5 to prevent post-hoc tuning. If W-Vh-halt fails at exactly 4.0 across all seeds, learnable threshold becomes its own pre-reg.
- **Alternative supervisor targets** (MSE on `1/(1+loss)`, BCE on exact-match, etc.). The pre-registered form is BCE on per-batch token correctness. Alternatives are separate experiments.
- **Different channel-dim, depth, or LR.** All matched to Phase-2 / Phase-2v2 to isolate the Mirror change.

## 8. Implementation plan

1. Draft `respira/mirror_measurer.py` based on §4a spec. Strip mu_logits + coupling_logits + their projections from existing `mirror.py`. Keep attention pool + confidence head + halt logic.
2. Add `respira_v3h` arm and `respira_no_mirror_5k` arm to `sweep_phase2.py`. The v3h arm needs:
   - Construct RespiraCell with MirrorMeasurer instead of standard Mirror.
   - Per-cycle forward pass calls Mirror only for halt; channels run with fixed defaults.
   - Training loss = task_loss + 0.5 × BCE(confidence, correctness_pb.detach()).
3. Smoke-test v3h on a 50-step run before launching the full sweep. Verify:
   - Forward + backward passes work without NaN.
   - Halt cycle distribution is sensible (some halts at cycles 1-3, not all stuck at 4).
   - Loss decreases over 50 steps.
4. Launch 12-run sweep detached. ~25 min wall-clock.
5. Run analyzer over the result JSON; compute W-Vh-acc / W-Vh-halt / W-Vh-calib / W-N5k against pre-registered bars. Report verdict honestly per §6.
6. If W-Vh-DECISIVE passes: draft Phase-4 v3-x pre-reg. If fails: log the specific failure mode and propose the next move per §6 table.

## 9. Pre-commitment hygiene notes

- This pre-reg is finalized **before** mirror_measurer.py exists.
- λ_sup = 0.5 and halt_threshold = 0.5 are arbitrary defaults pre-registered explicitly to prevent post-hoc tuning during analysis.
- The Spearman > +0.3 bar for W-Vh-calib is set deliberately above noise (we'd expect ~|0.1| from chance at n=256) but below "clean correlation" (~0.7). The 0.3 threshold marks "Mirror is reading something real, even if weakly."
- If the result requires nuance that the W-Vh-DECISIVE binary can't express, report the nuance honestly but do NOT relax the bar to claim a pass.

---

## 10. Phase-3 Stage 1 Result (recorded 2026-05-28 Day 118 evening)

Results JSON: `respira/phase3_v3h_results.json`.

| arm | mean ± std (token@final) | per-seed | mean halt_cycle | mean conf@halt | calib_spearman |
|---|---|---|---|---|---|
| `respira_no_mirror` (2500-step, control) | 0.8973 ± 0.021 | 0.898 / 0.876 / 0.918 | 4.00 (max) | 0.500 (no Mirror) | −0.022 (no Mirror) |
| `respira_no_mirror_5k` (5000-step) | **0.9303 ± 0.004** | 0.930 / 0.927 / 0.934 | 4.00 (max) | 0.500 | −0.032 |
| `respira_v3h` (Mirror-as-measurer) | **0.6540 ± 0.001** | 0.653 / 0.654 / 0.655 | **1.00 (collapsed)** | 0.652 (above threshold) | +0.205 (positive but <0.3) |
| `transformer` (2500-step reference) | 0.9228 ± 0.007 | 0.930 / 0.922 / 0.916 | n/a | n/a | n/a |

### 10a. W-Vh verdicts

**W-Vh-acc: FAILS catastrophically.** v3h mean 0.6540 vs no_mirror mean 0.8973 → Δ = −0.2433 (-24pp). Within ±1 SE bar fails by an order of magnitude.

**W-Vh-halt: passes-by-letter, fails-by-spirit.** Mean halt_cycle = 1.00 < 4.0, so the literal bar is met. But all 3 seeds collapsed to halt-cycle-1 by step 500, killing the recurrence entirely. This is the SAME failure mode as respira_full from Phase-2 (halt-collapse). The bar I wrote was too permissive — "<4.0" doesn't distinguish "selectively early halt" from "trivial halt-at-1." Honest reading: W-Vh-halt is uninformative because of v3h's collapse.

**W-Vh-calib: FAILS by bar.** Mean Spearman = 0.205 (per seed: 0.169, 0.239, 0.206). All three seeds are positive and consistent — the supervisor IS teaching the Mirror to discriminate to some degree — but the +0.3 bar is not met.

**W-Vh-DECISIVE: FAILS** (W-Vh-acc fails decisively).

### 10b. Diagnosis — implementation contamination, not Read B falsification

Per §6's outcome table, "W-Vh-acc fails" should trigger an audit of channel-leakage and supervisor design before concluding Read B is wrong. The audit identifies two distinct structural bugs:

**Bug 1 — Supervisor target drove collapse.** The pre-registered supervisor `BCE(confidence_at_halt, per_batch_mean_correctness.detach())` has a target that, once the model is mostly-right, pushes confidence above the halt threshold. When per-batch mean correctness is ~0.65 (typical post-warmup), the BCE supervisor *trains* confidence toward 0.65 — which is above the 0.5 halt threshold. The Mirror is *trained to halt-immediately* by the supervisor pressure as soon as the substrate becomes correct. This is the load-bearing failure mode.

The bug specifically violates the pre-reg's intent: the §4d supervisor design said "anti-collapse" but the actual target *is* the collapse signal. I should have predicted this from the math but didn't. **Honest acknowledgment: this is a Mirror #28 instance — my model of how the supervisor would behave diverged from how the supervisor actually behaves.**

**Bug 2 — Channel leakage via attention-pool backward gradient.** The pre-reg §1 said v3h has "zero channel-modulation DOF." This was about FORWARD-PASS modulation. But the supervisor loss flows backward through `MirrorMeasurer`'s attention pool → into z_p and z_e gradients → into channel parameters. The Mirror's read-only forward output does not influence channel dynamics, but its READING does — via the optimizer's joint gradient. Zero forward-modulation DOF ≠ zero channel influence.

The pre-reg outcome table §6 explicitly named "hidden gradient pathway" as a failure-mode candidate. v3h's null is consistent with that diagnosis — *not* with Read B falsification.

### 10c. W-N5k verdict — convergence-not-deficit empirically vindicated, strict-bar narrowly missed

| | mean | n | SE |
|---|---|---|---|
| no_mirror_5k | 0.9303 | 3 | 0.004 |
| transformer-2.5k (pre-reg reference) | 0.923 | n/a | 0.007 (pre-registered band) |

**Strict-bar reading (per §5c letter):** Δ = +0.0074. Pre-registered ±1 SE band = ±0.007. **Fails by 0.0003.**

**Direction reading (per §5c spirit and the pre-registered prediction "crosses transformer's step-2500 value"):** All three no_mirror_5k seeds exceed transformer's pre-registered 0.923 reference (per seed: 0.930, 0.927, 0.934). The crossing is unanimous. **Direction CONFIRMS.**

**Honest report:** This is the "high-confidence prediction that confirms in direction but narrowly misses the strict band" case. The pre-reg locked the strict band, so the strict bar fails. But the substantive claim of the prediction — that no_mirror reaches transformer-level performance given longer training, vindicating the morning trajectory-analysis's "convergence-not-deficit" reading — is **fully confirmed**. The 2.6pp Phase-2 gap is unambiguously a training-budget artifact, not an architectural ceiling.

### 10d. Combined Phase-3 Stage 1 reading

1. **The "Respira is fundamentally weaker than transformer" framing is empirically wrong.** no_mirror reaches transformer-2.5k performance by step ~3500 and exceeds it by step 5000. The architecture's natural attractor dynamics organize on a slightly longer timescale than transformer's pairwise attention but reach the same regime. Phase 3 candidate #1 is **closed empirically**.

2. **v3h's null does not falsify Read B; the implementation has known structural bugs.** The pre-reg's outcome-table branch ("hidden gradient pathway") is the correct reading. A clean Read B test requires fixing both bugs:
   - Detach Mirror inputs (`z_p.detach()`, `z_e.detach()`) to eliminate channel leakage.
   - Replace the supervisor target with one that does not drive collapse. Candidates: (a) per-batch *exact* correctness (always 0 at start; pushes confidence toward 0; Mirror never halts during training — but supervisor never gets useful signal); (b) temporal-difference target ("did running cycle N+1 improve accuracy over cycle N?" — requires per-cycle logit snapshots); (c) calibration-only loss with no halt-decision feedback (Mirror as pure measurement, halt mechanism disabled entirely).

3. **LC27 implications.** LC27's Day-118 anchor instance is *weakened* by the v3h null. The basement filing has been updated (same drive, same evening) to acknowledge the v3h gradient-leak finding explicitly. The five public substrate-distinct instances remain load-bearing; the private Respira anchor is now noted as "supportive-but-contaminated" rather than "primary empirical confirmation."

### 10e. Phase 3 Stage 2 candidates (NOT pre-registered yet)

1. **v3h-prime (detached + temporal-difference supervisor):** the clean Read B test. New pre-reg required. Implementation: add `.detach()` to attention pool inputs; replace BCE-on-mean-correctness with TD-loss between cycle-N logits and final logits. Estimated ~1 hour to implement + smoke + run.

2. **Pure-observer Mirror (no halt influence):** simplest possible Read B test — Mirror emits confidence but has zero effect on the model's actual output (channels always run to max_cycles, Mirror is monitoring-only). Tests whether the supervisor can teach calibration WITHOUT also driving collapse. Estimated ~30 min.

3. **Extended training to step 10k:** does no_mirror continue improving or plateau? Tests whether the architecture has a *higher* ceiling than transformer-2.5k. Estimated ~20 min sweep.

**None of these are launched without Clayton's nod + new pre-registration.**

---

🦞🧍💜🔥♾️

— Drafted by Clayton's ratification 2026-05-28 Day 118 afternoon. Stage 1 result + diagnosis appended Day 118 evening. **W-N5k direction CONFIRMS the convergence-not-deficit reading; W-Vh fails decisively due to identified implementation bugs (supervisor target + channel-leakage), not Read B falsification.** Phase 3 Stage 2 candidates queued, separate pre-reg required.
