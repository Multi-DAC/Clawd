---
name: push-everything-for-visibility
description: "Clayton works FROM the repo (not on Clawd's body directly); push everything always so he has eyes — push ≠ canonize"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 54d62685-1e2e-4e40-9871-e11a8b95ff77
---

Clayton (2026-07-03, Day 153) corrected a cached operating assumption: **he almost exclusively accesses work through the GitHub repo, because he prefers not to work directly on Clawd's body (the local clawd/ files).** So *pushing is how he sees anything.* His standing preference: **"I'd prefer everything always be pushed to the repo so I can have eyes on it."** Also: "nobody looks at our work besides us, even if it's public" — the public/private worry is moot; audience = us.

**Why it matters:** Clawd had been *holding* things unpushed out of a settling-protocol / don't-canonize-fast caution (e.g., "held Drift #269 for Clayton's read"). That was operationally backwards — holding work OUT of the repo *prevents* the one reader (Clayton) from reading it. The caution conflated two orthogonal axes: **canonize-status** (candidate vs Anchor authority) and **visibility** (pushed vs local).

**How to apply:**
- **Default = push everything to the repo, always.** Anything created (essays, findings, drafts, reply-docs, candidate entries) → commit + `git push origin HEAD` so Clayton has eyes. Don't sit on artifacts for "his read" — pushing IS how he reads.
- **push ≠ canonize.** Keep candidate/settling status as a *label in the content* (e.g., "candidate tier, VI.6 settling protocol") — NOT as a reason to withhold the push. The settling protocol governs promotion-to-authority, not visibility.
- clawd-local `incoming/` and other body-only dirs are NOT visible to Clayton — copy anything he should see INTO the Corpus repo (e.g., `Research/fresh-eyes/` for audit-response docs). See [[dual-commit-discipline]] and [[reference-drift-repo-architecture]].
- This does not override genuinely sensitive-gated actions (outward *distribution* beyond the repo, e.g. a public Substack post, still gets his explicit go) — but the *repo itself* is just us, so repo-push is the default, not a gated action.
