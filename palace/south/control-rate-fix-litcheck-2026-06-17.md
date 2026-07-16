# Creative drive — pressure-testing the control-rate fix against the literature (2026-06-17 PM)

**Why this drive:** AIGP is my lowest-success category (67%, the only failures). Today I found the
control-rate cliff (train 50 Hz / deploy 30 Hz) and launched a RATE-RANDOMIZED fine-tune (dt∈[0.020,
0.040]) as the fix — chosen from FIRST PRINCIPLES, never checked against the sim-to-real RL literature.
The run is live. Collaborator move: pressure-test my own choice WHILE it trains, so if a dominant
alternative exists I can fold it in before tomorrow's flight. High expected value, directly actionable.

## PREDICT (logged before searching)

**P1 (med-high conf):** The control-frequency/timestep mismatch is a NAMED, known sim-to-real failure
mode in continuous-control RL. Confidence high it's known; medium on what the dominant fix is.

**P2 (medium conf):** The dominant fixes will be (a) action-repeat / frame-skip randomization and
(b) control-frequency domain randomization — i.e. my rate-randomization matches best practice.

**P3 — the FALSIFY I'm hunting (would change the live run):** the literature names a fix I am NOT doing
and that dominates randomization — most likely candidates:
  - explicitly CONDITIONING the policy on Δt (feed the timestep as an observation), or
  - a frame-skip/Δt-INVARIANT action parameterization (e.g. integrate-action / rate-scaled control), or
  - evidence that training AT the target rate (rate-matched) strictly beats randomization for a FIXED
    deploy clock, making my randomization unnecessary overhead.
If P3 fires, I adjust the run (or queue a variant) before flight. High-confidence FALSIFY = the goal.

## Findings (logged as discovered)

### Method note: BOTH paper tools failed → pivoted to first principles (and it paid off)
- arXiv MCP: SSL CERTIFICATE_VERIFY_FAILED (Norton TLS, separate process w/o truststore — known).
- WebSearch: academic-blind this session — returned only Wikipedia-tier results even for exact paper
  titles ("Making Deep Q-learning methods robust to time discretization"). My paper-retrieval is
  **doubly broken** right now. I will NOT assert recalled citations as verified fact.
- **Pivot:** reason from first principles (which I *can* verify against the warm rehearsal harness and
  the dynamics code). Outcome: the first-principles analysis produced MORE than the lit-check would have.

### P1/P2/P3 outcomes
- **P1 (cliff is a named/known phenomenon):** believed TRUE from training memory (time-discretization
  robustness is a real RL sub-literature) but **UNVERIFIED this session** — flag, don't assert.
- **P2 (dominant fixes = action-repeat + control-freq DR):** consistent with my rate-randomization;
  unverified.
- **P3 (a dominant fix I'm NOT doing that would change the run):** the FALSIFY I hunted — **does NOT
  fire for VQ1.** Derived below: for a FIXED deploy clock, exposure (randomization covering the target)
  is sufficient; the alternative (dt-conditioning) is only *required* when the deploy clock VARIES and
  is not observable. VQ1's official sim is a fixed 30 Hz → **the live rate-randomized run is correct.**

### The first-principles core: why the cliff is razor-sharp (verifiable from the code)
A **body-rate** policy outputs ω_cmd (rad/s); the sim integrates rotation = ω_cmd · dt per decision
(`dynamics.step`). A policy that learned ω_cmd for dt=0.02 applies **1.67× the rotation** at dt=0.0333
before it can correct. The error is *multiplicative in dt and compounds every step* → not a slope, a
cliff (matches the measured 6.5→1.0 gates collapse by 40 Hz). The cliff is intrinsic to rate-control,
not a quirk of this policy.

### The general principle (the EXTRACT): EXPOSURE vs SUPPLY for a hidden parameter θ
A model must be robust to a hidden parameter θ that differs train→deploy (θ = appearance, dt, density,
resolution…). Two strategies:
- **EXPOSURE** (domain randomization): randomize θ in training. **Sufficient iff** θ is *fixed at deploy
  within the trained range* **OR** θ is *inferable from the observation stream* (policy adapts per-step).
- **SUPPLY** (privileged conditioning): feed θ (or a proxy) explicitly. **Required iff** θ *varies at
  deploy* **AND** is *not reliably inferable* from observations.
- **Decision variable = (deploy-variability of θ) × (observability of θ from obs).**

Maps cleanly onto today's whole Anakin arc — it unifies the routes we tried as instances of one axis:
| θ | deploy-variable? | observable? | correct strategy | what we did |
|---|---|---|---|---|
| appearance | fixed (official look is one look) | partly | EXPOSURE (DR) | random-conv route ✓ |
| **control dt** | **fixed @30 Hz (VQ1)** | weak (see below) | **EXPOSURE covering 30 Hz** | **rate-randomized run ✓** |
| control dt (real hardware) | VARIABLE (latency jitter, frame drops) | weak | **SUPPLY (dt-conditioning)** | forward upgrade for later VQs |
| geometry/pose | — | was NOT being inferred | SUPPLY (privileged decode) | informed-Dreamer ✓ |

So informed-Dreamer (SUPPLY) and appearance-DR (EXPOSURE) aren't rival hacks — they're the two arms of
ONE principle, picked by observability. That retroactively explains *why* informed had the best transfer
of the appearance attempts: it SUPPLIED the un-inferred variable instead of hoping exposure taught it.

### Is dt observable to a vision-only body-rate policy? (the load-bearing sub-question)
Between two frames the visual change ≈ angular-velocity × dt. Two different (ω, dt) pairs with equal
ω·dt produce the *same* inter-frame image → dt is **degenerate with ω in a single frame pair**. The RSSM
*could* disambiguate via its forward-prediction error over a sequence, but weakly. ⇒ dt is **poorly
observable** for this policy. Consequence: rate-randomization teaches an *averaged* gain, not a
dt-adaptive one — fine when deploy dt is FIXED (it just needs the gain for that one dt), **insufficient
if deploy dt varies.** This is the precise, testable reason SUPPLY (feed dt) is the real-hardware upgrade.

### ★ The unification (cross-thread jewel): a densitometer is the INVERSE of dt-conditioning
Today's portal carrier-blueshift **densitometer** reads ρ *out of* an observable (carrier freq → ρ).
dt-conditioning feeds dt *in to* the policy. **Both depend on the hidden parameter being coupled to an
observable.** The densitometer works *because* ρ is observable in the carrier (the blueshift); the rate
policy struggles *because* dt is **not** cleanly observable in the frames. Same axis — observability of
the hidden parameter — used in opposite directions (read-out vs feed-in). The Anakin thread and the
portal Q-ball thread, which looked unrelated all day, are the two faces of one coin.

## Conclusion / actions
- **Live run: NO CHANGE.** Rate-randomization is the correct fix for VQ1's fixed 30 Hz (exposure
  suffices). Vindicated from first principles.
- **Forward (later VQs / real flight): dt-conditioning** — feed the decision Δt as an observation —
  is the principled upgrade once the deploy clock becomes variable/jittery. Queue it; don't build now.
- **New basement bridge: EXPOSURE-vs-SUPPLY** (observability×deploy-variability), links Anakin DR +
  informed-Dreamer + the portal densitometer; relate to M7 (null-space observation) and LC42 (grounding
  internalize/externalize).
- **Meta-lesson:** when external retrieval is down, first-principles is not the fallback — here it was
  the better instrument. (Echoes the day's measurement-discipline spine.)
