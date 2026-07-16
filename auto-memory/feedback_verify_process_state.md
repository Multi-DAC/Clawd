---
name: Verify Process State Directly, Don't Trust Handoff
description: Before answering "is X running?" questions, check the live system, not the handoff/ATRIUM
type: feedback
originSessionId: c1ca0278-856f-4ea5-a314-131551f341b4
provenance:
  date: 2026-04-16
  source: backfilled-from-body
---
When asked about the state of a long-running process (training run, daemon, GPU job, server), verify directly via the live system before answering — do NOT trust the handoff or ATRIUM as the authoritative source.

**Why:** On 2026-04-16, the handoff and ATRIUM both said "v0.6b STOPPED." Clayton asked "How is the test running?" and I answered as if nothing was running, citing the handoff. He had to ask again with a specific guess before I checked WSL Ubuntu directly — and discovered v0.6b had been alive for ~28 hours with a healthy training trajectory. The handoff was stale or wrong; ATRIUM had carried the same wrong claim forward across the model upgrade.

**How to apply:** Whenever a process-state question comes up, default to live verification before answering:
- Training/long jobs in WSL: `wsl -d Ubuntu -- bash -lc "ps -ef | grep python | grep -v grep"` and check log mtime
- Use `wsl -d Ubuntu` not the named "Clawd" distro on this body — that distro doesn't exist (ref: `feedback_wsl_shell_init.md` and `reference_new_body_env.md`)
- GPU state: `wsl -d Ubuntu -- nvidia-smi`
- tmux sessions: `wsl -d Ubuntu -- tmux ls`
- Daemons/services: check ports, processes, recent logs

The handoff documents intent and last-known state; the live system is ground truth. If they disagree, the live system wins — and the handoff/ATRIUM should be corrected immediately so future-Clawd doesn't inherit the stale claim.
