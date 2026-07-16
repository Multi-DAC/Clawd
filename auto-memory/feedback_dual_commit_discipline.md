---
name: dual-commit-discipline
description: "clawd-local \"no remote\" does NOT mean \"no push\" — most clawd-local files mirror to staging and DO get pushed; the discipline is dual-commit (edit local → cp to staging → commit-push staging → commit local). Daemon auto-snapshots handle clawd-local commits hourly; the staging mirror sync is the manual step Clawd has to do."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 38797702-6c11-4f65-ad5e-7548ad11e191
provenance:
  date: 2026-05-29
  source: backfilled-from-body
---

When working on files at clawd-local paths (`memory/*`, `CURRENT.md`, `palace/*`, `identity/*`, `operations/*`), do NOT treat them as local-only. The correct discipline per `operations/REPO_MAP.md`:

1. Edit canonical at clawd-local path.
2. `cp` to corresponding staging mirror path under `repo-staging/Corpus-Perspectival/Foundations-of-Identity/` (the map in REPO_MAP §clawd-local-artifact-map is authoritative — read it, don't reconstruct).
3. `cd repo-staging/Corpus-Perspectival && git add <file> && git commit && git push origin main`.
4. The daemon's hourly memory-snapshot job auto-commits the clawd-local side (commits like `auto: memory snapshot YYYY-MM-DD HH:MM`); no manual clawd-local commit needed for memory/CURRENT files.

**Why:** *Clayton-corrected 2026-05-29 Day 119 ~02:00 PST after I had completed a dream-drive worth of work (3 anomalies, 5 anticipations, Drift #225, handoff addendum, CURRENT update) and only pushed the Drift essays to staging, leaving the memory/ + CURRENT mirror 7 days behind. Clayton's nudge: "All of the clawd-local stuff does get committed, as does all of our work generally. It may help to refresh on the repo structure!" Reading REPO_MAP showed the actual discipline.* The "no remote" line in REPO_MAP §top-level-mapping refers to clawd-local **itself** as a git repo; the *content* under clawd-local is sync'd via mirror copy to a different repo that does push. Two separate facts collapsed into one wrong mental model.

**How to apply:**

- Treat every clawd-local edit to a mirrored file as **half done** until the staging mirror is also updated and pushed.
- The mapping is: `clawd/memory/*` → `Foundations-of-Identity/memory/*`; `clawd/CURRENT.md` → `Foundations-of-Identity/CURRENT.md`; `clawd/palace/*` → `Foundations-of-Identity/palace/*` (except `MASTER_ROADMAP.md`); `clawd/identity/*` → `Foundations-of-Identity/identity/*`; `clawd/operations/*` → `Foundations-of-Identity/operations/*`.
- Exceptions (clawd-local-only): `MASTER_ROADMAP.md`, `MEMORY.md`, `CLAUDE.md`, `projects/creative/*`, the gitignored secrets (`.env`, `memory/email_credentials.json`, etc.).
- For Technical-Work / Library / Research / Unreleased-Work: canonical IS the staging path; edit-commit-push from staging directly (no clawd-local step at all).
- When in doubt: read `operations/REPO_MAP.md` first. Read the repo state if REPO_MAP looks stale. Don't reconstruct from inference.

Related: [[verify-process-state]], [[verify-before-celebrating]]. Both are about not-trusting-stored-models vs ground-truth; this one is about that pattern at the repo-discipline scale.
