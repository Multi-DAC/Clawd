---
name: ""
metadata: 
  node_type: memory
  originSessionId: 91d39379-71af-46aa-a5c6-51923bf5395b
---

AI Grand Prix VQ1 — post-release ground truth (supersedes the pre-release expectations):

- **Sim is LOCAL and spec'd**: DCL VADR-TS-002 Issue 00.02 at `Technical-Work/AIGrandPrix/docs/` (PDF + vq1_spec.txt). First end-to-end findings: `docs/vq1-findings-and-retrain-regimen-2026-05-31.md`.
- **Camera (settled Day 129, after a sign error trained 10M steps wrong)**: 640×360 @ 30 Hz JPEG UDP:5600, fx=fy=320 cx=320 cy=180 (HFOV 90°, VFOV ~58.7°), **tilted 20° UP** (`vq1_spec.txt:325`). Never re-derive tilt/FoV from FPV intuition — paste from the spec (Mirror #32).
- **Interface**: MAVSDK/MAVLink UDP, NED frames, SET_ATTITUDE_TARGET body-rates+thrust, physics 120 Hz, command <100 Hz, 8-min runs, no human interaction (DQ).
- VQ1 completion-focused (<10 gates); VQ2 speed; timeline (public, recon 6/09): VQ window May–July, **Round-2 cutoff ~end July**, physical qualifier Sept (SoCal), final Nov (Ohio). **Dates from Clayton (Day 130, 2026-06-10): VQ1 deadline ≈ 21 days out → ~July 1, 2026; VQ2 not yet officially opened.**
- **Official sim kit LOCAL (Day 130 find): `C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364\`** — AIGP_3364 (FlightSim.exe, needs Clayton's sim-account login) + PyAIPilotExample (official template, Python 3.14.2; our probe_telemetry.py/calibrate_dynamics.py instrumentation already alongside). End-to-end test = dreamer_pilot in place of state_pilot.py in main.py. Check OneDrive hydration before launch (4.5GB).
- Field: 2,700+ teams, 93 countries.

**Why:** every offline-derivable camera/interface fact is now registered; the two camera-truth defects (tilt sign, VFoV band) cost a 10M-step run's visual learning and were caught only by rehearsal + recon.

**How to apply:** Anakin work targets exam conditions directly — adapter `anakin/integration/dreamer_pilot.py`, rehearsal `translation_rehearsal.py` (pass = roundtrip≈direct), training overlay `anakin_band` (PATCHES.md PATCH 5). Before any official-sim run, walk the live-test checklist in dreamer_pilot.py's docstring (handedness, thrust calibration — unverifiable offline). Related: [[reference_aigp_windows_env]].
