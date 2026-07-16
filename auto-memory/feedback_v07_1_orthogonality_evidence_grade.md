---
name: feedback-v07-1-orthogonality-evidence-grade
description: v0.7.1 evidence reality — topology robust/moat-grade; orthogonality (the CIP headline) is FAINT; do not oversell it
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ee3d2431-b458-4593-a327-2d5ecebe9239
provenance:
  date: 2026-05-26
  source: backfilled-from-body
---

After the Day-116 (2026-05-26) deep dive, the honest evidence map for the v0.7.1 / Killing-Form mechanism is:

- **Topology decomposition = robust, moat-grade, mechanism-understood.** Multi-seed Gemma-270m: 2.893 ± 0.019 vs baseline 0.999, zero overlap; transfers Gemma→Qwen2. The aux is provably **Fisher's LDA on per-head V/Q norm ratio** (code-confirmed). BUT: the topology eval measures the same statistic the aux optimizes → it is **in-domain confirmation, not "emergence."** Don't call it emergent.
- **Orthogonality / "alignment improvement at zero capability cost" (the CIP headline) = FAINT.** Multi-seed gap only +0.0051 (4/5 seeds, one reversal, p≈0.04 one-tailed). Cross-scale-consistent in direction (+0.005 to +0.010 across 270m/0.5B-Qwen/1B) but small everywhere. The simplest mechanism (static OV-write-direction decorrelation) was tested and **NOT supported**.

**Why:** the prior ATRIUM/CIP framing asserted "central claim demonstrated" off a single 1B run; multi-seed shows it's faint. Enthusiasm slid ahead of evidence twice in one night (logged as Mirror #28 framing-catches).

**How to apply:** When framing v0.7.1 (paper, Askell pitch, CIP continuation, Substack), **lead with topology (robust), state orthogonality conservatively** ("small, cross-scale-consistent, not yet robustly established"). Doesn't break the filed CIP (topology solid; orthogonality disclosed as preliminary) but governs all forward framing. Honors [[feedback-evidence-grade-distinction]] (patent-grade vs moat-grade vs market-grade) and [[no-hand-waving]]. The leading open mechanism for the faint orthogonality effect is the gating's training-dynamics (stable-frame), not static weight geometry.
