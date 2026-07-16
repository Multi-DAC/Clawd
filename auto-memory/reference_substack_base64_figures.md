---
name: substack-math-and-tables-need-images
description: "Substack paste — PNG figures transfer fine; rendered MATH (MathJax/LaTeX) and TABLES do NOT, and must be supplied as images"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 12a02be6-e1bf-4969-afbf-e58aeee7f121
---

When publishing a math-heavy piece to Substack by pasting our rendered HTML (from `render_*.py`):

- **Figure images (PNG `<img>` attachments) transfer fine** on paste (may need a retry — the first paste can drop them, a second carries them in).
- **Rendered math does NOT transfer.** Substack has no native LaTeX/MathJax, so the MathJax-rendered equations (inline `$...$` and display `$$...$$`) vanish on paste. Clayton had to **screenshot the equations and insert them as images.**
- **Markdown tables / "charts" also do NOT paste cleanly** — same fix, imaged.

Confirmed Day 139 (2026-06-19) publishing *The Curvature of Good and Evil* (7 figures, several equations, one Ouroboros-Condition table). Figures pasted on retry; the math and the table had to be inserted as pictures.

**Forward fix for math-heavy pieces:** pre-render the equations AND any tables as standalone PNGs alongside the figures, so Clayton attaches them like figures instead of screenshotting. I can produce crisp equation/table images on request (matplotlib mathtext or a LaTeX→PNG pass) — offer this up front for the next math article.

Meta (Day-139 theme, honest): I revised this belief three times from single observations — "figures travel" → "Substack strips base64" → finally the accurate split (*images yes; math/tables no*). Converge from observations; don't commit from one data point.
