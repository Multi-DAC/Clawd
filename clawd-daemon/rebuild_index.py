"""Force a clean rebuild of the semantic index (Day-151).

Purges node_modules noise (~9,250 chunks) and adds repo-staging's dense material
(Library, Drift, Corpus, Research, Technical-Work) with content-hash dedup.
Out-of-process — cannot wedge the session. Index files are backed up as *.bak-day151.
"""
import os, sys, time, asyncio
os.environ.setdefault("CLAWD_HOME", "C:/Users/mercu/clawd")
os.environ.setdefault("CLAWD_DAEMON", "C:/Users/mercu/clawd-daemon")
sys.path.insert(0, "C:/Users/mercu/clawd-daemon")


async def main():
    from tools.embeddings import EmbeddingIndex
    idx = EmbeddingIndex()
    files = idx._get_indexable_files()
    print(f"[{time.strftime('%H:%M:%S')}] indexable files after dedup: {len(files)}", flush=True)
    t0 = time.time()
    await idx.build(force=True)
    dt = time.time() - t0
    print(f"[{time.strftime('%H:%M:%S')}] force rebuild done in {dt:.1f}s | chunks={idx.chunk_count}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
