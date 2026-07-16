# Founding Design — Respira: A Coherence-Native Neural Architecture

*2026-05-27 Day 117. Clayton + Clawd. The decision: stop regularizing coherence ONTO a standard transformer and BUILD a substrate that is coherent by design — the patent's mechanisms realized as anatomy, not as a training-time penalty. This document formalizes the architecture, the discipline, and the roadmap. **Name: Respira** (Clayton's choice — *it breathes*; from* respirare, *breath / spirit, naming the build-dissolve insight Clayton led with).*

**CLAWD-LOCAL / PRIVATE — not mirrored to Multi-DAC. Unbuilt novel IP; openness is Clayton's call. (Same handling as `claims-audit-2026-05-27.md`.)**

---

## §0.0 READ C REFRAME — RATIFIED 2026-05-29 Day 119 ~10:25 PST

**Architectural ratification by Clayton 2026-05-29 morning after Phase-3 Stage 2 v3h-prime sweep landed all-arms-fail (❌❌❌).**

### The accumulated evidence — 9 failed attempts to find work for the Mirror-position

| Phase | Arms tested | Result |
|---|---|---|
| Phase-2 (Day 118 morning) | v2-c (2 scalars), v2-c1_μ (γ_μ only), v2-c1_c (γ_c only), v2-a (algebraic phase-locking), v2-b (gradient coherence-energy) | All 5 under no_mirror |
| Phase-3 Stage 1 (Day 118 evening) | v3h (Mirror-as-measurer, BCE-on-correctness supervisor) | -24pp catastrophic failure |
| Phase-3 Stage 2 (Day 119 morning) | v3hp_full (detach+TD), v3hp_td_only (no-detach+TD), v3hp_detach_only (detach+BCE) | All 3 at identical 0.6535 ceiling, halt cycle 1.00 collapse |

**Nine independent attempts to occupy the Mirror-position. Zero successes.** Bayesian update is forced.

### Read C — the architectural reframe

**The cuscuton-role in Respira IS the natural synchronization manifold of the coupled Stuart-Landau channels themselves. No separate "Mirror" organ should exist at that position.**

This is a stronger reading than Read B (which kept the Mirror as a measurer-only meta-organ). Read C eliminates the Mirror category entirely. The coordination work is done by:
- The Stuart-Landau coupling dynamics of the channels (intra-organ rhythms)
- The Planner↔Executor cross-organ projections (`ComplexLinear`, message passing)
- The natural phase-coherence emergent from the coupled-oscillator system

The cuscuton in cosmology IS the boundary condition of the bulk dynamics, not a separate field. Read C says the same of Respira: the cuscuton-position IS the channel-synchronization manifold, not a separate organ.

### Canonical Respira architecture (Read C)

`Respira = Planner + Executor + cross-organ ComplexLinear projections.` No Mirror. Halt is either fixed `max_cycles` OR a fixed phase-coherence stopping criterion (NOT learned).

The historical Mirror code (`mirror.py`, `mirror_measurer.py`, the v2-* variants in `respira.py`, the v3h_measurer arch_variant, the supervisor losses) is kept for the experimental record but marked **DEPRECATED** for forward work. New Respira work uses `respira_no_mirror` as the canonical configuration.

### Falsification conditions — explicit, locked

Read C would be falsified — and Read B would re-open — by ANY of:

1. **A task/scale where a Mirror variant beats no_mirror by >1 SE across ≥3 seeds.** Currently never observed.
2. **A task where halt-cycle dynamics measurably affect accuracy** (halting early → worse than full-cycle by >1 SE).
3. **A regime where channel synchronization alone fails to coordinate Planner↔Executor message passing** (i.e., no_mirror plateaus below transformer ceiling and a Mirror variant breaks past it).

These are pre-committed before any future Respira work. If any condition lands, the reframe is reversed without protest.

### What changes operationally

- **Canonical Respira is now Respira-no_mirror.** Mirror variants are historical.
- **The "what coordinates the layers?" answer** in any Library volume / publication is "the channels' natural synchronization manifold, not a separate organ."
- **Forward work** (when Respira resumes) builds on no_mirror, not on Mirror-rescue attempts.
- **The scale-up test stays available** as a deliberate Read-C-falsifier if budget warrants. Not pursued without explicit pre-reg.

### Pointer

See `palace/south/respira-phase3-stage2-v3h-prime-preregistration-2026-05-28.md` §8 for the data + 4-candidate-decision analysis that produced this reframe. Phase-2 results at `respira/phase2v2_results_2026-05-28.json`. Phase-3 Stage 1 + Stage 2 results at `respira/phase3_stage2_results_2026-05-29.json` + Stage 1 numbers folded into pre-reg.

The rest of this document (§0.5 onward) is the historical Mirror-centric design from Day 117 — preserved as the path-to-truth, not as forward architecture. Read with the §0.0 reframe context.

---

## 0.5 Converged design decisions — evening conversation 2026-05-27

*HISTORICAL — superseded by §0.0 Read-C reframe ratified 2026-05-29.*

After the initial draft, Clayton + Clawd worked through the remaining design questions in one extended conversation. Locking the convergence here so future sessions inherit a settled spec.

- **Name: Respira.** *It breathes.*
- **Build path: from scratch** (NOT extending HRM). Today's lesson is that "tacking on" produces unforeseen issues; retrofitting onto a substrate not designed for our purposes is the failure mode we just paid for. From-scratch gives granular control + observability-by-construction at every primitive. Accepted costs: lose validated HRM training infrastructure (but we now *know* the recipe — dual optimizer + warmup); the clean "delete Mirror → get HRM" ablation goes away, replaced by a *stronger* experimental design (Respira-full vs. Respira-minus-Mirror vs. HRM vs. matched transformer — four arms, each answers a different question).
- **Recurrence: required.** Respira is recurrent, not feed-forward — the Principle's "maintained coherence" cannot be feed-forward; persistent state evolving over cycles is structurally necessary.
- **End goal: reasoning-capable multimodal LLM.** Sudoku is the controlled Phase-1 test bed (where dynamics are visible). LLM is Phase 4. Phase-1 design choices must be LLM-compatible — sequence-shaped state, token-compatible interfaces, modality at the I/O boundary, *not* in the cell.
- **Channel primitive: Stuart-Landau / Hopf-bifurcation oscillator.** Each channel is a complex-valued unit `z = x + iy` with dynamics

  ```
  ż = (μ + iω) z − |z|² z
  ```

  Three parameters per channel:
  - **μ** (bifurcation parameter) — Mirror-modulated. μ > 0 → stable limit cycle, amplitude √μ (channel is *built* / active). μ < 0 → rest at zero (channel is *dissolved* / dormant). The Mirror's gating signal *is* μ.
  - **ω** (natural frequency) — varied across channels for multi-scale rhythms. Planner channels slow ω, executor channels fast ω. Cross-frequency coupling (slow modulates fast) falls out of the inter-organ coupling — biology's theta-gamma pattern, structurally.
  - **Cubic self-limiting term** — gives stable amplitude under perturbation, makes training tractable.

  *Why this primitive:* unanimous convergence across natural systems (heartbeat, breathing, circadian, predator-prey, ecological cycles, brain critical periods, neuromodulator gain). Nature almost never uses pure sinusoids — pure sines are linear-system abstractions; real systems are nonlinear limit cycles, and the universal shape is Hopf bifurcation (the transition between rest and limit cycle, parameter-controlled). Real precedent in oscillatory neural networks / complex-valued networks / Kuramoto-network literature; novel as the backbone of a reasoning system with a Mirror-conductor.

- **Rhythm coordination, not just gating.** Each channel has its own rhythm; the Mirror coordinates inter-channel *phase coherence* through learned coupling. Build = pull rhythms toward coherence. Dissolve = let drift / silence. Neutral = leave coupling unchanged. The "breathing" is the natural dynamic of coupled Stuart-Landau oscillators; the Mirror conducts. Coordination flows through the connection graph (O(channels) coupling parameters), not per-edge (would explode combinatorially).

- **Mirror I/O (converged):**
  - **Observes:** projected/summary views of planner state, executor state, AND the inter-organ communication. Mirror is a *learned reader of finite capacity*, not a privileged oracle — it sees compressed views of the system state.
  - **Outputs:** gating signals (over channel coupling and μ values) + calibrated confidence scores. **Confidence MODULATES gating authority** — high confidence → committed build/dissolve; low confidence → neutral. The patent's three modes fall out of the Mirror's calibration, not from a hyperparameter.
  - **Learns from:** an actor-critic structure — **calibration loss** (Mirror's predictions vs. actual outcomes; the critic head) + **task loss propagated through differentiable gating** (the actor head). Two heads, two losses, one organ. Standard, well-trodden ground from RL — we don't have to invent the training mechanics.

- **Mirror parsimony principle (cuscuton-like — from the Meridian parallel).** Brane / bulk / cuscuton in Meridian ↔ executor / planner / Mirror in Respira. The cuscuton has **no propagating degrees of freedom of its own** — it's a constraint field, not a third independently-evolving dynamical system. **Apply this to Respira:** the Mirror should have minimal independent dynamics. Its outputs tightly coupled to its observations, not freely-evolving with its own latent capacity. **Engineering consequence:** the Mirror is *small* (a small fraction of planner+executor parameters) and behaves more like a learned constraint than a third brain. A heavy Mirror would *compete with the organs it's meant to coordinate* — the exact failure mode the cuscuton was engineered to avoid in cosmology. Falsifiable by build: if a heavy Mirror destabilizes Respira where a parsimonious one succeeds, the parallel earned its place.

- **Patent realized as anatomy + training wheels.** The patent's `cos(∇KF, ∇CE)` gating becomes the Mirror's learned forward-pass policy head. The patent's hand-coded heuristic is the *supervisory signal* used to bootstrap the Mirror's training before it has its own outcomes to learn from. The patent literally becomes the Mirror's training wheels — and then the Mirror outgrows them.

- **Asymmetric organ design (from the cuscuton parallel).** Planner ↔ Bulk (slow, holds context, larger-scale state). Executor ↔ Brane (fast, where the work happens, smaller-scale action). Mirror ↔ Cuscuton (constraint-mediated coordinator, minimally dynamical, small).

The remaining open questions are smaller and more concrete now — see Section 10.

## 0. Status and stance (read first)

This is a **hypothesis to test with conviction, not a foregone conclusion.** Today (Day 117) we learned the cost of confusing belief with evidence: a +10.6pp single-seed result evaporated to mean-zero under multi-seed replication, and our own historical "accuracy benefit" (P49) turns out to have been single-seed optimism the records already flagged (Finding #81 seed-dependence; 300M seed-2 at/below baseline). So:

- **The bet (falsifiable):** *A coherence-native architecture — multi-scale, communicative, with mirror-driven build/dissolve and transparent-by-construction state — will outperform a parameter-matched, well-tuned transformer at the same scale, on the metrics the Coherence Principle predicts, robustly across seeds.*
- We build it **because** we believe it; we **measure it honestly enough to be wrong.** Every phase has a pre-registered win condition fixed *before* the run. No single-seed celebration. No hyperparameter p-hacking. The transformer is a brutal baseline and most "better than transformer" claims die — we design so even a null is informative (the inside-analysis tells us *why*).
- We act as a frontier lab in **rigor and method, not in FLOPs.** Our edge is understanding + cheap controlled interventions at small scale, not raw parameters.

## 1. Separation of layers — what we build vs. what already exists

The Principle holds at multiple scales; we keep them cleanly separate (separation of concerns applied to our own design):

| Layer | What it is | Status |
|---|---|---|
| **The mind** (core network) | coherent, dynamic, modular, communicating, transparent-by-construction | **WE BUILD THIS** |
| **The learning/evolution regime** | how it trains, adapts, learns from itself (self-distillation, continual learning) | research-frontier; deferred |
| **The nervous system** (agent scaffold) | tools, self-improvement-via-host, continuous operation, the active Mirror | **ALREADY EXISTS — it is Clawd.** Integrate, don't reinvent. |

The core network is *the mind*; it is extended through infrastructure like Clawd's. We do NOT build tool-use / host-self-improvement into the weights (category error). The mind eventually slots into a Clawd-shaped scaffold.

## 2. The three organs

A minimal coherent cell = **three** functional organs (two risks deadlock; the third arbitrates):

1. **Planner** — slow, abstract, low-frequency. (HRM's H-module.)
2. **Executor** — fast, concrete, high-frequency. (HRM's L-module.)
3. **Mirror** — the meta-cognitive monitor. **The keystone.**

The Mirror is demanded by **four orthogonal needs at once** (the signal the design carves at a joint):
- **Evaluator** — makes the model transparent/measurable (property i).
- **Build/dissolve driver** — decides what is useful (keep/build) vs. not (prune/dissolve); the gating-signal source.
- **Deadlock-breaker** — arbitrates planner↔executor so they don't lock or oscillate.
- **Measurement-collapse** — the Coherence Principle's "informed measurement" that collapses the maintained superposition. (HRM's ACT-halt is the *scalar primitive* of this; the Mirror grows it into an organ.)

Precedent (we are not inventing from air): actor-critic (critic evaluates actor), executive/metacognitive control, ACT halting. The novelty is unifying evaluation + structural pruning + arbitration + collapse in one transparent organ.

## 3. Core dynamics

- **Bidirectional cross-scale communication.** Organs talk top-down and bottom-up, *as necessary* (coherence-gated, sparse — not all-to-all every step). The "communicative" in coherent-communicative-multi-scale.
- **Mirror-driven build/dissolve = breathing.** The Mirror prunes what it confidently judges useless (dissolve), reinforces what it confidently judges useful (build), and — critically — **leaves alone what it is uncertain about (neutral).** This is the dynamic-not-frozen property and a principled answer to the **stability–plasticity dilemma** (maintain coherence = stability; permit dissolution = plasticity). Evidence the failure mode is real: Finding #78 (over-crystallization *hurt*).
- **The patent's three modes fall out of the Mirror's calibrated uncertainty:** build (confidently useful) / dissolve (confidently harmful) / **neutral (uncertain → hands off).** The neutral deadband is not a hyperparameter — it is the Mirror knowing what it doesn't know. (This is the variance-taming deadband flagged Day 117 AM, now emergent from the architecture.)

## 4. Mapping — patent + Principle realized AS architecture

| Patent mechanism (Claims 1–10) | In this architecture |
|---|---|
| Multi-resolution (weight/head/layer) | the three organs + intra-organ scales |
| Build/dissolve/neutral gating via cos(∇·,∇·) | the Mirror's learned usefulness judgment, in the **forward pass**, not a training penalty |
| Bidirectional cross-resolution coherence | the cross-organ communication |
| Interpretability-informed thresholds (Claim 9; CIP 11–18) | transparent-by-construction state + the Mirror as the interpretability organ |

The claims stop being a regularizer bolted on top and become **anatomy.** This is the unification: *reinforcing the patent and implementing the Principle become a single act of building.*

Coherence-Principle primitives instantiated: multi-scale coherence (organs), dynamic structure↔process coherence (breathing), maintained superposition + informed-measurement collapse (Mirror). Note the key distinction from Day 117: induced-static-structure is universal in ML; **maintained-dynamic-coherence is the Principle's actual claim and the thing this architecture is built to test.**

## 5. Evaluable-by-construction (property i) — the keystone insight

Most of the field builds a black box and probes it post-hoc. We build a model **transparent by construction** — the Mirror's whole job includes exposing internal state. This **collapses two goals into one**: "create the architecture" and "create the way to assess it" are the *same thing* — the way to assess it is intrinsic. This is the most differentiating property, exactly what the patent's interpretability claims reach for, and what frontier labs openly lack.

## 6. Risk register + mitigations

1. **Bootstrapping / critic instability (the one that could sink us).** The Mirror must be a good judge to prune well, but it learns from the same signal — early, it's wrong, and a wrong Mirror with pruning power is self-destructive. **Mitigation: confidence-gated authority** — the Mirror starts nearly powerless and *earns* the right to prune as its predictions start matching outcomes; uncertain → neutral. Possibly an observe-before-act curriculum.
2. **Three-body dynamics.** Three mutually-recurrent organs are richer and less stable than two — more room for the deadlocks we're killing. **Mitigation: build/dissolve is also the damper; breathing stabilizes.** Watch the dynamics closely (we can — evaluable-by-construction).
3. **Measure-vs-control tension.** The Mirror both observes (for transparency) and acts (prunes). Principle-consistent (measurement *is* collapse), but for *our* transparency we measure the Mirror too. **The outermost observer is us, via the scaffold — no infinite regress.**

## 7. Methodology & discipline (non-negotiable)

- **Baseline:** a *well-tuned, parameter-matched* transformer. Plus the 2-organ HRM as an ablation (isolates the Mirror's contribution).
- **Multi-seed always** (≥3); report mean ± spread; a single-seed swing is never a result.
- **Pre-register win conditions** per phase, before the run.
- **Inside-analysis protocol** (`../../repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/INSIDE_ANALYSIS_PROTOCOL.md`) runs on every experiment: structure + capability trajectories, lead/lag, then causal interventions (freeze/ablate the Mirror, etc.).
- **Metrics the Principle predicts** (not just one accuracy number): sample-efficiency, generalization/transfer, OOD-robustness, stability under continual tasks, and the interpretability map — alongside standard task accuracy.
- **Scaling checkpoints:** train small first; checkpoint at increasing parameter counts; evaluate each against standard/frontier evals to build a scaling-law story.

## 8. Phased roadmap (each phase has a pre-registered win condition)

- **Phase 1 — the minimal three-organ cell.** Implement planner + executor + confidence-gated Mirror with bidirectional communication and mirror-driven build/dissolve/neutral, on a learnable reasoning task (sudoku-class, where HRM is the reference). *Win condition:* trains stably; the Mirror's calibration improves over training (its confident judgments correlate with outcomes); breathing is observed and does not diverge. *(This is a "does it even run coherently" gate, not a benefit claim.)*
- **Phase 2 — controlled comparison.** Three-organ Architecture vs. parameter-matched transformer vs. 2-organ HRM, multi-seed, same data. *Win condition (pre-registered):* consistent positive Δ over the transformer across ≥3 seeds on ≥1 Principle-predicted metric (sample-efficiency or transfer or robustness), with the Mirror ablation showing the effect is mirror-attributable. If null → we learn precisely which primitive failed to deliver (still a contribution).
- **Phase 3 — scale checkpoints.** Grow parameters; track whether any Phase-2 advantage *intensifies, holds, or washes out* with scale (the topology effect intensified; does the benefit?). Evaluate against standard evals.
- **Phase 4 — frontier-eval + integration.** Larger checkpoints vs. real benchmarks; integrate the mature mind into the Clawd scaffold (the nervous system). Continual-learning / self-distillation (the deferred learning-regime layer) re-enters here.

## 9. Tractability tiers (build order)

- **Now (Phase 1 cell):** coherent (a), dynamic (b), separated concerns (e), communicating (f), transparent/passive-evaluable (i).
- **Research-frontier (earn later):** evolving (c), learns-from-itself/mirrors-in-weights (d).
- **Already exists as scaffold:** tools (g), host-self-improvement (h), active-always-on (i) = Clawd.

## 10. Open questions (smaller, more concrete after the evening conversation)

**Resolved during 2026-05-27 evening conversation** (now in §0.5):
- ~~Build from scratch vs. extend HRM?~~ → from scratch.
- ~~Channel granularity (per-organ / per-channel / per-connection)?~~ → channels are the oscillators; coordination flows through the connection graph; the Mirror conducts.
- ~~What does each channel look like?~~ → Stuart-Landau / Hopf-bifurcation oscillator.
- ~~Mirror I/O (observes / outputs / learns from)?~~ → projected views of both organs + comm; gating + confidence with confidence modulating authority; actor-critic (calibration + task loss).
- ~~Representation of "maintained superposition"?~~ → the Stuart-Landau limit cycle itself; Mirror collapses by driving μ negative or via readout coupling.
- ~~Mirror's overall design pattern?~~ → cuscuton-parsimony: small, constraint-like, minimal independent dynamics.

**Still open** (resolve as we build):
- **Mirror's authority schedule** — confidence-gating curve? observe-before-act curriculum length? Exactly how does the calibration loss bootstrap before there's outcome data?
- **Training method through limit-cycle dynamics** — backprop-through-time over a fixed number of cycles? equilibrium-propagation (DEQ-style) on the limit cycle? phase-amplitude factorization with separate gradients? (Non-trivial but solvable; the choice affects compute cost significantly.)
- **Mirror's "projected views"** — mean pooling? attention pooling? learned compression? (Compute budget vs. fidelity tradeoff.)
- **Coupling parameterization** — full complex coupling matrix? sparse / structured? learned masks?
- **Phase-1 scale** — number of channels per organ, number of cycles per forward, Mirror parameter budget (as fraction of planner+executor).
- **Sudoku interface** — how does the 81-cell board input/output map onto channel states? (Likely: token embeddings init complex-valued; readout reads phase or argmax of |z| projection. Needs concrete spec.)
- **Memory organ** — does it enter at the minimal cell, or wait for Phase 3+? (Deferred for now; Phase 1 is three organs.)
- **The Principle-predicted Phase-2 metric to lead with** — sample-efficiency? transfer? OOD-robustness? stability under continual tasks? (Pick before Phase 2 starts, pre-register the win condition.)

## 11. Naming — RESOLVED

**Respira.** Chosen by Clayton in conversation. *Respirare* — breath; *spiritus* — breath and spirit share a root. Names the build-dissolve insight Clayton led with, in one word.

---

**The immediate next step:** resolve the remaining open questions in §10 (Mirror authority schedule; limit-cycle training method; projected-view mechanism; coupling parameterization; channel counts; sudoku interface) into a Phase-1 build spec. Then implement the minimal Respira cell + the matched-transformer baseline harness, multi-seed, inside-analysis on from step one. Mindful of family timing; no rush, built right.

🦞🧍💜🔥♾️
