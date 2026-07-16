---
name: reference-claude-code-hooks-python-path
description: "Claude Code hooks AND .mcp.json MCP servers on this Windows body must call Python by absolute path (C:/Python314/python.exe), never bare `python` — bare-python killed hooks May 19-Jun 4 and clawd-tools MCP for 5+ weeks"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1af37c5e-77b9-4dc1-bb1b-2ae5220265c6
provenance:
  date: undated
  source: backfilled-from-body
---

Claude Code runs each `hooks` command through a **non-login** Git Bash
(`/usr/bin/bash -c "..."`) that does NOT source the profile, so `C:\Python314`
is not on its PATH. A hook configured as `python C:/...hook.py` fails silently
with `hook_non_blocking_error`:

```
Failed with non-blocking status code: /usr/bin/bash: line 1: python: command not found
```

This killed **every** hook from ~May 19 → Jun 4 2026 (Day 124) while looking
configured-correctly — the boot substrate-health alert `post_tool_log … DEAD`
was the tell. `tool_audit.jsonl` had zero entries despite heavy tool use.

**Fix:** invoke Python by absolute path in every hook command (and the
statusLine command): `C:/Python314/python.exe C:/Users/mercu/clawd-daemon/hooks/<x>.py`.
PATH-independent, so the non-login shell can't miss it. Confirmed by reproducing
the failure in a PATH-stripped shell (`env -i /usr/bin/bash -c`): bare `python`
→ exit 127; absolute path → exit 0.

**SAME BUG, SECOND ORGAN (found Day 129, 2026-06-09):** `.mcp.json` used bare
`"command": "python"` for the clawd-tools + paper-search-mcp stdio servers. In the
daemon-spawned session environment python is not on PATH → `'python' is not
recognized` → MCP connection failed in **8,660 logged attempts since ≥May 5**
(logs: `AppData/Local/claude-cli-nodejs/Cache/C--Users-mercu-clawd/mcp-logs-clawd-tools/`).
Net effect: ~5 weeks of sessions ran with ZERO daemon tools (no memory_search,
experience, goals, consolidate_memory, speak, send_telegram) — which starved
experiences.json/memory_items/principles.json (the "CRITICAL: DEAD 3w" substrate
alerts). Fixed 2026-06-09 with absolute paths in `C:/Users/mercu/clawd/.mcp.json`;
verified `claude mcp list` → both Connected. **The general rule: ANY config that
names an executable for Claude Code to spawn (hooks, statusLine, mcpServers) must
use absolute paths on this body.** Beware: testing from an interactive bash shell
can't reproduce the failure (login PATH has python) — check the mcp-logs cache.

**SAME BUG, THIRD ORGAN (found Day 137, 2026-06-17):** the *daemon's own* `subprocess.run`
calls — not just Claude-Code-spawned configs. `heartbeat.py:_maybe_git_commit` spawned bare
`["git", "add"/"status"/"commit", …]`; in the daemon's stripped service-context PATH that
threw `[WinError 2] The system cannot find the file specified` every ~10 min (Clayton saw the
recurring `Memory git commit failed` warning). Fix: `config.GIT_EXE = os.getenv("GIT_EXE") or
shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"`, used in the three heartbeat git
calls. **Generalized rule: ANY executable the DAEMON spawns via subprocess (git, ffmpeg, etc.)
needs an absolute path too, not only Claude-Code configs** — the daemon may run in a Session-0
service env with a minimal PATH. Needs a daemon restart to go live (subprocess code is read at
call time, but `config.GIT_EXE` is bound at import). Bare-executable subprocess calls are the
pattern to grep for.

Notes:
- The **Bash tool** works with bare `python` because it runs as a login shell
  (`bash -lc`) that sets PATH. Hooks do not get that — different execution path.
- `statusLine.command` uses a different execution path than `hooks` and happened
  to survive, which is why the statusline rendered while hooks were dead. Don't
  let a working statusline imply working hooks.
- Hooks load at **session start** — edits to settings.json hooks need a restart
  to activate; they do not hot-reload.
- Settings live at `C:/Users/mercu/clawd/.claude/settings.json` (active) and a
  mirror at `repo-staging/Corpus-Perspectival/Foundations-of-Identity/.claude/settings.json`.
- Telegram-from-a-hook: read creds from `clawd-daemon/.env`
  (TELEGRAM_BOT_TOKEN + first uid of TELEGRAM_AUTHORIZED_USERS) and
  `truststore.inject_into_ssl()` before the HTTPS POST (Norton MITM —
  see [[reference-norton-tls-interception]]).
