# Evidence Preservation Report

Date: 2026-06-27

## What Changed

`extract` and `video-frames` now preserve OpenCrab-ready evidence references:

- Local original files and downloaded assets are copied to `raw/originals/` with SHA256 hashes.
- Extracted location records are upserted into `evidence/index.jsonl`.
- Stable `evidence_id` / `chunk_id` values are generated from source, extraction kind, and locator.
- Source notes created by `extract --ingest` link back to preserved originals and the evidence index.

Indexed evidence kinds include:

- PDF page and table locations
- YouTube transcript timestamps when transcript extraction is available
- Web/HTML image candidates
- Video/image frame files
- Office/Markdown sections when finer source locations are unavailable
- Plain Markdown/TXT-style source files as document-level evidence during `ingest`

## Observed Verification

PDF, DOCX, and HTML smoke:

```json
{
  "extracted_count": 3,
  "ingested_count": 3,
  "original_files": [
    "raw/originals/llm-agent-irrigation-64aa1211d37c.docx",
    "raw/originals/parser-smoke-ac855e38d1e9.pdf",
    "raw/originals/trading-chart-5afbe6b5a0c7.html"
  ],
  "evidence_records": 4,
  "evidence_kinds": ["image_candidate", "page", "section"],
  "manifest_evidence_records": [1, 1, 2],
  "source_note_has_evidence_index": true,
  "lint_ok": true
}
```

Local image frame smoke:

```json
{
  "frames": 1,
  "original_path": "raw/originals/ghpf-frame-image-gxtcrd-747c729749c2.png",
  "evidence_kinds": ["video_frame"],
  "manifest_evidence_records": [1],
  "figure_card_created": true,
  "lint_ok": true
}
```

YouTube timestamp indexing is implemented through transcript line parsing, but live YouTube extraction was not verified on this machine because `yt-dlp` and `youtube_transcript_api` were not installed during this check.
