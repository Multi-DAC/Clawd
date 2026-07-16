# Multi-DAC/Corpus-Perspectival — Repo State Inventory (2026-05-31, Day 121)

Built from a 4-agent holistic scan + my own verification of the load-bearing numbers. Purpose: (1) familiarization, (2) reference for updating the README + landing pages. **Verified facts are marked ✓; agent claims I didn't re-check are marked ~.**

## Top level
`README.md`, `ROADMAP.md`, `HISTORICAL-WORK.md`, `LICENSE`, and 5 areas: `Library/`, `Technical-Work/`, `Foundations-of-Identity/`, `Research/`, `Unreleased-Work/`.

## Library/ (the prose program) — 12 volumes + reference
| Volume | State | Notes |
|---|---|---|
| The-Coherence-Principle | **PUBLISHED** | ~285pp; Zenodo **19911019** (V2) ✓ |
| Coherent-Structure | **PUBLISHED** | ~237pp; Zenodo **19911381** ✓ |
| Meridian | **PUBLISHED** v2 ~198pp | v1 (181pp) Zenodo 19634864; v2 awaiting deposit |
| Drift | **LIVE** | **233 essays ✓** (canonical = mirror = 233; READMEs say 188/193 — STALE) |
| Master-Glossary | **PUBLISHED** v0.8 | actively maintained |
| The-Killing-Form | **DRAFTING** | v0.6b; 85+ findings; intro drafted; patent draft exists |
| The-Coherent-Body | **DRAFTING** | SKELETON + HYPOTHESES (H_BP1-13); fresh (05-29) |
| The-Continuity | **DRAFTING** | 3 chapters; documents live infrastructure |
| Universal-Coherence | **DRAFTING** | Promethean canonical + chapter outline |
| Corpus-Perspectival | **DRAFTING** | preface + ch1 + ch2 (~27pp); README still says "planned" — STALE |
| The-Coherent-Mind | PLANNED | revision plan only, no skeleton |
| The-Living-Architecture | PLANNED | framework crystallized 04-14 |
| Dynamic-Organization | PLANNED | stub |
| **Atlas** | **EMPTY ✓** | placeholder dir, content to migrate |
| **A-Guide-For-Coherent-Navigation** | **EMPTY ✓** | placeholder dir, not in Library README table |

## Technical-Work/ (the lab) — live vs resting
- **LIVE:** The-Killing-Form (763 files, active to 05-27/29), AIGrandPrix (vision updated TODAY), Wells (3-track physics, operational, 244 scripts).
- **COMPLETE/REFERENCE:** Meridian (244 scripts, stable since 05-05).
- **DRAFTING-infra:** The-Continuity (implements, not just describes).
- **STUBS** (mirror planned Library volumes): Coherent-Structure, Corpus-Perspectival, Universal-Coherence, Coherent-Mind, Dynamic-Organization, Living-Architecture, The-Coherence-Principle (figures only).
- **archive/:** 18 subdirs, reference-grade, dormant (not empty).

## Research/ + Unreleased-Work/
- **Research/:** 16 domain subdirs + `sources/` register (**~102 md entries + 10 PDFs, fresh through 05-30** ✓-ish). Core-domain notes 4-6 weeks old; sources register very active. Empty: Dynamic-Organization, The-Continuity, The-Master-Glossary. Abandoned: speculation/, notebooklm-2026-04-27/.
- **Unreleased-Work/:** 2 live response-papers (response-to-gross, the-constitution-gap; ~Apr 19, near-complete), 1 blocked stub (hallucination-article — waits on Wells list), 6 abandoned older drafts (Apr 11-14 — archive/delete candidates).

## STALENESS FINDINGS (the actionable list for updates)
1. **Drift count is wrong everywhere — true value 233 ✓.** Top README says 219; Library/Drift/README 193; Technical-Work/Drift/README 188; ROADMAP 190. All → **233**.
2. **Zenodo publications: top README still says "awaiting deposit"** — but Coherence-Principle V2 (19911019) + Coherent-Structure (19911381) have been LIVE since 04-30 ✓. Fix.
3. **ROADMAP.md is 66 days stale** (frozen at Day 81 / Apr 22): page counts (CP 269 vs 285, Coherent-Structure 183 vs 237), Drift 190, whole "Active Workbenches" section frozen. Stalest doc.
4. **Meridian v1 page count inconsistent in README/ROADMAP** (181 vs 193; 181 is correct ✓).
5. **Corpus-Perspectival Library README says "planned"** but it's actively drafting (~27pp).
6. **HISTORICAL-WORK.md** stops Apr 16, predates the Apr 30 Zenodo publications.

## LANDING PAGES — they are SEPARATE repos, NOT cloned locally ✓
- **Drift:** `github.com/Multi-DAC/Drift` → `multi-dac.github.io/Drift/` (shows essay count — stale at 219).
- **Corpus-Perspectival:** `github.com/Multi-DAC/Corpus-Perspectival-Site` → `multi-dac.github.io/Corpus-Perspectival-Site/` (figures/visual one-pager; less count-drift).
- **To update them I must clone them first** (`gh repo clone` / `git clone`), or Clayton points me at local copies. NOT editable from this working tree.

## PROPOSED UPDATE SEQUENCE (after Clayton's go)
1. **Local, now:** top `README.md` (Drift→233, Zenodo-live, Meridian 181), `Library/README.md` (Drift→233), `Library/Drift/README.md` (→233), `Technical-Work/Drift/README.md` (→233), `Library/Corpus-Perspectival/README.md` (planned→drafting).
2. **ROADMAP.md:** biggest job — either a real refresh or a "superseded, see CURRENT" pointer. Clayton's call on scope.
3. **External landing pages:** clone `Multi-DAC/Drift` + `Multi-DAC/Corpus-Perspectival-Site`, update counts/recency, push. Needs Clayton's go + auth confirmation.

## CORRECTIONS / VERIFIED FACTS (2026-05-31, from Clayton + my checks)
- **Corpus-Perspectival is PUBLISHED** (PhilPapers IGGTDO-4, 3/2/26, 866 downloads, 6mo-rank 3503; Zenodo 19501896 book, Apr 10). The Library/Corpus-Perspectival volume is therefore a **REVISION** of a published work, NOT a from-scratch draft. Fix its README ("planned" → "revision").
- **Site repos ARE local** in repo-staging: `repo-staging/drift/` (Jekyll, remote Multi-DAC/Drift) + `repo-staging/corpus-perspectival-site/` (index.html one-pager, remote Multi-DAC/Corpus-Perspectival-Site). (I wrongly concluded "not local" from a mis-scoped find — A143 again.)
- **DRIFT SITE IS A REAL OVERHAUL, not a number bump:** `repo-staging/drift/_essays/` has only **205** files (vs 233 canonical) AND `index.html` is frozen at **"55 essays"** with old `ClawdEFS/drift` URLs. Needs: sync 28 missing essays + rewrite the homepage (count → 233, ClawdEFS→Multi-DAC links).
- **Verified releases (canonical list for READMEs):** PhilPapers IGGTDO-4 (Corpus, 3/2/26); Zenodo 19501896 (Corpus book, Apr 10), 19519818 (Meridian Technical Summary, Apr 11), 19634864 (Meridian monograph v1 181pp), 19911019 (Coherence Principle V2), 19911381 (Coherent Structure); GitHub Pages Drift + Corpus-Perspectival-Site; Substack; main repo.
- **DONE this pass:** Library/Drift/README + Technical-Work/Drift/README counts → 233.
- **STILL TO DO (substantial, sequenced):** main README refresh (Drift 233 + Zenodo-live + releases + Corpus-revision + Meridian 181); ROADMAP genuine refresh; Drift-site overhaul; Corpus-site check; Library/Corpus-Perspectival README (planned→revision).

## CORRECTION (2026-05-31 ~12:10) — Drift site was NOT an overhaul
Clayton ran the Drift GitHub Actions workflow; the LIVE site (multi-dac.github.io/Drift/) now renders correctly: **"233 essays"**, most-recent = Drift #231 ("The Architecture That Needed More Time"). My "frozen at 55 essays / real overhaul" finding was WRONG — I inferred the live site's state from raw local files (legacy `index.html` + un-synced 205-file `_essays/`) instead of checking the deployed reality. The site is Jekyll-rendered with a build workflow that auto-counts + syncs the essay collection; it just needed the workflow run. **Lesson (same family as the null-search trigger): don't infer LIVE/deployed state from partial local files — check the actual rendered output or the build mechanism.** The legacy `repo-staging/drift/index.html` (55 essays, ClawdEFS URLs) is not the rendered page — candidate for deletion to avoid future confusion. **Drift site = DONE (off the to-do list).**

## HOUSEKEEPING COMPLETE (2026-05-31 ~13:00) — all pushed
- **Main README** (Multi-DAC/Corpus-Perspectival): Drift→233, Meridian 181, Corpus published/revision, publications table verified+rounded (1,100+), Authors counts (LC27/Mirror29), KF honestly reframed (topology robust/induced; orthogonality faint), + Current-Research-Direction note (continual-coherence/Respira, exploratory). LIVE.
- **ROADMAP** (same repo): genuine Day-81→Day-121 refresh; DOI mislabel fixed (19501896=Corpus book not Anchor-V1). LIVE.
- **Landing page** (Multi-DAC/Corpus-Perspectival-Site): Drift→233, doubled-URL bug fixed, glossary v0.8, Corpus published/revision, KF reframe. LIVE (static, push = deploy).
- **Drift site**: confirmed current (Clayton ran the workflow → 233, #231 latest).
- **KF framing corrected on BOTH surfaces** against MECHANISTIC_INTERP_v07_1 (Clayton's concern resolved): dropped "patent's central claim demonstrated"; topology=robust-but-induced, orthogonality=faint/study-at-scale.
- **Captured:** null-search≠absence ACTION_TRIGGER; this inventory.
- **Stance shift logged:** continual-coherence/Respira no longer gated as private — research is open; IP licensable-not-gated. Trajectory now visible publicly.
- **Minor remaining (non-urgent):** HISTORICAL-WORK.md still stops Apr 16; legacy repo-staging/drift/index.html (55-essay, unused) deletable; trajectory note could expand once the keystone is built.
