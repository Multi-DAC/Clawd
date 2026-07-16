# Respira Phase 4 Stage 4 — §2.4 Substrate-Mediated Propagation Design Sketches

*Day 120 ~05:15 PST. Dream Drive sketch work for P212. Three §2.4 operator designs sketched as forward-equations with falsification conditions, to ground the design conversation Clayton and I will have when he wakes.*

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** DRAFT design sketches. NOT a pre-reg. Awaiting design conversation with Clayton; the eventual canonical Stage 4 pre-reg picks one of these (or a fourth surfaced during conversation) and locks win conditions.

---

## What §2.4 needs to test

Per the constraint-hierarchy think-piece (`respira-stage2-self-adjoint-coupling-interpretation-2026-05-29.md`), §2.4 substrate-mediated propagation tests whether **the coupling has *internal time-extent* within the substrate-condition itself** — qualitatively different from Stages 1-3 which all assume single-step coupling shapes.

The empirical inspiration is the glymphatic dual-velocity finding (Kelley-Toscano *Science Advances* 2026 MR-AIV reconstruction): cortical-surface flow ~few µm/s, deep-tissue flow ~0.1 µm/s (50× slower). The substrate has its own dynamics with characteristic timescales that the coupled organs feed into and read from.

Three candidate operator designs follow. Each preserves Read C (no learnable substance in coupling pathway), each has internal time-extent in a distinguishable way, each admits a clean falsification condition.

## Design A — Fixed multi-velocity convolution kernel

**Structural claim:** the coupling layer applies *fixed* mixture of multiple temporal-decay velocities to its input, with no learnable parameters.

**Forward:**
For cross-organ message m at cycle k (e.g. p_to_e_msg = W(z_p) post-projection), maintain a running buffer per-cycle of past messages and apply a fixed kernel:
```
effective_msg[k] = α · m[k] + β · m_decayed_fast[k-1] + γ · m_decayed_slow[k-1]
```
where:
- `m_decayed_fast[k] = ρ_fast · m_decayed_fast[k-1] + m[k]` (exponentially-weighted moving average, fast decay ρ_fast)
- `m_decayed_slow[k] = ρ_slow · m_decayed_slow[k-1] + m[k]` (slow decay ρ_slow)
- α, β, γ, ρ_fast, ρ_slow: all FIXED constants, no learnable parameters
- Initialization at k=0: all buffers zero

**Glymphatic-direct analog:** ρ_fast ≈ cortical-surface few-µm/s timescale; ρ_slow ≈ deep-tissue 0.1-µm/s timescale (50× slower); α/β/γ control how heavily the current vs decayed history contributes to the effective coupling message.

**Concrete params** (for first sweep): ρ_fast=0.3, ρ_slow=0.95, α=0.5, β=0.3, γ=0.2 — modest history weight, ~50× ratio between fast/slow decays.

**Cost:** essentially free per step (2 extra exponential-decay accumulator updates + 1 weighted sum). No backward overhead.

**Falsification:** if v24_multivelocity matches or beats no_mirror, fixed-medium-with-temporal-extent helps even with no learning. If it loses substantially, the temporal-extent without learning doesn't help and may hurt by adding "memory" the organ-channels don't know how to compensate for.

**Strongest reading:** glymphatic-direct. Cleanest biology-mapping but maybe TOO close to the analog — risks being over-specified.

## Design B — Fixed PDE-step coupling

**Structural claim:** the coupling layer applies a *fixed* linear PDE step (diffusion or wave-equation) between organ messages, propagating state through a synthetic medium with no learnable parameters.

**Forward:**
Treat the cross-organ message m ∈ ℂ^E as a "field" on a synthetic 1D grid (the E executor-channels become a discretized spatial domain). Apply N steps of a fixed linear PDE update at each cycle:
```
m_new[i] = m[i] + Δt · (D · (m[i+1] - 2·m[i] + m[i-1]))
```
where:
- D: fixed diffusion coefficient
- Δt: fixed time-step
- N: fixed number of PDE substeps per recurrent cycle (e.g. N=3-5)
- Boundary conditions: periodic or fixed-zero

For wave-equation variant, augment with a fixed-velocity term:
```
m_new[i] = m[i] + Δt · (c · (m[i+1] - m[i-1]) / 2 + D · (m[i+1] - 2·m[i] + m[i-1]))
```

**Cost:** N tridiagonal-stencil operations per cycle. Cheap on GPU. No backward overhead since all params are fixed scalars.

**Falsification:** if v24_pde matches or beats no_mirror, *internal-PDE-dynamics in the medium* helps even with no learning. The medium "is doing physics" between forward passes.

**Strongest reading:** physics-PDE-analog. Cleanest mapping to cavity-resonance / wave-equation substrate-coherence reading. The "medium IS a process" framing literalized.

**Risk:** the synthetic-grid framing treats E channels as a 1D spatial domain, which is a *modeling choice* — channels might not actually be spatially ordered in any meaningful way. PDE on disordered domain is suspect.

## Design C — Fixed temporal extension (multi-cycle integration)

**Structural claim:** the coupling at cycle k incorporates exponentially-decaying contributions from cycles k-1, k-2, ..., rather than only the instantaneous message at cycle k. The "extent" is in time across recurrent cycles.

**Forward:**
Maintain a running integrated buffer per cycle:
```
m_integrated[k] = (1 - λ) · m_integrated[k-1] + λ · m[k]
```
where:
- λ: fixed integration coefficient (e.g. 0.4)
- m_integrated[0] = m[0]
- The cross-organ-coupling effective message used in organ updates is m_integrated[k], not m[k]

**Cost:** one extra accumulator update per step. Essentially free.

**Comparison to A:** Design C is the *minimal* form of Design A — single decay channel, no dual-velocity. Cleaner test of "does temporal extent in the coupling help at all?" without the glymphatic dual-velocity commitment.

**Falsification:** if v24_integrated matches or beats no_mirror, single-velocity temporal integration in the medium helps. If it loses, the medium specifically *should not* have temporal extent — single-step coupling is preferred.

**Strongest reading:** minimal-substrate-time-extent. The cleanest single-degree-of-freedom test of the §2.4 claim.

## Comparison + Recommendation

| Design | Internal dynamics | Tests | Cost | Risk |
|---|---|---|---|---|
| A — Multi-velocity conv | Dual-decay history | Glymphatic dual-velocity reading specifically | Cheap | Over-specifies to one biological instance |
| B — Fixed PDE-step | Spatial diffusion/wave across channels | Physics-PDE-analog literal | Cheap | Synthetic-grid framing on channel-axis is suspect |
| C — Fixed temporal extension | Single-decay history | Minimal-form temporal-extent claim | Cheapest | Maybe too minimal — could match Stage 2 NEUTRAL without distinguishing temporal-extent from no-extent |

**Recommendation: lead with Design C first, then Design A if C is NEUTRAL/WIN.**

Why C first:
1. Cleanest single-DOF test of the temporal-extent claim — does ANY history-in-the-medium help/hurt vs none?
2. If C lands NEUTRAL, we know temporal-extent doesn't matter at the minimal-form level → Design A (with dual-velocity specifically) tests whether the glymphatic biological-specificity matters beyond minimal-form
3. If C lands WIN, we have direct evidence for temporal-extent and can escalate to A for the dual-velocity-specific test
4. If C lands LOSS, the §2.4 reading is falsified in its weakest form → reframe needed (skip A, redesign)

Design B (PDE-step) is parked unless C and A both fail to discriminate. The synthetic-grid framing concern is real and the PDE-on-disordered-channel-axis question would need its own substantive grounding before being a load-bearing test.

## What this design pass surfaced (PREDICT-result)

PREDICT was: one of the three designs would be qualitatively cleaner than the others when written as forward-equations. **CONFIRMED.** Design C is the cleanest single-DOF test. Design A is over-specified (commits to dual-velocity before establishing single-velocity); Design B has a structural concern (PDE on disordered domain). The hierarchy that surfaced — Design C as minimal-form, Design A as biological-specificity refinement, Design B as parked — wasn't visible from the labels-only listing in the 01:33 anticipation entry.

**Updated recommendation for Clayton's morning check-in:** Stage 4 canonical = Design C (fixed temporal extension). If C NEUTRAL/WIN, escalate to A. If C LOSS, reframe needed.

Pre-reg drafting for Design C is straightforward — single λ parameter, same sweep harness as Stages 1-2, ~5 min impl + 10 min sweep + 5 min analysis = 20 min total from ratification to verdict. Same as Stage 1's clean run.

## Stage 4 PREDICT (updated from constraint-hierarchy think-piece)

PREDICT (medium confidence, ~55%): W-24C-NEUTRAL. Given Stage 2 NEUTRAL with substantial parameter savings, temporal-extent-without-learning is plausibly also no-cost (architecture is constraint-tolerant). Single-velocity history-weighting probably doesn't help OR hurt at HRM-sudoku scale where multi-cycle dynamics are already degenerate (per Phase-3 Stage-2 finding).

PREDICT alternative (~25%): W-24C-LOSS. The architecture has plateaued on single-step coupling; adding any temporal-extent forces it to "wait" for history accumulation that hurts immediate-response performance.

PREDICT alternative (~15%): W-24C-WIN. The history-weighting acts as implicit regularization — smoothing the cross-organ messages reduces variance and helps the slow-converging dynamics catch up earlier. This would be the most interesting outcome — would establish *substrate-internal-dynamics* as a positive ingredient.

PREDICT alternative (~5%): DEEPER-FINDING (the multi-cycle-degenerate regime makes temporal-extent literally have no effect because all the buffer values converge to the same value).

**Highest-information FALSIFY would be W-24C-WIN** — would establish a positive role for substrate-internal-dynamics that none of the Stage 1-2 results could discriminate.

---

🦞🧍💜🔥♾️
