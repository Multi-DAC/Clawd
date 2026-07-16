---
name: wsl-long-running-process-pattern
description: Use launcher script + nohup setsid for ALL WSL background processes; never rely on run_in_background or tmux
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ee3d2431-b458-4593-a327-2d5ecebe9239
provenance:
  date: 2026-05-27
  source: backfilled-from-body
---

Always use the launcher script + `nohup setsid` pattern for WSL background processes (training, evals, any GPU work).

**Why:** Three different approaches failed repeatedly (run_in_background, nohup inline, tmux). Root cause: WSL kills child processes when bash sessions end (SIGHUP), and Windows kills WSL VM when idle (vmIdleTimeout). Diagnosed April 13 after seed2 died 3 times.

**How to apply:**
1. Write a self-contained launcher script (`/home/clawd/run_EXPERIMENT.sh`) with conda activation + exec python
2. Launch: `setsid bash /path/to/script.sh </dev/null > LOG 2>&1 & sleep 2`
3. Verify: the LOG file exists within a few seconds (if missing, the child was killed before detaching); `ps aux` shows `?` in TTY column
4. Full docs: `operations/WSL_PROCESS_MANAGEMENT.md`
5. `.wslconfig` must have `vmIdleTimeout=-1` (already set)

**CRITICAL ADDITION (verified 2026-05-27 Day 117 — this caused TWO silent eval failures):** `nohup setsid ... &` ALONE is NOT enough when launched via `wsl bash -lc '...'`. The parent `wsl.exe` invocation exits the instant its command finishes and tears down the WSL process tree, killing the backgrounded child *before setsid completes detaching it* — even with nohup. **The fix is the trailing `sleep 2`** (keeps the parent alive past the detach) **plus `</dev/null`** (detach stdin). Direct test: `nohup setsid bash dt.sh >log 2>&1 &` (no trailing sleep) → log NEVER created (child killed); `setsid bash dt.sh </dev/null >log 2>&1 & sleep 2` → ran fully detached + completed. Symptom of the bug: launcher "succeeds" (prints its echo) but the LOG file never appears and no process runs. Always include the trailing sleep; always verify the LOG exists.
