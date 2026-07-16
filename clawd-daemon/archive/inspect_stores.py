"""Measure the actual state of Clawd's storage layers — is SQL running, what's in it, is the KG SQL or JSON, is it live."""
import os, json, sqlite3, time
from pathlib import Path

MEM = Path("C:/Users/mercu/clawd/memory")


def stat_line(p):
    if not p.exists():
        return f"MISSING  {p.name}"
    age_h = (time.time() - p.stat().st_mtime) / 3600
    return f"{p.stat().st_size/1e6:8.1f} MB   mtime {age_h:6.1f}h ago   {p.name}"


def inspect_db(path):
    print(f"\n=== {path.name} ===")
    print("  " + stat_line(path))
    for wal in (path.with_suffix(path.suffix + "-wal"), path.with_suffix(path.suffix + "-shm")):
        if wal.exists():
            print(f"  {stat_line(wal)}   <- live WAL activity" if wal.suffix.endswith("wal") else f"  {stat_line(wal)}")
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)
        cur = con.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        print(f"  tables ({len(tables)}):")
        for t in tables:
            try:
                n = cur.execute(f"SELECT COUNT(*) FROM '{t}'").fetchone()[0]
            except Exception as e:
                n = f"err:{e}"
            # try to find a recency column
            recent = ""
            cols = [c[1] for c in cur.execute(f"PRAGMA table_info('{t}')")]
            for tc in ("created_at", "timestamp", "ts", "updated_at", "created", "valid_from"):
                if tc in cols:
                    try:
                        mx = cur.execute(f"SELECT MAX({tc}) FROM '{t}'").fetchone()[0]
                        recent = f"   latest {tc}={mx}"
                    except Exception:
                        pass
                    break
            print(f"     {n:>8}  {t}{recent}   cols={cols[:8]}")
        con.close()
    except Exception as e:
        print(f"  OPEN FAILED: {type(e).__name__}: {e}")


for db in ("clawd_memory.db", "kg_index.db"):
    inspect_db(MEM / db)

# Knowledge graph JSON
print("\n=== knowledge_graph.json (is the KG SQL or JSON?) ===")
kg = MEM / "knowledge_graph.json"
print("  " + stat_line(kg))
try:
    data = json.loads(kg.read_text(encoding="utf-8"))
    print(f"  top-level keys: {list(data.keys())[:12]}")
    for k in ("nodes", "entities", "edges", "relationships", "relations"):
        v = data.get(k)
        if isinstance(v, (list, dict)):
            print(f"  {k}: {len(v)}")
    edges = data.get("edges") or data.get("relationships") or data.get("relations") or []
    if isinstance(edges, dict):
        edges = list(edges.values())
    if edges and isinstance(edges[0], dict):
        active = sum(1 for e in edges if not e.get("valid_to") and not e.get("invalidated_at") and e.get("active", True))
        invalid = len(edges) - active
        print(f"  edge sample keys: {list(edges[0].keys())}")
        print(f"  edges active={active}  invalidated={invalid}")
except Exception as e:
    print(f"  READ FAILED: {type(e).__name__}: {e}")
