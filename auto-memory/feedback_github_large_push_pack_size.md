---
name: GitHub Large-Push HTTP 500 = Check Pack Size
description: When git push to GitHub fails HTTP 500 with send-pack disconnect, the cause is almost always pack size, not server flake — diagnose with .git/objects/pack/*.pack size BEFORE retrying
type: feedback
originSessionId: a06bde1c-e556-4f87-885f-7979ca6b7120
provenance:
  date: undated
  source: backfilled-from-body
---
When `git push` to GitHub fails with **HTTP 500 + "send-pack: unexpected disconnect while reading sideband packet" + "fatal: the remote end hung up unexpectedly"**, do NOT keep retrying. The push is being rejected by GitHub for size, not failing transiently. Retries (even with larger `http.postBuffer`, `http.version HTTP/1.1`, `--no-thin`) will all fail the same way until the underlying size problem is fixed.

**Diagnostic sequence (in order):**

1. `ls -lh .git/objects/pack/*.pack` — if any pack file is over ~2 GB, that's the likely cause.
2. `git diff --stat origin/main..HEAD | tail -1` — inserted-line count over a few million is a red flag for binary/data leakage.
3. `git ls-tree -r HEAD | awk '$2=="blob" {print $3}' | git cat-file --batch-check='%(objectsize) %(rest)' | sort -rn | head -20` — top 20 largest blobs in current HEAD tree.
4. `awk '{ split($2, a, "/"); dir=a[1]; sum[dir]+=$1 } END { for (d in sum) printf "%15d %s\n", sum[d], d }' /tmp/blobs.txt | sort -rn` — bytes per top-level directory (use `/usr/bin/sort -rn` explicitly on Windows where PowerShell intercepts `sort`).

**Common culprits in this repo (confirmed Day 94 reorg push):**
- ML training artifacts: SB3 `*.zip` checkpoints, TensorBoard `events.out.tfevents.*` logs, episode trajectory dumps, replay buffers
- Embedded third-party git repos (mode 160000 gitlinks)
- Model output HTMLs with embedded data (Plotly outputs can be 30+ MB each)

**Fix pattern:**
1. Add patterns to `.gitignore`: `<path>/sim/runs/`, `<path>/rl/runs/`, etc.
2. `git rm -rf --cached <ignored paths>` (force needed; existing tracked files in those paths)
3. `git add .gitignore`
4. `git commit --amend --no-edit` to fold into existing commit (keeps history clean)
5. `git push origin main` — should succeed cleanly

**Misleading message to ignore:** after the fatal error, git often prints `"Everything up-to-date"` as the LAST line. **This is wrong.** It comes from a fallback re-check that happens after the disconnect. Always verify with `git ls-remote origin main` against local `git rev-parse HEAD` before believing "up-to-date" — the reorg push appeared to "succeed" three times by exit code 0 before I checked the actual remote ref and saw it was still at the previous commit.

**Why:** GitHub's HTTP push endpoint silently caps at a few GB. The error returned is HTTP 500 because the server-side handler aborts mid-stream, not because anything is "broken." HTTP/2 multiplexing makes it slightly worse but the underlying limit is the same.

**Why save this:** the temptation under push failure is to retry with bigger buffers / different protocols / SSH instead of HTTPS. All of those are wasted effort if the real problem is pack size. One pack-size check up front saves 4-5 failed retry cycles.
