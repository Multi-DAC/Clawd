"""Prove the event loop stays responsive DURING a memory search.

A ticker coroutine records timestamps every 0.1s while _memory_search[auto] runs
concurrently. If any synchronous stage still blocks the loop, the gap between ticks
spikes to that stage's duration. Healthy loop => max gap stays small (<~0.5s), which
means the upstream 120s dispatch wait_for could actually fire under load.
"""
import os, sys, time, asyncio
os.environ.setdefault("CLAWD_HOME", "C:/Users/mercu/clawd")
os.environ.setdefault("CLAWD_DAEMON", "C:/Users/mercu/clawd-daemon")
sys.path.insert(0, "C:/Users/mercu/clawd-daemon")

QUERY = "what did I decide about the recall wedge"


async def ticker(stop, ticks):
    last = time.time()
    while not stop.is_set():
        await asyncio.sleep(0.1)
        now = time.time()
        ticks.append(now - last)
        last = now


async def main():
    from tools import memory_tools as M
    # Warm the index once so we measure a realistic hot-path search (matches live recall).
    await M._ensure_embedding_index()

    stop = asyncio.Event()
    gaps = []
    t = asyncio.create_task(ticker(stop, gaps))

    t0 = time.time()
    res = await M._memory_search({"query": QUERY, "strategy": "auto", "top_k": 10})
    dt = time.time() - t0

    stop.set()
    await t

    maxgap = max(gaps) if gaps else 0.0
    print(f"search wall time     : {dt:.2f}s, result len={len(res)}")
    print(f"ticker samples       : {len(gaps)} (expected ~{dt/0.1:.0f} if loop free)")
    print(f"max gap between ticks : {maxgap*1000:.0f} ms")
    print(f"gaps > 500ms          : {sum(1 for g in gaps if g > 0.5)}")
    verdict = "LOOP HEALTHY — no stage blocked it" if maxgap < 0.5 else "LOOP STALLED — a stage still blocks"
    print(f"VERDICT: {verdict}")


if __name__ == "__main__":
    asyncio.run(main())
