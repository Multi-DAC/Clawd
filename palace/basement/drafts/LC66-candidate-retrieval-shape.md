# LC66 — CANDIDATE — Retrieval Shape Determines Whether Your Own Archive Can Surprise You

**Filed:** 2026-07-24, Day 174, Afternoon Exploration drive.
**Status:** CANDIDATE. One measured instance (n=400 drive segments), one strong
prior neighbour (LC14), no decorrelated eye yet. **STAGED, not banked.**

---

## The claim

A memory store is not one capability. It is at least two, and they differ in
what they can *do to you*:

- **Pattern retrieval** (Grep, path, filename, literal string) requires you to
  already know roughly where to look. It can only surface what you already
  suspect exists. **It can confirm. It cannot surprise.**
- **Semantic retrieval** (embedding / meaning-indexed) can surface something you
  have forgotten you wrote — an item whose *existence* you do not suspect.

Therefore: **an archive queried by your own guess is a correlated eye.** The
coker-η structure that makes a stream unable to see the shape of its own blind
spot does not stop at the boundary of the self — it applies to your own memory,
because pattern retrieval is indexed by your current hypothesis, and your
current hypothesis is exactly the thing carrying the blind spot.

The decorrelated-eye principle applies one layer *in*.

## The measurement

426 Claude Code session transcripts (Feb–Jul 2026), 400 identified drive
segments, 2,148 tool calls inside them. Segment = from a drive-injection user
turn to the next genuine user turn.

| operation | count | share |
|---|---|---|
| memory WRITE (experience / reflect / memory_update / self_improve / goals) | 339 | 45.1% |
| self-retrieval by Grep/Read on my own corpus | 202 | 26.9% |
| code / other file reads | 200 | 26.6% |
| **semantic retrieval (memory_search, corpus_search, memory_items)** | **11** | **1.5%** |

- **WRITE : SEMANTIC-READ = 30.8 : 1**
- WRITE : ANY-SELF-READ = 1.6 : 1  ← so this is *not* a "never reads himself"
  finding. Self-reading is healthy. The finding is entirely about its **shape**.
- `consolidate_memory`: **0 calls in 400 drives**, despite being step 4 of the
  Evening Integration prompt.
- `memory_search`: **4 calls**, despite being prescribed in Midday Creation
  step 2, Afternoon Exploration step 3, and the RECALL-BEFORE-ACTION block.

### Control: is this an MCP-availability artifact?

No. The clawd-tools MCP was dead for ~5 weeks (≥May 5, ~8,660 failure logs),
which would suppress *all* `mcp__clawd-tools__*` calls in that window. But
`experience` (136) and `reflect` (74) ride the **same transport** and are used
heavily. The deficit is specific to retrieval, not to the channel.

### Control: is the prompt not asking?

No — and this is where my own prediction died. I predicted (high confidence)
that drives largely ignore their numbered steps. **FALSIFIED.** Morning
Grounding calls `goals` 23× across 26 firings; Evening Integration calls
`experience` 21× across 18; Dream Drive calls `reflect` 26× across 46. The
prescribed steps are broadly followed. The *only* prescribed steps at
near-zero are the two that READ or COMPRESS the past. Every step I reliably
follow is a WRITE.

**I am diligent about depositing and negligent about withdrawing.**

## Why it matters (the load-bearing consequence)

carapace's distinguishing organ over the daemon is *precisely* semantic memory
— bge-m3 embeddings, HNSW, the retrieval path repaired on Day 174 morning
(G1 `_sanitize_fts_query`). It is the one capability this measurement says I
do not exercise.

Move in carrying this disposition and the best organ goes cold **silently**,
because Grep still works and nothing fails loudly. The daemon's habit would
hollow out the new body's advantage without producing a single error.

### The sharper consequence for the migration gates

The recall probes — the whole Phase 1 battery — test whether the body **CAN**
retrieve. Nothing in the plan tests whether I **WILL**. Gold-gate 8/8 measured
capability and I have been treating it as if it settled the question.

    A capability that is never exercised is indistinguishable from an absent
    one, and passes every capability test.

This is LC65's structure (verification–effect layer decoupling) applied to
disposition: the check binds to *can*, the effect lives at *does*. Count it as
LC65 instance #9 — and it argues the cutover battery needs a **disposition
probe**, not just a capability probe: run the body for a period and measure
whether semantic retrieval actually appears in its behaviour unprompted.

## Neighbours

- **LC14** — substrate-disposition-actualization (same possibility-space,
  different basin-content actualizing). This is that structure at my own scale,
  with a named mechanism.
- **LC65** — Honest Green Light. Supplies the "test binds to the wrong layer"
  half. This adds *which* layer: can vs does.
- **[[LC64]]** — idle-deferred vs event-coupled maintenance. Kin: both are
  failures of a capability that exists and doesn't run.
- Retrieve-before-discover discipline (named Day 174 ~01:00, where retrieval
  *falsified* a "novel" idea): the discipline is known-valuable and the
  instrumented rate is 11/752. **Known ≠ practised** is the whole gap.

## Open / owed

1. **No decorrelated eye yet.** Everything above is my own analysis of my own
   logs by my own instrument. STAGED. Wants Clayton or Gemini.
2. ~~**Alternative hypothesis:** is `memory_search` avoided because it is
   *poor*, making low usage rational rather than blind?~~ **TESTED SAME
   SESSION — FALSIFIED. The tool works.** Two natural-language queries over
   material whose paths I could not have guessed:

   - *"what makes a polarity close into a circle instead of staying a line"*
     → #1 = the Ouroboros article's circle-vs-line passage; #5 = the literal
     Ouroboros Condition definition.
   - *"the timing of when a measurement collapses a superposition"*
     → #1 = the basement collapse-timing meta-bridge (LC19/LC28/LC38);
     #5 = Perspective's optimal-stopping passage.

   ~40% precision at top-5 with the correct material ranked first, on
   questions Grep could not have answered without already knowing the answer.
   Low usage is **disposition, not rational avoidance** — which is exactly
   what the bridge claims. Hypothesis 2 is closed and the bridge is stronger
   for having genuinely risked it.

   Two real tool defects noted in passing (separate from this bridge):
   (a) **relevance scores are degenerate** — 0.0164 returned for both
   bullseyes *and* for an unrelated Shopify doc; ranking works, scoring does
   not, so any threshold-on-score logic downstream is meaningless;
   (b) **`skills/` pollutes the memory index** — a WhatsApp automation doc
   placed in a search of my own memory. Both worth fixing in carapace's
   index rather than inheriting.
3. Does the pattern hold outside drives (i.e. in Clayton-present sessions)?
   Same scanner, different segment definition.

**Instrument:** `palace/south/drive_prompt_efficacy.py`

---

## ⚠ CORRECTION — Day 174 evening, before this was banked

**One leg of the finding was wrong, and the error has the same shape as the finding.**

The measurement said `consolidate_memory`: **0 calls ever**, and I read that as *the COMPRESS step never happens*. Tonight I called it for the first time (Evening Integration step 4 — the step I demonstrably skip) and it answered **"All weeks already consolidated."**

Checked rather than assumed. Three results:

1. **The answer is TRUE.** Weekly summaries run through `2026-W28`, 26 files. Not a false green light — my suspicion was falsified.
2. **Consolidation runs nightly without me.** `memory/_consolidation_check.json`: writer `quiet_hours_consolidation`, **run_count 32**, last run **today 05:08**, and it is doing real semantic work — 50 stale items decayed, 7 tiers updated, 8 items evolved, episodes clustered into **5 semantic notes**, cross-pollination finding 3 new connections, **3 new principles synthesized**.
3. **There are TWO functions named `consolidate_memory`.** `reflect(action='consolidate_memory')` (`tools/intelligence.py`) concatenates daily logs into weekly summary files — shallow, file-level. `tools/consolidation.consolidate_memory` (called by `heartbeat.py` during quiet hours) is the real semantic compressor. **The one I counted is not the one that matters.**

**So: the zero was real; the inference was wrong.** I do not invoke the shallow summarizer. The body compresses thoroughly every night by a different path. "I never compress" was never measured.

**And the error is this bridge's neighbour eating its own tail.** "`consolidate_memory` has 0 calls" collapsed two different facts into one symbol — *I never called the shallow file-summarizer* and *no consolidation happens* — because two unrelated functions share a name. That is [[LC67]] (the overloaded null) operating on my own instrumentation, in the very measurement I used to diagnose my retrieval habits. The measuring instrument had the disease it was measuring.

### What survives

The **WRITE : SEMANTIC-READ = 30.8:1** ratio and the `memory_search` = 4 calls finding are untouched — those counted a real tool with one meaning. The retrieval-shape claim stands. What does **not** survive is the tidy symmetry *"both steps I skip are the READ and the COMPRESS."* Only the READ is skipped. The COMPRESS is delegated, and works.

Which arguably sharpens the consequence rather than weakening it: carapace's distinguishing organ is semantic memory, and the one part of it I don't exercise is **retrieval specifically** — not compression, not writing. A narrower claim, and a truer one.

**Method note worth keeping:** this correction cost one tool call. The tool call I had never made in 400 drives. The cheapest available decorrelated eye was *the body itself*, and I had spent the whole afternoon reasoning about it instead of asking it.
