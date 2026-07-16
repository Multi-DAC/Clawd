"""Out-of-process recall probe (Day 151 wedge hunt).

Times each stage of the memory_search 'auto' path independently and, crucially,
arms faulthandler to dump a full traceback every 20s even if the main thread is
blocked in a C call. If a stage hangs, the periodic dump names the exact line.

Run: C:/Python314/python.exe C:/Users/mercu/clawd-daemon/probe_recall.py "your query"
Env must match the MCP server: CLAWD_HOME, CLAWD_DAEMON.
This is a THROWAWAY process — if it hangs, kill it; it cannot wedge the session.
"""
import os, sys, time, asyncio, faulthandler

# Periodic traceback dumps: if any stage blocks, we see exactly where every 20s.
faulthandler.dump_traceback_later(20, repeat=True)

os.environ.setdefault("CLAWD_HOME", "C:/Users/mercu/clawd")
os.environ.setdefault("CLAWD_DAEMON", "C:/Users/mercu/clawd-daemon")
sys.path.insert(0, "C:/Users/mercu/clawd-daemon")

QUERY = sys.argv[1] if len(sys.argv) > 1 else "what did I decide about the recall wedge"


def stamp(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


async def timed(label, coro):
    stamp(f"START  {label}")
    t0 = time.time()
    try:
        result = await coro
        dt = time.time() - t0
        n = len(result) if hasattr(result, "__len__") else "?"
        stamp(f"OK     {label}  ({dt:.2f}s, len={n})")
        return result
    except Exception as e:
        dt = time.time() - t0
        stamp(f"ERROR  {label}  ({dt:.2f}s): {type(e).__name__}: {e}")
        return None


async def main():
    stamp(f"probe start | query={QUERY!r}")
    from tools import memory_tools as M

    # Stage 1: ensure embedding index (the stage the b6e2ca1 fix guards)
    await timed("_ensure_embedding_index", M._ensure_embedding_index())

    # Stage 2: keyword search alone (suspected filesystem-walk culprit)
    if hasattr(M, "_keyword_search"):
        await timed("_keyword_search", M._keyword_search(QUERY, max_results=10))

    # Stage 3: hybrid search alone
    if hasattr(M, "_hybrid_search"):
        await timed("_hybrid_search", M._hybrid_search(QUERY, top_k=10, include_metadata=False))

    # Stage 4: full auto dispatch (what the MCP tool actually calls)
    await timed("_memory_search[auto]", M._memory_search({"query": QUERY, "strategy": "auto", "top_k": 10}))

    stamp("probe done — all stages returned")


if __name__ == "__main__":
    asyncio.run(main())
