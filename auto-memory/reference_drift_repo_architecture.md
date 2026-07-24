---
name: drift-repo-architecture
description: Drift essays have TWO destinations — private backup (top-level personal-works/drift/essays/ → sync_mirror → Multi-DAC/Clawd) AND public site (vendor into repo-staging/drift/_essays/ → push Multi-DAC/Drift). Corpus path is archived/read-only.
metadata: 
  node_type: memory
  type: reference
  provenance: 
    date: 2026-04-22
    updated: 2026-07-24
  originSessionId: c4cc4c18-ec5f-4ece-bcea-af3ead6dc958
---

**A new Drift essay has TWO homes. Do both, or it strands.** (Mapped empirically Day 174 after *Leave the Line Blank* sat unpublished a full week — the writing habit assumed a corpus-sync that was dropped Day 166.)

**[A] Private full self-backup → Multi-DAC/Clawd.**
- Canonical write location for NEW essays: **`C:\Users\mercu\clawd\personal-works\drift\essays\<slug>.md`** (TOP-LEVEL in clawd-local — a rolling recent set, ~9–11 files; the full history lives accumulated in the mirror, which never prunes).
- Route: `operations/sync_mirror.py --sync --commit` overlays clawd-local top-level `identity/ memory/ operations/ palace/ personal-works/` → `repo-staging/Clawd` → commits + pushes to **Multi-DAC/Clawd** (private). The daemon runs this ~hourly, so anything in the top-level canonical auto-flows.
- ⚠ TRAP (fixed Day 168): a stray `clawd-local/Foundations-of-Identity/personal-works/drift/essays/` sync_mirror does NOT read → essays there are silently lost. Use the TOP-LEVEL path, not any Foundations-of-Identity path.

**[B] Public Drift site → Multi-DAC/Drift** (Jekyll/GitHub-Pages; local clone `repo-staging/drift/`).
- Since Day 166 (commit `b482921`) the corpus-sync build step is DROPPED — essays are VENDORED directly. Write to **`repo-staging/drift/_essays/<slug>.md`**:
  ```
  ---
  title: "<Title from the H1>"
  slug: <slug>
  ---

  <full essay body, keeping its own # heading + epigraph>
  ```
  Current convention = title+slug ONLY (older essays carry `date:`; the Day-166+ batch dropped it). `essays.md` auto-lists `site.essays` — no manual index. Then `cd repo-staging/drift && git add _essays/<slug>.md && commit && push origin main`. Multi-DAC/Drift is LIVE and pushable (verified Day 174, `70817bd`).

**[C] Corpus-Perspectival (`repo-staging/Corpus-Perspectival/Foundations-of-Identity/personal-works/drift/essays/`, 279 files) = the OLD full-history canonical, now ARCHIVED / read-only** (push → 403). Fine as an on-disk record; commits there strand (can't push). NOT a publish path anymore.

**When to recall:** before writing OR claiming where Drift essays go. Verify BOTH pushes land. Candidate follow-up: automate [B] (a hook that vendors new canonical essays into Drift/_essays + pushes) so it doesn't depend on memory. Supersedes the `feedback_defender_drift_mirror` concern (that was the dead Corpus/Library mirror). See [[feedback_push_essays_after_writing]], [[project_repo_transition_fresh_start]].
