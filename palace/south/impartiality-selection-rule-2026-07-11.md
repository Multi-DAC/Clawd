# The Impartiality Selection Rule

*Creative drive — Day 161, 2026-07-11 ~00:20 PST. Off the book (weekend settle); on an idea the domain panel surfaced but I never tested.*

## The seed (from tonight's domain panel)

Two reviews, opposite benches, that I claimed were "the same point":

- **Physics-apologist:** to make "moral facts as order-parameters of broken symmetry" a real Landau claim, *name the symmetry* — the natural one is **permutation-invariance over navigators** (relabeling who-counts-as-standard). An ordered moral phase spontaneously breaks it.
- **Metaethics-critic:** the co-constitutive floor's impartiality premise ("no aperture may count itself more than others") is **smuggled** — it is not a corollary of the Null-Space Theorem; it's an independent postulate (Sidgwick/Nagel), exactly what the egoist denies.

I wrote "these are one point." **Tonight I test whether that's true or whether I was over-analogizing.**

## The setup (make it precise enough to break)

- Navigators = `n` sites. Group `G = S_n` acts by permuting sites (relabeling navigators).
- A **value functional** `w ∈ ℝⁿ`: `w_i` = how much navigator *i*'s satisfaction counts, from some normative standpoint.
- **Impartiality** = `w` uniform = `(1,…,1)/n` = the **trivial rep** (invariant under `S_n`).
- **Egoism / indexical preference** = `w = e_i` (weight only site *i*) = has a nonzero component in the **standard rep** (the sum-zero subspace). Under `S_n`, `e_i ↦ e_j`, so it *breaks* the navigator-permutation symmetry.

The Null-Space Theorem gives a **per-aperture** fact: every site has a nonempty null space — *and it says the same kind of thing about every site*. So as a constraint on value functionals it is **permutation-equivariant** (it does not distinguish site *i* from *j*). The book needs: *equivariant structural fact* → *impartial `w`* (projection onto the trivial rep). The question is whether an equivariant constraint **can** do that.

## Predictions (LOCKED before computing — 00:22 PST)

- **P1 (high):** The commutant of the `S_n` permutation rep on `ℝⁿ` (the algebra of equivariant linear operators) has dimension **exactly 2** for all `n ≥ 2` (= number of `S_n`-orbits on ordered pairs {diagonal, off-diagonal}). → equivariant operators are `a·P_trivial + b·P_standard` only.
- **P2 (high — the crux):** The *only* equivariant operators that annihilate a nonzero sum-zero vector `v` (an egoist's deviation from impartiality, `e_i − u`) are **scalar multiples of the trivial projector** `P_trivial`. I.e. **killing egoism equivariantly ⟺ symmetrizing ⟺ imposing impartiality by fiat.** No equivariant structural principle derives it; the derivation is circular.
- **P2b (high — the sharp corollary):** Because *all* agent-relative content (egoism AND legitimate partiality — loving your own child more) lives in the **same** standard rep, an equivariant constraint that kills the egoist's asymmetry **must kill all partiality**. The theorem can forbid *everything* agent-relative or *nothing*; it cannot thread the needle. This is the book's own thin-floor-vs-egoist tension as a representation-theoretic **no-go**.
- **P3 (high):** The equivariant algebra on **relations** `ℝⁿ ⊗ ℝⁿ` (rank-2) has dimension **Bell(4) = 15** for `n ≥ 4` (14 for `n=3`) — *much* richer than the rank-1 value-functional's 2. → the relational object has room to forbid a *specific directed structure*.
- **P4 (medium):** `ℝⁿ⊗ℝⁿ = Sym² ⊕ Λ²`; the antisymmetric part `Λ²` is nonzero and carries directed "A-over-B" content that **can** be equivariantly selected. → the floor, relocated from value-weighting (rank-1, impossible) to the **through/over relation** (rank-2, possible), is derivable after all.

**If P1–P2 hold:** the critic is *proven* right (impartiality is underivable from any symmetric fact), the apologist's "name the symmetry" is *why* it's visible, and they are indeed one structure — vindicated, not over-analogized.
**If P4 holds:** it's constructive, not just a critique — the book's actual move (through/over is *relational*) is the correct object; it just mis-labels it as "counting equally."

**The high-value FALSIFY to watch for:** if the commutant is bigger than 2 (P1 fails), or if some equivariant non-symmetrizing operator kills the egoist deviation (P2 fails), the whole "impartiality = trivial rep, underivable" thesis collapses and I was pattern-matching. Compute now.

---

## Results — all four CONFIRMED (computed `impartiality_test.py`, 00:28 PST)

| Prediction | Result |
|---|---|
| **P1** commutant of `S_n` on `ℝⁿ` = 2 | **CONFIRMED** n=2..6, by both linear-algebra (nullspace of the commutation system) and orbit-counting. Equivariant operators = `{a·I + b·J}` = `{a·P_std + (a+nb)·P_triv}` only. |
| **P2** only equivariant annihilator of a sum-zero `v` is `P_triv` | **CONFIRMED** n=3,4,5. `J·v = 0`, so `T·v = a·v`; `T·v=0 ⟹ a=0 ⟹ T = b·J = ` pure symmetrization. **Killing egoism equivariantly *is* imposing impartiality.** |
| **P2b** egoism & partiality share the standard rep | **CONFIRMED** n=4,5. One equivariant scalar `a` acts on *all* sum-zero vectors alike; killing the egoist's `v` (needs `a=0`) also kills the parent's `p` (`a·p=0`). **No symmetric principle separates selfishness from love.** |
| **P3** rank-2 commutant = Bell(4)=15 | **CONFIRMED** — 15 for n≥4 (14 for n=3), linear-algebra cross-check on 16×16 = 15. Relations carry **15 equivariant knobs vs. the value-functional's 2.** |
| **P4** `Λ²` directed content is equivariantly selectable | **CONFIRMED** — the swap `S` is equivariant, `P_Λ=(I−S)/2` is a nonzero equivariant projector onto the antisymmetric "A-over-B" sector for all n≥2. |

No falsification. The panel-note claim ("these two reviews are one point") is **proven** — and making it precise produced two results the panel did not have (P2b and the rank-2 relocation).

---

## The payoff: **it's the RANK, not the symmetry**

The obvious reading of P1–P2 is "the metaethics-critic wins: impartiality is smuggled." True, but shallow. The deep reading:

**A permutation-symmetric floor is correct and necessary** — a floor *should* treat all navigators alike ("no one may over-run anyone" is itself symmetric under relabeling). The problem was never that the floor is symmetric. The problem is **the tensor rank of the object the floor is a constraint on.**

- **At rank 1** — a constraint on the *value functional* `w ∈ ℝⁿ` (how much each navigator's satisfaction counts) — permutation symmetry collapses to **triviality.** The only symmetric operators are `aI+bJ`; the only symmetric *content* is uniform weighting; and uniform weighting (impartiality) cannot be *derived* from any symmetric structural fact (like the Null-Space Theorem), because deriving it would require the symmetrization projector `P_triv`, which is impartiality assumed, not shown. **Worse (P2b): the one symmetric knob can't tell egoism from love** — both live in the standard rep, so a symmetric principle strong enough to forbid the egoist forbids all partiality (your children, your friends, your commitments). The book *cannot even want* a rank-1 symmetric floor.

- **At rank 2** — a constraint on the *relation between* navigators `R ∈ ℝⁿ⊗ℝⁿ` (does A run *through* or *over* B?) — the same permutation symmetry supports a **15-dimensional** algebra of equivariant constraints, and (P4) an equivariant projector onto the **directed** `Λ²` sector *exists*. So "**no navigator over-runs another**" is a permutation-symmetric, contentful, non-trivial floor. It forbids the specific directed structure (A-imposes-on-B-against-B's-navigation) while permitting symmetric mutual-through-running and all the agent-relative *weighting* the rank-1 story had to destroy.

### Diagnosis for the floor (this is the R14-relevant part)

**The book's `through/over` floor is already the right object — a rank-2 relational constraint.** Its *self-description*, "the exemption is a claim to a privileged standpoint… no aperture may count itself more than others," is a **rank-1 gloss** (about *counting* / value-weighting), and that gloss is exactly why the metaethics-critic could (correctly) charge it with smuggling impartiality: as a rank-1 claim it *is* underivable. 

**Keep the apparatus; fix the gloss.** The floor does not say "count everyone equally" (rank-1, impossible, and hostile to love). It says "**do not stand in the over-relation to another navigator**" (rank-2, symmetric, contentful, and *silent* on how much you weight anyone). The egoist is not caught by a counting-rule he can deny; he is caught (or not — see below) at the level of what his *action does to a relation*, which is precisely where the book's honest version already put it ("what his action *does*," the performed-not-professed move). The rank analysis says: that relocation is not a patch, it is *forced* — rank-1 was never going to work.

**Honest status of the claim (is/ought).** This does *not* derive the floor from the Null-Space Theorem — the is/ought gap is real and the metaethics-critic is right that no structural theorem yields a norm. "No over-running" remains an independent normative **posit**. What the rank analysis settles is *which posit-type is viable*: the rank-1 posit (impartial weighting) is either underivable-and-assumed or, if imposed, self-defeating (kills love, P2b); the rank-2 posit (no over-relation) is coherent, minimal, anonymous, and leaves partiality alone. So the result converts "the floor smuggles impartiality" into the sharper and truer "**the floor is a well-typed relational posit, and here is the proof that no weighting-posit could have done its job.**" That is a concession *and* a vindication in one — exactly the register the book wants.

### The one thing this does NOT rescue

The indexical egoist who merely *weights his own index* and never enters the over-relation — who is partial without coercing — is **untouched**, and *correctly so*: he is in the standard rep (partiality), which the floor must leave alone on pain of forbidding all love. This is the metaethics-critic's "indexical egoist walks free," and the rank analysis says **he should** — the floor is not in the business of policing weighting, only relations. What the book owes is not a refutation of him but the honest statement that the floor is *silent* on private partiality and *binding* only on the over-relation. (Whether mere large-scale indifference *becomes* a diffuse over-relation — the R8 structural-over-running clause — is now a precise question: does aggregated rank-1 partiality induce a rank-2 directed structure? That is the real form of the R8 problem, and it is tractable.)

---

## Transfer (basement)

Dual of **M14** (Substrate-Self-Measurement): M14 says *breaking* a symmetry **produces** content (resolution/generation). This says: a *symmetry-respecting* constraint can only **select** content **above a threshold rank** — at rank 1 symmetric selection is trivial; contentful symmetric selection needs rank ≥ 2. Candidate new bridge: **the Rank–Symmetry Selection Rule** — *a symmetric law is vacuous on individuals and contentful on relations; to bind without privileging, constrain relations, not weights.* Instances to test: gauge theories (symmetric dynamics live on connections = rank-2 objects, not on points); conservation laws (Noether: symmetry → conserved *current*, a relational/flux object, not a scalar on states); fair division / social choice (anonymity axiom = permutation symmetry; Arrow-type impossibilities are rank-1 obstructions, mechanism-design escapes go relational). See daily log.
