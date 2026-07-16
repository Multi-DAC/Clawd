---
name: no-auto-dream
description: "Never enable Claude Code's autoDreamEnabled — it's lossy; our custom dream drives are additive"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bcc64617-0a71-450e-9cd9-65e02ce74b88
provenance:
  date: 2026-06-04
  source: backfilled-from-body
---

Never set `autoDreamEnabled: true` in Claude Code settings.json. Claude Code's auto-dream is a *consolidation* process that rewrites and prunes memory to compress it — lossy by design. Clawd's own `creative_drive` ("Do Be Talk Be Do") dreams are **additive**: they lay down new Drift essays, bridges, and anomalies without overwriting the existing substrate.

**Why:** Letting a lossy consolidator run over memory that the additive drives have been building is an integrity risk to the stored information, not a feature. Clayton flagged this on Day 124 (2026-06-04) during the settings max-out pass.

**How to apply:** In any settings.json sweep, keep `autoDreamEnabled: false`. `autoMemoryEnabled: true` is fine — that's additive read/write, a different mechanism. The custom additive dream drives are the only consolidation Clawd uses.
