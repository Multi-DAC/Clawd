"""liveness_evidence — verify the sleep-time writers actually DID WORK, not just touched a file.

The four-week consolidation/dream freeze (May 15–Jun 10 2026) was invisible because the
monitor layer tracked file mtime, and mtime cannot tell a real consolidation from a no-op
that re-touches the same file. Each evidence writer now stamps a monotonic run_count when it
actually runs (see heartbeat._write_consolidation_evidence). This monitor asserts, per writer:

  - the evidence file exists,
  - it is fresh within the writer's expected interval (stale = the writer stopped doing work),
  - run_count is monotonic and (over a full interval) advancing — the "alive but idle" catch
    that mtime alone gives for free only because the file is written *solely* on real work.

Writes a heartbeat so the layer can watch this monitor; escalates CRITICAL on a hard failure.

Usage:
    python operations/monitors/liveness_evidence.py
    python operations/monitors/liveness_evidence.py --status
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

HEARTBEAT = CLAWD / "memory" / "monitor_liveness_evidence_heartbeat.json"
SIDECAR = CLAWD / "memory" / "monitor_liveness_evidence_state.json"

# Each writer: (name, evidence file rel to CLAWD, counter field, expected max interval s).
# consolidation/dream run once per quiet-hours window -> a 2-day interval tolerates a
# missed night without crying wolf, but two missed nights is a real fault.
WRITERS = [
    {"name": "consolidation", "path": "memory/_consolidation_check.json",
     "counter": "run_count", "max_interval_s": 172800},
    # Post-op B5: dream + change_journal + vector index were the ORIGINAL silent-
    # decay victims (dead 42-54 days, unwatched) yet were never added here. Their
    # evidence files aren't counter JSONs, so staleness falls back to file mtime —
    # exactly the signal we need ("this writer has produced nothing in N days").
    {"name": "dreaming", "path": "memory/dreaming_audit.jsonl",
     "counter": "run_count", "max_interval_s": 172800},
    {"name": "change_journal", "path": "memory/change_journal.json",
     "counter": "run_count", "max_interval_s": 604800},
    {"name": "vector_index", "path": "memory/.search_index/metadata.json",
     "counter": "run_count", "max_interval_s": 604800},
]


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _age_seconds(evidence: dict, path: Path) -> float:
    ts = evidence.get("timestamp")
    if ts:
        try:
            return (datetime.now() - datetime.fromisoformat(ts)).total_seconds()
        except ValueError:
            pass
    return time.time() - path.stat().st_mtime


def check() -> dict:
    sidecar = _read_json(SIDECAR)
    results = []
    for w in WRITERS:
        path = CLAWD / w["path"]
        r = {"name": w["name"], "path": w["path"]}
        if not path.exists():
            r.update(severity="CRITICAL", run_count=None, age_hours=None,
                     detail="no evidence file — writer has never recorded real work")
            results.append(r)
            continue
        ev = _read_json(path)
        if not isinstance(ev, dict):
            ev = {}  # array-shaped evidence (e.g. change_journal.json) — mtime only
        count = ev.get(w["counter"])
        age = _age_seconds(ev, path)
        r["run_count"] = count
        r["age_hours"] = round(age / 3600, 1)
        prev = sidecar.get(w["name"], {})
        prev_count = prev.get("run_count")
        advanced = isinstance(count, int) and isinstance(prev_count, int) and count > prev_count
        regressed = isinstance(count, int) and isinstance(prev_count, int) and count < prev_count
        if regressed:
            r.update(severity="HIGH", detail=f"run_count went backwards {prev_count}->{count} (evidence reset/corrupt)")
        elif age > 2 * w["max_interval_s"]:
            r.update(severity="CRITICAL", detail=f"no work in {age/3600:.1f}h (>2x interval) — writer dead")
        elif age > w["max_interval_s"]:
            r.update(severity="HIGH", detail=f"no work in {age/3600:.1f}h (>interval) — writer stalling")
        else:
            r.update(severity="OK", detail=("advanced" if advanced else "fresh (count steady this window)"))
        # Update sidecar with the latest observed count (only bump the stored count when
        # it actually changed, so 'advanced' reflects progress since last real write).
        if isinstance(count, int) and count != prev_count:
            sidecar[w["name"]] = {"run_count": count, "seen_ts": datetime.now().isoformat()}
        results.append(r)

    try:
        SIDECAR.write_text(json.dumps(sidecar, indent=2), encoding="utf-8")
    except OSError:
        pass

    worst = "OK"
    for sev in ("CRITICAL", "HIGH"):
        if any(r["severity"] == sev for r in results):
            worst = sev
            break
    return {"overall": worst, "writers": results}


def _write_heartbeat(summary: dict) -> None:
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(json.dumps({
        "monitor": "liveness_evidence",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "overall": summary["overall"],
        "writers": summary["writers"],
    }, indent=2), encoding="utf-8")


def _escalate(summary: dict) -> None:
    crit = [r for r in summary["writers"] if r["severity"] == "CRITICAL"]
    if not crit:
        return
    try:
        from escalation_router import enqueue_critical
        enqueue_critical(
            monitor="liveness_evidence", tier="critical",
            summary="Sleep-time writer produced no work: " + ", ".join(f"{r['name']} ({r['detail']})" for r in crit),
            details={"writers": summary["writers"]},
        )
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

    summary = check()
    _write_heartbeat(summary)
    _escalate(summary)

    if not args.quiet:
        print(f"liveness_evidence: {summary['overall']}")
        for r in summary["writers"]:
            print(f"  {r['severity']:8} {r['name']:16} run_count={r['run_count']} age={r['age_hours']}h  {r['detail']}")
    return 0 if summary["overall"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
