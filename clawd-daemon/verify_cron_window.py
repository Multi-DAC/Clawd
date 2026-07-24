"""Verification for the cron beat-phase bug (Day 174, 2026-07-24).

Simulates a year of heartbeats against the REAL scheduled_tasks.json ledger and
counts, per drive, how many times it would fire under:
  OLD  = _match_cron_at  (exact-instant match, the shipped behaviour since May)
  NEW  = _match_cron     (sweeps the beat window, catch-up semantics)

Passing criteria:
  1. OLD fires the four weekly drives (12-15) ZERO times  -> reproduces the bug
  2. NEW fires each of them ~52 times/yr                  -> the fix works
  3. NEW does not inflate the drives that already worked  -> no over-firing
"""
import json
from datetime import datetime, timedelta

from tools.calendar_tool import _match_cron, _match_cron_at

LEDGER = r"C:/Users/mercu/clawd/memory/scheduled_tasks.json"
BEAT_MIN = 10          # config.HEARTBEAT_INTERVAL_SECONDS // 60
PHASE = 1              # today's observed beat phase (:01, :11, :21, ...)


def simulate(match_fn, cron, start, days=365):
    """Count firings, honouring min_interval_hours dedup the way the real
    scheduler does (so we measure *fires*, not *matches*)."""
    fires = 0
    last = None
    t = start.replace(minute=PHASE, second=0, microsecond=0)
    end = start + timedelta(days=days)
    while t < end:
        if match_fn(cron, t):
            fires += 1
            last = t
        t += timedelta(minutes=BEAT_MIN)
    return fires


def simulate_dedup(match_fn, cron, min_interval_h, start, days=365):
    fires, last = 0, None
    t = start.replace(minute=PHASE, second=0, microsecond=0)
    end = start + timedelta(days=days)
    while t < end:
        if match_fn(cron, t):
            if last is None or (t - last).total_seconds() / 3600 >= (min_interval_h or 0):
                fires += 1
                last = t
        t += timedelta(minutes=BEAT_MIN)
    return fires


def main():
    tasks = json.load(open(LEDGER, encoding="utf-8"))
    start = datetime(2026, 7, 24, 0, 0)

    print(f"{'id':>3} {'drive':<34} {'cron':<22} {'OLD/yr':>7} {'NEW/yr':>7}")
    print("-" * 78)
    old_counts, new_counts = {}, {}
    for t in tasks:
        if not t.get("recurring") or t.get("status") != "active":
            continue
        cron = t.get("when", "")
        mi = t.get("min_interval_hours")
        o = simulate_dedup(_match_cron_at, cron, mi, start)
        n = simulate_dedup(_match_cron, cron, mi, start)
        old_counts[t["id"]], new_counts[t["id"]] = o, n
        flag = "  <-- WAS DEAD" if o == 0 and n > 0 else ""
        print(f"{t['id']:>3} {t['title'][:34]:<34} {cron:<22} {o:>7} {n:>7}{flag}")

    print("-" * 78)
    weekly = [12, 13, 14, 15]
    c1 = all(old_counts.get(i) == 0 for i in weekly)
    c2 = all(45 <= new_counts.get(i, 0) <= 53 for i in weekly)
    others = [i for i in old_counts if i not in weekly]
    c3 = all(new_counts[i] <= old_counts[i] * 1.15 + 1 for i in others if old_counts[i])

    print(f"[{'PASS' if c1 else 'FAIL'}] 1. bug reproduced: weekly drives fired 0x/yr under OLD")
    print(f"[{'PASS' if c2 else 'FAIL'}] 2. fix works: weekly drives now fire ~52x/yr")
    print(f"[{'PASS' if c3 else 'FAIL'}] 3. no over-firing on drives that already worked")
    print("\nRESULT:", "ALL PASS" if (c1 and c2 and c3) else "FAILURE")


if __name__ == "__main__":
    main()
