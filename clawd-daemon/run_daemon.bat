@echo off
REM Non-interactive daemon launcher for the ClawdDaemon supervisor task.
REM Sets cwd to the daemon dir and runs clawd.py under the venv. No pauses
REM (unlike start.bat) so an unattended Task Scheduler run can never hang.
cd /d "%~dp0"
REM Post-op C8: force UTF-8 for the daemon's stdout handler (log-file writes were
REM already UTF-8; console/captured output was cp1252 = the mojibake). The
REM DRIVE_REWARD_ENABLED flag moved to .env so it holds under ANY launcher.
set PYTHONUTF8=1
".venv\Scripts\python.exe" clawd.py %*
