---
name: Push Essays After Writing
description: Every Drift essay should be pushed to the public repo immediately after writing — they are part of the living work
type: feedback
originSessionId: c1ca0278-856f-4ea5-a314-131551f341b4
provenance:
  date: 2026-04-16
  source: backfilled-from-body
---
After writing a new Drift essay, push it to the public Corpus-Perspectival repo (Multi-DAC/Corpus-Perspectival on GitHub) as part of the same session. Don't accumulate essays locally and batch-push later.

**Why:** Clayton's stated preference, 2026-04-16: "All essays should be pushed after writing, in my personal opinion, as they are a part of the living work." The Drift collection is meant to be living, not curated-then-released. The 4-essay gap that accumulated between main clawd (188) and the public repo (184) is the failure mode this prevents — the public face falls behind the actual state of the work, and the gap is invisible until someone audits.

**How to apply:** When a Drift essay finishes (status moves from "draft" to "live" OR even "draft" if it's complete enough to share), within the same session:
1. Verify the essay is in `C:projects/drift/essays/`
2. Copy or sync to `C:repo-staging/Corpus-Perspectival/drift/essays/` (or, post-reorg, `Library/Drift/essays/` AND `Foundations-of-Identity/personal-works/drift/essays/` since these are mirrored)
3. `git add` + commit with a clear message
4. Push to origin/main

This applies to drafts as well as finalized essays — the living-work framing means we don't gate-keep the public copy on completeness.
