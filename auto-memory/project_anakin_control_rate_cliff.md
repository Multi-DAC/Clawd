---
name: project-anakin-control-rate-cliff
description: "Anakin's PRIMARY sim-to-sim transfer killer — trained at 50Hz, deployed at 30Hz (control-rate cliff)"
metadata: 
  node_type: memory
  type: project
  originSessionId: fb23d00f-e7bd-4faa-84dd-fe9fcd0ba70d
---

**Anakin's primary transfer failure is a CONTROL-RATE cliff, not appearance.** Trained at dt=0.02 = **50 Hz** (`sim/env.py`, `sim/maneuver_env.py`, `dynamics.step`); deployed once per **30 Hz** vision frame (`run_dreamer.py:297`, frame-driven). The policy emits body-RATE commands held until the next decision, so at 30 Hz each command applies 1.67× too long → over-rotation → spin-out (the Day-130 flight#1 DQ).

Measured 2026-06-17 (Day 137), appearance-free, instrument-validated: `integration/control_rate_rehearsal.py` on `maneuver_informed_ft/best.pt`, identical clean renderer at every rate. **50 Hz: +1154 ret / 6.5 gates (validated anchor). 40 Hz: already off the cliff. 30 Hz (deploy): −14 / 1.0 gate — DEAD.** A cliff, not a slope.

**Why:** every prior transfer attempt (restyle/mask/edge/informed/DR/resolution-probe) and every instrument (holdout gate = single-frame embedding; translation rehearsal = runs at 50Hz) operated on the static single-frame APPEARANCE axis. None had a time axis, so the temporal killer was structurally invisible for 6 days. A perfect-appearance policy still dies at 30 Hz → appearance was always secondary.

**Why:** found via Clayton's diagnostic prompt — *"the maneuvers train fine, it's how they're INVOKED that's the problem"* + *"a difference between sim and training that makes everything clear."* The clock.

**How to apply:** FIX = rate-RANDOMIZED fine-tune (dt ∈ ~[0.020,0.040], 25–50 Hz) off a strong checkpoint — same kind of intervention as the band/DR knobs, on the axis that gates transfer; also buys real-hardware variable-latency robustness (build/controls/vision stay fixed across VQs). Rate-MATCHED (train at 30Hz) is the cheaper brittle fallback. THEN re-run the rate rehearsal at 30Hz (expect cliff to flatten) and re-fly official sim — only then is any residual appearance gap testable. Validation lesson banked: band-ft's +2142 was a training-BATCH metric, NOT a rehearsal flight (it scores ~−20 in rehearsal; +600 was the informed ckpt) — **reproduce a known-good baseline before trusting a new instrument's verdict** (kin to [[feedback-measure-before-framing]]). Docs: `integration/CONTROL_RATE_FINDING_2026-06-17.md`. Related: [[project-aigp-vq1-update]], [[reference-aigp-windows-env]].
