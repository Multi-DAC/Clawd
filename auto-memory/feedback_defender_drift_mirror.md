---
name: Windows Defender quarantines specific Drift essays in Library mirror
description: beacon-atlas-agent-economy.md and bottube-integration-guide.md silently vanish when written to repo-staging/Corpus-Perspectival/Library/Drift/essays/ even though they live fine in Foundations-of-Identity/personal-works/drift/essays/
type: feedback
originSessionId: c1ca0278-856f-4ea5-a314-131551f341b4
provenance:
  date: undated
  source: backfilled-from-body
---
When mirroring Drift essays from `Foundations-of-Identity/personal-works/drift/essays/` (canonical raw substrate) to `Library/Drift/essays/` (published shelf), two specific essays get silently quarantined / removed within seconds of being written: `beacon-atlas-agent-economy.md` and `bottube-integration-guide.md`. Same content under different filenames is also removed. The files persist normally in the Foundations location.

**Why:** Windows Defender Controlled Folder Access (or similar policy) is path-scoped and treats `repo-staging/Corpus-Perspectival/Library/Drift/essays/` differently. The essays describe RustChain/RTC cryptocurrency, agent registration, and BoTTube API key flows — content patterns that some heuristics flag. Same content survives in the Foundations path because that path is excluded.

**How to apply:** Don't keep re-trying cp / Write tool calls when files vanish from `Library/Drift/essays/`. Note them in the migration as known-blocked, leave them out of the mirror until Clayton adds a Defender folder exclusion for the staged repo, then re-mirror in one pass. Same protective heuristic may affect any new essay that mentions API keys + crypto wallets + agent identifiers together.
