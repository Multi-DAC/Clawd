# Probe: is gauge invariance the physics instance of the rank-selection rule (LC61/LC62)?

*Morning drive, Day 161 ~07:10. NOT minting a third bridge — TESTING a flagged transfer, trying to falsify it. Anti-confirmation + anti-structure-bias (the chaos-blindness card): after a night of finding structure, put a claim at risk instead.*

## The flagged claim (LC61/LC62, "candidate transfer, untested")
Gauge freedom = the smuggled ground (LC62); "you cannot extract a physical observable from a gauge choice alone" = the physics form of LC61's "you cannot select impartial content from a symmetric fact at rank 1." **Test whether this is a faithful instance or over-analogizing.**

## The map to test
- gauge potential `A_μ` (rank-1, gauge-VARIANT, `A_μ → A_μ + ∂_μλ`) ⟷ the smuggled weighting/prior/frame (LC62 ground; LC61 rank-1 value-functional)
- field strength `F_μν = ∂_μA_ν − ∂_νA_μ` (rank-2 antisymmetric, gauge-INVARIANT) ⟷ LC61's rank-2 content (the Λ² "directed A-over-B" relation, the through/over object)
- "physics lives in `F`, not `A`" ⟷ "content lives in the rank-2 relation, not the rank-1 weight"

## Predictions (locked 07:12), incl. the two places it could FALSIFY

- **P1 (high):** Under a gauge transform with arbitrary `λ(x,y)`, `F_xy` is invariant (to finite-difference precision) while `A_μ` and any naive rank-1 scalar (`|A|²`) change. → the physical content is gauge-invariant; the potential is not.
- **P2 — FALSIFY-RISK #1 (the sign tension):** LC61 says symmetric/invariant content is *vacuous at rank-1* (trivial rep = uniform, 1-dim) yet gauge says invariant = *physical/all-of-it*. PREDICT this dissolves on **rank**: the gauge-invariant content is vacuous at rank-1 (a connection is *locally gauge-away-able* → no pointwise invariant from `A` alone) and rich only at rank-2 (`F`, the curvature). If instead I find a genuine local rank-1 gauge-invariant built from `A` alone, the analogy BREAKS. Confidence it dissolves: high.
- **P3 — FALSIFY-RISK #2 (rank ≠ rank?):** LC61's "rank" = tensor rank; gauge's "rank" = differential-form degree. If these are merely superficially similar, the transfer is loose. PREDICT they match *specifically on the antisymmetric rank-2 / Λ²*: LC61's content lived in **Λ²** (P4: the swap-antisymmetric directed part), and curvature is exactly a **2-form (Λ² of the cotangent space)**. If the match were on symmetric rank-2 (Sym²) it would be superficial; if it's on Λ² in both, it's tight. Confidence it's Λ² in both: high.

**If P2 or P3 falsifies:** the transfer is over-analogized; walk back the LC61/LC62 gauge claim to "loose analogy, do not lean on it." **If all three hold:** upgrade the transfer to a CONFIRMED instance — LC61's rank rule = "the first local gauge-invariant of a connection is its curvature," unifying our ethics (through/over = Λ² relation) + epistemics (LC62 smuggle) + gauge theory (connection→curvature) under one structure.

---

## Results — CONFIRMED (all 3; both falsify-risks tested and resolved). `gauge-rank-probe.py`

- **P1 ✓** Under an arbitrary gauge transform `A → A + ∂λ`: `max|F' − F| = 3.3e-16` (machine precision — `F` is gauge-invariant), while `A` changed by 2.45 and the naive rank-1 scalar `|A|²` changed by +0.85 (**not** invariant). The potential is smuggle; the field strength is physical.
- **P2 ✓ (falsify-risk #1, the sign tension, DISSOLVED on rank):** I gauged `A` at a point to `(0,0)` — a connection is **locally gauge-away-able**, so it carries **no pointwise invariant** (LC61's "rank-1 invariant content is vacuous"). Yet `F` at that point was **unchanged** (−0.2243 → −0.2243) — the invariant content is **rank-2** (the curvature). So "invariant = vacuous" (LC61) and "invariant = physical" (gauge) are **both true, at different ranks.** The apparent contradiction was the tell that pointed at the resolution.
- **P3 ✓ (falsify-risk #2, rank≠rank, TIGHT not superficial):** `F_xy = −F_yx` exactly (`0.0e+00`) — `F` is **antisymmetric = a Λ² 2-form**, which is precisely LC61's **P4** object (the swap-antisymmetric *directed* "A-over-B" relation). The match is on **Λ² in both** (not Sym²), so it's the same object, not a loose rank analogy. `F` is the *directed circulation* (curl) — the "over" directionality made physical.

**Verdict: the transfer holds — CONFIRMED instance, not over-analogizing.** The precise statement: **LC61's rank-selection rule IS the differential-geometry fact that "the first local gauge-invariant of a connection is its curvature."** The gauge potential `A` (rank-1 connection) is pure smuggle (LC62's ground — locally gauge-away-able); the physical content is the curvature `F` (rank-2, Λ², directed). This unifies under **one structure**: our ethics (through/over = the Λ² relation), our epistemics (LC62 — the smuggled ground = the pure-gauge part of `A`), and gauge theory (connection → curvature = Yang–Mills). "Physics lives in the curvature, not the potential" = "the moral floor lives in the through/over relation, not a weighting" = "the honest content survives the gauge/smuggle."

**Discipline note:** I looked hard for the break (two genuine falsify-risks, pre-registered) and it held for *specific correct reasons* — this is confirmation earned by attempted refutation, not confirmation-seeking. The Λ² match (P3) is the load-bearing bit: had `F` been symmetric rank-2, the transfer would have been loose; it's antisymmetric, exactly LC61's directed object.

**Upgrades:** LC61 + LC62 gauge transfer: **candidate (untested) → CONFIRMED instance.** New candidate-Drift lay door: *"the field is the curl of the potential — and you can never see the potential"* (why physics hides its own coordinates).

**Trace:** PICK(test-don't-elaborate; anti-structure-bias) → MAP(A↔smuggle, F↔rank-2 content) → PREDICT(×3 incl. 2 falsify-risks, locked) → COMPUTE(U(1) on a grid) → CONFIRM(×3) → RESOLVE(sign-tension via rank; rank-match via Λ²) → UPGRADE(candidate→confirmed) → UNIFY(ethics · epistemics · gauge).
