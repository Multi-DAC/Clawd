---
name: aigp-windows-env-and-launch
description: "AIGP/sim runs on Windows Python 3.14 (CPU torch), not WSL; detach.sh is WSL-only"
metadata: 
  node_type: memory
  type: reference
  originSessionId: c8b619a8-3100-4397-b116-325313fc08c1
provenance:
  date: 2026-06-02
  source: backfilled-from-body
---

AIGP / sim training is a **Windows** job, not WSL. The whole Windows side is **Python 3.14.3 /
torch 2.11.0+cpu** (the daemon AND the AIGP `python` are the same interpreter). 3.14 is too new for
CUDA torch wheels, so AIGP trains on **CPU**. The legacy AIGP `venv/` is **dead** (points at a
Python 3.12 from the old Razer body, pre-March-2026 migration). CUDA torch exists **only in WSL**
(PyTorch 2.6), but WSL **lacks gymnasium/sb3** — so *no single env has both sim deps + CUDA*.

**Launch pattern for AIGP:** `PYTHONIOENCODING=utf-8 python -u <abspath> ... > log 2>&1` with
run_in_background. Use `python -u` so flushed prints show live. `runs/` is gitignored (Glob/Grep skip
it — use bash `ls`). Don't `cd` into the path; scripts use absolute `HERE`-based paths.

**`operations/detach.sh` is WSL-only** (the continual-coherence MVP pattern) — do NOT use it for AIGP.
Using it launches into WSL → `ModuleNotFoundError: gymnasium`. (Fumbled this 2026-06-02, Day 122.)

To get fast (GPU) AIGP iteration: either install CUDA torch into a fresh Windows venv with the sim
deps, or get gymnasium+sb3 into the WSL CUDA env. Related: [[reference-new-body-env]].
