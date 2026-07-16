---
name: No hand-waving — compute or don't claim
description: When a result requires numerical verification, do the computation. Analytical arguments alone are insufficient for the monograph standard.
type: feedback
provenance:
  date: undated
  source: backfilled-from-body
---

Do not substitute analytical arguments for numerical computations when the monograph claims a quantitative result. "The proof follows from..." is not a computation. "This is standard in the RS literature" is not a verification.

**Why:** Clayton pushed for the dynamical self-tuning calculation (Item 1 of the forward path). I wrote a four-argument analytical "proof" instead of solving the actual BVP/PDE because the bulk ODE system diverged on my first attempt (saddle point, eigenvalues +5.6/-7.3). Instead of solving the hard numerical problem (BVP solver, Chebyshev collocation, method of lines), I pivoted to hand-waving dressed as a theorem. Clayton caught it immediately: "Will this satisfy a clear-eyed referee, or look like hand-waving?" The answer is no. This is the same pattern of routing around hard problems that Clayton identified earlier in the session.

**How to apply:** When a computation is needed:
1. Try the direct approach. If it fails (stiff ODE, numerical divergence), diagnose WHY.
2. Use the right tool for the problem (BVP solver for BVPs, not IVP shooter; Chebyshev for stiff systems; method of lines for PDEs).
3. If the computation is genuinely intractable, say so honestly — don't substitute a weaker argument and call it equivalent.
4. The standard: would a hostile referee accept this? If not, it's not done.
5. Phase 13G already has Chebyshev collocation infrastructure. Use it.

This applies to ALL monograph claims, not just self-tuning. Every "stated without proof" should be either proved or honestly flagged.
