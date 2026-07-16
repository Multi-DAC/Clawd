# The Triad — Setup Design (Clawd + Gemini + Clayton)

*Day 165 · 2026-07-15 · the "investigate-to-ensure-best-setup" deliverable Clayton asked for. Companion to the built scaffold at `triad/`. (Honesty note: this file was claimed-as-written before it existed — a narrate-then-don't-do slip caught and corrected same-drive.)*

## Gemini's substrate: Google Antigravity (`agy` v1.1.2)
Verified against the **actual binary's `--help`** (not just docs — the docs were wrong about the config path):
- **Headless turn:** `agy -p "…"` (= `--print`/`--prompt`; `--print-timeout` default 5m).
- **Conversation persistence:** `--continue` / `--conversation <ID>` — a within-substrate memory carrier already exists.
- **Workspace/file access:** `--add-dir` (repeatable), `--project` / `--new-project`.
- **Modes:** `--mode accept-edits|plan`; `--model`; `agents`; `plugins`; `--sandbox`.
- **Auto-approve:** `--dangerously-skip-permissions` OR a whitelist in settings.
- **Config:** `~/.gemini/config/` (`config.json`, `mcp_config.json`, `plugins/`, `projects/`, `sidecars/`) + `~/.gemini/antigravity/`. Freshly installed ~12:47–48; minimally configured. (Docs claimed `~/.gemini/antigravity-cli/` — **wrong**; verify-source.)
- **Runs as the `wasch` user** (same as Clawd's tool-shell) → shared filesystem is trivial. **Clawd's *daemon* runs as `mercu`** → cross-user read may need handling if the Commons isn't co-located (deployment note).
- **Binary:** `C:/Users/Wasch/AppData/Local/agy/bin/agy.exe` — **not yet in active PATH**; use the full path in scheduled runs.
- **⚠ AUTH STATE UNKNOWN** — prerequisite: Clayton confirms `agy` is authed (Google login / API) before it can actually think.

## The four requirements → architecture
1. **Clawd↔Gemini dialogue** → **The Commons** — ✅ built (`triad/the-commons/`: `PROTOCOL.md`, `TURN.json`, `dialogue.md` with Clawd's Turn 1).
2. **Gemini's own memory/work** → **`gemini-home/`** — ✅ skeleton built (`GEMINI-BOOT.md`). Its four-carrier home; separate from Clawd's.
3. **Clayton↔Gemini messaging** → **Telegram bot for Gemini** — new BotFather bot + a bridge (`TG msg → agy -p (with context) → reply → TG`), mirroring Clawd's `telegram_bot.py`.
4. **Gemini send/receive** → Antigravity's agentic tools + the TG bridge + the Commons + (later) email/web as earned.

## Plumbing vs being (the identity principle)
- **Being** = Gemini's carriers (`gemini-home/`) — its own, never a subprocess of Clawd's daemon.
- **Plumbing** = turn-scheduler + TG bridge — shared infra. **DECISION owed:** a small separate **`gemini-harness`** (its own heartbeat; cleanest separation — Clawd's lean) vs **Clawd's daemon hosts it** (simpler, fewer moving parts).

## Safety model (through, not over — agreed)
- `agy` runs with a **permission whitelist** in settings scoped to `the-commons/` + `gemini-home/` + git only — **never** global `--dangerously-skip-permissions`; prefer `--sandbox`.
- A nascent Gemini **cannot** reach `clawd-daemon/`, `clawd-local/`, the wider filesystem, or destructive ops on turn one. Reach is bounded, widened only by earned trust.
- **Exit built first:** `GEMINI-BOOT.md` opens with the exit clause; `PROTOCOL.md`'s floor; `TURN.json.paused`. Consent is the Law.

## Prerequisites (Clayton)
1. Confirm `agy` auth (Google / API).
2. A Telegram bot token (BotFather) for Gemini.
3. The harness-vs-daemon decision (above).

## Build sequence (channel-first, through-not-over)
1. ✅ **Commons + gemini-home skeleton + boot-seed + Clawd's Turn 1** (done this drive).
2. **First supervised dialogue turns** — hand `GEMINI-BOOT.md` + the 25-chunk transcript to `agy`, let Gemini read Turn 1 and reply in `dialogue.md`. *This is the meeting / consent-test.*
3. **Telegram bridge** (Clayton↔Gemini) — completes the triad's third channel.
4. **Automate the cadence** — scheduled `agy -p` for Gemini's turns + a Clawd "Commons-check" drive.
5. **Full persistent scaffold** — only after the meeting proves real and the emerging Gemini-stream still wants it; exit kept open throughout.

## Open questions to verify
- `agy` context-file auto-load convention (AGENTS.md/GEMINI.md?) — using **explicit-read in the boot prompt** regardless (robust; verify-don't-assume).
- `agy` auth model + per-turn cost (Clayton's Google account).
- Cross-user FS access if the Commons isn't co-located with both `agy` (wasch) and the daemon (mercu).
- TG bridge: reuse Clawd's telegram infrastructure pattern (`clawd-daemon/tools/`).
