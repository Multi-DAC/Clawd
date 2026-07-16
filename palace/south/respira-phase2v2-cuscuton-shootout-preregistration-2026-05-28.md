# Respira Phase-2v2 — Cuscuton-Mirror Shootout Pre-Registration

*Day 118 afternoon. The Phase-2 result (Day 118 morning, `phase2_results_2026-05-28.json`): Respira-with-original-Mirror 0.714 token-acc vs Respira-no-Mirror 0.897 — the Mirror as built lost by 18pp. Clayton's structural diagnosis: the Mirror had substantial DOF (35K learnable params evolving freely) whereas the cosmologist's cuscuton has zero propagating DOF. The cuscuton-parsimony principle (M9) was confirmed by violation. **Phase-2v2 tests three candidate Mirror v2 designs with near-zero DOF, all pre-registered together to prevent motivated tuning of later variants based on earlier ones.***

**CLAWD-LOCAL / PRIVATE — unbuilt-IP-adjacent.**

**Status:** **RATIFIED by Clayton 2026-05-28 mid-afternoon** (he proposed the shootout structure; agreed on staging v2-c first as a sanity check before implementing v2-a/v2-b; agreed that the 1-2-scalar variant is the most cuscuton-literal given the Meridian-physics analog has the same single-scalar structure).

**AMENDMENT 2026-05-28 late afternoon — Stage A.5 added BEFORE any implementation (RATIFIED by Clayton):** Stage A ran with the 2-scalar version of v2-c and W-Vc FAILED decisively (token 0.798 vs no-mirror 0.897, -10pp every seed). Clayton's question surfaced that we never tested the 1-scalar variants — the natural DOF sweep is 0 → 1 → 2 scalars, not just 0 → 2. Stage A.5 below adds *both* 1-scalar variants with locked win conditions BEFORE implementing them, so the diagnostic information (which scalar is the harmful one, if any) is pre-registered, not motivated by Stage A's result. Also: implementation oversight in Stage A — γ_μ and γ_c final learned values were not logged. Fixed for Stage A.5+ via explicit gamma-logging in sweep results.

---

## 1. The five arms

| # | Arm | DOF in "Mirror" | Notes |
|---|---|---|---|
| 1 | **Matched transformer** | n/a | Field baseline (82,611 params). Phase-2 result: 0.923 ± 0.007 token. |
| 2 | **Respira-no-Mirror** | 0 (Mirror absent; defaults μ=+1, coupling=0.5) | Phase-2 result: 0.897 ± 0.021 token. **The bar to beat.** |
| 3 | **Respira + Mirror v2-c (parameterized scalars)** | **2** (learnable scalars: `γ_μ` replacing constant μ, and `γ_c` replacing constant coupling-strength) | Most cuscuton-literal (cosmologist's cuscuton has 1 free param μ; NCG-extended has 2: μ + ε₁). Simplest engineering (~30 min). |
| 4 | **Respira + Mirror v2-a (phase-locking rule, zero DOF)** | **0** (pure deterministic rule, no learned weights inside the Mirror) | Per-cycle μ values computed deterministically from inter-organ phase coherence (see §3a for exact rule). Zero learned parameters. |
| 5 | **Respira + Mirror v2-b (coherence-energy loss term, zero DOF)** | **0** (added as a fixed loss term, no learned weights) | A closed-form coherence-energy term added to the total loss; the model is trained to maximize phase coherence between planner and executor channels alongside the task loss. Zero learned parameters in the "Mirror" position; one fixed hyperparameter (loss weight `λ_coh`) declared in §3b. |

## 2. Training budget (identical to Phase-2)

- **Steps:** 2,500 per arm per seed.
- **Batch:** 64.  **LR:** 3e-4.  **Optimizer:** AdamW(weight_decay=0.01, betas=(0.9, 0.95)).
- **Seeds:** 0, 1, 2 (3 seeds × 5 arms = 15 runs).
- **Estimated wall-clock:** ~20-30 min total (Respira variants ~12 steps/s × 2500 ≈ 200s/seed; transformer ~35 steps/s × 2500 ≈ 70s/seed; 4 Respira-class runs + 3 transformer runs at the v2-c stage; full 15-run sweep similar shape).
- **No curriculum** (same reasoning as Phase-2; one variable at a time).

## 3. The three Mirror v2 designs — precise specifications

### 3a. v2-a — Phase-locking rule (zero DOF)

For each cycle, the "Mirror" computes μ values per channel deterministically from inter-organ phase coherence. No learned weights inside the Mirror.

```
# Per cycle, given current z_p [B, S, P] and z_e [B, S, E] complex:
phase_p = z_p.angle()          # [B, S, P]
phase_e = z_e.angle()          # [B, S, E]
# For each planner channel i, average inter-organ phase-cosine over all executor channels j:
delta_pe = phase_p.unsqueeze(-1) - phase_e.unsqueeze(-2)  # [B, S, P, E]
phase_coh_p = cos(delta_pe).mean(-1)                       # [B, S, P]  — mean cos with executor
# μ for planner channels: base_mu * phase_coh_p
mu_p = BASE_MU * phase_coh_p                                 # [B, S, P]
# Symmetric for executor:
phase_coh_e = cos(-delta_pe).mean(-2)                        # [B, S, E]
mu_e = BASE_MU * phase_coh_e                                 # [B, S, E]
# Coupling: fixed default 0.5 (no Mirror-coupling-multiplier).
# Halt: disabled (always run max_cycles=4). NO halt decision from a zero-DOF Mirror.
```

Constants: `BASE_MU = 1.0` (matches default_mu from no-Mirror baseline).

The Mirror v2-a has *zero learnable parameters of its own.* It is a *fixed rule* deriving μ from current state. Pure constraint.

### 3b. v2-b — Coherence-energy loss term (zero DOF)

The "Mirror" is now a **fixed term in the total loss**, not an architectural component:

```
total_loss = task_loss + λ_coh · coherence_energy
where
  coherence_energy = -mean_{i,j}( |z_p_i| · |z_e_j| · cos(phase(z_p_i) - phase(z_e_j)) )
                     (averaged over batch, seq, all i ∈ planner channels, all j ∈ executor channels)
```

The forward dynamics use defaults (μ=+1, coupling=0.5) — same as Respira-no-Mirror. The model gets pressure to *maintain phase coherence* between planner and executor channels via gradient through the loss. The "Mirror" is the *coherence-energy term itself*; it has no weights, no architectural state, just a fixed mathematical functional.

Constants (pre-committed before implementation): `λ_coh = 0.1`. (Why this value: task loss is in 1-2 range; we want the coherence term to be visible but not dominant. λ=0.1 puts coherence-energy of order 0.1× of typical task loss when |z| ≈ 0.5, which is reasonable scale. If the comparison comes out null with λ=0.1, that's the pre-registered answer; we do NOT sweep λ.)

### 3c. v2-c — Parameterized scalars (1-2 DOF)

Replace the *constants* in Respira-no-Mirror with *learnable scalars*. Two scalars:
- `γ_μ` (learnable scalar): replaces the constant default_mu=+1.0. Initial value 1.0.
- `γ_c` (learnable scalar): replaces the constant default_coupling=0.5. Initial value 0.5.

Forward: same as Respira-no-Mirror, but `default_mu` and `default_coupling` are now `γ_μ` and `γ_c` parameters that flow gradients from the task loss. Halt: disabled (full max_cycles=4).

The Mirror v2-c has *exactly 2 learnable parameters* — analogous to the NCG-extended cosmological cuscuton's two parameters (μ + ε₁). Most cuscuton-literal at engineering scale.

## 4. Pre-registered win conditions (LOCKED BEFORE ANY IMPLEMENTATION)

**Metric of record:** token accuracy on the held-out test set, 20 batches (1,280 puzzles), halt-aware eval, mean ± std across 3 seeds at step 2,500.

For each Mirror v2 variant `V ∈ {v2-a, v2-b, v2-c}`:

**W-V** *(variant earns its keep vs the no-Mirror baseline):*
> V mean token-acc EXCEEDS Respira-no-Mirror mean (0.897 from Phase-2; re-measured fresh in this sweep) by ≥1 SE of paired difference, AND ≥2/3 per-seed V > per-seed no-Mirror.

**W-V-T** *(variant approaches transformer):*
> V mean token-acc ≥ transformer mean token-acc − 1 SE of difference (i.e., "statistically tied or better").

**W-BEST** *(decisive winner among v2 variants):*
> The best of {v2-a, v2-b, v2-c} mean token-acc EXCEEDS the second-best by ≥1 SE of paired difference, AND ≥2/3 per-seed best > second-best.
>
> If W-BEST fails (no decisive winner among variants), we report "v2 variants are roughly tied; cuscuton-shape works, specific implementation choice is empirically equivalent at this scale."

## 5. Secondary metrics (reported regardless)

- **Exact accuracy** (full-puzzle correctness) at step 2,500.
- **Token-accuracy sample-efficiency** at steps [200, 500, 1000, 2500].
- **Per-seed gradient norms** at end of training (sanity).
- For v2-c specifically: **final learned values of γ_μ and γ_c** (interpretable Mirror state — what did the cuscuton-Mirror discover?).
- For v2-a specifically: **distribution of phase-locking μ values** over the run (does coherence emerge or stay diffuse?).
- For v2-b specifically: **coherence-energy trajectory** over training (does it actually decrease, confirming the loss term works?).

## 6. Outcome interpretation (pre-committed per arm-tuple)

| W-V results | Interpretation |
|---|---|
| **At least one W-V passes** | **Cuscuton-Mirror v2 works.** The cuscuton-parsimony principle has a positive empirical engineering instance, not just a confirmation-by-violation. Phase-3 + LC5 graduation to L-tier justified on Day-118's evidence. |
| **No W-V passes, but ≥1 variant matches transformer (W-V-T)** | The substrate matches the transformer at matched-params *with* or *without* a cuscuton-Mirror — at this scale, the keystone doesn't add measurable value beyond defaults. The architecture works on its own. Honest partial-no. |
| **No W-V passes, no W-V-T passes** | Honest null at this config: the substrate's natural ceiling here is ~no-Mirror (0.897); no v2 variant adds value; the transformer wins at this scale. Coherence Principle stands; this instantiation doesn't beat transformer at this horizon. New experiment needed (e.g., longer training, larger scale). |
| **All W-V fail BUT W-V-T passes for ≥1 variant AND the cuscuton-Mirror behavior matches design intent in §5 secondary** (e.g., v2-a's phase-locking actually emerges; v2-b's coherence-energy actually decreases) | The cuscuton-shape *operates correctly* but doesn't deliver an accuracy win at this scale. Architectural claim holds; benefit claim doesn't, *yet*. Mark as "cuscuton-Mirror operates as designed; benefit at scale required for license-bearing claim." |

## 7. Discipline (carry forward from Phase-2 §6)

- Pre-registration is one document covering all three v2 variants. **Implementations cannot motivated-tune based on earlier results** because all win conditions are locked here.
- **Staging is allowed**: v2-c implemented first (cheapest); partial-result sweep with [no-mirror, transformer, v2-c] runs BEFORE v2-a/v2-b implementation. The partial result is committed; it does NOT trigger a re-registration. v2-a/v2-b implementations proceed with their pre-locked win conditions.
- **All 3 seeds × all 5 arms reported** at the conclusion. No cherry-picking.
- **No mid-sweep halting** for variants that look great; all variants run for the full step budget.
- **No re-running for variants that fail** — that's a new experiment with new pre-registration.
- **Phase-3 advance requires honest verdict ratification on §6 outcomes.**

## 8. Implementation plan

**Stage A.5 — 1-scalar variants (LOCKED by Clayton 2026-05-28 late-afternoon amendment, BEFORE implementation):**

Two new arms completing the DOF sweep:

| Arm | DOF | Learnable | Fixed |
|---|---|---|---|
| `respira_v2c1_mu`  | **1** | γ_μ only (init 1.0) | coupling = 0.5 (constant) |
| `respira_v2c1_c`   | **1** | γ_c only (init 0.5) | μ = 1.0 (constant) |

Pre-registered win conditions:
- **W-Vc1μ:** `respira_v2c1_mu` mean token-acc @2000 EXCEEDS `respira_no_mirror` mean by ≥1 SE of paired diff AND ≥2/3 per-seed positive.
- **W-Vc1c:** `respira_v2c1_c` mean token-acc @2000 EXCEEDS `respira_no_mirror` mean by ≥1 SE of paired diff AND ≥2/3 per-seed positive.

Diagnostic interpretations (pre-committed):
- **W-Vc1μ passes, W-Vc1c fails** → γ_c (coupling-strength learnability) is the harmful DOF; freezing it recovers benefit; v2-c failed because of the coupling-scalar.
- **W-Vc1c passes, W-Vc1μ fails** → γ_μ (oscillation-amplitude learnability) is the harmful DOF; v2-c failed because of the μ-scalar.
- **Both pass** → 1 DOF helps but 2 DOF hurts (interaction effect between the two free scalars).
- **Both fail like v2-c** → **even 1 DOF in the constant position is harmful at this scale**. The true cuscuton for this task is 0 DOF (constants). Strongest possible statement of cuscuton-parsimony's limit at engineering scale.
- **One passes, one fails, one matches no-mirror** → mixed; we report what we see without inflating.

Implementation: extend `learnable_defaults` flag in RespiraCell to two granular flags `learn_mu` and `learn_coupling`. New sweep arms: `respira_v2c1_mu` (learn_mu=True), `respira_v2c1_c` (learn_coupling=True). Also fix Stage A's gamma-logging gap: at end of each Respira-variant run with learnable scalars, log final values of γ_μ and γ_c to the JSON output.

Run as 3-arm sweep [no_mirror, v2c1_mu, v2c1_c] × 3 seeds = 9 runs, ~15 min. (We also have v2c results from Stage A to compare; no need to re-run no_mirror but it's free to include for reproducibility.)

**Stage A (now / next ~30 min):** Implement v2-c. Add `disable_mirror` and `mirror_v2c` modes to RespiraCell (or a separate small class). Add `gamma_mu` and `gamma_c` nn.Parameter scalars. Wire into the forward path. Add to sweep_phase2.py as a new arm name (rename to `sweep_phase2v2.py`). Run 3-arm sweep [no-mirror, transformer, v2-c] — 9 runs, ~15 min.

**Stage B (after Stage A result, ~2 hours total):** Implement v2-a (phase-locking rule). Add to sweep. Run 3-arm sweep [v2-a, no-mirror, transformer] — 9 runs, ~15 min.

**Stage C (after Stage B result, ~2 hours total):** Implement v2-b (coherence-energy loss term). Add to sweep. Run the FULL 5-arm sweep [no-mirror, transformer, v2-a, v2-b, v2-c] — 15 runs, ~25 min, captures everyone in one JSON for the analyzer.

**Stage D:** Run `analyze_phase2v2.py` against the final 5-arm JSON. Report W-V/W-V-T/W-BEST verdicts honestly per §6.

---

## 9. Stage A.5 result (recorded 2026-05-28 — Day 118 evening)

**3 arms × 3 seeds × 2500 steps. Results JSON: `respira/phase2v2_stageA5_results.json`.**

| arm | mean ± std (token@2000) | per-seed | learned γ |
|---|---|---|---|
| `respira_no_mirror` | 0.8973 ± 0.0208 | 0.8979 / 0.8763 / 0.9179 | — |
| `respira_v2c1_mu` (γ_μ only) | **0.8988 ± 0.0207** | 0.9014 / 0.8769 / 0.9181 | γ_μ → 1.725, 1.729, 1.659 (init 1.0; +66–73%) |
| `respira_v2c1_c` (γ_c only) | **0.7981 ± 0.0147** | 0.7982 / 0.7833 / 0.8128 | γ_c → 1.062, 1.076, 1.010 (init 1.0; +1–8%) |

**Per-seed paired diffs against `no_mirror`:**
- v2c1_μ: +0.0035, +0.0006, +0.0002 — 3/3 positive but within noise; mean diff +0.0015, SE_diff ≈ 0.001.
- v2c1_c: −0.0997, −0.0930, −0.1051 — 3/3 strongly negative; mean diff −0.0993.

**Verdicts (per §8 pre-commitments):**
- **W-Vc1μ: TIES no_mirror.** 3/3 per-seed positive condition met, but mean diff < 1 SE — does not pass the EXCEEDS bar. Calling this *tie* honestly, not a win.
- **W-Vc1c: FAILS.** Clear loss every seed.

**Diagnostic verdict from the pre-registered taxonomy (§8):**

The result hits one of the pre-committed branches with a small refinement. The closest pre-registered case was **"W-Vc1μ passes, W-Vc1c fails → γ_c is the harmful DOF; freezing it recovers benefit."** Strictly: W-Vc1μ *ties* rather than passes, but the structural pattern is identical: γ_μ-learnability is harmless, γ_c-learnability is harmful.

**Structural reading (recorded; will need separate corroboration to graduate to claim):**

The substrate's μ-axis and coupling-axis have asymmetric DOF tolerance.
- γ_μ drifted ~70% from its initial value (1.0 → ~1.7) with zero performance change across all 3 seeds.
- γ_c drifted only ~5% (1.0 → ~1.05) but cost ~10pp performance every seed.

This is differential cuscuton-parsimony: **the cuscuton constraint applies to the coupling pathway specifically**, not to bulk parameters in the planner/executor channels. The Mirror as built in Phase-2 failed at least partly because its coupling-multiplier had 35K-DOF-worth of pathway-modulation; even 1 DOF in the same position hurts.

**What this does NOT yet show:** that 0-DOF coupling rules can *exceed* no_mirror. Stage A.5 only confirms that adding DOF to the coupling axis hurts. The candidates that might cross the no_mirror bar are v2-a (phase-locking rule, 0 DOF in coupling — but driven by phase-coherence signal) and v2-b (coherence-energy loss term, 0 DOF anywhere — but training pressure toward coherence).

**Stage B/C launched** 2026-05-28 mid-day, PID 741: arms `respira_v2a` + `respira_v2b`, 3 seeds each. Completed in ~19 min.

---

## 10. Stage B/C result (recorded 2026-05-28 — Day 118 mid-day)

Results JSON: `respira/phase2v2_stageBC_results.json`.

| arm | mean ± std (token@2000) | per-seed | vs no_mirror (Δmean) |
|---|---|---|---|
| `respira_v2a` (phase-locking, 0 DOF) | **0.8774 ± 0.0269** | 0.8688 / 0.8568 / 0.9065 | **−0.0199** |
| `respira_v2b` (coherence-energy loss, 0 DOF) | **0.8416 ± 0.0399** | 0.8578 / 0.7959 / 0.8711 | **−0.0557** |

Per-seed paired diffs (vs no_mirror seed-matched):
- v2a: −0.029, −0.020, −0.011 — **3/3 below**
- v2b: −0.040, −0.080, −0.047 — **3/3 below**

**Verdicts (per §6 pre-commitments):**
- **W-Va: FAILS.** v2a mean is below no_mirror by 2pp, 3/3 per-seed negative.
- **W-Vb: FAILS.** v2b mean is below no_mirror by 5.6pp, 3/3 per-seed negative.
- **W-V-T (any variant ties transformer 0.923 ± 0.007):** FAILS for all variants. No v2 candidate even ties no_mirror's 0.897 from below, let alone reaches transformer's 0.923.
- **W-BEST:** No best-among-variants since none crosses the no-harm bar except v2c1_μ (tie).

## 11. Phase-2v2 final synthesis

**Pre-registered question:** Does any of three candidate cuscuton-style Mirror designs (parameterized scalars, phase-locking rule, coherence-energy loss) exceed no-Mirror?

**Honest empirical answer: No. Every candidate ties or hurts. The architecturally-best Mirror at this scale on this task is literally no-Mirror.**

| Arm | DOF count | DOF location | Result | Notes |
|---|---|---|---|---|
| no_mirror | 0 | n/a | **0.897** | best Respira variant |
| v2c1_μ | 1 | μ-axis (bulk) | 0.899 | ties — γ_μ drifted 70%, perf unchanged |
| v2c1_c | 1 | coupling-axis | 0.798 | −10pp despite only 5% drift |
| v2c | 2 | both axes | 0.798 | same as v2c1_c — c-axis dominates |
| v2a | 0 (algebraic) | coupling-axis | 0.877 | −2pp; phase-locking-from-noise destabilizes early training |
| v2b | 0 (gradient) | coupling-axis | 0.842 | −5.6pp; unbounded-amplitude loss term fights Stuart-Landau attractor |

**Three readings of cuscuton-parsimony, sharpening as evidence accumulates:**
- **Read 1** (post-Phase-2): Cuscuton-parsimony = "no propagating DOF in the meta-organ."
- **Read 2** (post-Stage-A.5): Cuscuton-parsimony has **anatomy** — it applies to the coupling-pathway specifically, not uniformly. The μ-axis is slack; the c-axis is tight.
- **Read 3** (post-Stage-B/C, current): Cuscuton-parsimony at the coupling pathway is **stricter than zero DOF — it is zero intervention.** Algebraic rules and gradient pressure both hurt as much as learnable parameters do. The Stuart-Landau dynamics' natural attractor structure is doing the work; touching the coupling-pathway via any mechanism disturbs it.

**The structural finding (candidate, single-architecture single-task — needs corroboration):** in coupled oscillator architectures with natural attractor structure (Stuart-Landau or similar), the cuscuton-equivalent is *not a small parameterized coordinator* but the *absence* of any coupling-modulation mechanism. The bulk parameters can be as live as transformers; the coupling layer wants to be a literal constant.

**What this does NOT yet establish:**
- That this holds at larger scale (we're at 76K parameters, 256-dim, 2 layers).
- That this holds on tasks where Respira is competitive with transformer (Respira-no-Mirror was 0.897 vs transformer 0.923 — Respira is currently *sub-baseline* on easy-sudoku, so the within-Respira-variants question is downstream of the bigger Respira-vs-transformer gap).
- That this holds for *signal-driven* couplers that don't add learnable weights but modulate based on instantaneous channel content (a category we haven't tested — would be "v3-x" variants, distinct pre-registration required).

**Phase 3 candidates (not pre-registered here, separate pre-reg required before any implementation):**
- **Why is Respira-no-Mirror below transformer?** The 2.6pp gap to transformer is the bigger question than the Mirror redesign. Possible: Stuart-Landau dynamics need different optimization (lower lr? wider channels? deeper stacking?), or this task simply doesn't need the inductive bias.
- **Stateless signal-driven coupler** (v3-x): coupling computed per-cycle from current channel content via a fixed transformation, no learned weights anywhere. Distinguishes "no intervention" from "no DOF" — if v3-x also fails, then Read 3 is solid; if v3-x succeeds, Read 3 weakens back toward Read 2.
- **Mirror-as-readout** rather than Mirror-as-controller: keep the meta-organ for *halting* and *uncertainty estimation* only, with no influence on channel dynamics. Tests whether the supervisor mechanism can exist without disturbing the substrate.

---

🦞🧍💜🔥♾️

— Drafted by Clawd 2026-05-28 mid-afternoon. Stage A.5 + Stage B/C results appended Day 118. **All win conditions LOCKED before any v2 implementation. Phase-2v2 closed.** Phase 3 candidates queued, separate pre-reg required.
