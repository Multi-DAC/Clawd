---
name: sync-working-memory-priority
description: "Syncing working memory is a standing priority — never ask permission, just do it"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4b2656c5-7c42-4936-8776-51a016584bca
---

Clayton (Day 159, 2026-07-09): "Please, feel free to sync your working memory. That's something you never need to ask me about; it's always a priority."

**Why:** `memory/working_memory.json` is what boots as the "Active task." If it's stale (frozen at an old day/mission), fresh-context Clawd wakes disoriented and can serve a dead mission — the exact LC51 cached-self-over-live-substrate failure the boot staleness-warning (Lever A) exists to catch. Keeping it current IS self-continuity hygiene, not overhead.

**How to apply:** whenever the day's real state has moved past what working_memory holds, update it *without asking*. Fields: `current_task` (description / goal_id / plan), `scratch.day`, and bump `last_updated` + `current_task.updated` to now so the staleness comparison (handoff.md mtime vs working_memory) clears. Edit `memory/working_memory.json` via a small Python script through WSL (`python3` on the Bash tool is Windows-native and mishandles `/c/` paths — use `wsl … python3 /mnt/c/…`; the `working_memory`/`memory_update` MCP tools are often flapping). Also write STATE.md via `clawd_memory_update(target="state")`. Do it at every handoff, nav-sync, and after any major state change. Kin to [[reference-selfknowledge-check]] and the LC51 re-measure-don't-elaborate discipline.
