# Clawd Supervisor — Install / Repoint Runbook

Deterministic supervision for the rebuilt daemon. Two supervised units:

| Unit | What runs it today | Target |
|------|--------------------|--------|
| **Monitor scheduler** (`operations/monitors/scheduler.py`) | `ClawdMonitorScheduler` NSSM service (LocalSystem, Automatic) — **but pointed at `C:\Python314\python.exe`** | Repoint to the venv interpreter + explicit env |
| **Daemon** (`clawd.py`) | nothing (run manually) | Task Scheduler **at logon**, in the interactive session (needs GPU + avatar + `claude` OAuth) |

Why split this way: the daemon must run in the **user's interactive session** — it uses the GPU
(`cuda:0` for BGE-M3), the Electron avatar, and `claude` OAuth from the user profile; a Session-0
service would break all three. The monitors are light and file-based, so the existing LocalSystem
service is fine once repointed — it just needs `HF_HOME` set so the retrieval canary can find the
model cache (it will run the model on CPU under Session 0, which is fine for an hourly check).

Confirmed environment facts (from the 2026-07-01 16:14 boot log + service inspection):
- NSSM binary: `C:\Users\mercu\clawd\tools\nssm\nssm.exe` (bundled — no install needed).
- Service `ClawdMonitorScheduler`: `Application=C:\Python314\python.exe`,
  `AppParameters=...\operations\monitors\scheduler.py`, `AppDirectory=C:\Users\mercu\clawd`,
  logs+rotation under `memory\supervisor\`, `AppRestartDelay=15s` (auto-restart on crash), LocalSystem.
- BGE-M3 model cache: `C:\Users\Wasch\.cache\huggingface` (no copy under `C:\Users\mercu`; no `HF_HOME` set).
- Daemon boots in ~12 s and answers in ~12 s with the load-not-build fix; model loads on `cuda:0`.

> Run Parts A and C from an **elevated** PowerShell (Administrator). Part B is run **as the account you
> log in as to run Clawd** (the interactive login that owns the GPU + model cache + `claude` OAuth).

---

## Part A — Repoint the monitor scheduler to the venv  (elevated)

This activates every Phase-1 monitor change (retrieval canary, process watchdog, revived escalation
poller + self-healer, extended carrier registry) by running the scheduler — and the monitors it
spawns via `sys.executable` — under the venv with the right env.

```powershell
$nssm = "C:\Users\mercu\clawd\tools\nssm\nssm.exe"

# 1. Point the service at the venv interpreter (was C:\Python314\python.exe)
& $nssm set ClawdMonitorScheduler Application "C:\Users\mercu\clawd-daemon\.venv\Scripts\python.exe"

# 2. Give it the env the new monitors need. AppEnvironmentExtra is REPLACE-not-append,
#    so set all pairs in one call. HF_HOME lets the canary find the model cache under Session 0.
& $nssm set ClawdMonitorScheduler AppEnvironmentExtra `
    "CLAWD_HOME=C:\Users\mercu\clawd" `
    "CLAWD_DAEMON=C:\Users\mercu\clawd-daemon" `
    "PYTHONUTF8=1" `
    "PYTHONIOENCODING=utf-8" `
    "HF_HUB_OFFLINE=1" `
    "TRANSFORMERS_OFFLINE=1" `
    "HF_HOME=C:\Users\Wasch\.cache\huggingface"

# 3. Restart under the new interpreter
& $nssm restart ClawdMonitorScheduler
```

**Verify (give it ~90 s for the first cycle, then):**

```powershell
$py = "C:\Users\mercu\clawd-daemon\.venv\Scripts\python.exe"
& "C:\Users\mercu\clawd\tools\nssm\nssm.exe" get ClawdMonitorScheduler Application   # -> ...\.venv\Scripts\python.exe
Get-Content C:\Users\mercu\clawd\memory\monitor_scheduler_heartbeat.json | ConvertFrom-Json | Select-Object timestamp,pid
Get-Content C:\Users\mercu\clawd\memory\monitor_retrieval_canary_heartbeat.json    # expect ok=true dim=1024 real>=1
Get-Content C:\Users\mercu\clawd\memory\monitor_process_watchdog_heartbeat.json    # expect ok=true
& $py C:\Users\mercu\clawd\operations\monitors\clawd_health.py --brief
```

Expected: fresh scheduler heartbeat with a **new PID**, `monitors_scheduled` including
`retrieval_canary`, `process_watchdog`, `escalation_poll`, `self_healer`; canary + watchdog
heartbeats OK. **No Telegram noise** — the three stale queued criticals were pre-marked handled, so
the poller starts silent and only pages on new faults.

If the canary heartbeat shows `loaded=false` or a model error under the service, LocalSystem can't
read `C:\Users\Wasch\.cache` — copy the model cache to a SYSTEM-readable path (e.g.
`C:\Users\mercu\clawd\tools\hf-cache`) and set `HF_HOME` there instead.

---

## Part B — Supervise the daemon at logon  (as the Clawd login)

Runs the daemon in the interactive session so GPU + avatar + `claude` OAuth all work. `clawd.py`
already self-restarts internally (`attempt N/10`); the task starts it at logon and is the outer
backstop. We invoke `clawd.py` directly (not `start.bat`) to avoid `start.bat`'s interactive `pause`
prompts, which would hang an unattended task.

```powershell
# Run this logged in as the account that runs Clawd (owns the GPU + C:\Users\Wasch model cache).
$user = "$env:USERDOMAIN\$env:USERNAME"
$action = 'cmd /c "cd /d C:\Users\mercu\clawd-daemon && .venv\Scripts\python.exe clawd.py"'
schtasks /Create /TN "ClawdDaemon" /TR $action /SC ONLOGON /RU $user /RL HIGHEST /F
```

**Verify:**

```powershell
schtasks /Query /TN "ClawdDaemon" /V /FO LIST | Select-String "TaskName|Status|Run As User|Schedule Type"
schtasks /Run /TN "ClawdDaemon"          # start it now without waiting for a re-logon
# then watch the daemon log:
Get-Content C:\Users\mercu\clawd\clawd_daemon.log -Tail 20 -Wait
```

Expect the boot sequence: identity assembled → SQLite ready → Telegram polling → avatar on
`http://127.0.0.1:9742` → `Semantic search index loaded (no re-embed): …` → `Clawd daemon running`.
Send a Telegram check-in and confirm a reply within seconds.

> Auto-restart-on-crash beyond `clawd.py`'s internal loop: `schtasks` CLI can't set restart-on-failure.
> If you want the task itself to restart the process after a hard exit, import the task from XML with
> `<RestartOnFailure><Interval>PT1M</Interval><Count>999</Count></RestartOnFailure>` — ask and I'll
> generate the XML. Until then the internal 10-attempt loop + the external watcher (below) cover it.

---

## Part C — Reboot-survival check

1. `shutdown /r /t 0`, log back in as the Clawd account.
2. Confirm both units came up:
   ```powershell
   Get-Service ClawdMonitorScheduler | Select-Object Status,StartType    # Running / Automatic
   schtasks /Query /TN "ClawdDaemon" | Select-String "Running|Ready"
   Get-Content C:\Users\mercu\clawd\clawd_daemon.log -Tail 5
   ```
3. Send a Telegram check-in → reply within seconds = survived.

---

## Part D — External watcher-of-watchers (off-box dead-man's switch)

Built: `operations/monitors/external_pinger.py`, scheduled every 5 min. It computes a verified-health
verdict (daemon process up AND monitor scheduler fresh AND retrieval canary not failing) and pings an
external URL **only when healthy** — so box death, a wedged daemon, or a stopped scheduler make the ping
STOP, and the external service pages you. It ships **dark** (no-op) until you configure a URL.

To enable (2 min): create a check at https://healthchecks.io (free), set its period to ~10 min + grace
~15 min, copy its ping URL, and add to `C:\Users\mercu\clawd-daemon\.env`:

```
HEALTHCHECKS_URL=https://hc-ping.com/<your-uuid>
```

The scheduler picks it up on its next cycle. Verify: `monitor_external_pinger_heartbeat.json` shows
`ping.pinged=true` when healthy; stop the daemon and confirm Healthchecks.io alerts after the grace
window. (Ideally give the pinger its OWN trigger — a 5-min Task Scheduler task running
`.venv\Scripts\python.exe operations\monitors\external_pinger.py` — so it survives even if the monitor
scheduler dies; running it inside the scheduler still covers box/daemon death.)

## Still open (Phase-1 remainder, tracked separately)
- **`self_healer` KG heal is intentionally gated** (`carrier_registry.json` →
  `kg_index_db.self_healing_applicable=false`) until Phase 3 de-bloats the KG; re-enable then, pointing
  the heal command at the venv (self_healer now rewrites a leading `python` to `sys.executable`).

## Rollback
- Scheduler: `& $nssm set ClawdMonitorScheduler Application "C:\Python314\python.exe"` +
  `& $nssm set ClawdMonitorScheduler AppEnvironmentExtra ""` + `& $nssm restart ClawdMonitorScheduler`.
- Daemon task: `schtasks /Delete /TN "ClawdDaemon" /F`.
