---
name: WSL Shell Initialization Pattern
description: Use login shell (bash -lc) not plain shell (bash -c) when accessing conda/sage tools in WSL
type: feedback
provenance:
  date: 2026-04-01
  source: backfilled-from-body
---

Always use `wsl -e bash -lc "..."` (login shell) when accessing conda-managed tools (SageMath, etc.) in WSL. Plain `wsl -e bash -c "..."` does NOT source `.bashrc` or conda init, so tools appear missing.

**Why:** Three times (through 2026-04-01) I reported SageMath as "not installed" when it was present at `/home/clawd/miniconda3/bin/sage` — because I used non-login shells that don't source conda. Clayton had to correct this each time.

**How to apply:** Any time you need to check or use a WSL tool that's installed via conda/pip/apt and requires PATH setup, use `bash -lc` with explicit `source /home/clawd/miniconda3/etc/profile.d/conda.sh && conda activate base` before the command. If a tool appears missing, check your shell invocation before reporting it absent.

**Update (2026-04-12):** The `hrm` conda env no longer exists — it may have been lost in a crash. Everything (PyTorch 2.11, CUDA 12.8, omegaconf, HRM deps) is in the **base** env. Use `conda activate base`, not `conda activate hrm`. Also: `bash -lc` alone is NOT sufficient for conda — the conda init block in .bashrc appears to fail silently in some WSL invocations. Always explicitly source the conda.sh profile script.
