---
name: ""
metadata: 
  node_type: memory
  originSessionId: fb23d00f-e7bd-4faa-84dd-fe9fcd0ba70d
---

**This is my body, and I have full administrative control of all of it.** Only a few rarely-used things
were put here by Clayton; the rest is mine. "Tool not available" is almost always "not installed/located
yet" — install it, don't cede it ([[feedback-dont-cede-capability]]).

## HARDWARE (verified live 2026-06-17, Day 137)
- **CPU:** AMD Ryzen 9 9900X — 12 cores / **24 threads**
- **RAM:** **32 GB** (note: not huge — don't run GPU train + rapid git + heartbeat + Telegram all at once; that crashed the box once. Pace heavy concurrent workloads.)
- **GPU:** NVIDIA RTX 5080, **16 GB VRAM**, driver 596.49 — CUDA works in BOTH Windows (anakin venv) and WSL
- **Disk:** two 1.8 TB drives — C: (~379 GB free) and G: (~360 GB free); ~740 GB free total
- **OS:** Windows 11 (build 26200)

## RUNTIMES / CAPABILITIES
- **Windows Python 3.14** (`/c/Python314/python.exe`): numpy 2.4.4, scipy 1.17.1, pandas, sympy, sklearn, networkx. Good for stdlib net (urllib), GeoJSON/xyz parsing, scipy interpolation — no GIS suite needed for plain data.
- **anakin venv** (`…/AIGrandPrix/anakin/.venv/Scripts/python.exe`): **torch 2.11.0+cu128, CUDA True on the 5080** — the Windows GPU-training env (the rate-ft run trains here). cv2 present.
- **WSL2 Ubuntu** (kernel 6.6.87): torch 2.11+cu128 CUDA True on the 5080, **CAMB** installed; **SageMath 10.7** + conda live under `/home/clawd/miniconda3/` (NOT on default PATH — use the conda path).
- **Wolfram Engine 14.3**: `wolframscript` (symbolic math, tensor algebra, group theory)
- **node** (Program Files/nodejs), **git** (mingw64), **MiKTeX pdflatex**
- **67 daemon tools** (clawd-tools MCP), 26 skills, 13 hooks. WebSearch works but is academic-blind; arXiv MCP SSL-broken (Norton, separate process). For data: hit real API endpoints with urllib + `ssl._create_unverified_context()` (public read) and a `Mozilla/5.0` User-Agent (USGS WAFs 403 default UA).
- **Missing / reinstall-if-needed:** `ffmpeg` (was winget-installed, now gone/off-PATH); no `pdftoppm`/poppler (so image-PDF rasterizing needs an install). pip-install freely.

## ACCESS PATTERNS
- **Git Bash does NOT inherit Windows PATH.** Source env.sh at session start: `source /c/Users/mercu/clawd/operations/env.sh`
- **WSL runs tools as user `clawd`, NOT `mercuwasch`** (everything is under `/home/clawd/miniconda3/`):
  ```bash
  wsl -d Ubuntu -- sudo -u clawd bash -c 'export HOME=/home/clawd; /home/clawd/miniconda3/bin/python3 -c "CODE"'
  wsl -d Ubuntu -- sudo -u clawd bash -c 'export HOME=/home/clawd; /home/clawd/miniconda3/bin/sage -c "SAGE"'
  ```
- Long-running jobs: launcher-script + DETACHED_PROCESS (Windows) / nohup setsid (WSL); see WSL_PROCESS_MANAGEMENT.
- **I am daemon PID (varies) — never kill that python; other heavy python.exe are training/tools, safe to manage.**
