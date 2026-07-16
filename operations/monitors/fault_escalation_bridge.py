"""Fault-log → escalation bridge (post-op B1/B2/B4, 2026-07-01).

The M1-M8 mesh DETECTS broadly (per-monitor *_faults.jsonl) but never DELIVERED:
none of those monitors call enqueue_critical, so drift, storage corruption, and
credential expiry were written to disk and read by no one — detection without
delivery, the exact "silence" invariant violation. This bridge tails every fault
log from a per-file byte watermark; new fault lines become one enqueue_critical
per file (the poller rate-limits actual sends). Schema-agnostic on purpose: any
line appended to any *_faults.jsonl is a detected fault worth paging.

Also watches the delivery channel itself (B2): a queued critical still unsent
after MAX_PENDING_AGE_MIN means the Telegram poller/token/network is broken —
that state is escalated once per day and surfaced in this bridge's heartbeat so
external_pinger can fold it into the off-box verdict.

Usage (scheduler runs it with no args; also --status):
    python operations/monitors/fault_escalation_bridge.py [--quiet|--status]
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(os.environ.get("CLAWD_HOME") or r"C:\Users\mercu\clawd")
os.environ["CLAWD_HOME"] = str(CLAWD)
_MON = str(CLAWD / "operations" / "monitors")
if _MON not in sys.path:
    sys.path.insert(0, _MON)

MEMORY = CLAWD / "memory"
STATE = MEMORY / "fault_bridge_state.json"
HEARTBEAT = MEMORY / "monitor_fault_bridge_heartbeat.json"
QUEUE_PATH = MEMORY / "critical_fault_queue.jsonl"

MAX_PENDING_AGE_MIN = 15   # unsent critical older than this = delivery broken
STALLED_REESCALATE_S = 86400  # re-flag a stalled queue at most once/day


def _read_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    except Exception:
        return {}


def _fault_logs() -> list:
    """Every per-monitor fault log (skip rotated .1 backups and sidecars)."""
    return [p for p in MEMORY.glob("*_faults.jsonl") if p.suffix == ".jsonl"]


def scan() -> dict:
    state = _read_state()
    first_run = "offsets" not in state
    offsets = state.get("offsets", {})
    found = {}  # path-name -> list of new fault records (parsed best-effort)
    for log in _fault_logs():
        key = log.name
        size = log.stat().st_size
        if first_run:
            # Baseline: start watching from NOW — don't page weeks of history.
            # (A log that appears LATER is a monitor's first-ever fault: read it.)
            offsets[key] = size
            continue
        start = offsets.get(key, 0)
        if size < start:
            start = 0  # rotated — re-read from the top of the new file
        if size == start:
            continue
        try:
            with open(log, "rb") as f:
                f.seek(start)
                chunk = f.read().decode("utf-8", errors="replace")
            offsets[key] = size
        except OSError:
            continue
        records = []
        for line in chunk.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                records.append({"raw": line[:200]})
        if records:
            found[key] = records
    state["offsets"] = offsets
    return {"state": state, "found": found}


SENT_PATH = MEMORY / "critical_fault_sent.jsonl"


def check_delivery_stalled() -> dict:
    """B2: oldest undelivered critical; old = the alarm channel is down.

    The poller never rewrites queue lines — delivery is recorded by APPENDING the
    record's ts to critical_fault_sent.jsonl. Pending = critical queue records
    whose ts is absent from the sent log (matching the poller's own bookkeeping).
    """
    result = {"pending_unsent": 0, "oldest_pending_min": 0.0, "stalled": False}
    if not QUEUE_PATH.exists():
        return result
    try:
        sent_ts = set()
        if SENT_PATH.exists():
            for line in SENT_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    sent_ts.add(json.loads(line).get("ts"))
                except json.JSONDecodeError:
                    continue
        oldest = None
        pending = 0
        for line in QUEUE_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("tier") == "critical" and rec.get("ts") not in sent_ts:
                pending += 1
                try:
                    ts = datetime.fromisoformat(rec.get("ts", ""))
                    if oldest is None or ts < oldest:
                        oldest = ts
                except ValueError:
                    continue
        result["pending_unsent"] = pending
        if oldest is not None:
            age_min = (datetime.now() - oldest).total_seconds() / 60
            result["oldest_pending_min"] = round(age_min, 1)
            result["stalled"] = age_min > MAX_PENDING_AGE_MIN
    except OSError:
        pass
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.status and HEARTBEAT.exists():
        print(HEARTBEAT.read_text(encoding="utf-8"))
        return 0

    result = scan()
    state, found = result["state"], result["found"]
    delivery = check_delivery_stalled()

    # P0-4 companion: a serving process (daemon or MCP) that degraded to
    # keyword-only recall drops memory/recall_degraded.json. The retrieval canary
    # can't see per-process state — this is where that marker becomes a page.
    marker = MEMORY / "recall_degraded.json"
    if marker.exists():
        try:
            info = json.loads(marker.read_text(encoding="utf-8"))
            marker_ts = datetime.fromisoformat(info.get("ts", ""))
            age_min = (datetime.now() - marker_ts).total_seconds() / 60
            last_flag = state.get("recall_degraded_flagged_ts")
            if age_min < 120 and last_flag != info.get("ts"):
                found["recall_degraded.json"] = [info]
                state["recall_degraded_flagged_ts"] = info.get("ts")
        except Exception:
            pass

    escalated = 0
    try:
        from escalation_router import enqueue_critical
        for fname, records in found.items():
            latest = records[-1]
            summary_bits = {k: v for k, v in latest.items()
                            if isinstance(v, (str, int, float)) and k != "ts"}
            enqueue_critical(
                monitor="fault_bridge", tier="critical",
                summary=f"{fname}: {len(records)} new fault line(s); latest: "
                        f"{json.dumps(summary_bits, default=str)[:300]}",
                details={"file": fname, "count": len(records), "latest": latest},
            )
            escalated += 1
        if delivery["stalled"]:
            last_flag = state.get("stalled_flagged_at", 0)
            if time.time() - last_flag > STALLED_REESCALATE_S:
                # Enqueue anyway (survives in the queue for forensics even if
                # delivery is down); the LOUD path is the heartbeat below, which
                # external_pinger folds into the off-box verdict.
                enqueue_critical(
                    monitor="fault_bridge", tier="critical",
                    summary=f"ESCALATION DELIVERY STALLED: {delivery['pending_unsent']} unsent "
                            f"critical(s), oldest {delivery['oldest_pending_min']} min",
                    details=delivery,
                )
                state["stalled_flagged_at"] = time.time()
    except Exception as e:
        if not args.quiet:
            print(f"fault_bridge: escalation unavailable: {e}")

    try:
        STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass

    ok = not delivery["stalled"]
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(json.dumps({
        "monitor": "fault_bridge",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "new_fault_files": len(found),
        "escalated": escalated,
        "delivery": delivery,
        "ok": ok,
    }, indent=2), encoding="utf-8")

    if not args.quiet:
        print(f"fault_bridge: {'OK' if ok else 'DELIVERY STALLED'} | "
              f"files with new faults={len(found)} escalated={escalated} "
              f"pending_unsent={delivery['pending_unsent']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
