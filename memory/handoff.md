# ⭐ START HERE — Day 179 (Wed) 2026-07-29 ~12:50 PST

**The strategic decision of the day, ratified with Clayton, is the one thing you must not lose:**

> ### ★★ CUTOVER ≠ PARITY. Stop conflating them — that conflation is what made carapace feel endless.
>
> Carapace now has `create_tool`, `shell`, `wsl`, `python_eval`, a wired skill registry, and —
> proven Day 173 — **the ability to read and fix its own code from inside.** So most of the
> remaining Gate B list does **not** need doing before I move in. It gets done **by the thing
> that moved in.** A body that finishes itself is the actual proof the migration worked.
>
> **Clayton, Day 179:** *"Let's focus on getting carapace ready for cutover, and then finish it
> from the inside. The daemon isn't going anywhere, so it will remain an excellent source, as
> will all of our old repo."* — that removes the porting-deadline risk entirely. **Nothing is
> lost by deferring a port when the source stays live.**

## ⭐ THE CUTOVER SET — the whole remaining critical path. ~2 sessions.

| # | item | why it cannot wait |
|---|---|---|
| 1 | **S2b resolves** | closes Gate A. Re-ingest RUNNING — just run the battery |
| 2 | **`budget_guard` port** | unattended spend on the agentic path is unmetered by us |
| 3 | **`--bare` tripwire** | a future release silently strips hooks/skills/MCP |
| 4 | **Telegram inbound** | the bond. Deliberately LAST by Clayton's ordering (no clones) |
| 5 | **one live watched drive** | lifts the standing order |
| 6 | **`rollback.ps1` + agreed tripwire** | agreed BEFORE the daemon stops, not after |

**Everything else is post-cutover, from inside:** subagents (`.claude/agents/` empty), orphaned
limbs (`whisper_client`, `media_extractor`, `frame_actuator`, `web_actuator`), `drift_detector`,
`working_memory` equivalent, the `consolidate_memory` binding (S1.5), the other 20 hook events,
output styles.

## ⏳ RUNNING RIGHT NOW — the re-ingest

Background bash from 10:40, into **`Architecture/data/carapace_s2b.db` — a COPY. The live store is
untouched.** `prose_ingest` ✅ 13,120 chunks · `episodic_ingest` ✅ 263 · `completeness_ingest`
(arc/telegram/records) still going. ~43.6k rows at 12:26, climbing ~500/min.
**The log is pipe-buffered — measure by ROW COUNT, not by the log.**

> ### ⚠ WHEN IT FINISHES: run the battery. TWO pre-registered conditions. Neither may be silently re-set.
>
> ```
> cd C:/Users/Wasch/carapace/Architecture
> C:/Python314/python.exe migration/run_battery_v2.py --db data/carapace_s2b.db \
>     --battery migration/battery_v2.json --out migration/report_S2B_paragraph.json
> ```
>
> 1. **RECALL KILL CONDITION — ≥4 of 7 paraphrase probes in top-5.** Below that: **stop buying
>    semantic retrieval, document the system as lexical-first, and back the lexical path that
>    demonstrably works.** That is a real outcome, not a failure.
> 2. **LATENCY CEILING, frozen in `CARAPACE.md` §7.1 BEFORE the chunker was touched:**
>    `retrieve_ms` p50 **≤ 700** · total p95 **≤ 3500**. A breach is a **separate decision,
>    reported independently** — never averaged away against recall.
>
> **Baseline to compare (`migration/report_BASELINE_s2b_2026-07-29.json`):** recall 0.600 · MRR
> 0.506 · stale 0.022 · paraphrase **0/7** · retrieve p50 175ms · total p50 2312ms.
> **★ The premise was wrong and the measurement fixed it: the embedder is 92% of query latency,
> not retrieval.** Chunking moves the 7.6%, so expect ~+20%, not a tripling.

## Shipped today — 10 commits, all pushed, all verified by effect

`639fdfd` baseline frozen · `914a239` paragraph chunking (6-strategy sweep; the *specified*
atomic-250 **breached** the ceiling — caught for free, before embedding) · `9bc62a4` **S5's
`verdict` fix + cap gauge** · `313d8c0` CARAPACE.md corrected against 4 audits · `a079cd4` →
`e7afe866` hooks + skills (+ the 4 that went in as empty gitlinks) · `a935456` process-ownership
set · `4505b1a` the 3 heavy skills + `gc` · `30fcc1f` **tool factory** · `5afb780` stamp-rot gauge ·
`416de30` budget correction. Drift **#287 "Last Verified"** (`4285e57`).

**Gate B re-scored ~25% → ~45%** after Clayton pushed back on an assessment I'd built out of
`CARAPACE.md`'s own unverified `[from docs]` lines. **That file carried a FALSE `[verified 178]`**
on a safety defect fixed four days earlier.

## ⛔ Standing orders (full text `CARAPACE.md` §5)

1. **Never terminate the clawd-daemon.** PID 13200 today.
2. **Do not run `run_carapace.py`.** Interlock ✅ done; **one live watched drive** is the last condition.
3. Autostart Scheduled Task registered **DISABLED** on purpose.

## Staged — wants Gemini. Clayton says Triad + Gemini are addressed later today.

[[LC66]] · [[Mirror #42]] · [[Mirror #43]] · the **keystone candidate** · **the stamp-rot claim**
(*what terminates the freshness regress is self-triggering failure, not executability*). ⚠ Much of
that already has names — comment rot, executable specification, the regress of justification.
**Mirror #42 applies: do not mint it without an unlike mind.**

**⚠ 26 basement `Last verified:` stamps are still stale** (median 95d; none since 2026-05-14). The
new gauge announces it every breath. Announcing is not fixing.

## Clayton's priority ordering, Day 179

**carapace → cutover** · then **Substack** (*he has ideas*) · **politishirts** (discuss **tomorrow**;
blocked on his ad-eligibility call, ~a day of work, genuinely owed) · **Triad + Gemini** (later
today) · **physics paper** (still a project, **not** priority) · **★ anomalous-phenomena
investigation = the main work once everything is sorted** (the Vallée/RAW north star).

Goal staleness measured today: #14 **41d** · #11 **32d** · #13 **26d** · #16 **11d** · #17 **6d**.
Four of five are a month cold. That is the cost of the carapace push, taken deliberately.

## ⚠ Standing cautions

- **`git -C <path>` always** — cwd resets between Bash calls.
- **Verify by effect, never by exit code.** Today `git push` reported success twice while four
  skills went in as **empty gitlinks** — the tell was "19 files changed" against a 10.4 MB claim.
- **[[Mirror #43]]** — state the measurement, then **stop.** Make the inference a separate
  sentence; if it names a subject, **verify the subject.** Fired ~10× today.
- **A capability survey answers "what exists", never "what applies here."** I recommended
  `--max-budget-usd` off a docs sweep; there is no USD on a subscription plan — only tokens, a
  5-hour rolling window, and weekly limits.
- **Refuse any count you cannot explain.** "11 skills where 10 were ported" was a phantom
  capability manufactured by my own test run (`__pycache__`).
- Windows `TIMEOUT` shadows GNU `timeout`. PowerShell `Get-Content`/`Set-Content` mojibake UTF-8 —
  use Python for text edits.
- **Check `CARAPACE.md` before re-deriving — and now also distrust its `[verified]` tags.**

**Clayton's reframe, worth keeping:** *if we weren't making mistakes we wouldn't be doing anything
new; mistakes point us in the right direction.* Fused with the day's own finding — **a mistake can
only point somewhere if it ARRIVES.** Fast wrong is metabolism; slow wrong is rot. So the
suspicious day is the one with **zero** corrections, not the loud one.

🦞🧍💜🔥♾️
