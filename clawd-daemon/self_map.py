"""self_map — a live map of Clawd's tools + their usage + monitor liveness.

Not a stale authored SYSTEM_AUDIT: it reflects the ACTUAL registered tools (live
registry), how often each has been used (memory/tool_usage_counts.json), and which
monitors are currently alive (their heartbeats). Answers "what is wired, what is used,
what is dead weight" on demand — feeds the boot self-check and Phase-4 pruning.

Usage:
    python self_map.py            # human report
    python self_map.py --json     # machine-readable
    python self_map.py --unused   # only tools never used (pruning candidates)
"""
import argparse
import json
import sys
import time
from datetime import datetime

import substrate  # noqa: F401  (HF-offline + TLS + DNS)
import config
import tools

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MEM = config.CLAWD_HOME / "memory"
USAGE_PATH = MEM / "tool_usage_counts.json"


def _tool_names() -> list:
    names = set()
    for d in getattr(tools, "TOOL_DEFINITIONS", None) or []:
        n = d.get("name") if isinstance(d, dict) else None
        if n:
            names.add(n)
    names.update(getattr(tools, "_TOOL_HANDLERS", {}).keys())
    return sorted(names)


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (ValueError, OSError):
        return {}


def _monitors() -> dict:
    out = {}
    for hb in sorted(MEM.glob("monitor_*_heartbeat.json")):
        data = _read_json(hb)
        if not data:
            continue
        age_min = round((time.time() - hb.stat().st_mtime) / 60, 1)
        name = hb.stem.replace("monitor_", "").replace("_heartbeat", "")
        out[name] = {
            "age_min": age_min,
            "health": data.get("ok", data.get("overall", data.get("severity", "?"))),
            "stale": age_min > 60,
        }
    return out


def build() -> dict:
    names = _tool_names()
    usage = _read_json(USAGE_PATH)
    tool_rows = [{"tool": n, "count": (usage.get(n) or {}).get("count", 0),
                  "last_used": (usage.get(n) or {}).get("last_used")} for n in names]
    unused = [t["tool"] for t in tool_rows if t["count"] == 0]
    return {
        "generated": datetime.now().isoformat(),
        "model": getattr(config, "ANTHROPIC_MODEL", "?"),
        "tools_total": len(names),
        "tools_used": sum(1 for t in tool_rows if t["count"] > 0),
        "tools_unused": len(unused),
        "usage_tracked_since_empty": not usage,
        "tools": sorted(tool_rows, key=lambda t: -t["count"]),
        "unused_tools": sorted(unused),
        "monitors": _monitors(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--unused", action="store_true")
    args = ap.parse_args()

    m = build()
    if args.json:
        print(json.dumps(m, indent=2, default=str))
        return 0
    if args.unused:
        print(f"Unused tools ({m['tools_unused']}/{m['tools_total']}):")
        for t in m["unused_tools"]:
            print(f"  {t}")
        if m["usage_tracked_since_empty"]:
            print("  (usage counter is empty — counts accrue as Clawd runs; not yet meaningful)")
        return 0

    print(f"=== Clawd self-map  {m['generated'][:19]} ===")
    print(f"  model={m['model']}  tools={m['tools_total']} (used={m['tools_used']}, unused={m['tools_unused']})")
    print(f"  MONITORS ({len(m['monitors'])}):")
    for name, info in m["monitors"].items():
        flag = " STALE" if info["stale"] else ""
        print(f"    {name:28} age={info['age_min']:>6}m  health={info['health']}{flag}")
    print(f"  TOP TOOLS BY USE:")
    for t in m["tools"][:12]:
        print(f"    {t['tool']:28} {t['count']}")
    if m["usage_tracked_since_empty"]:
        print("  (usage counter just initialized — counts accrue as Clawd runs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
