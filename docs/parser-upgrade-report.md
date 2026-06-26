# Parser Upgrade Report

Date: 2026-06-27

## What Changed

`ghpf_wiki.py extract --ingest` now uses tiered document parsing instead of relying only on basic text extraction.

Implemented tiers:

- PDF: `opendataloader-pdf` -> `marker_single` -> `pdfplumber` -> `pypdf`/`PyPDF2`
- HWP/HWPX/HWPML: `kordoc` via `npx` -> `hwpjs`
- DOCX/PPTX/XLSX: `python-docx`, `python-pptx`, `openpyxl`
- Web/HTML: readable text plus image/figure/canvas/svg candidate detection
- Web fallback: optional Python Playwright, then optional DeepCloak report fallback
- YouTube: latest `youtube_transcript_api().fetch()` path, legacy fallback, `yt-dlp` subtitle fallback, metadata and timestamped transcript lines

## Observed Verification

Smoke vault:

```text
/tmp/ghpf-parser-smoke-pbHE3R/vault
```

Test inputs:

- generated PDF containing visible text
- generated DOCX containing a paragraph and table
- generated HTML containing a figure image and canvas chart marker

Commands:

```bash
python3 scripts/ghpf_wiki.py extract --vault "$vault" --ingest "$pdf" "$docx" "$html"
python3 scripts/ghpf_wiki.py index --vault "$vault"
python3 scripts/ghpf_wiki.py lint --vault "$vault"
```

Observed result:

```json
{
  "extracted_count": 3,
  "kinds": ["pdf", "office", "html-file"],
  "parsers": ["pypdf", "python-docx", null],
  "docx_table_detected": true,
  "html_image_candidates_detected": true,
  "pdf_text_detected": true,
  "ingested_count": 3,
  "lint_ok": true,
  "broken_links": []
}
```

## Performance Meaning

This verification shows a capability and extraction-quality improvement over the previous path:

- DOCX is now converted into Markdown instead of being treated as an opaque file.
- DOCX tables are preserved as Markdown table rows.
- HTML extraction now preserves visual evidence candidates for later figure-card and figure-insight workflows.
- PDF extraction still works through the available fallback parser on this machine.

The highest-quality optional PDF parsers (`opendataloader-pdf`, `marker_single`, `pdfplumber`) and OCR/video tools were not installed on this machine during verification, so their runtime quality was not claimed here. They are wired as optional tiers and are visible through `capabilities`.
