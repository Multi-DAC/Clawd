---
name: MAXIMUS / Northlake Labs + DCL Platform
description: Public competitor stack and DCL platform constraints for AI Grand Prix; key facts that shape AIGP roadmap
type: reference
originSessionId: 10776292-b5f9-49b5-b48b-4447b7e9e6d4
provenance:
  date: undated
  source: backfilled-from-body
---
**MAXIMUS = Northlake Labs (Geoff Brown + agent), Project ICARUS for AI Grand Prix.**
- Public blog: northlakelabs.com/max/blog/ — failure log published in detail, treat as free curriculum.
- Stack: SB3-PPO + gym-pybullet-drones + YOLOv8 vision + 2x256 MLP + relative gate encoding + curriculum + EMA action smoothing α=0.5.
- Code is private (only marketing site is on github.com/northlakelabs).
- Key banked findings: norm_reward=False (their VecNorm trap cost weeks); EMA α=0.5 → 71.4% jerk reduction; sustain ≥80% over 50 episodes for promotion; anneal entropy/randomness/LR on promotion; no jerk penalty until policy competent; relative gate vectors only.
- They have no real flight data and no recurrence in policy. Possible leapfrog: LSTM head + learned pose head for VQ2.

**DCL platform constraints (publicly documented at dcl-project.com):**
- Single FPV camera (~12MP wide-angle) + IMU. **No LiDAR. No position telemetry after starting coordinate.** VIO mandatory.
- Onboard compute ~100 TOPS (Jetson-class).
- VQ1 May 2026 (gates visually highlighted, simplified course); VQ2 June 2026 (real 3D-scanned environment, harder); both close July.
- SoCal physical qualifier September; Ohio finals November.
- $500K prize + Anduril job offers.

**DCL submission spec (leaked via Northlake, not publicly confirmed):**
- Python-only `.zip` ≤500 MB, Python 3.12, Ubuntu 24.04, CUDA 12.x.
- `metadata.json` + `requirements.txt` + `DCLAgent` class implementing `compute_action(telemetry)`.
- 120-second per-heat limit; headless containerized eval.

**Lineage / reference architectures:**
- Swift (Kaufmann et al. 2023, Nature, DOI 10.1038/s41586-023-06419-4) — visual-inertial RL drone racing, no public code.
- TU Delft AlphaPilot (Springer Auton. Robots, DOI 10.1007/s10514-021-10011-y) — gate-detect CNN + planner + MPC, conservative fallback.
- A2RL × DCL Abu Dhabi April 2025 — direct precedent, TU Delft won with Guidance & Control Networks.
- awesome-autonomous-drone-racing: github.com/aimarket/awesome-autonomous-drone-racing — canonical curated list.
- UZH-RPG learned_inertial_model_odometry: github.com/uzh-rpg/learned_inertial_model_odometry — public VIO code.

**Roadmap reference:** `projects/aigrandprix/ROADMAP_v2.md` (Day 84 afternoon).
