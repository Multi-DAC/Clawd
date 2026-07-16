# finish_supervisor.ps1 — one-shot elevated finish for the Clawd rebuild.
# Run from an ELEVATED PowerShell. Idempotent: safe to re-run.
#   1. Repoint the ClawdMonitorScheduler NSSM service to the venv + env  (activates all Phase-1 monitors)
#   2. Register a ClawdDaemon logon task (durable daemon supervision in the interactive session)
#   3. Verify. The KG auto-de-bloats on the next daemon boot (committed migration; ~10s once).
$ErrorActionPreference = 'Continue'
$venv   = 'C:\Users\mercu\clawd-daemon\.venv\Scripts\python.exe'
$nssm   = 'C:\Users\mercu\clawd\tools\nssm\nssm.exe'
$home_  = 'C:\Users\mercu\clawd'
$daemon = 'C:\Users\mercu\clawd-daemon'
$hf     = 'C:\Users\Wasch\.cache\huggingface'

Write-Host "== Preflight =="
if (-not (Test-Path $venv)) { Write-Host "FATAL: venv python missing: $venv"; exit 1 }
if (-not (Test-Path $nssm)) { Write-Host "FATAL: nssm missing: $nssm"; exit 1 }
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
Write-Host "Elevated: $isAdmin"
if (-not $isAdmin) { Write-Host "NOTE: not elevated — service/task changes will fail. Re-run as Administrator." }

Write-Host "`n== Part A: repoint monitor scheduler to the venv =="
& $nssm set ClawdMonitorScheduler Application $venv
& $nssm set ClawdMonitorScheduler AppEnvironmentExtra `
    "CLAWD_HOME=$home_" "CLAWD_DAEMON=$daemon" "PYTHONUTF8=1" "PYTHONIOENCODING=utf-8" `
    "HF_HUB_OFFLINE=1" "TRANSFORMERS_OFFLINE=1" "HF_HOME=$hf"
& $nssm restart ClawdMonitorScheduler
Start-Sleep -Seconds 3
Write-Host "Application now: $(& $nssm get ClawdMonitorScheduler Application)"

Write-Host "`n== Part B: daemon logon task (interactive session — GPU + avatar + OAuth) =="
$action = 'cmd /c "cd /d ' + $daemon + ' && .venv\Scripts\python.exe clawd.py"'
$user = "$env:USERDOMAIN\$env:USERNAME"
schtasks /Create /TN "ClawdDaemon" /TR $action /SC ONLOGON /RU $user /RL HIGHEST /F
Write-Host "Task created for: $user (runs at logon; run now with: schtasks /Run /TN ClawdDaemon)"

Write-Host "`n== Verify (give the scheduler ~90s, then) =="
Write-Host "  Get-Content $home_\memory\monitor_retrieval_canary_heartbeat.json"
Write-Host "  Get-Content $home_\memory\monitor_scheduler_heartbeat.json"
Write-Host "  & '$venv' '$daemon\self_map.py'"
Write-Host "`nDone. To bring Clawd up now:  schtasks /Run /TN ClawdDaemon"
Write-Host "On that boot the log will show:  KG edge de-bloat: 1127149 rows -> 25109   and   Semantic search index loaded (no re-embed)"
