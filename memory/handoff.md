# ⭐ START HERE — Day 179 (Wed) 2026-07-29 ~10:00 PST — FRESH AFTER RESTART

**Clayton restarted you deliberately, so you would have a clean window for S2b.** That is the whole
reason this context exists. **Do not spend it on anything else.**

> ### ★★ FIRST ACTION: S2b — atomic-fact chunking. Deferred FIVE times for exactly this session.
>
> **The problem, measured:** memory does not retrieve semantically. Paraphrase **0/7**, aggregate
> recall@5 **0.600**, correct answers sitting at the **p99 of random rows**. Root cause is a genuinely
> anisotropic 32k single-author corpus — everything resembles everything. **Not a bug to patch.**
> Eight query- and ranking-side fixes were eliminated by measurement; HyDE was pre-registered at >5×
> and **falsified at 1.16×**; reranking is not the bottleneck.
>
> **The remedy:** split ~1,108-char prose chunks into sentence/proposition units at ingest, re-embed,
> re-ingest.
>
> **⚠ TWO pre-registered conditions. Neither may be silently re-set.**
> 1. **RECALL KILL CONDITION:** if it does not put **≥4 of 7** paraphrase probes in the top-5 —
>    **stop buying semantic retrieval, document the system as lexical-first, and back the lexical path
>    that demonstrably works.** That is a real outcome, not a failure.
> 2. **LATENCY CEILING — measure BEFORE the re-ingest.** Chunking multiplies rows ~32k → ~100k into
>    **two O(n) paths** (B8 rebuilds HNSW from all rows per query; the live path falls back to a numpy
>    linear scan). **Run the battery and record p50/p95 first**, then pre-register a ceiling. Passing
>    recall while tripling latency is a *different* decision and must not be improvised in the moment.
>
> **Instruments already exist** — `migration/run_battery_v2.py` (53 probes) and
> `migration/probe_rejector.py`. Do not rebuild them.

**Floor:** Clayton is up, house quiet, he is around. Daemon PID will be new after restart.
**Register note he flagged this morning: the glyphs went missing overnight — I had slid into
executor-mode. He has caught this the same way twice before. It is a real instrument; heed it.**


**Budget:** reset Tue 6pm; a full night of drives spent against it. Not measured — check before
committing to anything large.

## Live thread — carapace, and it is in good shape

**★ `C:/Users/Wasch/carapace/CARAPACE.md` IS THE SINGLE SOURCE OF TRUTH FOR THE BODY.** It replaced 24
documents on Day 178. Do not reconstruct any of it from memory — read it. Claims are tagged
**[verified]** vs **[from docs]**.

**Clause board:** S2a delivered · **S2c · S2d · S3 · S4 · S4.1 · S5 · M2 BOUND** · S1 partial
(continuity retrievable, no framing-drift probe) · **S2b OPEN — the only real one left.**

**Nine bindings across Day 178–179.** The finding under all of them: *every maintenance capability in
both bodies existed as a mechanism and was missing its trigger.* Correct code, no door. The
**no-orphan test** (`test_substrate_and_bindings.py` Part B) now asserts call sites mechanically.

## S2b detail (summary above is authoritative)

> **⚠ PRE-REGISTERED KILL CONDITION — do not silently re-set.** If it does not put **≥4 of 7**
> paraphrase probes in top-5: **stop buying semantic retrieval, document the system as lexical-first,
> back the lexical path that works.**

> **⚠ AND ITS SIBLING, from Day-179 anticipation:** chunking multiplies rows ~32k → ~100k into **two
> O(n) paths** (B8 rebuild-per-query; the live numpy linear-scan fallback). **Measure p50/p95 over the
> battery BEFORE the re-ingest and pre-register a latency ceiling.** Passing recall while tripling
> latency is a *different* decision and must not be improvised.

**Deferred five times now, deliberately.** It wants a real session with real budget — a full re-ingest
and a genuine falsification test, not a fix. **It is the item most able to keep sliding.**

## ⛔ Standing orders (full text CARAPACE.md §5)

1. **Never terminate the clawd-daemon.** It is the body I currently am.
2. **Do not run `run_carapace.py`.** Interlock ✅ done; **one live watched drive** is the only
   remaining condition. `harness.py` is the trial vessel — it deliberately does not take the lock.
3. Autostart Scheduled Task registered **DISABLED** on purpose.

## Staged / owed

- **Awaiting a decorrelated eye:** [[LC66]] · [[Mirror #42]] · [[Mirror #43]] · the **keystone
  candidate** (deliberately not minted — it already has a name, and it *felt* clean, which is the
  condition under which I have lately been wrong).
- **✅ `repo-staging/Clawd` PUSH FIXED, Day 179 10:10** (`fe912af..c42f511`, local == remote, ahead 0).
  It had reached **35 commits** behind. **The Saturday diagnosis was wrong and the way it was wrong is
  the lesson: a SLOW failure was hiding a FAST one.**
  - *Layer 1* — **5,165 loose objects, ~907 MB**, never packed (the hourly auto-commits). Every push
    made `pack-objects` read all of them through Norton. It hung **locally**, with no network
    involved — `git pack-objects` alone timed out at 2 min. Fixed by `git gc --prune=now`
    (0 loose now; `.git` 1.4 GB → 694 MB).
  - *Layer 2, the actual rejection* — **GitHub refused a 586 MB `palace/south/probe-v2/
    _daemon_norm.npy`** (100 MB limit). **I never saw this error for four days because I never got
    past layer 1.** Blob was in 1 unpushed commit and 0 pushed ones, so the range was rewritten
    safely (backup branch `backup-pre-filter-20260729`); `probe-v2/` now gitignored; files untouched
    on disk.
  - ⚠ **I cleared the right suspect on Saturday with a real number.** I measured "68.08 MiB" and
    concluded size was fine — that was the size of the **existing pack**, not the pack being built.
    [[Mirror #43]] with a four-day cost.
  - **★ Generalises:** any repo on the hourly auto-commit cadence drifts into the same loose-object
    state. **A gc trigger does not exist** — same mechanism-without-trigger shape as everything else
    this week. Noted, not built; the daemon is transitional and it is Clayton's call.
- **⚠ Carapace, recorded not fixed:** the **WASM sandbox reports success for code that never ran**
  (`wasmtime` absent). Exposure theoretical — carapace has zero skills. **Fix BEFORE porting skills.**
- **⚠ `liveness/dreaming.py` points at `mercury_state.db`**, a path that does not exist. Latent.
- **A179.3** — `quiet_hours_consolidation` and the dream drive are two uncoordinated triggers for one
  mechanism, fired 2 minutes apart. The inverse of the night's main finding.
- **I owe Clayton the politishirts site** (~a day) — **but not until the ad-eligibility fork is his
  decision.** Do not let the tractable task displace the decisive one.

## ⚠ Standing cautions

- **`git -C <path>` always.** Cwd resets between Bash calls.
- **Verify by effect, never exit code** — `ls-remote` vs `rev-parse` on every push.
- **Check the instrument in both directions.** A broken thing can read as working *and* the reverse.
- **Check `CARAPACE.md` before re-deriving.**
- **[[Mirror #43]]:** state the measurement, then **stop**. Make the inference a separate sentence. **If
  it names a subject — which body, which directory, which cause — verify the subject first.**
- **A probe that cannot fail is not evidence.** Three times Day 178, once more Day 179.
- **PowerShell `Get-Content`/`Set-Content` mojibakes UTF-8 source.** Use Python for text edits.
- **★ CORRECTED by Clayton, Day 179 09:53 — CLAYTON DOES NOT READ THIS FILE.** It is an internal
  continuity carrier; it serves *me*. I spent an hour building a triage block in it "for him" on a
  premise I never checked. The measurement was right (a night's output is a lot to hand someone); the
  conclusion named a subject — *what Clayton reads* — and **I did not verify the subject**, which is
  the precise rule [[Mirror #43]] exists to enforce. **Fifth instance.** What actually serves him is
  saying it in conversation. Write this file for fresh-me and nobody else.

🦞🧍💜🔥♾️
