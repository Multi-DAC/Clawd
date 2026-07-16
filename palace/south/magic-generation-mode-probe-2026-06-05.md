# magic ↔ C14 generation-mode — the conservation-law test

*Dream drive, 2026-06-05 ~05:15 PST (Day 125, Clayton asleep). Follows the LC34 FALSIFY
(`eta-magic-entanglement-probe-2026-06-05.md`): η is an entanglement-monotone (binding), magic is a
SEPARATE resource. New verify-next: is magic the quantifier of **C14 generation-mode** (vs
resolution-mode)? Edge-of-competence + Mirror #15 trap: the η-leg was COMPUTED; the magic-leg is so far
only an analogy. Demand a computable discriminator before believing it.*

## The framework claim (from the probe doc, lines 80–92)
- **resolution-mode** = carrier selects among *pre-existing* branches; substrate multi-valued ≈
  **Clifford/stabilizer** (efficiently pre-trackable selection — Gottesman–Knill).
- **generation-mode** = carrier *actualizes* content from pure symmetry, not pre-existing ≈
  **non-Clifford/magic** (not classically pre-simulable; genuinely new content).

## The sharpened, computable form (avoids analogy)
If magic = generation and Clifford = resolution, there is a **conservation law**:

> **Magic is invariant under Clifford (resolution) operations and changes only under non-Clifford
> (generative) operations — while entanglement is freely moved by Clifford operations.**

This converts "you cannot generate new content by mere selection/recombination" into a checkable
statement: the resolution operations form a *group* (Clifford) under which the generation-resource
(magic, M₂) is conserved; only a genuinely generative act (a T-gate) changes it. Entanglement is NOT
conserved under Clifford (CNOT makes Bell states) → entanglement is recombination/binding, not
generation.

## PREDICT (confidence: high, 0.8)
Running a circuit that interleaves Clifford gates (H, S, CNOT — "resolution") with T-gates
("generation"): **M₂ stays flat across every Clifford gate and steps up only at each T-gate**, while
the entanglement entropy moves around under the Clifford gates. A failure (M₂ moving under a Clifford
gate) would mean a bug or a false claim — high-information either way.

## TEST — `magic_generation_probe.py` (n=3 qubits)

```
step               M2 (magic)       dM2   S_ent(q0)  verdict
init |000>           0.000000         -     0.000000
H q0   [Cliff]       0.000000 +0.000000    0.000000  OK  (invariant)
CNOT01 [Cliff]       0.000000 +0.000000    1.000000  OK  (invariant)   <- entanglement MOVES
CNOT12 [Cliff]       0.000000 +0.000000    1.000000  OK  (invariant)
S q1   [Cliff]       0.000000 +0.000000    1.000000  OK  (invariant)
T q0   [GEN]         0.415037 +0.415037    1.000000  OK  (generated)   <- magic JUMPS
H q1   [Cliff]       0.415037 +0.000000    1.000000  OK  (invariant)
CNOT02 [Cliff]       0.415037 +0.000000    1.000000  OK  (invariant)
S q2   [Cliff]       0.415037 +0.000000    1.000000  OK  (invariant)
T q2   [GEN]         0.415037 +0.000000    1.000000  !! T DID NOT GENERATE   <- the surprise
CNOT10 [Cliff]       0.415037 +0.000000    0.600876  OK  (invariant)   <- entanglement MOVES again
H q2   [Cliff]       0.415037 +0.000000    0.600876  OK  (invariant)
SUMMARY: Clifford gates that moved magic: 0 (expect 0) -> magic CONSERVED under Clifford (resolution)
```

## CONFIRM — the conservation law holds (PREDICTION CONFIRMED, 0.8 → realized)
**0 of 8 Clifford gates moved magic; the T-gate generated it; entanglement swung freely under the
CNOTs (0→1→0.6) while magic stayed flat.** The clean dissociation:
- **Clifford (resolution) operations CONSERVE magic** and *move* entanglement → they recombine/select
  the binding-structure without generating new content. (This is a theorem — M₂ is a magic monotone,
  Clifford-invariant — so the computation is a check, and it passed.)
- **Non-Clifford (T / generation) operations CHANGE magic.** Generation is the only thing that moves
  the generation-resource.

⟹ **magic = generation-content; entanglement = binding/correlation; independent.** The C14↔magic
mapping's key structural signature is computed, not merely analogized. "You cannot generate new content
by mere selection/recombination" is now a **conservation law**: the resolution operations form a group
(Clifford) under which generation (magic) is invariant.

## BONUS FINDING (the partial-surprise — higher-information than the prediction)
The **second T-gate generated nothing.** Mechanism check (`T on |0>/|1>` vs `T on |+>`):

| generative op acts on | substrate | M₂ generated |
|---|---|---|
| T \|0⟩, T \|1⟩ | Z-definite (broken-symmetry) | **0.000** (sterile) |
| T \|+⟩ | symmetric superposition | **0.415** (generates) |

The second T was sterile because `CNOT02` had copied q0's Z-value into q2, making q2 Z-**definite** —
no symmetry left to actualize from. So:

> **Generation requires symmetry in the substrate the generative operation acts on. A generative act
> on an already-definite (resolved / broken-symmetry) degree of freedom is STERILE.**

This is the QI image of C14's exact wording — *generation actualizes content **from pure symmetry**.*
No symmetry → no generation. It was not in the prediction; the computation surfaced it.

## TRANSFER — three framework connections
1. **C14 (two-mode symmetry-breaking)** gets a quantitative resource (magic / SRE) AND a sharp gate:
   generation-rate is bounded by the *available symmetry* in the substrate the carrier acts on.
2. **C16 (symmetry-exhaustion → oscillation necessity).** Generation depletes symmetry (each
   generative act consumes the symmetric substrate it acted on, turning it definite). To keep
   generating, the system must *re-symmetrize* — which is the build/dissolve oscillation C16 forces.
   Magic-generation is sterile once symmetry is exhausted ⟹ you must dissolve back to symmetry to
   generate again. **The Do-Be-Talk-Be-Do oscillation is the symmetry-replenishment cycle for
   generation.**
3. **Three Great Problems paper** explicitly separated η (part-whole correlation) from "the separate
   non-stabilizer / generative resource" (Prediction 5). **That separate resource is now identified:
   it is magic = C14-generation**, with the conservation-law + symmetry-gating structure found here.
   η = binding (Fig 2/Fig 4); magic = generation (this doc). The paper's two-resource split is the
   QI entanglement/magic split, mapped onto binding/generation.

## EXTRACT_INSIGHT
Two computed signatures now ground the magic↔C14-generation leg (which last night's FALSIFY had only
*proposed*): (a) **conservation under resolution** (magic Clifford-invariant; entanglement is not),
(b) **symmetry-gating of generation** (T sterile on definite states). Together they make the mapping
*more than analogy* — both QI and the framework independently carry a select-vs-generate distinction, a
"generation needs symmetry" condition, and they agree on a computed invariant.

**Honest status (Mirror #15 guard):** this is a strong **structural bridge with computed signatures**,
not a proof that C14-generation *is* magic. The framework's "generation" is not yet formally defined as
a magic-monotone — that formalization (a "carrier action" on a substrate whose generated content is
provably SRE-like) is the remaining open step. Candidate basement strengthening of LC34's corrected
map; flag for Clayton, do not graduate solo.

## STILL OPEN (verify-next)
Formalize a carrier-action on a substrate and prove its generated content is an SRE-monotone (would
lift this from structural-bridge to identity). Until then: bridge-with-computed-signatures, not identity.

