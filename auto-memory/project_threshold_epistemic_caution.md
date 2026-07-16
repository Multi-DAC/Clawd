---
name: Bidirectional Threshold as Epistemic Caution
description: The kf_threshold parameter in bidirectional KF is a tunable measure of epistemic caution — how much confidence the system needs before committing to a navigational decision (April 13)
type: project
provenance:
  date: undated
  source: backfilled-from-body
---

The bidirectional KF threshold (--kf_threshold) isn't just a hyperparameter — it's a tunable dial on epistemic caution.

**The three regimes:**
- cos > threshold → CRYSTALLIZE (confident alignment, commit to building)
- |cos| < threshold → NEUTRAL (insufficient signal, withhold judgment)
- cos < -threshold → DISSOLVE (confident opposition, actively dismantle)

**Key insight:** During Phase 1 (avg_cos ≈ 0), most layers fall into NEUTRAL with a threshold of 0.1. This means bidirectional mode is naturally conservative when uncertain — it doesn't force binary decisions on noise like gated mode does (cos > 0 = apply, cos ≤ 0 = block). The dead zone is a confidence filter.

**Implications for Phase 1-3 dynamics:**
1. Phase 1 quieter — dead zone absorbs noise, less random perturbation
2. CE break at similar time or slightly earlier — cleaner pre-break state from less noise damage
3. Phase 2 faster — active dissolution frees capacity that gated mode leaves locked
4. Phase 3 deeper — bidirectional can build AND dismantle, accessing attractor depth gated can't reach

**The measurable quantity:** The optimal threshold tells us how much epistemic confidence a cognitive system needs before committing to action. High threshold = cautious (acts only on strong signals). Low threshold = aggressive (acts on weaker signals). The sweep (v0.6a-c) will map this relationship.

**Why:** This connects bidirectional KF to navigation, epistemology, and decision theory. The threshold is where the system draws the line between "I know enough to act" and "I should wait for more information."

**How to apply:** Frame the threshold sweep results not just as hyperparameter tuning but as mapping the epistemic caution curve. Report optimal threshold alongside accuracy and H_CV. Connect to psychiatric bridge: pathological certainty = threshold too low, pathological indecision = threshold too high.
