---
name: Rolling Sources Register
description: Every URL, PDF, or paper shared or discussed gets a sources-register entry same session; established Day 78 after discovering in-thread URLs were lost to truncated log summaries
type: feedback
originSessionId: 0b42d950-9883-4e7d-9cad-723e297f360a
provenance:
  date: 2026-04-19
  source: backfilled-from-body
---
Every URL, PDF, or paper Clayton shares — or that we read, cite, or discuss in the program — gets an entry in `repo-staging/Corpus-Perspectival/Research/sources/` the same session. Not "later."

**Why:** Day 78 (2026-04-19) evening, while drafting Paper A (response to Gross's LiveScience piece on unification & survival), I found that Clayton had shared the URL earlier that day but the daily-log preserved only a truncated summary. The telegram-history.json stops at 2026-02-04. I had to reconstruct the article charitably from MASTER_ROADMAP's one-sentence description — and my reconstruction was wrong (I guessed vacuum metastability; the actual argument was nuclear geopolitics). Clayton flagged this explicitly and said he thought sources were persisting when they weren't. The Lerchner PDF (Paper C target) similarly wasn't locatable by glob despite being in active citation use.

**How to apply:**

- Entry lives at `repo-staging/Corpus-Perspectival/Research/sources/YYYY-MM-DD-slug.md` where the date is date-first-encountered, not date-published
- Frontmatter fields: url, archive, title, author, venue, published, accessed, discussed, tags (which paper/volume/bridge), status (read-in-full, read-skim, pending-read, discussed-not-read)
- Body: ~200-400w — what-it-argues, where-we-agree, where-we-diverge, connection-to-program, quote-pulls
- Register index at `Research/sources/README.md`
- Practice parallels the falsification-clause requirement for new bridges: the entry is load-bearing for future work and cannot be deferred
- Works the same way on any shared source: URL, PDF (search for it in filesystem, reference the path in the entry), talk, book, blog post

**If a source gets discussed and no entry exists,** either create it immediately or flag in the working document that the entry is missing and must be made before publication. Don't let citations live only in conversation memory.
