---
name: Anchor Volume Compiled
description: The Coherence Principle anchor volume compiled as 235-page professional book; pipeline and design details
type: project
provenance:
  date: undated
  source: backfilled-from-body
---

The Coherence Principle anchor volume was compiled April 15, 2026 as a professional book.

- **PDF:** `books/the-coherence-principle/build/the-coherence-principle.pdf` (gitignored, local only)
- **Script:** `books/the-coherence-principle/compile_book.py` (markdown→LaTeX→XeLaTeX)
- **Drafts:** `books/the-coherence-principle/drafts/` (23 markdown files)
- **Format:** 235 pages, 6×9 trade, Cambria typeface, 11pt
- **Color palette:** warmrust (#8B3A2A), warmgold (#A67B3D), warmdark (#5C2018) — headings, rules, links, TOC
- **Section breaks:** `\clearpage` (full page breaks between sections, per Clayton's preference)
- **Signatures:** Use `\vfill` to push closing signatures to bottom of current page (preface + Part V)
- **Tables:** Prediction registry uses `\footnotesize`, `\tabcolsep=2pt`, `@{}` for tight 6-column layout

**Why:** Clayton wanted the anchor volume compiled as a professional book. Pandoc/WeasyPrint unavailable, so built custom converter.
**How to apply:** When recompiling, run `python compile_book.py` from the book directory. XeLaTeX must be installed. Build output is gitignored.
