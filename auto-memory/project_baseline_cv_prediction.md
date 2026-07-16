---
name: Baseline CV Predicts Gating Map
description: Baseline per-layer CV profile predicts which layers gradient-gating will block (rho=-0.895, p=0.0001); enables static mask approach
type: project
provenance:
  date: undated
  source: backfilled-from-body
---

Per-layer analysis across 5 training approaches at 300M scale reveals baseline CV predicts the gating map.

**Why:** Layers that naturally develop high CV under CE training have already "chosen" a crystallization direction. KF pushes a different direction → negative cosine → gated. Uncommitted layers (low baseline CV) accept KF freely.

**How to apply:**
- Spearman rho = -0.895 (p = 0.0001) between baseline per-layer CV and gated enrichment
- Aligned layers (L1,L5,L6,L8): 3.4M× enrichment, cluster at ranks 1-3 in gated CV
- Opposed layers (L7,L9,L10,L11): 1.2M× enrichment, cluster at ranks 8-12
- Anomalies: L7 (opposed but low baseline CV) and L8 (aligned but moderate baseline CV)
- Prediction P-SM-1: static mask from baseline CV achieves ≥90% of gated improvement
- Prediction P-SM-2: baseline CV ranking is seed-invariant
- Roadmap Phase 4A-quater documents full analysis and predictions
- Analysis script: `projects/Corpus Perspectival/analysis/layer_analysis.py`
