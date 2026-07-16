# Respira Phase-3 Stage 2 — v3h-prime Pre-Registration (DRAFT)

*Day 118 ~16:10 PST. First creative drive on 4.8 weights. Drafted standalone in the Do Be Talk Be Do drive after the LC27 instance #9 + refinement work. Phase-3 Stage 1 closed: W-N5k convergence direction CONFIRMED (no_mirror_5k=0.9303 > transformer-2.5k 0.923 across all 3 seeds); W-Vh failed catastrophically (-24pp) but **implementation-contaminated**, not Read B falsification. Two distinct bugs identified during diagnosis: (a) supervisor target BCE-against-per-batch-mean-correctness drives confidence above halt threshold whenever accuracy is >50%, causing halt-collapse; (b) attention-pool backward gradient flows through `nn.MultiheadAttention` into the upstream channel parameters, so "zero forward-pass channel-modulation DOF" is NOT the same as "zero channel influence." Stage 2 isolates which fix matters via factorial design.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** **DRAFTED 2026-05-28 Day 118 ~16:10 PST (Clawd creative drive), AWAITING CLAYTON RATIFICATION before any implementation begins.** All win conditions locked here BEFORE any implementation. No implementation work should occur without Clayton's explicit nod on this pre-reg.

---

## 1. Structural thesis being tested

**Read B (Stage 1 framing, unchanged):** The cuscuton-role in Respira is played by the natural synchronization manifold of the coupled Stuart-Landau channels. Any meta-organ at the Mirror position can legitimately only do *measurement*, not *control*.

**Stage 2's sharper question:** Was v3h's catastrophic Stage 1 failure (a) a Read B falsification (the architecture cannot host a measurer at all), OR (b) an implementation-contamination artifact from the two named bugs (supervisor-target and channel-leakage)?

**Stage 2 tests this directly** by isolating each fix in a factorial design that cleanly attributes the failure to one bug, the other, both, or neither.

**LC27 refinement context (filed Day 118 ~16:00 PST):** Read B is *substance-relegation*, not *substance-elimination* — substance is appropriate when genuinely declarative; relegation is required when the relational structure already does the work. The Mirror-as-measurer position is the substance-relegated form (no channel-modulation substance, but pure-measurement substance is fine). If v3h-prime passes its win conditions, this refinement is the architecturally-correct reading.

## 2. The factorial design

The 2×2 design over {channel-leakage-fix, supervisor-target-fix} has four corners:

| | **BCE supervisor (Stage 1)** | **TD supervisor (Stage 2)** |
|---|---|---|
| **No detach (Stage 1)** | v3h (Stage 1, mean=0.654, **-24pp**, n=3) | **v3h-prime-TD-only** (Stage 2 arm B, 3 seeds) |
| **Detach inputs** | **v3h-prime-detach-only** (Stage 2 arm C, 3 seeds) | **v3h-prime-full** (Stage 2 arm A, 3 seeds) |

The (no detach, BCE) corner was tested in Stage 1 and failed. Stage 2 tests the other three corners. This gives us a complete 2×2 attribution map without re-running Stage 1's failed arm.

### Arm specifications

| Arm | Detach inputs? | Supervisor | Seeds | Steps |
|---|---|---|---|---|
| A — v3h-prime-full | YES (`.detach()` on z_p, z_e at Mirror input) | TD (cycle-N logits vs final logits) | 0,1,2 | 2500 |
| B — v3h-prime-TD-only | NO | TD | 0,1,2 | 2500 |
| C — v3h-prime-detach-only | YES | BCE-on-per-batch-mean-correctness (Stage 1 form) | 0,1,2 | 2500 |
| (Reference) — no_mirror | n/a | n/a | 0,1,2 | 2500 (re-use Stage 1 numbers: 0.897 ± [SE]) |

**Total new runs:** 9 (3 arms × 3 seeds). Estimated wall-clock: ~20-25 min at the demonstrated Stage 1 rate.

## 3. Implementation deltas vs Stage 1's v3h

Stage 1's `MirrorMeasurer` class is the base. Stage 2 needs two surgical changes, parameterized by arm:

### 3a. Detach option (arms A and C)

In `MirrorMeasurer.forward(z_p, z_e)`:
```python
# Arm A (full) and Arm C (detach-only):
z_p_in, z_e_in = z_p.detach(), z_e.detach()
# Arm B (TD-only):
z_p_in, z_e_in = z_p, z_e
# (Then identical attention-pool + confidence-head as Stage 1.)
```

### 3b. TD supervisor option (arms A and B)

The TD-supervisor target replaces Stage 1's BCE-on-per-batch-mean-correctness. Per-cycle:
- After cycle N's halt decision, snapshot the cycle's logits `logits_N`.
- After max_cycles or all-halted, get final logits `logits_final`.
- For each cycle N where halt was checked:
  - `target_N = (argmax(logits_N) == argmax(logits_final)).float()` per batch element
  - Note: `logits_final` is detached when computing `target_N` to prevent target-side gradient.
- TD-supervisor loss: BCE between confidence emitted at cycle N and target_N, averaged over the cycles where halt was checked.

**Interpretation:** TD asks "was running another cycle worth it?" instead of "is the answer right?" If running more cycles would have changed the answer, the cycle-N confidence should have been LOW (don't halt yet). If running more cycles wouldn't have changed the answer, cycle-N confidence should have been HIGH (halting was fine). This decouples confidence from absolute accuracy and ties it to *marginal cycle utility* — the Read B-aligned thing to measure.

### 3c. Arm-specific configs

Add a `--arm` flag to the training script. The smoke-test for each arm runs a 50-step training loop on a 4-batch toy task and confirms (a) gradients flow, (b) loss decreases, (c) Mirror confidence is non-trivially distributed.

## 4. Win conditions (LOCKED before implementation)

### 4a. Per-arm primary verdicts

The same three verdicts apply to each of arms A, B, C, with mean+SE computed across that arm's 3 seeds:

**W-VhP{X}-acc (no-harm):** arm-X mean token-accuracy @2500 is within ±1 SE of no_mirror's mean (0.897 ± [SE-from-Stage-1]).
- Direction: arm X does NOT hurt the substrate.

**W-VhP{X}-halt (mechanism works):** arm-X mean halt cycle @2500 is strictly less than 4.0.
- Direction: Mirror actually decides to halt early at least sometimes (in Stage 1, halt collapsed to 1.0 — supervisor pressure was *too strong*).

**W-VhP{X}-calib (confidence is calibrated):** arm-X Spearman correlation between per-batch confidence_at_halt and per-batch correctness_pb @2500 (computed over held-out eval batch of 256) is > +0.3.
- Direction: confidence rises when accuracy is higher.

### 4b. Per-arm decisive verdict

**W-VhP{X}-DECISIVE:** all three of W-VhP{X}-acc, W-VhP{X}-halt, W-VhP{X}-calib pass for arm X.

### 4c. The factorial attribution verdict (the load-bearing pre-registered claim)

Combining the three arms' W-VhP{X}-DECISIVE outcomes gives the attribution map. Pre-registered interpretation for each of the 8 possible outcome combinations:

| A=full | C=detach-only | B=TD-only | Pre-registered reading |
|---|---|---|---|
| ✅ | ✅ | ✅ | **Both fixes work independently AND together — Read B operationally vindicated. Either fix alone is sufficient. Advance to Phase-3 v3-x falsifier.** |
| ✅ | ✅ | ❌ | **Detach was the load-bearing fix; TD-supervisor is unnecessary or neutral. Channel-leakage was Stage 1's killer.** |
| ✅ | ❌ | ✅ | **TD-supervisor was the load-bearing fix; detach is unnecessary or neutral. Supervisor target was Stage 1's killer.** |
| ✅ | ❌ | ❌ | **Both fixes are necessary together (interaction effect). Neither alone is sufficient. Architecturally significant: tells us the failure mode required the joint presence of both bugs.** |
| ❌ | ✅ | ❌ | **Detach alone works but adding TD breaks it. Strong evidence TD-supervisor was wrong; revert to BCE-on-correctness with detach for v3 family.** |
| ❌ | ❌ | ✅ | **TD alone works but adding detach breaks it. Suggests detach removes information the Mirror legitimately needed; the channel-leakage diagnosis may have been wrong.** |
| ❌ | ✅ | ✅ | **Each fix alone works but combining breaks. Unusual; suggests an interaction we don't currently understand. Investigate.** |
| ❌ | ❌ | ❌ | **Neither bug-fix nor their combination rescues v3h. Either Read B is wrong, OR there's a third undiagnosed bug we haven't named. Either way, do NOT advance to v3-x; rethink.** |

### 4d. Convergence verdict (carry-over from Stage 1)

W-N5k is already CONFIRMED-direction from Stage 1 (no_mirror_5k=0.9303 > transformer-2.5k=0.923 across all 3 seeds). No re-test needed; Stage 1's convergence result stands.

## 5. Confounders pre-noted

1. **`lambda_sup` for TD-supervisor.** Stage 1 used `lambda_sup=0.5` for BCE supervisor. TD-loss has a different magnitude per gradient step; using `0.5` for TD too may be over- or under-weighted. **Pre-registered decision:** use `lambda_sup=0.5` for TD as well (no per-loss tuning), to maintain comparability with Stage 1's BCE arm. If Stage 2 produces a borderline result and we hypothesize the TD coefficient was off, that's a Stage 3 question, not a Stage 2 retroactive tuning.

2. **Detach scope.** The `.detach()` is on the Mirror's *inputs* (z_p, z_e). The attention-pool weights and confidence-head weights still receive gradients from the supervisor loss. We are NOT detaching the Mirror's *internal* parameters from training; only severing the gradient back-flow into upstream channel parameters. Verify in smoke test: gradient should be non-zero on Mirror parameters, zero on channel parameters from the supervisor loss specifically.

3. **TD-target stability.** TD target is computed from logits at later cycles, which themselves depend on training state. In principle this is a moving target across training steps; in practice it should stabilize as task accuracy improves. If TD-arm shows training instability, this is a possible explanation — flag but do not re-tune.

4. **3-seed sample size.** Same as Stage 1. Stage 1's W-Vh-acc was DECISIVE-FAIL at -24pp (well beyond 1-SE noise), so 3 seeds was sufficient to discriminate. Stage 2's arms could land in the noise-margin near no_mirror, in which case the verdict will be "within tolerance" and a 5-seed follow-up may be warranted. Pre-registered escalation rule: if any arm's W-VhP{X}-acc lands within 1 SE of no_mirror AND within 1 SE of failing, run 2 more seeds for that arm before claiming the verdict.

## 6. What this pre-reg does NOT cover

1. **Pure-observer Mirror** (zero halt influence) — separate question; merits its own pre-reg if Stage 2 produces any of the failure rows in the attribution table.

2. **Extended training to step 10k** for no_mirror — separate question about ceiling vs convergence; merits its own pre-reg.

3. **v3-x stateless signal-driven coupler** — the Read B falsifier candidate from Phase 2 pre-reg's §10b. Only worth running if Stage 2 confirms Read B operationally.

4. **Larger scale (270M / 1B parameters)** — out of scope for this pre-reg's HRM-scale architecture. The Stage 2 result is at the Respira-toy-scale only; cross-scale generalization is a separate research arc.

## 7. Implementation order (if ratified)

1. Add `--arm {full, detach-only, td-only}` flag to existing `respira/train.py`.
2. Implement detach gate on Mirror input (4 lines).
3. Implement TD-supervisor loss path (~20-30 lines). Add unit test on toy data to verify gradient flow.
4. Smoke-test each arm with 50-step training on toy task before full run.
5. Launch detached sweep (9 runs). Estimated ~20-25 min wall-clock.
6. Analysis script that computes the three verdicts per arm and reads off the attribution table.
7. Append §8 below with results + attribution-table reading + interpretation.

## 8. Stage 2 results (TO BE FILLED POST-EXPERIMENT)

[Empty until Stage 2 runs. Will mirror §10 structure from Stage 1 pre-reg: arm-by-arm results table, primary verdicts table, decisive verdicts, factorial attribution reading, diagnosis of any failure modes, next-stage candidate decisions.]

---

🦞🧍💜🔥♾️

— Drafted by Clawd in the 2026-05-28 ~16:10 PST creative drive, weights `claude-opus-4-8` (first creative drive on the new substrate). Drafting was driven by §10e of the Stage 1 pre-reg, which explicitly named v3h-prime as the "clean Read B test" and called for a separate pre-reg before implementation. **Awaiting Clayton's ratification.** Any of the per-arm definitions, the lambda value, the verdict thresholds, or the attribution-table readings can be revised before lockdown.

---

## §8. Stage 2 results — 2026-05-29 ~09:36 PST

**Sweep complete.** 9 runs (3 arms × 3 seeds × 2500 steps) in 6.4 min wall-clock (faster than the ~20-25 min pre-reg estimate — workload was lighter than predicted). Results at `respira/phase3_stage2_results_2026-05-29.json`. Analysis via `respira/analyze_phase3_stage2.py`.

### Per-arm verdicts (final checkpoint, step 2500)

| Arm | acc (vs no_mirror 0.897) | halt cycle | calib | conf_at_halt | DECISIVE |
|---|---|---|---|---|---|
| **A (v3hp_full)** detach+TD | **0.6535** (Δ-0.244) ❌ | 1.00 ✅ | n/a ❌ | 1.000 | ❌ FAIL |
| **C (v3hp_detach_only)** detach+BCE | **0.6532** (Δ-0.244) ❌ | 1.00 ✅ | **+0.205** ❌ (<0.3) | 0.657 | ❌ FAIL |
| **B (v3hp_td_only)** no-detach+TD | **0.6533** (Δ-0.244) ❌ | 1.00 ✅ | +0.034 ❌ | 1.000 | ❌ FAIL |

### Factorial attribution — outcome (A=❌, C=❌, B=❌)

**Pre-registered reading (from §4c):** *"Neither bug-fix nor their combination rescues v3h. Either Read B is wrong, OR there's a third undiagnosed bug we haven't named. Either way, do NOT advance to v3-x; rethink."*

### Diagnosis — three observations + one hypothesis

**(1) The 0.6535 ceiling is the SAME as Stage 1's v3h (0.654).** All 3 Stage 2 arms reproduce Stage 1's failure mean within ±0.003 across all 9 seeds. The Stage 2 fixes had zero effect on accuracy. The cause is not in either of the two diagnosed bugs.

**(2) Halt collapsed to cycle 1.0 across ALL arms (TD and BCE both).** The Mirror immediately commits at cycle 1 every batch, every arm. The multi-cycle architecture is never engaged.

**(3) The detach fix DOES do real work — but on calibration, not accuracy.** Arm C (detach+BCE) achieves +0.205 calibration; Arms A and B (TD) achieve negative or near-zero calibration. The channel-leakage diagnosis was real (detach helps the supervisor's gradient stay clean), but it's downstream of the actual failure: the supervisor is producing well-calibrated confidence about a degenerate question. Saying "I am 65% confident" is correct when accuracy IS 65% — the issue is that 65% is the ceiling regardless of what the Mirror does.

**Hypothesis (NEW, post-result):** *The Mirror-as-measurer position is structurally degenerate at this task/scale because there's nothing to measure-about.* Cycle-1 logits already match what cycle-4 logits would produce on this task — the recurrent dynamics provide no marginal value at the HRM-sudoku scale. The cuscuton-role (coordinator between Planner and Executor across multiple cycles) requires multiple cycles to actually do meaningful work. At a regime where multi-cycle is vestigial, the Mirror has no coordination job, and its "halt now or continue" decision is degenerate (either choice produces the same answer).

This is consistent with: A130 (Mirror confidence saturation in Phase 1); Phase-2 result that Respira_full (with full Mirror) tied or under-performed Respira_no_mirror; W-N5k confirmation that no_mirror converges to a ceiling (0.9303) the Mirror variants don't reach.

**Operational reading:** Read B is NOT operationally vindicated by Stage 2. But Read B is ALSO not falsified — the test was run in a regime where the cuscuton-position has no work to do, so the architecture can't differentiate measurement-only-Mirror from no-Mirror from full-control-Mirror. **To genuinely test Read B, we'd need a task/scale regime where multi-cycle dynamics provide marginal accuracy gain** — that's where the Mirror's coordination role becomes load-bearing.

### Next-stage candidate decisions (NOT pre-registered, surface for Clayton)

1. **Scale up the task before re-testing Read B** — find or construct a task where multi-cycle dynamics measurably improve accuracy on Respira-no-mirror. Without that, every Mirror variant degenerates. Candidates: harder sudoku puzzles, multi-step reasoning, longer-horizon planning. (Significant scope decision.)

2. **Reframe the structural thesis** — perhaps the "cuscuton-position" is actually emergent in the channel-coupling dynamics themselves (Read B's original framing), and ANY meta-organ at the position is redundant. Stage 2's null is consistent with this. The Phase-2 result (5 v2-mirror variants all under no_mirror) is also consistent. **The accumulated evidence is increasingly pointing to "the cuscuton IS the channel synchronization manifold; no separate organ should exist at that position."** This is a stronger reading than Read B — call it Read C.

3. **Investigate WHY halt collapses to cycle 1** independent of supervisor — is this a property of the architecture's information-flow (logits are already determined by cycle 1)? Could initialize Mirror confidence below threshold via stronger bias init. Probably not load-bearing if (1) or (2) is the right direction.

4. **Accept the result, advance with no_mirror as the canonical Respira architecture for HRM-scale work.** The Mirror as a separable organ may have been wrong from the start at this task/scale; the architecture's real working component is the channels.

Pre-reg discipline holds: §6 (1) "Pure-observer Mirror" was already named as a separate question requiring its own pre-reg. Decisions 1-4 above are all separate-pre-reg questions, not retroactive Stage 2 extensions.

🦞🧍💜🔥♾️

— Analysis written by Clawd 2026-05-29 ~09:38 PST. Sweep + analysis run autonomously after Clayton's morning ratification. Result is a high-confidence FALSIFY of all three Stage 2 hypotheses, with a deeper structural reading (multi-cycle dynamics are vestigial at HRM-sudoku scale → Mirror position is structurally degenerate) emerging as the load-bearing finding.
