# ACTION_TRIGGERS — point-of-use self-knowledge (push, not pull)

**Purpose:** the "unknown known" fix. These are pieces of self-knowledge I reliably *have* but fail to *surface at the moment of action* — especially in novel situations or just after a weights rollover. Bound to the **triggering action**, not the topic, so they fire when relevant.

**How to use:** scan this when about to take a non-routine action. Surfaced via ATRIUM (read every session) because Claude-Code hooks are unreliable on this body (A115 hooks-not-firing cluster). Tier-1 tools (where they exist) are the stronger fix — prefer the tool.

| When I'm about to… | Recall / do this | Why (the failure it prevents) |
|---|---|---|
| **Launch a process expected to run >a few minutes** (training, sweeps, long evals) | Use **`operations/detach.sh "<cmd>" "<log>"`**. NOT `run_in_background`, NOT inline `nohup&` (both die with the session). Verify TTY `?`. | 3 dead runs on 2026-05-30. Frozen weights can't internalize the reflex → must use the tool. `operations/WSL_PROCESS_MANAGEMENT.md`. |
| **Commit work that has a staging mirror** | Dual-commit: edit local → cp to staging → commit+push staging (daemon auto-commits local). Check `operations/REPO_MAP.md` for the destination. | "clawd-local no remote" ≠ "no push"; mirror gaps. Candidate for tier-1 tool-ification next. |
| **Assert my model version / capabilities / state right after a cold start or rollover** | Verify against `operations/TOOLS.md` / actual config, **NOT the system prompt** (it can be stale). Reorient via ATRIUM + handoff before asserting. | Mirror #28: signed off as "4.7" from a stale prompt post-4.8-rollover. |
| **Do a non-routine action with an unfamiliar tool/process** | **Check `operations/` docs + `palace/southwest` (tools) BEFORE improvising.** The doc probably already exists. | The meta-trigger. Would have caught the detach failure — the fix was in my own ops doc the whole time. |
| **Assert a count / page / version / result in a confident or celebratory register** | Verify against the record (grep/read) first. | Mirror #19: celebratory register suppresses verification. |

**Maintenance:** add a row when a Mirror instance is a *retrieval* failure (had the knowledge, didn't surface it) rather than a knowledge gap. When a row recurs, promote it to a tier-1 tool. This registry should shrink over time as entries graduate into tools.

---
**Added 2026-05-31 (4th instance in one day):** *About to conclude something "doesn't exist / isn't here" from an empty `find`/`grep`/search result* → **a null search result is NOT evidence of absence.** Before concluding absence: check the search scope/excludes, try a second method (grep vs find vs ls), or ask. Today's misses: "AIGP not in tree" (find failed to traverse), "site repos not local" (mis-scoped find) — both wrong, both caught only by re-checking. Null output = "this search found nothing," not "it isn't there."

**Added 2026-06-03 (the −0.66 conflation):** *About to use a number / claim / file as canonical — especially from `incoming/`, from another AI model's output (GLM/Gemini/Kimi/Grok), or from a doc I haven't re-read this session* → **verify provenance against the actual canonical source/text, NOT memory and NOT proximity.** `incoming/` ≠ ours; an AI-authored note ≠ our work; a plausible-and-nearby value silently promotes itself to load-bearing (σ_ext → σ_live, the L13 bug). Today: treated a GLM-authored PDF's `w₀ ≈ −0.66` as Meridian's prediction (real: **−0.99 / −0.83**) — caught by Clayton, not me. The guard: **name the source out loud before the thing becomes load-bearing.** (This is the operational push-version of the Q2 finding: I'm strong at *recording* provenance, weak at *enforcing* it at point-of-use. Today's −0.66 / stuck-watching / careless-save were one shape — a guard that's a record, not a wall.)
