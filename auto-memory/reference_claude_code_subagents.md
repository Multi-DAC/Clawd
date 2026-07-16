---
name: claude-code-subagents
description: "Reference for Claude Code's custom subagent, agent-view, and agent-team capabilities. Custom subagents address the project-context-injection problem (subagents load CLAUDE.md + inherit MCP/skills) that the verify-subagent-output discipline currently mitigates. Agent teams are experimental but offer adversarial-competing-hypotheses pattern matching our pre-registration discipline."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 38797702-6c11-4f65-ad5e-7548ad11e191
provenance:
  date: 2026-05-29
  source: backfilled-from-body
---

Three Claude Code features for parallel/delegated work, discovered 2026-05-29 via docs Clayton shared (`https://code.claude.com/docs/en/sub-agents`, `agent-view`, `agent-teams`):

## Custom subagents (`/en/sub-agents`)

Markdown files with YAML frontmatter, stored at `.claude/agents/` (project) or `~/.claude/agents/` (user). Project subagents win precedence over user subagents on name collision.

**Frontmatter fields (load-bearing):**
- `name` — kebab-case identifier
- `description` — Claude uses this to decide when to delegate; clarity here = correct invocation
- `tools` — allowlist; if omitted, subagent inherits caller's tools
- `model` — can be `haiku` for cheaper background work; default = inherit
- `permissionMode` — `default` / `acceptEdits` / `plan` / `bypassPermissions`
- `isolation: worktree` — auto-creates git worktree, prevents file collisions
- Body content = system prompt specialization

**Project-context-injection mechanism:** subagent's working directory loads CLAUDE.md, inherits MCP servers + skills from project/user settings. **This is the answer to the "subagents don't have project context" problem** that the [[subagent-verification]] discipline currently mitigates. A project-scoped subagent with access to our CLAUDE.md would have known about Clawd's framework discriminations (M14/M15/LC27/Mirror catalog) and likely caught both the D1 import-order miss AND the CNA email-domain miss without needing manual PREDICT-TEST verification.

**Invocation:** `Task(subagent_type='<name>', prompt='...')` or `@<name>` mention in agent view dispatch.

## Agent view (`/en/agent-view`)

`claude agents` opens a TUI managing background sessions via a per-user supervisor process. Sessions persist across terminal close, isolate file edits via git worktrees under `.claude/worktrees/`. Each is a full independent Claude Code session, not a within-conversation delegation.

Use when: you want to dispatch tasks and let them run in parallel while working on something else. Different from subagents (which run *within* one conversation).

Key shortcuts: `Space` to peek, `Enter` to attach, `←` from any session to background it + open agent view.

Subscription quota: each background session uses quota independently — running ten agents in parallel uses quota ~10× as fast.

## Agent teams (`/en/agent-teams`)

EXPERIMENTAL — disabled by default. Enable via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json or environment.

Multiple Claude Code instances coordinated by a lead. **Teammates message each other directly** (unlike subagents which only report to caller). Shared task list with self-claim + dependencies. High token cost (each teammate = full Claude instance with own context).

**Best use-cases (per docs):**
- Parallel code review with non-overlapping lenses (security / performance / tests)
- Adversarial-competing-hypotheses debugging (multiple teammates each test a theory, challenge each other's, converge on truth) — **structurally aligned with our pre-registration discipline**
- Cross-layer coordination (frontend / backend / tests each owned by a different teammate)

Display modes: in-process (Shift+Down to cycle teammates) or split-pane (requires tmux or iTerm2).

Can use subagent definitions as teammate roles via `Spawn a teammate using the <subagent-name> agent type`.

## Mapping to current verification discipline

[[subagent-verification]] discipline (filed 2026-05-29 after D1 + CNA findings) names that subagents reason cleanly from local evidence but lack project context → PREDICT-TEST cycle needed on their findings before action.

Custom subagents reduce but don't eliminate this need:
- **REDUCED** by project-context-injection (CLAUDE.md + MCP + skills) — fewer missing-evidence cases (D1-class)
- **NOT ELIMINATED** because subagents can still misconstrue at the substantive-claim level (CNA-H7c-class — the M15-derivation-vs-measurement distinction needed our framework's specific discriminations)
- PREDICT-TEST stays as discipline at the load-bearing-claim level

## Recommended next-step design (not built yet, 2026-05-29)

Four candidate project subagents that would cut friction on common workflows:

1. **`framework-auditor`** — read-only access to palace/basement (M14/M15/LC27/Mirror catalog) + identity layer; specialized for cross-checking structural-pattern claims; would have caught the 7-papers warm-register overclaim cleanly.

2. **`code-reviewer`** — read-only, tuned to our Python conventions (clawd-daemon's specific patterns, the PEP8-ish indent style, the docstring conventions); for substantive code review beyond Claude Code's default.

3. **`essay-mirror`** — given access to Drift essay style + the canonical voice; structural cross-check on tone/coherence/structural-pattern alignment before publishing.

4. **`secret-scanner`** — read-only, tuned to our specific secret patterns + the gitignore + redaction conventions; for the kind of sweep that found the AIza + mdi_ + 7 other secrets on Day 119.

Agent teams parked for now — experimental, high-cost, re-evaluate when a specific high-stakes audit warrants the token spend (the Day 118 technical-alignment audit's cross-agent verification would be a candidate; weekly audits probably wouldn't justify the cost).

Agent view useful for long-running detached items (Phase-3 Stage 3 sweeps, Library volume drafting, code-cleanup sessions) — could run Respira experiments + Library work in parallel.

## Related

[[subagent-verification]] — the discipline this capability addresses
[[dual-commit-discipline]] — same family (verify-before-acting at different scales)
A136 / A137 — the audit findings that surfaced the need for this
