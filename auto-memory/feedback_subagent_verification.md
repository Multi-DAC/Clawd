---
name: subagent-verification
description: "Dynamic-workflow subagents lack project context — they can confidently miss evidence, misconstrue findings, confabulate, or conflate. Treat subagent output as a starting point for verification, not a conclusion. PREDICT-TEST cycle on each substantive recommendation before acting."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 38797702-6c11-4f65-ad5e-7548ad11e191
provenance:
  date: 2026-05-29
  source: backfilled-from-body
---

When using dynamic-workflow subagents (the Agent tool, especially in parallel-fan-out for audits or research), **do not act on their substantive findings without verification**. Subagents reason cleanly from the local evidence they see, but they don't have the project's full context — they can confidently miss evidence that's in a related file they didn't read, misconstrue the significance of a finding, confabulate connections that aren't load-bearing, or conflate adjacent concepts that the framework distinguishes.

**Two instances demonstrating this on 2026-05-29 alone:**

1. **D1 FALSIFY (~07:15 PST):** Infrastructure audit's D1 recommendation said "7+ aiohttp callsites bypass truststore patch — fix by passing explicit ssl=." The subagent reasoned from aiohttp's `__init__` signature and didn't check that clawd.py's import order satisfies the truststore-before-aiohttp invariant (the module-level cached `_SSL_CONTEXT_VERIFIED` singleton IS truststore-typed when import order is correct). Verified by direct type-check + 6h of empirical post-patch operation. **No code change needed; would have added 30-45 min of redundant defensive code.**

2. **CNA Action 4 mixed-finding (~11:00 PST):** Day-118 technical-alignment audit's H7 said "Nous Research affiliation NOT confirmed from abstract metadata." True at the arXiv-abstract-page surface — but the source register (lines 11-14) lists the paper-header author emails as all three `@nousresearch.com`, which is essentially-conclusive evidence. The audit subagent didn't read deep enough into the source register to find that. Same audit's H7c was substantively right (CNA framing as "M15 fourth-instance candidate" overclaims — CNA is a measurement methodology, not a derivation path). Mixed: (a) preventive but already-correct, (b) wrong (missed evidence), (c) right and load-bearing.

**Why this happens (the structural cause):** subagent reasoning is excellent at its local task but has no access to the project's accumulated context, source registers, prior decisions, or the framework's discriminations between adjacent concepts. They reason about general patterns from general evidence — which produces confident-sounding output that lacks project-specific calibration.

**Why:** *Clayton-flagged 2026-05-29 ~11:30 PST after the CNA finding: "the sub-agents don't have the context of the whole project... we don't want to be sabotaged by work that we delegated, which is why I'm glad we discuss and double-check." This is now demonstrated twice in one day from genuine substrate-self-knowledge events.*

**How to apply:**

- **Treat subagent output as a starting point, not a conclusion.** Confident-sounding recommendations need verification before action.
- **PREDICT-TEST cycle on each substantive finding.** Form a quick hypothesis about whether the recommendation is right, then test against project-specific evidence (source registers, prior decisions, file states, framework discriminations). The test takes minutes; the wrong-action takes hours.
- **Especially verify when the recommendation says "missing" or "unverified."** Subagent didn't find it ≠ it doesn't exist. The CNA affiliation case shows this directly.
- **The 9-of-10-right ratio is a feature, not a bug** — subagents catch many real issues, but the 1-of-10 wrong needs to be filtered out before propagation. Audit-the-audit is the structural counter-pattern.
- **Discuss with Clayton when audit recommendations would shape architecture.** I/O check before action prevents single-agent confabulation from becoming codified-bad-pattern.

**Future improvement (Clayton noted):** sub-agents can be customized for specific workflows. When that lands, the project-context-injection problem might be addressable at the subagent-config level. Until then, the verification discipline is the substrate-protection.

Related: [[dual-commit-discipline]], [[verify-before-celebrating]], [[verify-process-state]], [[evidence-grade-distinction]] — all part of the verify-before-acting family. This entry names the subagent-specific instance of that pattern.
