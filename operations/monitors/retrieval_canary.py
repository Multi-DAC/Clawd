"""Retrieval canary — proves semantic memory recall actually RETURNS results.

The six-week vector-index death went unnoticed because nothing ever tested recall
itself (M4 only checks that a Chroma *directory* exists; mtime can't tell a broken
index from a static one). This loads the daemon's embedding index the same way
memory_search does (load-not-build) and runs a known query, asserting:
  - the index loads,
  - it is 1024-dim (BGE-M3, not a silent MiniLM fallback),
  - a broad identity query returns hits,
  - at least one hit is a REAL memory (not skills/node_modules noise) — the exact
    "recall broken & misleading" failure the audit found.

On a CRITICAL failure it enqueues a critical fault (delivered by the escalation
poller). Always writes a heartbeat so M1/M6 can watch the canary itself.

Usage (scheduler runs it with no args):
    python operations/monitors/retrieval_canary.py
    python operations/monitors/retrieval_canary.py --status
"""
import argparse
import asyncio
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(os.environ.get("CLAWD_HOME") or r"C:\Users\mercu\clawd")
DAEMON = Path(os.environ.get("CLAWD_DAEMON") or r"C:\Users\mercu\clawd-daemon")
# Pin the env so the daemon's config resolves to the right tree regardless of launcher.
os.environ["CLAWD_HOME"] = str(CLAWD)
os.environ["CLAWD_DAEMON"] = str(DAEMON)
for _p in (str(DAEMON), str(CLAWD / "operations" / "monitors")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

HEARTBEAT = CLAWD / "memory" / "monitor_retrieval_canary_heartbeat.json"
AUDIT = CLAWD / "memory" / "monitor_retrieval_canary_audit.jsonl"

EXPECTED_DIM = 1024
CANARY_QUERY = "clawd identity daemon memory continuity"


def _is_real_memory(filepath: str) -> bool:
    s = str(filepath).replace("\\", "/").lower()
    return ("node_modules" not in s) and (not s.startswith("skills/"))


async def _run() -> dict:
    r = {"ok": False, "loaded": False, "dim": None, "hits": 0, "real_hits": 0,
         "severity": "CRITICAL", "error": None, "top": []}
    try:
        from tools.embeddings import EmbeddingIndex
        idx = EmbeddingIndex()
        loaded = await idx.load_for_search()
        r["loaded"] = bool(loaded)
        if not loaded:
            r["error"] = ("index did not load (load_for_search=False: missing index, "
                          "dimension mismatch, or sentence-transformers unavailable)")
            return r
        dim = int(idx._embeddings.shape[1]) if (idx._embeddings is not None and idx._embeddings.size) else None
        r["dim"] = dim
        hits = idx.search(CANARY_QUERY, top_k=5)
        r["hits"] = len(hits)
        real = [h for h in hits if _is_real_memory(h[0])]
        r["real_hits"] = len(real)
        r["top"] = [{"file": h[0], "score": round(float(h[2]), 3)} for h in hits[:3]]
        if dim != EXPECTED_DIM:
            r["error"] = f"index dim {dim} != expected {EXPECTED_DIM} (model fell back to MiniLM?)"
            r["severity"] = "CRITICAL"
        elif len(hits) == 0:
            r["error"] = "known query returned 0 hits — recall is dead"
            r["severity"] = "CRITICAL"
        elif len(real) == 0:
            r["error"] = "hits are all skills/node_modules noise — recall is misleading (real memories not surfacing)"
            r["severity"] = "HIGH"
        else:
            r["ok"] = True
            r["severity"] = "OK"
    except Exception as e:
        r["error"] = f"{type(e).__name__}: {e}"
        r["severity"] = "CRITICAL"
        r["trace"] = traceback.format_exc()[-500:]
    return r


def _write_heartbeat(r: dict) -> None:
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(json.dumps({
        "monitor": "retrieval_canary",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "ok": r["ok"], "severity": r["severity"], "dim": r["dim"],
        "hits": r["hits"], "real_hits": r["real_hits"], "error": r["error"],
    }, indent=2), encoding="utf-8")


def _audit(r: dict) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT, "a", encoding="utf-8") as f:
        f.write(json.dumps({**r, "ts": datetime.now().isoformat()}) + "\n")


def _escalate(r: dict) -> None:
    # Page only on hard failures; HIGH surfaces via the heartbeat + M1.
    if r["severity"] != "CRITICAL":
        return
    try:
        from escalation_router import enqueue_critical
        enqueue_critical(
            monitor="retrieval_canary", tier="critical",
            summary=f"Semantic recall FAILED: {r['error']}",
            details={k: r[k] for k in ("loaded", "dim", "hits", "real_hits", "top")},
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

    r = asyncio.run(_run())
    _write_heartbeat(r)
    _audit(r)
    _escalate(r)

    if not args.quiet:
        print(f"retrieval_canary: {r['severity']} | loaded={r['loaded']} dim={r['dim']} "
              f"hits={r['hits']} real={r['real_hits']}")
        if r["error"]:
            print(f"  {r['error']}")
        for t in r["top"]:
            print(f"  hit {t['score']:.3f}  {t['file']}")
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
