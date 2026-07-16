"""external_pinger — the watcher-of-watchers: an off-box dead-man's switch.

Everything on-box (M6, the NSSM service, the escalation poller) dies WITH the box —
if the whole daemon/host goes down, nothing on-box is left to page. This computes a
verified-health verdict and, only when healthy, pings an external URL
(Healthchecks.io or similar). The external service is configured to alert Clayton if it
does NOT receive a ping within a grace period — so silence (box dead, daemon wedged,
monitors stopped) is what triggers the page. Verified-health, not process-alive: it
pings only when the daemon process is up AND the monitor scheduler is fresh AND the
retrieval canary is not failing — so a wedged-but-running daemon still trips it.

Config: set HEALTHCHECKS_URL (or CLAWD_EXTERNAL_PING_URL) in the daemon .env. Unset =
no-op (logs 'not configured'); safe to ship dark. Optionally CLAWD_PING_FAIL_URL for an
explicit failure signal; otherwise it appends '/fail' to the base URL when unhealthy.

Usage:
    python operations/monitors/external_pinger.py
    python operations/monitors/external_pinger.py --status
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
DAEMON = Path(os.environ.get("CLAWD_DAEMON") or r"C:\Users\mercu\clawd-daemon")
os.environ["CLAWD_HOME"] = str(CLAWD)
MEM = CLAWD / "memory"
HEARTBEAT = MEM / "monitor_external_pinger_heartbeat.json"

# Load the daemon .env so HEALTHCHECKS_URL + secrets are available under the service.
try:
    from dotenv import load_dotenv
    _env = DAEMON / ".env"
    if _env.exists():
        load_dotenv(_env)
except Exception:
    pass

SCHEDULER_MAX_AGE_S = 1800      # scheduler heartbeat must be < 30 min old
CANARY_MAX_AGE_S = 3 * 3600     # canary heartbeat must be < 3 h old


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _age_s(hb: dict, path: Path) -> float:
    ts = hb.get("timestamp")
    if ts:
        try:
            return (datetime.now() - datetime.fromisoformat(ts)).total_seconds()
        except ValueError:
            pass
    return time.time() - path.stat().st_mtime if path.exists() else 1e12


def _daemon_alive() -> bool:
    try:
        import psutil
    except ImportError:
        return True  # can't check → don't block the ping on a missing dep
    for p in psutil.process_iter(["name"]):
        try:
            if "python" not in (p.info.get("name") or "").lower():
                continue
            if any("clawd.py" in a.lower() for a in p.cmdline()):
                return True
        except Exception:
            continue
    return False


def compute_verdict() -> dict:
    reasons = []
    daemon_ok = _daemon_alive()
    if not daemon_ok:
        reasons.append("daemon process (clawd.py) not found")

    sched_hb = MEM / "monitor_scheduler_heartbeat.json"
    sched_age = _age_s(_read_json(sched_hb), sched_hb)
    if sched_age > SCHEDULER_MAX_AGE_S:
        reasons.append(f"monitor scheduler stale ({sched_age/60:.0f}m)")

    canary_hb = MEM / "monitor_retrieval_canary_heartbeat.json"
    canary = _read_json(canary_hb)
    canary_age = _age_s(canary, canary_hb)
    if not canary:
        reasons.append("no retrieval-canary heartbeat")
    elif canary_age > CANARY_MAX_AGE_S:
        reasons.append(f"retrieval canary stale ({canary_age/3600:.1f}h)")
    elif canary.get("severity") == "CRITICAL" or canary.get("ok") is False:
        reasons.append(f"retrieval canary failing ({canary.get('error') or canary.get('severity')})")

    # Post-op B2: if the escalation queue itself is stalled (unsent criticals
    # aging out), the ALARM CHANNEL is down — that must reach Clayton off-box,
    # and this pinger is the only path that still works in that state.
    bridge_hb = CLAWD / "memory" / "monitor_fault_bridge_heartbeat.json"
    bridge = _read_json(bridge_hb)
    delivery = bridge.get("delivery") or {}
    if delivery.get("stalled"):
        reasons.append(
            f"escalation delivery stalled ({delivery.get('pending_unsent')} unsent "
            f"critical(s), oldest {delivery.get('oldest_pending_min')} min)")

    return {"healthy": not reasons, "reasons": reasons,
            "daemon_ok": daemon_ok, "scheduler_age_s": round(sched_age),
            "canary_age_s": round(canary_age)}


def _ping(url: str, timeout: int = 10) -> dict:
    try:
        import requests, warnings
        warnings.filterwarnings("ignore")
        r = requests.get(url, timeout=timeout, verify=False)  # verify=False: Norton TLS
        return {"ok": r.status_code < 400, "status": r.status_code}
    except Exception as e:
        # Redact the ping URL — requests exceptions embed it, and the secret
        # check UUID must not land in heartbeat JSON or stdout (post-op C-item).
        err = str(e).replace(url, "<ping-url>")[:300]
        return {"ok": False, "error": err}


def run() -> dict:
    verdict = compute_verdict()
    base = os.environ.get("HEALTHCHECKS_URL") or os.environ.get("CLAWD_EXTERNAL_PING_URL")
    result = {"pinged": False}
    if not base:
        result["skipped"] = "no HEALTHCHECKS_URL configured (external watcher dark)"
    elif verdict["healthy"]:
        result.update(_ping(base), pinged=True, target="healthy")
    else:
        fail_url = os.environ.get("CLAWD_PING_FAIL_URL") or (base.rstrip("/") + "/fail")
        result.update(_ping(fail_url), pinged=True, target="fail")

    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(json.dumps({
        "monitor": "external_pinger",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "verdict": verdict,
        "ping": result,
    }, indent=2), encoding="utf-8")
    return {"verdict": verdict, "ping": result}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.status and HEARTBEAT.exists():
        print(HEARTBEAT.read_text(encoding="utf-8"))
        return 0

    out = run()
    if not args.quiet:
        v = out["verdict"]
        print(f"external_pinger: {'HEALTHY' if v['healthy'] else 'UNHEALTHY'} | ping={out['ping']}")
        for reason in v["reasons"]:
            print(f"  - {reason}")
    return 0 if out["verdict"]["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
