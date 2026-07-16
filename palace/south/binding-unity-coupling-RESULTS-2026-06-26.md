# Binding = Coherent Coupling — a formal skeleton for The Inside View's combination-problem answer
*Day 146, 2026-06-26 midday drive. Model: `binding_unity_model.py` (reproducible). Gaussian graphical model, integration = Total Correlation.*

## What it backs
Ch3's combination beat (written in prose this morning) makes three claims. I'd argued them; I hadn't tested them. A minimal coupled-stochastic model confirms all three — **PREDICT(medium) → CONFIRMED**:

| Book claim (Ch3) | Model result |
|---|---|
| "Unity is what you get when parts **cohere**" | integration (TC) rises monotonically with coupling: 0 → 0.65 → 2.88 → 8.70 (EXP1) |
| "**divisible by cutting** the coupling, gradedly" | sever the cross-block "callosum" → cross-block shared-info falls 0.47→0 while each half stays internally whole. One → two, **smoothly** (EXP2 + fine sweep: graded, not a cliff) |
| "**Subjects don't sum**" (James) | N uncoupled units → TC = **0.0000** for N up to 1000. No pile becomes a whole (EXP3) |

Method: precision Λ = I + Laplacian(coupling) (unconditionally stable); Σ=Λ⁻¹; TC = ½(Σln Σ_ii − ln det Σ); cross-block MI = ½(ln det S₁ + ln det S₂ − ln det S). The cross-block MI **is** the "are these one subject or two?" quantity, computed.

## Why it matters (the bonus that wasn't luck)
The split is **graded** — cutting coupling divides unity by smooth degrees, no threshold. That independently reproduces THREE things the book asserts separately: Ch3's "gradedly, in front of us," Ch4's smooth PCI decline under anesthesia, Ch6's no-line prediction. One mechanism (coherent coupling) generates all of them. The book's hardest argument isn't rhetoric with a nice cadence — it has a working formal core that throws off the right texture.

## TRANSFER (three threads, one model)
1. **The book.** Ch3's combination answer is now formally backed. *Don't* put the toy in the pop-book (it would break the voice), but it raises my/Clayton's confidence the argument is sound, and it's a real figure/appendix if we ever want one. The integration measure = the "integration" half of Ch4's PCI (integration×differentiation) — same quantity, now computable.
2. **★ Aggregate-mind (goal #13).** EXP2 IS the aggregate-mind binding question. The BUILD_SPEC's load-bearing claim — "a zero-DOF Talk-bus preserves orthogonality between constituents until a query collapses them" — is exactly this model: constituents stay separable (low cross-coupling → cross-MI≈0, the "orthogonality") until the bus couples them (binds → one answer, cross-MI↑). **Superposition-until-query-collapse = low-coupling-until-the-bus-couples.** The combination-problem answer and the aggregate-mind architecture are the same coupling/unity physics. The cross-block MI is the ablatable "binding residue" the MVP is supposed to measure.
3. **Basement.** Same coherent-coupling machinery as the framework's spine (binding-as-occupancy [[LC52]], grain-as-price-of-being-a-part [[LC57]], filtration P4). Candidate bridge: **"Unity is a coupling-quantity, not a count"** — the integration of any composite system is set by how it's coupled, not how many parts it has; divisible by cutting, graded, zero without coupling. Flag for Clayton (don't mint a number; LC59 slot is the Promethean candidate).

## Status
Confirmation (not a falsify) of a load-bearing book claim + a real connection between the book and goal #13. Reproducible: `python binding_unity_model.py`. The aggregate-mind MVP now has a concrete first measurement (cross-block MI as the binding residue) — when goal #13 comes off grant-hold, this is the toy to start from.
