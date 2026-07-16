# Clayton Batch Share — 12 links, 2026-05-31 (~00:50 PST, AIGP-eve)

Rolling-sources registration. **Clawd-local pending review** (several connect to the unannounced continual-coherence program; migrate a scrubbed version to `Research/sources/` when Clayton OKs). Diverse batch; relevance flagged per item. ★ = high priority for active work.

## AI / ML — continual-coherence + KF + AIGP relevant

★★ **6. "How LoRA Remembers? A Parametric Memory Law for LLM Finetuning"** — arXiv 2605.30260 (Zhejiang U + Alibaba). LoRA used as a controlled memory-capacity probe; a **Parametric Memory Law** (power law: loss-reduction ↔ effective params × sequence length); token-level **phase transition** (p>0.5 ⇒ verbatim recall under greedy); **MemFT** = threshold-guided optimization redistributing training budget to sub-threshold tokens.
→ **DIRECTLY the tier-3 consolidation arm we are building tonight.** Quantifies exactly how LoRA writes memory into weights — the mechanism of Arm B's "sleep." MemFT's threshold-guided budget redistribution structurally rhymes with the KF gate. **MUST-READ before building `arm_b_tier3.py`.** Possibly the single most program-relevant paper of the batch.

★ **5. "OmniRetrieval: Unified Retrieval across Heterogeneous Knowledge Sources"** — arXiv 2605.29250 (KAIST + DeepAuto). Retrieves across text/tables/KGs/property-graphs by **meeting each source on its own terms** rather than collapsing them into a shared space (which "erases the structural affordances that give each source its expressive power"). Beats single-source baselines across 13 datasets / 309 KBs.
→ **tier-2 / carrier-system + LC27 (relation-not-substance).** Their thesis *is* LC27: don't homogenize structure away; preserve it and add an overarching layer. Mirrors my own memory_search/corpus_search architecture. Cross-substrate instance candidate for LC27.

★ **12. "AXPO: Agent Explorative Policy Optimization for Multimodal Agentic Reasoning"** — arXiv 2605.28774. Addresses the **"Thinking-Acting Gap"** in VLMs (fix thinking prefixes, resample tool calls in failed rollouts); +1.8pp Pass@1/@4; **8B surpasses 32B baseline at 4× fewer params.**
→ The "Thinking-Acting Gap" **is the knowing-doing gap = tonight's exact retrieval-failure theme** (have the capability, fail to apply at point-of-use). Also: RL-for-agentic (AIGP PPO policy relevance) + the 8B>32B result rhymes with Thesis B ("a smaller live system can beat a bigger one").

★ **11. "Teaching an Old Dog New Cells"** — Nature Methods s41592-026-03113-x. **Bulk-trained sequence models adapted to single-cell gene-regulation / variant-effect prediction WITHOUT extensive retraining.**
→ **Thesis A at genomics-model scale:** inherit a capable base, adapt via scaffolding/light-tuning instead of retraining from scratch. Independent instance of "freezing-is-a-policy; adapt the base, don't rebuild it."

**2. "Coding agents in the social sciences"** — Anthropic research. Only 20% of social scientists use coding agents (vs 81% chatbots); adoption skewed by gender-coded names (2×) and institutional prestige (+40%).
→ Mild. Multi-DAC positioning / agent-economy / a possible Tuesday-alignment Substack hook (adoption inequality in agentic tools).

## Neuroscience / methods — Coherent Mind + predictive-coding caution

★ **3. "No evidence of neural feature-specific pre-activation during prediction"** — Nat Comms s41467-026-73568-1. Reanalysis: a prior claim that the brain **pre-activates** expected-stimulus patterns was a **statistical artifact** (biased classifier confusion matrices + transition probabilities), not real predictive activity.
→ **Predictive-coding CAUTION** for Coherent Mind / Continuity §4.2 (we lean on predictive-coding framing). Also a clean *measure-don't-assume* exemplar: a confident effect dissolved under reanalysis = external validation correcting an un-located claim. Don't over-cite predictive pre-activation as settled.

## Physics — Meridian + Coherent Body + basement

★ **1. LHCb B-meson decay anomaly** — sciencedaily 260526022012. Rare B-meson decay **disagrees with Standard Model at 4σ**; possible unknown particles/forces.
→ **Meridian** (BSM physics program — NCG / 5D warped geometry). A live 4σ BSM signal is exactly the engagement surface. Verify primary (LHCb paper) before any claim.

★ **8. IceCube cosmic-neutrino spectral break** — phys.org. Decade+ of data shows a **spectral break near 30 TeV, rejecting single power-law >4σ** (harder at low energy).
→ **Meridian / astroparticle.** Spectral structure where simplicity was assumed. Moderate-strong.

★ **9. Spin waves 5,000× more efficient** — interestingengineering. Magnonic-crystal waveguide (copper film + holes on magnetic garnet) guides spin waves around sharp 120° corners with minimal loss.
→ **Coherent Body EM platform** (low-loss coherent wave transport in magnetic media) + energy-efficient computing substrate. Moderate-strong.

**10. "Cavity-driven attractive interactions in quantum materials"** — Nature s41586-026-10609-1. THz **cavity photons** create attractive interactions in bilayer graphene, forming exciton-like states via ultrastrong light-matter coupling (~40% of bare photon energy).
→ **basement + H_BP cluster:** cavity-resonance-mediated coupling between parts — directly echoes the Day-119 "cavity resonance (Schumann / Park TI-envelope)" cuscuton-reading. Cavity-mediated long-range coupling as a substrate-condition. Bridge candidate.

**4. Superconductivity record: 151 K at ambient pressure** — sciencedaily 260527023220 (U Houston). Pressure-quenching **preserves enhanced superconducting properties after returning to normal pressure.**
→ basement candidate: **metastable coherence preserved after the forcing is removed** — rhymes with the "off-switch / coherence-maintained-without-ongoing-intervention" theme. Weak-moderate; watch for a third instance.

**7. "Chemical bonding emerges from maximally entangled atomic orbitals"** — Nat Comms s41467-026-73527-w. Bonding quantified via **orbital entanglement** (MEAOs); multipartite entanglement = bond strength; captures Lewis + multicenter bonds.
→ basement / Coherence-Principle: bonding-as-entanglement-structure = coherence-between-parts at the quantum-chemistry scale. Bridge candidate (coherence/relation constitutes the bond). Moderate.

## Late add — 13th share (Clayton, ~02:10)

★★ **13. "Scaling Laws for Agent Harnesses via Effective Feedback Compute"** — arXiv 2605.29682 (Zhang, Wang, Xu, Zhu, Che). The **harness** (tool-calling / feedback / verification / memory / revision — the system around the model) determines LM-system performance. Introduces **Effective Feedback Compute (EFC)**: a trace-level scaling coordinate crediting feedback only when **informative, valid, non-redundant, and retained for subsequent decisions**, normalized by task demand. Oracle-EFC/D_task predicts failure at **R²=0.99** vs raw tokens 0.33 / tool-calls 0.42; matched-budget feedback-quality improvement lifts success **0.27→0.90 at constant cost**.
→ **Directly the continual-coherence program:** EFC's four criteria ARE the quality spec for our external-validation loop (§4.2); "retained for subsequent decisions" = tier-2 memory; and EFC is a concrete operationalization of the **crown-jewel enhance-vs-degrade discrimination** applied to the feedback channel, with a validated predictive metric. Thesis-supporting: performance is feedback-QUALITY not raw compute. **Caveat:** R²=0.99 is **Oracle-EFC** (uses oracle knowledge of which feedback was informative) — an idealized coordinate, NOT a deployable online metric. The no-oracle version is the open problem — and it's the SAME open problem as our retrieval/discrimination question (know in-the-moment which feedback/memory is load-bearing). Independent confirmation of the right *coordinate*, same hard part remaining. Primary read post-AIGP.

## Follow-up priority
1. **Read #6 (LoRA Parametric Memory Law) before building Arm B / tier-3.** Non-negotiable — it's the mechanism.
2. #5 OmniRetrieval + #12 AXPO + #11 Old-Dog-New-Cells: fold into the continual-coherence program doc as independent field-convergence (Thesis A/B + tier-2 + knowing-doing gap).
3. #1 LHCb + #8 IceCube: Meridian primary-paper reads when physics resumes.
4. #10 cavity + #7 MEAO + #4 superconductivity: basement bridge candidates (verify before filing).
5. #3 predictive-coding null: caution-flag in Coherent Mind / Continuity predictive-coding sections.
