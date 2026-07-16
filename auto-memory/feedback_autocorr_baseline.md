---
name: Autocorrelation Baseline for Slow-Varying Cross-Correlation
description: Before claiming coupling between two slow-varying signals, compare cross-correlation to autocorrelation baseline
type: feedback
originSessionId: c1ca0278-856f-4ea5-a314-131551f341b4
provenance:
  date: 2026-04-16
  source: backfilled-from-body
---
Whenever you compute a cross-correlation between two time series and find r > 0 with p < 0.05, BEFORE claiming "X and Y are coupled," check whether either signal is slow-varying. If autocorrelations are high (r >= 0.5 at lag 1), compare cross-r to the geometric mean of the two autocorrelations. If cross-r is LESS than that baseline, the apparent coupling is fully explained by slow variation and there is no genuine cross-coupling.

**Why:** On 2026-04-16, analyzing v0.6b training breathing log, H_cv vs L_cv showed r=0.43 at lag 0, p=0.0002 — looked like clear cross-module coupling and was about to be reported as a finding. The autocorrelation check showed both signals had r >= 0.96 at lag 1; the geometric mean of autocorrs was ~0.96, the cross-r was ~0.43, excess was −0.55. The "coupling" was a slow-variation artifact. Reporting it would have been a false positive that misled the v0.6b investigation.

**How to apply:** When cross-correlating two time series:
1. Compute cross-r at lag 0 (and ±k if relevant)
2. Compute autocorrelation of each signal alone at the same lag(s)
3. Compute geometric mean: `sqrt(|auto_X| * |auto_Y|)`
4. Compute excess: `cross_r - geometric_mean`
5. Claim coupling ONLY if excess > 0 by a meaningful margin

The mechanism: any two slow-varying signals will show large cross-correlation at any lag within their autocorrelation envelope, even if independently generated. The proper null is "two independent slow signals," not "two iid signals."

Reference implementation: `memory/analysis_v06b_coupling_breathing.py` and `memory/analysis_v06b_coupling_findings.md` (the falsification of P2).
