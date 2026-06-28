---
name: ghpf-wiki
description: Set up, maintain, query, and export a GHFP Obsidian-first LLM Wiki for research papers, trading strategy notes, codebase knowledge, graph/context sidecar artifacts, and agent task memory. Use when the task mentions GHFP, LLM Wiki, Obsidian vaults, paper ingestion, Bitcoin/trading strategy synthesis, backtest notes, Codex/Claude/Antigravity wiki setup, context packs, wikilinks, or SwarmVault-style sidecar features.
---

# GHFP Wiki

Use this skill to create and operate a portable LLM Wiki.

## Core Model

- Use `wiki/` as the canonical human-readable Markdown wiki.
- Use `raw/` as the immutable source intake folder.
- Use `raw/originals/` as the preserved original/downloaded asset archive.
- Use `evidence/index.jsonl` as the machine-readable source-location index for OpenCrab promotion.
- Use `raw/graphify_articles/` for bulk Graphify intake; normal `ingest` skips this folder.
- Support `_raw/` as a compatibility intake folder for Obsidian capture tools.
- Use `graph_imports/` as a non-canonical Graphify reference layer.
- Use `swarmvault/` for sidecar graph, context-pack, export, and task-ledger artifacts.
- Use `swarmvault/cache/` only for disposable cache.
- Keep `schema/AGENTS.md`, `wiki/index.md`, `wiki/log.md`, and `wiki/manifest.json` current.
- Preserve existing notes. Merge targeted updates instead of rewriting broad folders.
- Add `[[wikilinks]]` between papers, methods, claims, entities, strategies, experiments, and code modules.

## Setup

Before assuming optional extractors exist, check the local environment:

```bash
python3 scripts/ghpf_wiki.py capabilities --vault <path>
```

For a fresh clone, prefer the one-command install:

```bash
./install.sh
```

This creates `./my-vault`, installs project skills for Codex/Claude Code/Antigravity, checks capabilities, runs lint, and writes `my-vault/swarmvault/exports/install-report.json`.

Run:

```bash
python3 scripts/setup_vault.py --vault <path> --profile auto
```

Use explicit profiles when the user already knows the domain:

```bash
python3 scripts/setup_vault.py --vault <path> --profile research
python3 scripts/setup_vault.py --vault <path> --profile trading
python3 scripts/setup_vault.py --vault <path> --profile codebase
python3 scripts/setup_vault.py --vault <path> --profile mixed
```

## Ingest

Use the helper for deterministic intake:

```bash
python3 scripts/ghpf_wiki.py ingest --vault <path> [source files...]
```

For PDF, web page, local HTML, Office/HWP, or YouTube transcript sources, extract and ingest in one step:

```bash
python3 scripts/ghpf_wiki.py extract --vault <path> --ingest <pdf-or-url-or-youtube>
python3 scripts/ghpf_wiki.py extract --vault <path> --ingest <docx-or-pptx-or-xlsx-or-hwp>
```

Natural-language aliases such as "이 문서를 LLM Wiki에 저장해줘", "이 PDF 위키화해줘", "이 웹주소를 LLM Wiki에 저장해줘", "이 유튜브를 위키에 저장해줘", or "save this URL to the LLM Wiki" mean:

```bash
python3 scripts/ghpf_wiki.py extract --vault <path> --ingest <pdf-or-url-or-youtube-or-office-doc>
python3 scripts/ghpf_wiki.py index --vault <path>
python3 scripts/ghpf_wiki.py lint --vault <path>
```

Use the explicit vault when provided; otherwise use the current known vault or `./my-vault` after setup. Report the source note, preserved original or source URL, `evidence/index.jsonl`, evidence count, and lint status. If the user explicitly asks for YouTube/video/image frame analysis, also run `video-frames --ingest --figure-card`.

Extraction tiers:

1. PDF: `opendataloader-pdf`, then `marker_single`, then `pdfplumber`, then `pypdf`/`PyPDF2`.
2. HWP/HWPX/HWPML: `kordoc` via `npx`, then `hwpjs`.
3. DOCX/PPTX/XLSX: Python office libraries when installed.
4. Web/HTML: static extraction plus image/figure candidates, then optional Playwright/DeepCloak fallback.
5. YouTube: latest `youtube_transcript_api.fetch()` with timestamped lines, metadata from `yt-dlp`, and `yt-dlp` subtitle fallback.

For YouTube, local video, or image visual evidence, sample frames, analyze them, ingest the generated Markdown, and create a figure card:

```bash
python3 scripts/ghpf_wiki.py video-frames --vault <path> --source <youtube-or-video-or-image> --every-seconds 30 --max-frames 12 --ingest --figure-card
```

For each source in `raw/` or `_raw/`:

1. Create a source note under `wiki/sources/`.
2. Add frontmatter, source provenance, a source coverage checklist, and key `[[wikilinks]]`.
3. Extract durable concepts, entities, claims, methods, strategies, experiments, and open questions.
4. Merge into existing `wiki/concepts/`, `wiki/entities/`, project, paper, trading, or code notes.
5. Add source references and `[[wikilinks]]`.
6. Append the operation to `wiki/log.md`.

If older source notes still read like extraction logs or web navigation text, regenerate them with:

```bash
python3 scripts/ghpf_wiki.py source-curate --vault <path> wiki/sources/<source-note>.md
python3 scripts/ghpf_wiki.py source-curate --vault <path> --all-sources
```

`source-curate` keeps source provenance and rewrites the note into Summary, Key Claims, Relevance To Current Work, Limitations, Key Links, Source Coverage, and Open Questions sections.

## Graphify Import

Use Graphify for bulk source maps, then import the generated graph as a reference layer:

```bash
python3 scripts/ghpf_wiki.py graphify-import --vault <path> --graph <graph.json>
```

Rules:

1. Put bulk source articles in `raw/graphify_articles/`.
2. Keep imported map notes under `graph_imports/`.
3. Search `graph_imports/` for broad context, but promote durable findings into `wiki/`.
4. Do not treat `graph_imports/` as canonical source-of-truth notes.

## Maintain

Use pipeline state to prevent skipped steps:

```bash
python3 scripts/ghpf_wiki.py state --vault <path> init
python3 scripts/ghpf_wiki.py state --vault <path> check ingest
python3 scripts/ghpf_wiki.py state --vault <path> complete ingest
```

Run lint after ingest, file-back, or broad wiki edits:

```bash
python3 scripts/ghpf_wiki.py lint --vault <path>
```

Run quality scoring for wiki pages. Use `--strict` when a pass/fail gate is needed:

```bash
python3 scripts/ghpf_wiki.py quality --vault <path> --strict wiki/sources/<source-note>.md
```

Compare two Markdown notes section-by-section before merging or replacing content:

```bash
python3 scripts/ghpf_wiki.py diff --vault <path> wiki/syntheses/old.md wiki/syntheses/new.md
```

File reusable answers back into the wiki:

```bash
python3 scripts/ghpf_wiki.py file-back --vault <path> --title "<answer title>" --body "<markdown>"
```

## Sidecar Features

Refresh graph artifacts:

```bash
python3 scripts/ghpf_wiki.py graph --vault <path>
```

Audit graph health and strengthen relevant links:

```bash
python3 scripts/ghpf_wiki.py link-audit --vault <path>
python3 scripts/ghpf_wiki.py link-strengthen --vault <path> --page wiki/sources/<source-note>.md --max-links 5 --backlink
```

Build a context pack:

```bash
python3 scripts/ghpf_wiki.py context --vault <path> --query "<task>"
```

Record task memory:

```bash
python3 scripts/ghpf_wiki.py task start --vault <path> --title "<task>"
python3 scripts/ghpf_wiki.py task finish --vault <path> --title "<task>" --note "<result>"
```

## Insight Workflows

Use cards and hybrid retrieval for paper, experiment, and strategy insight:

```bash
python3 scripts/ghpf_wiki.py card --vault <path> --type paper --all-sources
python3 scripts/ghpf_wiki.py card --vault <path> --type experiment wiki/sources/<source-note>.md
python3 scripts/ghpf_wiki.py card --vault <path> --type strategy wiki/sources/<source-note>.md
python3 scripts/ghpf_wiki.py index --vault <path>
python3 scripts/ghpf_wiki.py search --vault <path> --query "<query>"
python3 scripts/ghpf_wiki.py insight --vault <path> --type experiment --query "<query>"
python3 scripts/ghpf_wiki.py insight --vault <path> --type strategy --query "<query>"
python3 scripts/ghpf_wiki.py evaluate --vault <path> --type experiment --target wiki/syntheses/<insight>.md
```

Prefer this shape:

1. Paper cards for contribution, method, relevance, and limitation.
2. Experiment cards for hypothesis, variables, metrics, baselines, and risks.
3. Strategy cards for thesis, components, backtest plan, risk controls, and rejection rules.
4. Hybrid search before synthesis.
5. Lightweight evaluation before treating an insight as durable.

## Figure Workflows

Use figure cards and figure design exports for manuscript figures, experiment diagnostics, and trading charts:

```bash
python3 scripts/ghpf_wiki.py figure-card --vault <path> --domain auto --all-sources
python3 scripts/ghpf_wiki.py figure-insight --vault <path> --domain irrigation --query "<figure task>"
python3 scripts/ghpf_wiki.py figure-insight --vault <path> --domain trading --query "<figure task>"
python3 scripts/ghpf_wiki.py figure-export --vault <path> --design wiki/figure-designs/<design>.md --domain trading --name Figure_1 --run
```

Use `video-frames` first when useful visual evidence lives in chart screenshots, YouTube strategy videos, experiment videos, or slide frames.

Rules:

1. Use `wiki/cards/figures/` for reusable visual patterns.
2. Use `wiki/figure-designs/` for proposed panel layouts and manuscript/report guidance.
3. Use `swarmvault/exports/figures/` for generated Python, PDF, SVG, and PNG files.
4. Export PDF/SVG first; PNG is for preview or raster fallback.
5. Keep captions in the manuscript or note, not inside the image.

Prune disposable cache without touching `raw/` or `wiki/`:

```bash
python3 scripts/ghpf_wiki.py cache-clean --vault <path> --max-age-days 30 --keep-latest 10 --dry-run
python3 scripts/ghpf_wiki.py cache-clean --vault <path> --max-age-days 30 --keep-latest 10
```

## Query

Answer from the wiki first:

1. Read `wiki/index.md`.
2. Search titles, headings, tags, and summaries.
3. Open the smallest set of relevant pages. If needed, search `graph_imports/` for broad Graphify context.
4. Cite page paths.
5. If the answer should compound, save it under `wiki/syntheses/` or an appropriate domain folder with `file-back`.

## Quality Gates

Before using the wiki as high-value context, prefer this loop:

1. `capabilities` to know what this machine can extract.
2. `extract --ingest` for PDF, web, local HTML, or YouTube transcript sources.
3. `video-frames --ingest --figure-card` for YouTube/local-video/image visual evidence.
4. `ingest` to compile raw material into source notes.
5. `card`, `index`, `search`, and `insight` for paper, experiment, or strategy insight.
6. `figure-card`, `figure-insight`, and `figure-export` for figure design and chart exports.
7. `quality` and `lint` to check metadata, coverage, broken links, and manifest drift.
8. `link-audit` and `link-strengthen` to improve graph connectivity.
9. `evaluate` before relying on generated insight.
10. `graphify-import` when a bulk Graphify map should become searchable reference context.
11. `file-back` to save reusable answers.
12. `graph` and `context` to export sidecar artifacts for agents.
13. `cache-clean --dry-run` before deleting disposable cache.
