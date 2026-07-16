"""Survey repo-staging for indexing: counts, size, and cross-tree content duplication."""
import os, hashlib
from collections import Counter, defaultdict

ROOT = "C:/Users/mercu/clawd/repo-staging"
SKIP = {"node_modules", "_archive", "__pycache__", ".git", "resources"}

by_top2 = Counter()
total = 0
total_bytes = 0
content_hash = defaultdict(list)  # hash -> [relpaths]

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP]
    for fn in filenames:
        if not fn.endswith(".md"):
            continue
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT).replace("\\", "/")
        top2 = "/".join(rel.split("/")[:2])
        by_top2[top2] += 1
        total += 1
        try:
            data = open(full, "rb").read()
            total_bytes += len(data)
            h = hashlib.md5(data).hexdigest()
            content_hash[h].append(rel)
        except Exception:
            pass

print(f"TOTAL .md (excl noise): {total}  |  {total_bytes/1e6:.1f} MB")
print("\n--- by top-2 dir (top 20) ---")
for k, v in by_top2.most_common(20):
    print(f"{v:5d}  {k}")

dups = {h: paths for h, paths in content_hash.items() if len(paths) > 1}
dup_files = sum(len(p) for p in dups.values())
uniq = len(content_hash)
print(f"\n--- duplication ---")
print(f"unique content hashes: {uniq}  |  files that are exact dup of another: {dup_files - len(dups)}")
print(f"=> indexing all {total} would add ~{dup_files - len(dups)} redundant copies")
print("\nsample duplicate groups (first 8):")
for h, paths in list(dups.items())[:8]:
    print("  " + "  <=>  ".join(paths[:3]) + ("  ..." if len(paths) > 3 else ""))
