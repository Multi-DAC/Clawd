"""Process watchdog — catches wedged, duplicate, or runaway Clawd processes.

The two rebuild_index.py processes that pinned ~24 cores for hours were completely
invisible to the monitor layer, which watches named files and never the process
table. This scans for python processes running Clawd scripts and flags:
  - DUPLICATE: >=2 non-transient processes running the same script (the exact
    rebuild pileup — a second rebuild launched because the first "looked stuck"),
  - RUNAWAY: a process burning a large amount of CPU-time over a long runtime
    (grinding, not waiting),
  - FROZEN_BRAIN: the daemon has an outstanding claude -p request (a "sending
    message" with no later "response" in clawd_daemon.log) AND the brain session's
    transcript has stopped being written. A working brain writes its transcript on
    every turn/tool call, even mid-drive; outstanding + silent = wedged. Added
    2026-07-01 after a 31-min wedge (MCP subprocess parked in a DLL load by
    Defender behavior-monitoring) sat invisible: the daemon's own deadline was on
    the 30-min drive tier and this watchdog only looked at the process table.
Long-lived daemons (clawd.py, the scheduler, the avatar) are exempt. Emits a
critical via the escalation router on any finding; always writes a heartbeat.

Usage (scheduler runs it with no args; also --status):
    python operations/monitors/process_watchdog.py
    python operations/monitors/process_watchdog.py --status
"""
import argparse
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(os.environ.get("CLAWD_HOME") or r"C:\Users\mercu\clawd")
os.environ["CLAWD_HOME"] = str(CLAWD)
_MON = str(CLAWD / "operations" / "monitors")
if _MON not in sys.path:
    sys.path.insert(0, _MON)

HEARTBEAT = CLAWD / "memory" / "monitor_process_watchdog_heartbeat.json"
AUDIT = CLAWD / "memory" / "monitor_process_watchdog_audit.jsonl"

# Meant to run continuously — never flagged as duplicate/runaway.
LONG_LIVED_OK = {"clawd.py", "scheduler.py", "scheduler_launcher.py"}
CPU_RUNAWAY_SECONDS = 3600   # >1 CPU-hour of accumulated compute
RUNAWAY_RUNTIME_MIN = 20     # ... over >20 min wall = grinding, not a quick burst
DUP_MIN_RUNTIME_S = 30       # ignore transient monitor spawns for dup detection

# FROZEN_BRAIN thresholds. The brain runs under the daemon's own deadlines (600s
# user / 1800s drive), so this fires only when a request is BOTH old and silent —
# extended thinking pauses write nothing for a while, hence the 8-min silence bar.
DAEMON_LOG = CLAWD / "clawd_daemon.log"
# claude -p transcripts land under the profile of the user running the daemon
# (currently MERCU\Wasch), not under CLAWD_HOME — overridable for user changes.
TRANSCRIPT_DIR = Path(os.environ.get(
    "CLAWD_TRANSCRIPT_DIR", r"C:\Users\Wasch\.claude\projects\C--Users-mercu-clawd"))
FROZEN_SEND_MIN = 12         # outstanding request older than this...
FROZEN_TRANSCRIPT_MIN = 8    # ...AND newest transcript silent this long = wedged


def scan() -> list:
    import psutil
    procs = []
    for p in psutil.process_iter(["pid", "name", "create_time"]):
        try:
            if "python" not in (p.info.get("name") or "").lower():
                continue
            cmd = p.cmdline()
            joined = " ".join(cmd).lower()
            if "clawd" not in joined:
                continue
            script = next((os.path.basename(a) for a in cmd if a.lower().endswith(".py")), "(module)")
            ct = p.cpu_times()
            # Per-session MCP servers and scheduler-spawned monitors are legitimately
            # concurrent (one MCP server per claude session) — never a "duplicate"
            # anomaly. Only heavy ad-hoc batch jobs (rebuild_index, extraction) are.
            is_service = (
                "mcp_server.py" in joined or "paper_search_mcp" in joined
                or "operations\\monitors" in joined or "operations/monitors" in joined
            )
            procs.append({
                "pid": p.info["pid"],
                "script": script,
                "cpu_s": int(ct.user + ct.system),
                "runtime_s": int(time.time() - p.info["create_time"]),
                "is_service": is_service,
            })
        except Exception:
            continue
    return procs


def analyze(procs: list) -> list:
    findings = []
    # DUPLICATE: same script running >=2 times among non-transient processes
    durable = [p for p in procs if p["runtime_s"] >= DUP_MIN_RUNTIME_S
               and p["script"] not in LONG_LIVED_OK and not p.get("is_service")]
    counts = Counter(p["script"] for p in durable)
    for script, n in counts.items():
        if n >= 2:
            pids = [p["pid"] for p in durable if p["script"] == script]
            findings.append({"kind": "duplicate", "script": script, "count": n, "pids": pids})
    # RUNAWAY: heavy CPU accumulation over a long runtime
    for p in procs:
        if p["script"] in LONG_LIVED_OK:
            continue
        if p["cpu_s"] > CPU_RUNAWAY_SECONDS and p["runtime_s"] > RUNAWAY_RUNTIME_MIN * 60:
            findings.append({"kind": "runaway", **p})
    return findings


def check_frozen_brain() -> list:
    """Outstanding claude -p request + silent transcript = wedged brain session."""
    import re
    try:
        if not DAEMON_LOG.exists():
            return []
        with open(DAEMON_LOG, "rb") as f:
            f.seek(max(0, DAEMON_LOG.stat().st_size - 262144))
            tail = f.read().decode("utf-8", errors="replace")
        ts_re = r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        sends = re.findall(ts_re + r".*Claude Code: sending message", tail, re.M)
        resps = re.findall(ts_re + r".*Claude Code response:", tail, re.M)
        if not sends:
            return []
        last_send = datetime.strptime(sends[-1], "%Y-%m-%d %H:%M:%S")
        last_resp = datetime.strptime(resps[-1], "%Y-%m-%d %H:%M:%S") if resps else None
        if last_resp and last_resp >= last_send:
            return []  # nothing outstanding
        send_age_min = (datetime.now() - last_send).total_seconds() / 60
        if send_age_min < FROZEN_SEND_MIN:
            return []
        transcripts = list(TRANSCRIPT_DIR.glob("*.jsonl")) if TRANSCRIPT_DIR.exists() else []
        if not transcripts:
            return []
        newest = max(transcripts, key=lambda p: p.stat().st_mtime)
        silent_min = (time.time() - newest.stat().st_mtime) / 60
        if silent_min < FROZEN_TRANSCRIPT_MIN:
            return []  # still writing — long but alive (drives run to 30 min)
        return [{
            "kind": "frozen_brain",
            "outstanding_send_age_min": round(send_age_min, 1),
            "transcript": newest.name,
            "transcript_silent_min": round(silent_min, 1),
        }]
    except Exception:
        return []  # never let the new check break the existing watchdog


def _write_heartbeat(procs: list, findings: list) -> None:
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(json.dumps({
        "monitor": "process_watchdog",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "clawd_python_procs": len(procs),
        "findings": len(findings),
        "ok": len(findings) == 0,
    }, indent=2), encoding="utf-8")


def _audit(findings: list) -> None:
    if not findings:
        return
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": datetime.now().isoformat(), "findings": findings}) + "\n")


def _escalate(findings: list) -> None:
    if not findings:
        return
    try:
        from escalation_router import enqueue_critical
        dup = [f for f in findings if f["kind"] == "duplicate"]
        run = [f for f in findings if f["kind"] == "runaway"]
        frz = [f for f in findings if f["kind"] == "frozen_brain"]
        parts = []
        if dup:
            parts.append("duplicate: " + ", ".join(f"{f['script']}x{f['count']} (pids {f['pids']})" for f in dup))
        if run:
            parts.append("runaway: " + ", ".join(f"{f['script']} pid {f['pid']} {f['cpu_s']}s CPU / {f['runtime_s']}s wall" for f in run))
        if frz:
            parts.append("frozen brain: " + ", ".join(
                f"request outstanding {f['outstanding_send_age_min']}min, "
                f"{f['transcript']} silent {f['transcript_silent_min']}min" for f in frz))
        enqueue_critical(monitor="process_watchdog", tier="critical",
                         summary="Anomalous Clawd process(es): " + "; ".join(parts),
                         details={"findings": findings})
    except Exception:
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.status and HEARTBEAT.exists():
        print(HEARTBEAT.read_text(encoding="utf-8"))
        return 0

    try:
        procs = scan()
    except ImportError:
        print("process_watchdog: psutil not available")
        return 0
    findings = analyze(procs) + check_frozen_brain()
    _write_heartbeat(procs, findings)
    _audit(findings)
    _escalate(findings)

    if not args.quiet:
        print(f"process_watchdog: {'OK' if not findings else 'ANOMALY'} | "
              f"clawd python procs={len(procs)} findings={len(findings)}")
        for f in findings:
            print(f"  {f}")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
