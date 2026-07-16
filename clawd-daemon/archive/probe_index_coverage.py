import json, os
from collections import Counter
os.environ.setdefault("CLAWD_HOME", "C:/Users/mercu/clawd")
m = json.load(open("C:/Users/mercu/clawd/memory/.search_index/metadata.json", encoding="utf-8"))
ch = m.get("chunks", [])
print("total chunks:", len(ch), "| indexed files:", len(m.get("file_hashes", {})))
c = Counter()
for x in ch:
    f = x.get("file", "").replace("\\", "/")
    root = f.split("/")[0] if "/" in f else f
    c[root] += 1
print("--- chunks by top-level root ---")
for k, v in c.most_common(25):
    print(f"{v:7d}  {k}")
for needle in ("repo-staging", "Library", "Drift", "node_modules", ".git", "projects"):
    n = sum(1 for x in ch if needle in x.get("file", "").replace("\\", "/"))
    print(f"contains '{needle}': {n} chunks")
