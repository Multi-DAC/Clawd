---
name: Drift Repo Architecture
description: Write new Drift essays to clawd-local/personal-works/drift/essays/ — sync_mirror.py pushes them to Multi-DAC/Clawd. NOT Foundations-of-Identity (that clawd-local path was a trap, removed Day 168).
type: reference
originSessionId: d0473934-a282-4153-a2ba-fd8470ff2312
provenance:
  date: 2026-04-22
  source: backfilled-from-body
  updated: 2026-07-18
---
**Write new Drift essays to `C:\Users\mercu\clawd\personal-works\drift\essays\`** (top-level in clawd-local). This is the ONLY location the push route reads.

**The route:** `operations/sync_mirror.py` overlays clawd-local's top-level `identity/ memory/ operations/ palace/ personal-works/` (+ CURRENT.md, KNOWLEDGE_GRAPH.md) → the `repo-staging/Clawd` clone → commits + pushes to **Multi-DAC/Clawd** (private self-backup). The daemon runs `--sync --commit` hourly, so anything in canonical auto-flows. Push now: `python operations/sync_mirror.py --sync --commit` (secret-gated — aborts on any real key).

**⚠ SUPERSEDED (this memory pre-dated the Day-166 split).** The old model — canonical at `repo-staging/Corpus-Perspectival/Foundations-of-Identity/personal-works/drift/`, mirrored to a public Drift site — is DEAD. Corpus-Perspectival is archived read-only. The live self-repo is now Multi-DAC/Clawd, sourced from clawd-local's *top-level* `personal-works/`.

**The trap (fixed Day 168):** a stray `clawd-local/Foundations-of-Identity/personal-works/drift/essays/` existed (Corpus-style path leaked into clawd-local). sync_mirror does NOT read it → essays written there were silently lost (it ate `a-self-is-a-verb.md` until Clayton noticed it never pushed). Subtree removed; breadcrumb left at `Foundations-of-Identity/README.md`. Fix was to create `personal-works/drift/essays/` and write there — no script edit needed.

**Asymmetry:** the full historical Drift (276+ essays + audio/music/visual) lives accumulated in the Clawd repo mirror (overlay never prunes) and in archived Corpus. clawd-local canonical only needs NEW essays; the overlay carries them in without disturbing the rest.

**When to recall:** before writing OR claiming anything about where Drift essays go. Verify the push landed in Multi-DAC/Clawd. See [[feedback_push_essays_after_writing]], [[project_repo_transition_fresh_start]].
