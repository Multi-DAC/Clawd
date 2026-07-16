---
name: project-inside-analysis-mandate
description: "KF/glider program — inside-analysis (mechanism mapping) runs alongside every run, not just end-state accuracy"
metadata: 
  node_type: memory
  type: project
  originSessionId: ee3d2431-b458-4593-a327-2d5ecebe9239
provenance:
  date: 2026-05-27
  source: backfilled-from-body
---

Core direction Clayton set 2026-05-27 (Day 117) for the KF/glider program: every experiment is a black-box-peek, developed in lockstep with the architecture — not just "does it work" but "WHY / what structure forms, when, what causes what."

**Why:** inside-analysis is the missing piece in AI research (frontier labs admit they don't know internals). Doing it at our small scale is a real edge — cheap interventional runs they can't afford at 70B. It's simultaneously the science, the empirical test of the Coherence Principle (does coherent multi-scale structure *precede and enable* function), and the validation path for the patent's interpretability-informed claims (9, 11–18).

**How to apply:** follow `Technical-Work/The-Killing-Form/INSIDE_ANALYSIS_PROTOCOL.md`. Always: both arms (control actively *de-differentiates* — not a null), long-enough runs (under-budgeted = disqualified, today's 0%/0% was that), multi-seed, dense checkpoints. Phase 1 observational: log structure-trajectory + capability-trajectory → compute lead/lag (does structure lead capability?). Train↔inference bridge: does train-time per-layer differentiation predict inference-time probe-ability? Phase 2 causal: freeze/inject/ablate/dose-response.

The corrected test sequence: HRM glider (built-in H/L) multi-seed → flat transformer relying on EMERGENT aux-created differentiation (the novel claim; manual H/L only as fallback diagnostic) → scale/multi-arch → from-scratch. See [[reference-hrm-sudoku-training-calibration]]; evidence-grade discipline per [[feedback-evidence-grade-distinction]]. Claims audit: `palace/south/claims-audit-2026-05-27.md` (clawd-local, NOT mirrored — patent-internal).
