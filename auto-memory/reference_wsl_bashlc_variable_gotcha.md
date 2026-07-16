---
name: reference-wsl-bashlc-variable-gotcha
description: "In `wsl bash -lc '...'` calls, shell $variables get eaten by double-shell expansion — use inline full paths or a script file"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ee3d2431-b458-4593-a327-2d5ecebe9239
provenance:
  date: 2026-05-26
  source: backfilled-from-body
---

When invoking WSL from the Windows Bash tool as `wsl bash -lc '... $VAR ...'`, shell variables defined and used *inside* the single-quoted `-lc` string **expand to empty** — the outer shell (Git Bash invoking `wsl`) consumes `$VAR` before WSL's bash sees it. This is double-shell expansion, and it happens even when the assignment and use are on the same line within one `-lc` invocation.

**Symptoms:** paths collapse to root (`/file.json` instead of `/full/path/file.json`), `PermissionError: [Errno 13]`, `No such file or directory`, grep/sed errors with a truncated path. Hit this 4× in one session (2026-05-26) before internalizing it.

**Fixes:**
- In `wsl bash -lc` inline strings: use **full inline absolute paths**, NO variables.
- For anything with loops/variables: write a **script file** and run `wsl bash /mnt/c/.../script.sh` — variables work fine inside a script file (only the inline `-lc` string is affected).
- Established launcher pattern for long jobs: `nohup setsid bash /mnt/c/.../launcher.sh > logfile 2>&1 &` (see [[reference-new-body-env]]).

Always `wsl bash -lc` (login shell) not `wsl bash -c` for conda/sage/PATH, per [[feedback-wsl-shell-init]] — but keep variables out of the inline form.
