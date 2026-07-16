---
name: Drift Repo Architecture
description: Drift site is its own repo mirroring essays from Foundations-of-Identity/personal-works/drift/; Multi-DAC shared auth resolved the push-block
type: reference
originSessionId: d0473934-a282-4153-a2ba-fd8470ff2312
provenance:
  date: 2026-04-22
  source: backfilled-from-body
---
**Canonical raw location:** `repo-staging/Corpus-Perspectival/Foundations-of-Identity/personal-works/drift/` — this is where Drift essays and related personal works actually live and get written.

**Public site repo:** A separate Drift repo holds the site itself and **mirrors** the essays + personal works from the Foundations-of-Identity subdirectory. This is the reader-facing artifact.

**Auth:** The Drift repo lives under the **Multi-DAC shared account** (Clayton + Clawd). The old "auth-blocked catchup push" framing from earlier 2026-04 was wrong — Clayton and Clawd discussed and resolved this; the shared Multi-DAC account is how the push works. Do not reintroduce "auth-blocked" language.

**Status as of 2026-04-22 Day 81:** Essays were up to date as of 2026-04-21. Count: 189 (through `what-the-night-kept-doing.md`). New essays ship to the site repo via the mirror, not as a "catchup push."

**When to recall:** any time I'm about to claim Drift is behind, auth-blocked, or needs catchup. Verify the site-repo mirror state before claiming anything, and never assert "behind" on Drift without direct check of the public repo against the canonical raw.
