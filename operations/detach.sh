#!/bin/bash
# detach.sh — robust detached launch for long-running WSL jobs.
# Encodes the ONLY-correct pattern from operations/WSL_PROCESS_MANAGEMENT.md so it
# cannot be improvised wrong (tier-1 tool-ification of self-knowledge, 2026-05-30).
#
# Use this for ANY run expected to exceed a few minutes (training, sweeps, long evals).
# It launches the command fully orphaned (setsid -> TTY '?'), so it survives Claude/
# Bash-tool session cleanup and the 1-hour zombie-net (which only fires when Clawd is
# BLOCKED on a session-attached process). Requires vmIdleTimeout=-1 (.wslconfig; set).
#
# Usage (from a Claude Code Bash call):
#   wsl bash -lc 'bash /mnt/c/Users/mercu/clawd/operations/detach.sh "python3 path/to/job.py" "path/to/job.log"'
# Then stay free to think/converse; check progress any time with: tail -f <logfile>
# NOTE: no `set -u` — sourcing /etc/profile (byobu) references unbound vars and would abort.
CMD="${1:?usage: detach.sh \"<shell command>\" \"<logfile>\"}"
LOG="${2:?usage: detach.sh \"<shell command>\" \"<logfile>\"}"

# Source login env so deps (torch, etc.) resolve under the non-login setsid context.
[ -f /etc/profile ]     && . /etc/profile 2>/dev/null
[ -f "$HOME/.profile" ] && . "$HOME/.profile" 2>/dev/null
[ -f "$HOME/.bashrc" ]  && . "$HOME/.bashrc" 2>/dev/null

: > "$LOG"
nohup setsid bash -c "$CMD" > "$LOG" 2>&1 < /dev/null &
sleep 3

echo "[detach] launched -> $LOG"
echo "[detach] orphaned processes (success = '?' in TTY column):"
ps -o pid,tty,stat,etime,cmd -A 2>/dev/null | grep -F -- "$CMD" | grep -v -e grep -e 'detach.sh' | head -5
echo "[detach] monitor anytime:  tail -n 20 $LOG"
