---
name: reference-hrm-sudoku-training-calibration
description: "HRM sudoku training — sampler/step-rate, eval cost, P49 budget, env path"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ee3d2431-b458-4593-a327-2d5ecebe9239
provenance:
  date: 2026-05-27
  source: backfilled-from-body
---

Calibration for running the 27M HRM on sudoku (`/home/clawd/HRM/`, config `hrm_v1.yaml` = H=4L L=4L hidden=512 heads=8, 27.3M params). Established 2026-05-27 Day 117 building Path A. Saves re-deriving these every run.

- **Python env:** `/home/clawd/miniconda3/bin/python3` (torch 2.11+cu128, omegaconf 2.3, RTX 5080). System python3 has NO torch. The HRM scripts `sys.path.insert(0,'/home/clawd/HRM')` so they run from any cwd.
- **Sampler draws ONE puzzle per group per epoch** (`PuzzleDataset._iter_train`). So real rate = `total_groups / batch_size`, NOT × `mean_puzzle_examples`. For easy-1k-aug-1000 (1000 groups, batch 384) → ~2.5 steps/epoch. The "31 steps/epoch" in old 300M logs = smaller batch (~32). Sizing `epochs_per_iter` off the wrong (×mean_examples) formula collapses it to ~2 and the loop runs ~5 batches then exits silently — looks like a hang/no-op.
- **Test set is 1M examples** (1000×1000 aug) → a FULL eval is ~19 min at ~2.3 steps/s. For frequent eval, cap to a subset (~15 batches ≈ 5,760 puzzles is a stable estimate).
- **Throughput ~2.3 steps/s** on the 27M model (ACT halt_max_steps=16 dominates per-step cost, ~batch-insensitive at this size).
- **P49 budget (the easy-sudoku accuracy benefit, KF_ROADMAP Findings #74-75):** train_and_measure.py defaults (batch 384, lr 7e-5) ⇒ epoch 1000 ≈ **2,500 steps** (Δ+17.6%, baseline 37%/KF 43%, KF H/L 193 vs baseline 1.2); epoch 2000 ≈ **5,000 steps** (baseline 73.68%/KF 77.78%, Δ+5.6%). Sudoku accuracy is sharply nonlinear — ~0 until it "gets it" then climbs; baseline first hits nonzero well after step ~625.
- **Baseline vs KF structural signature:** baseline H_CV *decreases* during training (heads de-differentiate, H/L stays ~1.0-1.2); KF/gated H_CV *increases* and H/L compounds toward ~190 over gating applications. Confirmed live in Path A probe.

See [[reference-wsl-bashlc-variable-gotcha]] and [[feedback-wsl-process-mgmt]] for the launch mechanics. Path A scripts: `Technical-Work/The-Killing-Form/Glider/scripts/train_kf_gated_hrm_easy.py` (+ `run_path_a_multiseed.sh`, `analyze_path_a.py`).
