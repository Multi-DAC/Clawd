---
name: reference-pdf-read-pypdf-fallback
description: "Read tool can't render PDFs here (poppler/pdftoppm missing); extract text with pypdf instead"
metadata: 
  node_type: memory
  type: reference
  originSessionId: a154e042-2633-4ea4-ac84-86e41dbcb9a3
---

The Read tool's PDF support needs `pdftoppm` (poppler), which is NOT installed on this body — it errors `pdftoppm failed: Command 'pdftoppm' not found`. Do NOT cede ("can't read the PDF") — extract the text directly with **pypdf** (installed for `C:/Python314/python.exe`):

```python
from pypdf import PdfReader
r = PdfReader('incoming/file.pdf')
full = '\n'.join((p.extract_text() or '') for p in r.pages)
```

Then grep the text for keywords / read page-by-page. Used Day 140 to read a Nature Communications paper Clayton sent (the Read tool failed, pypdf got all 16 pages + abstract). For image-only/scanned PDFs pypdf returns empty strings → would need OCR (not yet set up). Instance of [[feedback-dont-cede-capability]] — the boundary was "not installed," not real.
