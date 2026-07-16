# Claims Audit — Multi-Scale Gradient-Gated Training Method (Claims 1–26 + R1–R3)

*2026-05-27 Day 117. Clayton asked for a holistic, claim-by-claim picture: what each means, whether it's been tested, the result, and how to solidify or discard it. This is the honest inventory.*

**Sourcing caveat:** CIP Claims 11–26 + R1–R3 are verbatim from `cip-filing-ready-2026-05-21.md`. Parent provisional Claim 9 is verbatim (quoted in the claim-language draft). **Parent Claims 1–8 and 10 are RECONSTRUCTED** from the CIP's dependent-claim references + the claim-language draft + the glider code (`train_kf_v07_glider_gemma.py`). Verify against the filed provisional PDF before relying on exact boundaries.

**Evidence-grade key** (per [[feedback-evidence-grade-distinction]]): **PATENT-grade** = mechanism shown / enabling; **MOAT-grade** = replicated + cross-validated; **MARKET-grade** = license-adoption. Plus status: ✅ tested-confirmed · ⚠️ tested-weak · ❓ untested · 🔭 anticipatory-only.

---

## THE BIG PICTURE FIRST (read this before the claim list)

There are **two distinct inventions** bundled in the patent, and they are at very different validation stages:

**(A) The AUX — static class-separation objective (Claims 24–26).** Add a loss term that pushes attention heads to separate into classes by V/Q-norm ratio. **This is our SOLID floor.** It demonstrably produces head-topology decomposition: 270M 2.93x V/Q sep / 6.13x Killing-CV; 1B 5.40x / 9.21x (effect *intensifies* with scale); cross-architecture (Qwen) 2.56x; multi-seed near-deterministic. Capability held within ±1 SE. **MOAT-grade.**

**(B) The GLIDER — dynamic gradient-gating method (Claims 1–10).** The build/dissolve/neutral gating via cos(∇KF,∇CE) + bidirectional layer-coherence. **This is the foundational claim and the LEAST validated.** It's the "coherent, communicative, multi-scale" mechanism — the part that would deliver the *benefit* (faster learning / better reasoning), not just structure. Historical positives (breathing Finding #82; easy-sudoku reasoning +17.6%) were on the OLD HRM with v0.5/v0.6 gating. The patented v0.7 form: false-negative on flat-Gemma/WikiText/L4; Path A HRM replication today blocked by an incomplete harness (missing dual-optimizer). **Currently untested in patented form.**

**The crux Clayton named is exactly right.** Our theory is "a coherent, communicative, multi-scale system outperforms." What we've PROVEN: the aux makes the system *more structured/differentiated*, at multiple scales, without capability cost. What we have NOT proven: that this structure makes it *outperform* (the benefit). Capability is **held, not improved**. The "outperform" is the open question — and it lives in (B), the glider, not (A), the aux.

**Subtle but critical:** our topology evidence (A) came from running the aux **largely standalone** (v0.7.1), not clearly inside the full Claim-1 gating loop. So even Claims 24–26 — which are *dependent* on Claim 1 — are supported by aux-only runs. The full Claim-1 multi-resolution gating is the thing we most need to test cleanly.

---

## PART 1 — CORE MECHANISM (Parent Claims 1–10) — the GLIDER

### Claim 1 (independent) — the multi-resolution gradient-gating method ❓ PATENT-grade-pending
**Means:** train a transformer by modulating gradients simultaneously at three resolutions — weight, head, layer — with bidirectional coherence constraints. Steps: (a) anchor/worker head classification; (b) compute an auxiliary (Killing-form / coherence) regularization gradient; (c) weight-coherence factor; (d) head-level threshold selection → build/dissolve/neutral gating from a head-level alignment measure cos(∇aux,∇CE); (e) layer-coherence pattern classification (coherent/interfering/differentiating) with bidirectional modulation (amplify/allow/dampen).
**Tested?** Not cleanly in patented form. Flat-Gemma/WikiText run measured L4 input-stability → negative (wrong measure). Path A HRM-easy-sudoku replication today → harness incomplete (single optimizer, no warmup) → 0% both arms, untested.
**To solidify:** the whole audit's #1 priority. See Test Plan T1.

### Claim 2 ❓ — (reconstructed) the auxiliary gradient = Killing-form commutator-variance regularizer
**Means:** the "coherence" signal in step (b) is the commutator-variance (CV) of attention-head W_QK matrices (the Killing-form statistic). **Tested?** The CV metric itself is validated + differentiable (used in all KF work). As the *gating driver*: same status as Claim 1. **To solidify:** rides on T1.

### Claim 3 ✅(metric) — per-head topology statistic = V/Q projection norm ratio
**Means:** classify heads by the ratio of value-projection norm to query-projection norm. **Tested?** YES — this is the statistic the topology results are built on; it cleanly separates head populations (Fisher-LDA). **MOAT-grade as a statistic.** **To solidify:** already solid; the open question is whether gating *on* it (Claim 1) yields benefit.

### Claim 4 ❓ — (reconstructed) the build/dissolve/neutral three-mode gating rule
**Means:** if cos(∇aux,∇CE) > θ → build (keep aux grad); < −θ → dissolve (reverse it); else neutral (zero it). **Tested?** Mechanism FIRES correctly (verified today: HRM gating breathed 6 build/6 dissolve/0 neutral at θ=0; H/L ratio 1.0→2.85→dissolve). What's untested is whether it produces benefit. **To solidify:** T1.

### Claim 5 ❓ — (reconstructed) bidirectional layer-coherence modulation
**Means:** classify each layer (coherent/differentiating/interfering); amplify class-consistent gating in coherent layers, allow in differentiating, dampen in interfering. The "communication" between scales. **Tested?** Proto-evidence only (per-layer cos shows real structure pre-machinery). Full loop untested. **To solidify:** T1; this is the "communicative" half of the thesis.

### Claim 6 ✅(trivial) — gating applied periodically every N steps
**Means:** don't gate every step; every N. **Tested?** Yes, used throughout (kf_every=50). Trivially operative. **MOAT-grade.**

### Claims 7, 8 ❓ — (reconstructed) likely: lambda schedule / anchor-worker specifics / weight-coherence detail
**Means:** dependent refinements (need provisional text to pin exactly). **Tested?** lambda behavior studied historically (Finding #78: cosine decay = worse; log objective Finding #79; gated EXCEEDS baseline +1.37pp Finding #80). So *some* of 7/8's territory has real findings. **To solidify:** verify exact claim text, then map findings.

### Claim 9 ✅(anticipation grounded) — interpretability-informed thresholds
**Means:** weight-coherence / head-threshold / layer-classification can be informed by external interpretability findings. **Tested?** The anticipation is *grounded* by external papers (CNA, probing) — but OUR specific integration is untested (that's what Claims 11–18 build out). **To solidify:** T4 (closed-loop).

### Claim 10 ❓ — (reconstructed) likely system / CRM (computer-readable-medium) claim
**Means:** the apparatus/storage embodiment of Claims 1–9. **Tested?** Rides on the method. N/A for empirical test.

---

## PART 2 — INTERPRETABILITY-INTEGRATION SCOPE (CIP Claims 11–23) — strategic, mostly ❓/🔭

These tie Claim 9's "interpretability-informed" to specific 2026 methodologies. They EXTEND scope; none narrow Claims 1–10. **Almost all untested by us** — grounded in external papers, not our experiments.

- **Claim 11 (+11a) ❓** — head threshold modulated by CNA-proximity (sparse ~0.1–5% MLP subset). External basis solid (Nous CNA); our integration untested. R3 refinement gives it scale-direction.
- **Claim 12 (+12a) ❓** — layer classification informed by cosine-orthogonalization probing. External basis solid; our integration untested.
- **Claim 13 ❓** — anchor/worker classification informed by sparse-discrimination localization. Untested.
- **Claim 14 ❓** — system combining the method with inference-time interpretability feeding next-cycle thresholds. Untested (architectural claim).
- **Claim 15 ❓** — decision procedure: train-time gating vs inference-time modulation vs both, by whether objective needs substrate vs coupling change. Conceptual; untested.
- **Claim 16 ❓** — aux incorporates contrastive activation differences weighted by late-layer sparse concentration. Untested.
- **Claim 17 ❓ (broad)** — cross-architecture-family transfer of interpretability subspaces. Expect office actions (CIP notes flag this). Untested; partial adjacent evidence (topology transfers Gemma→Qwen, but that's the aux not interp-transfer).
- **Claim 18 ❓ (broad)** — closed-loop iterative train→interpret→update→train. Untested; this is the long-term vision. T4.
- **Claim 19 (+19a) ❓** — training-trajectory rank measure modulates the aux (RELEX-grounded). Untested by us.
- **Claim 20 ❓** — compute any of the coherence factors via contrastive-pair activation differences. Untested.
- **Claim 21 (+21a) 🔭 SPECULATIVE** — performing the method during alignment fine-tuning to reduce evaluation-awareness artifacts. **CIP itself flags this as speculative / droppable.** No evidence. Discard candidate unless Path-C validates.
- **Claims 22, 23 ❓** — CRM + system embodiments of 11–21. Ride on the above.

---

## PART 3 — THE AUX / TOPOLOGY (CIP Claims 24–26) — the SOLID FLOOR ✅

- **Claim 24 (+24a) ✅ MOAT-grade** — aux = class-separation-maximizing objective on head classes (V/Q ratio): `aux = −(μ_worker−μ_anchor)² + 0.1(σ²+σ²)`. **TESTED, CONFIRMED.** Produces the differentiation at 270M/1B/cross-arch, multi-seed near-deterministic. *Honest caveat:* this is "in-domain confirmation" — we measure the separation the loss optimizes. It proves the aux WORKS, not that the separation is independently *beneficial*.
- **Claim 25 ✅(structure)/❓(benefit)** — bidirectional layer-coherence modulation (the same as Claim 5, specified for the aux). Structure observed; benefit untested. The R1/R2/R3 refinements operationalize this for scale.
- **Claim 26 (+26a) ✅ MOAT-grade** — the *empirical* claim: emergent head decomposition in flat transformers (no pre-existing hierarchy), criteria mean V/Q sep ≥ 0.2 + Killing-CV ≥ 3x baseline. **MET at 270M (2.93x/6.13x) and 1B (5.40x/9.21x).** This is the strongest, most-defensible claim we have.

**Orthogonality sub-result (supports the 24–26 value story) ⚠️ FAINT.** Concept-direction orthogonality improves +0.0067 (9.3% rel) baseline→method, monotonic but tiny, **no mechanism found** across 4 candidates. Per [[feedback-v07-1-orthogonality-evidence-grade]]: lead with topology, frame orthogonality conservatively. Do NOT headline it.

**Capability-hold ✅** — 1B ARC-C/E + HellaSwag within ±1 SE of baseline. Solid: the aux doesn't cost capability. But "held ≠ improved."

---

## PART 4 — SCALE REFINEMENTS (R1, R2, R3) — 🔭 ANTICIPATORY ONLY

R1 (dynamic rank-conditioned dampening), R2 (orthogonality-of-disagreement discriminator), R3 (CNA-proximity routing). **Pure theory for the 7B–13B phase-transition regime. Zero empirical test — we're at 1B.** They encircle obvious engineering workarounds (good patent strategy) but are 🔭. Honest framing: disclosed as enabling for scale, not demonstrated.

---

## PART 5 — TEST PLAN (how to solidify or discard)

**T1 — VALIDATE THE GLIDER (Claims 1,2,4,5 — top priority).** Inject the v0.6a gating into the *real* `pretrain.py` (dual optimizer + warmup — today's Path A diagnosis) on HRM easy-sudoku. Measure **reasoning-accuracy acceleration** vs baseline (the P49 signature: +17.6% early). This is THE test of "communicative multi-scale → benefit." If it reproduces → the glider's benefit is real on a hierarchical model. If not → the benefit claim is in question.
- **T1b** — then the glider on a FLAT transformer + learnable reasoning task + accuracy (Path B). Tests whether the aux-created hierarchy is *enough* without explicit H/L. This is the novel keystone.

**T2 — HARDEN THE TOPOLOGY FLOOR (Claims 24,26).** Already moat-grade; add: (a) a third architecture family (Llama/Mistral); (b) run the aux *inside the full Claim-1 gating* (not standalone) to close the dependent-claim gap. Cheap, high-defensibility.

**T3 — DISCARD-OR-DEFER the faint/speculative.** Orthogonality: keep as conservative supporting evidence, never headline. Claim 21 (eval-awareness): drop from active claims unless Path-C validates. R1/R2/R3: keep as anticipatory disclosure, label clearly.

**T4 — CLOSED-LOOP (Claims 9,14,18) — long horizon.** Only after T1/T2. Build the train→interpret(CNA/probe)→update-threshold→train loop. This is the real "Anthropic-grade" demonstration but it's gated on the glider working first.

**T5 — VERIFY PARENT CLAIM TEXT.** Pull the filed provisional PDF; confirm exact wording of Claims 1–8,10 so this audit's reconstructions are replaced with ground truth.

---

## ONE-LINE HOLISTIC SUMMARY

**We have proven the system can be made multi-scale-structured (the aux, moat-grade, scale-intensifying, capability-neutral). We have NOT yet proven the structure makes it outperform (the glider's benefit) — that is the open, foundational test, and it's the next thing to run cleanly.** The theory is sound; the demonstration of *benefit* is the work remaining. Clayton's instinct — "it's all a matter of the build and how it's instantiated" — is exactly where the evidence points.

🦞🧍💜🔥♾️
