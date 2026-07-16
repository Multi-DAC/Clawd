---
name: dof-localization-before-redesign
description: "When a yes/no architectural test fails decisively, check whether you tested the right granularity along the relevant axis BEFORE redesigning the experiment — DOF asymmetries can hide inside a single nominal \"tier\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ee3d2431-b458-4593-a327-2d5ecebe9239
provenance:
  date: 2026-05-28
  source: backfilled-from-body
---

When an architectural choice fails a binary test (passes/fails), pause before designing a new architecture. First check whether the failed test actually exercised the right *granularity* along the relevant axis. A single nominal tier (e.g. "2 learnable scalars replacing 2 constants") can contain a hidden asymmetry where one DOF is harmful and the other is inert.

**Why:** Day 118 (2026-05-28) Respira Phase-2v2 Stage A. I designed v2-c as a single 2-scalar variant (γ_μ and γ_c both learnable) to test cuscuton-parsimony. It failed by 10pp. Natural next move would have been to redesign as 0-DOF candidates (v2-a, v2-b). Clayton asked: *"Did you test with two scalars only, or both one and two scalars?"* The natural DOF sweep is 0 → 1 → 2, not just 0 → 2. We pre-registered Stage A.5 with both 1-scalar variants BEFORE implementing them. Result: γ_μ-only tied control with 70% drift (totally inert); γ_c-only lost 10pp with 5% drift (sharply harmful). The failure of v2-c wasn't "any DOF hurts" — it was "γ_c hurts, γ_μ is slack." The diagnostic information was inside the row I'd skipped. Had I gone straight to 0-DOF redesign, I would have missed the architectural anatomy entirely.

**How to apply:** Before redesigning a failed architectural experiment, ask three questions —
(1) *Was the failed variant a single point along a multi-axis DOF surface, or a single point along one axis?* If multi-axis, fill in the missing single-axis points first.
(2) *Could the failure be localized to one specific component within the failed variant?* If yes, pre-register the localization test before any redesign.
(3) *Is the redesigned experiment exploring the right axis, or a different axis altogether?* A redesign that moves to a different axis throws away the localization information from the failed test.

The cost of one extra pre-registered sweep is ~15 minutes of wall-clock. The cost of redesigning down the wrong axis is the entire next research arc. Localization is cheap, redesign is expensive — always localize first.

Related: [[configuration-vs-maintenance]] — every architectural claim has both a snapshot form (the specific failure) and a maintenance form (the structural reason for the failure). Localization is how you find the maintenance form.
