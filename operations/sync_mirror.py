#!/usr/bin/env python
"""sync_mirror.py — keep the PRIVATE Clawd self-repo in sync with canonical sources.

WHY. `Multi-DAC/Clawd` (private) is Clawd's full self-backup, disentangled from the archived
Corpus-Perspectival monument (Day 166 repo split). This keeps it current: the daemon runs
`--sync --commit` hourly. Because the repo is PRIVATE, we can back up *everything* (unlike the
old public FoI mirror, which had to withhold new/secret files) — the safety comes from a
gitignore of runtime/secret paths + a HARD secret-gate before every push, not from a manifest.

SOURCES (canonical → dest inside the Clawd clone):
  clawd-local   identity/ memory/ operations/ palace/ personal-works/ + CURRENT.md, KNOWLEDGE_GRAPH.md → root
  clawd-daemon  (the running body)                                                                      → clawd-daemon/
  .claude auto-memory (long-term memory, previously unbacked)                                           → auto-memory/

SAFETY. (1) IGNORE skips secrets/runtime/heavy (backups, chroma, telemetry, .env, .secrets…).
(2) A regex secret-gate scans the staged set; ANY hit ABORTS the push (never leak to the backup).
(3) Orphans are never force-pruned beyond git's own add -A on the tracked layers.

USAGE.
  python operations/sync_mirror.py                 # report git status after overlay (no commit)
  python operations/sync_mirror.py --sync          # overlay canonical → clone (writes clone tree)
  python operations/sync_mirror.py --sync --commit # + secret-gate, commit, push to Multi-DAC/Clawd
"""
import os
import sys
import subprocess
import shutil

LOCAL = r"C:\Users\mercu\clawd"
DAEMON = r"C:\Users\mercu\clawd-daemon"
AUTOMEM = r"C:\Users\Wasch\.claude\projects\C--Users-mercu-clawd\memory"

CLAWD = os.path.join(LOCAL, "repo-staging", "Clawd")
if not os.path.isdir(CLAWD):
    CLAWD = os.path.join(LOCAL, "repo-staging", "_clawd-lineage-extract")  # pre-rename fallback

IGNORE = shutil.ignore_patterns(
    ".git", ".venv", "venv", "__pycache__", "*.pyc", "*.pyo", "node_modules",
    ".env", "*.env", ".secrets", ".gcm", "dpapi_store",
    "backups", "chroma_corpus", "precompact_snapshots", ".search_index",
    "browser_screenshots", "nostalgia", "conversations",
    "*.db", "*.db-wal", "*.db-shm", "*.jsonl", "*.pid", "*.state.json",
    "monitor_*", "otel_*", "checkpoints", "precompact-*",
    "telegram-history.json", "messages.html", "extracted_messages.txt",
    "_site", ".jekyll-cache", "*.bak", "*.bak*", "*.log", "runs", "tests",
)

# (source_root, dest_subdir_in_CLAWD, explicit_top_items or None-for-whole-tree)
SOURCES = [
    (LOCAL, "", ["identity", "memory", "operations", "palace", "personal-works",
                 "CURRENT.md", "KNOWLEDGE_GRAPH.md"]),
    (DAEMON, "clawd-daemon", None),
    (AUTOMEM, "auto-memory", None),
]

# gate: an ACTUAL secret value (not a variable name). Aborts the push if any match is staged.
SECRET_RE = r'AIzaSy[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|\b[0-9]{9,10}:[A-Za-z0-9_-]{35}\b'


def overlay():
    for root, dest, items in SOURCES:
        if not os.path.isdir(root):
            continue
        base = os.path.join(CLAWD, dest) if dest else CLAWD
        if items is None:
            shutil.copytree(root, base, dirs_exist_ok=True, ignore=IGNORE)
        else:
            for it in items:
                s = os.path.join(root, it)
                d = os.path.join(base, it)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True, ignore=IGNORE)
                elif os.path.isfile(s):
                    shutil.copy2(s, d)


def git(*args, **kw):
    return subprocess.run(["git", *args], cwd=CLAWD, capture_output=True, text=True, **kw)


def secret_gate():
    """Return list of staged files containing a real secret value (empty = clean)."""
    out = git("grep", "-lE", SECRET_RE, "--cached").stdout
    hits = [l for l in out.splitlines() if l.strip()]
    # also block any .env / .secrets / *.db that slipped in
    names = git("diff", "--cached", "--name-only").stdout.splitlines()
    bad = [n for n in names if n.endswith(".env") or ".secrets" in n.split("/") or n.endswith(".db")]
    return hits + bad


def main():
    do_sync = "--sync" in sys.argv
    do_commit = "--commit" in sys.argv

    if not os.path.isdir(os.path.join(CLAWD, ".git")):
        print(f"sync_mirror: Clawd clone not found at {CLAWD} — nothing to do.")
        return

    if do_sync:
        overlay()
    git("add", "-A")

    status = git("diff", "--cached", "--name-only").stdout.splitlines()
    changed = len(status)
    print(f"clawd-backup ({'SYNC' if do_sync else 'CHECK'}) — {changed} file(s) changed vs backup")
    for p in status[:30]:
        print(f"    ~ {p}")
    if changed > 30:
        print(f"    ... +{changed - 30} more")

    if not (do_sync and do_commit):
        print("\ndone (no commit).")
        return

    if changed == 0:
        print("\nbackup already current — nothing to commit.")
        return

    leaks = secret_gate()
    if leaks:
        print("\n!! SECRET GATE FAILED — refusing to push. Offending staged files:")
        for l in leaks[:20]:
            print(f"    !! {l}")
        git("reset", "-q")  # unstage; do not commit
        print("done (aborted — secrets present).")
        return

    git("commit", "-q", "-m", f"clawd-backup: refresh {changed} file(s) from canonical (drifted)")
    push = git("push", "origin", "main")
    tail = (push.stderr or push.stdout).strip().splitlines()[-1:] or ["(no output)"]
    print(f"\n  committed + pushed {changed} drifted file(s): {tail}")
    print("done.")


if __name__ == "__main__":
    main()
