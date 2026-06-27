# ghpf-llm-wiki

Obsidian-first LLM Wiki scaffold for research papers, trading strategy notes, codebase knowledge, and agent task memory.

The default pattern is:

- **Canonical wiki writer:** Obsidian-style Markdown under `wiki/`
- **Raw source intake:** `raw/` with `_raw/` compatibility for Obsidian capture tools
- **Bulk graph reference layer:** Graphify intake in `raw/graphify_articles/` and imported maps under `graph_imports/`
- **Sidecar intelligence:** SwarmVault-inspired graph, context packs, exports, and task ledger under `swarmvault/`
- **Agent compatibility:** Codex via `AGENTS.md`, Claude Code via `CLAUDE.md`, and Antigravity via `.agent/`

## Quick Start

```bash
git clone https://github.com/sung-minkwon/ghpf-llm-wiki.git
cd ghpf-llm-wiki
./install.sh
```

`./install.sh` runs the default post-clone flow: create `./my-vault`, install Codex/Claude Code/Antigravity project skills, print capabilities, run lint, and write `my-vault/swarmvault/exports/install-report.json`.

Manual equivalent:

```bash
python3 scripts/bootstrap_install.py --vault ./my-vault --profile auto --agents codex,claude,antigravity
```

Manual step-by-step install:

```bash
python3 scripts/setup_vault.py --vault ./my-vault --profile auto
python3 scripts/install_agents.py --scope project --agents codex,claude,antigravity
python3 scripts/ghpf_wiki.py capabilities --vault ./my-vault
python3 scripts/ghpf_wiki.py lint --vault ./my-vault
```

Then open `my-vault/` as an Obsidian vault and ask your agent to use the GHFP wiki workflow.

### Existing Obsidian Vaults

When connecting GHFP to an existing Obsidian vault, pass the folder that directly contains `.obsidian`:

```bash
python3 scripts/setup_vault.py --vault /path/to/your-vault --profile auto
python3 scripts/ghpf_wiki.py doctor --vault /path/to/your-vault
```

Do not pass a parent folder that merely contains an Obsidian vault as a child. `setup_vault.py` refuses that case and prints the nested vault path to use instead.

## Profiles

`setup_vault.py` can create folders from a profile:

- `research`: papers, methods, citations, thesis notes
- `trading`: strategies, backtests, market data, risk rules
- `codebase`: architecture, modules, experiments
- `mixed`: combined research + trading + code workflow
- `auto`: scan source material and choose the profile

Example:

```bash
python3 scripts/setup_vault.py --vault ~/obsidian/ghpf --source ~/papers --source ~/trading-notes --profile auto
```

## Sidecar Commands

Check installed optional capabilities:

```bash
python3 scripts/ghpf_wiki.py capabilities --vault ./my-vault
```

Ingest source files into the compiled wiki:

```bash
python3 scripts/ghpf_wiki.py ingest --vault ./my-vault ./paper-notes.md
```

Extract PDF, web page, local HTML, Office/HWP documents, or YouTube transcript sources into Markdown, then ingest them:

```bash
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest ./paper.pdf
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest ./report.docx
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest ./korean-document.hwp
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest https://example.com/article
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest https://www.youtube.com/watch?v=<id>
```

Sample and analyze YouTube, local video, or image frames as visual evidence:

```bash
python3 scripts/ghpf_wiki.py video-frames --vault ./my-vault --source https://www.youtube.com/watch?v=<id> --every-seconds 30 --max-frames 12 --ingest --figure-card
python3 scripts/ghpf_wiki.py video-frames --vault ./my-vault --source ./chart-frame.png --ingest --figure-card
python3 scripts/ghpf_wiki.py video-frames --vault ./my-vault --source ./strategy-video.mp4 --ocr --ingest --figure-card
```

Track the Karpathy-style pipeline so steps are not skipped:

```bash
python3 scripts/ghpf_wiki.py state --vault ./my-vault init
python3 scripts/ghpf_wiki.py state --vault ./my-vault complete setup
python3 scripts/ghpf_wiki.py state --vault ./my-vault check ingest
```

Lint wiki health and write a quality report:

```bash
python3 scripts/ghpf_wiki.py lint --vault ./my-vault
python3 scripts/ghpf_wiki.py quality --vault ./my-vault --strict wiki/sources/paper-notes.md
```

File a reusable answer back into the wiki:

```bash
python3 scripts/ghpf_wiki.py file-back --vault ./my-vault --title "BTC regime filter" --body "Reusable synthesis with [[wikilinks]]."
```

Compare section-level changes between two notes:

```bash
python3 scripts/ghpf_wiki.py diff --vault ./my-vault wiki/syntheses/old.md wiki/syntheses/new.md
```

Build a wikilink graph:

```bash
python3 scripts/ghpf_wiki.py graph --vault ./my-vault
```

Obsidian Graph View note: `wiki/index.md` is a navigation hub and intentionally links many pages, so it can dominate the visual graph. For a more semantic graph, filter it out in Obsidian:

```text
-path:wiki/index.md -path:wiki/log.md -path:wiki/overview.md
```

Import an external Graphify map as a non-canonical reference layer:

```bash
python3 scripts/ghpf_wiki.py graphify-import --vault ./my-vault --graph ./graphify-output/graph.json
```

Audit and strengthen wikilinks:

```bash
python3 scripts/ghpf_wiki.py link-audit --vault ./my-vault
python3 scripts/ghpf_wiki.py link-strengthen --vault ./my-vault --page wiki/sources/paper-notes.md --max-links 5 --backlink
```

Create a compact context pack for an agent:

```bash
python3 scripts/ghpf_wiki.py context --vault ./my-vault --query "bitcoin regime filter strategy"
```

Turn sources into reusable insight cards, build a local hybrid index, and synthesize insight:

```bash
python3 scripts/ghpf_wiki.py card --vault ./my-vault --type paper --all-sources
python3 scripts/ghpf_wiki.py card --vault ./my-vault --type experiment wiki/sources/paper-notes.md
python3 scripts/ghpf_wiki.py card --vault ./my-vault --type strategy wiki/sources/strategy-note.md
python3 scripts/ghpf_wiki.py index --vault ./my-vault
python3 scripts/ghpf_wiki.py search --vault ./my-vault --query "LLM agent irrigation safety memory"
python3 scripts/ghpf_wiki.py insight --vault ./my-vault --type experiment --query "LLM agent automatic irrigation system"
python3 scripts/ghpf_wiki.py insight --vault ./my-vault --type strategy --query "Bitcoin regime momentum volatility strategy"
python3 scripts/ghpf_wiki.py evaluate --vault ./my-vault --type experiment --target wiki/syntheses/<insight>.md
```

Create figure design cards, propose a manuscript/strategy figure, and export Matplotlib outputs:

```bash
python3 scripts/ghpf_wiki.py figure-card --vault ./my-vault --domain auto --all-sources
python3 scripts/ghpf_wiki.py figure-insight --vault ./my-vault --domain irrigation --query "LLM agent automatic irrigation result figure"
python3 scripts/ghpf_wiki.py figure-insight --vault ./my-vault --domain trading --query "BTC regime momentum strategy diagnostic chart"
python3 scripts/ghpf_wiki.py figure-export --vault ./my-vault --design wiki/figure-designs/<design>.md --domain trading --name Figure_1 --run
```

Prune temporary cache data without touching `raw/` or `wiki/`:

```bash
python3 scripts/ghpf_wiki.py cache-clean --vault ./my-vault --max-age-days 30 --keep-latest 10 --dry-run
python3 scripts/ghpf_wiki.py cache-clean --vault ./my-vault --max-age-days 30 --keep-latest 10
```

Record an agent task:

```bash
python3 scripts/ghpf_wiki.py task start --vault ./my-vault --title "Test BTC strategy candidate"
python3 scripts/ghpf_wiki.py task finish --vault ./my-vault --title "Test BTC strategy candidate" --note "Rejected after walk-forward drawdown."
```

## Design Rule

Keep `wiki/` as the human-readable canonical knowledge base. Use `raw/originals/` for preserved source artifacts, `evidence/index.jsonl` for machine-readable evidence locators, and `graph_imports/` only as an imported Graphify reference layer. Let sidecar tools write only to `raw/originals/`, `evidence/`, `swarmvault/`, `graph_imports/`, `wiki/tasks/`, and explicit exports unless a human asks for canonical wiki edits.

## Quality Loop

The maintenance loop follows Karpathy's LLM Wiki idea while keeping the vault portable:

1. Put immutable source material in `raw/`.
2. Compile durable notes into `wiki/` with source coverage checklists and `[[wikilinks]]`.
3. Run `quality`, `lint`, and `link-audit` before relying on the wiki as context.
4. Use `link-strengthen` and manual review to add missing bidirectional links.
5. File reusable agent answers back into `wiki/syntheses/`.
6. Refresh `graph` and `context` exports for downstream agents.

For bulk material, put source articles in `raw/graphify_articles/`, run Graphify externally, then import the resulting `graph.json` with `graphify-import`. Durable findings should be promoted into `wiki/`; `graph_imports/` can be regenerated or pruned.

For paper, experiment, and trading strategy insight, use cards first. `card` creates compact reusable structure, `index` builds a local hashed-vector/keyword index, `search` runs hybrid retrieval, `insight` writes evidence-backed synthesis, and `evaluate` records lightweight quality checks.

For figure work, use `figure-card` to capture reusable figure patterns, `figure-insight` to design panels from data goals and evidence, and `figure-export` to generate final-size Matplotlib code plus PDF/SVG/PNG outputs.

For video/image visual evidence, `video-frames` stores sampled frames in `raw/figures/video-frames/`, writes a frame-analysis Markdown source, can ingest it into `wiki/sources/`, and can create a figure card for later `figure-insight` work.

Extraction preserves ontology-ready evidence by default:

- Local original files and downloaded web/PDF assets are copied into `raw/originals/` with SHA256 hashes.
- Extracted evidence locations are indexed in `evidence/index.jsonl` with stable `evidence_id` / `chunk_id` values.
- PDF pages/tables, YouTube transcript timestamps, web image candidates, and video/image frames keep machine-readable location metadata for later OpenCrab promotion.
- Source notes in `wiki/sources/` link back to the preserved original and evidence index when `extract --ingest` is used.

Document parsing is tiered and optional-tool aware:

- PDF: `opendataloader-pdf` -> `marker_single` -> `pdfplumber` -> `pypdf`/`PyPDF2`
- HWP/HWPX/HWPML: `kordoc` via `npx` -> `hwpjs`
- DOCX/PPTX/XLSX: `python-docx`, `python-pptx`, `openpyxl` when available
- Web/HTML: standard-library extraction plus image/figure candidate detection; optional Playwright/DeepCloak fallback when installed
- YouTube: `youtube_transcript_api` latest `.fetch()` path -> legacy API -> `yt-dlp`/`uvx yt-dlp`, with timestamps and metadata when available

YouTube/local-video frame extraction requires `ffmpeg`; YouTube frame download also requires `yt-dlp` or `uvx yt-dlp`. Local image analysis uses Pillow when available. OCR, office parsing, and browser automation remain optional capabilities. `capabilities` reports what is available on the current machine so another user can clone the repo and let the workflow adapt to their environment.

## Cache Policy

- Preserve `raw/`, `evidence/`, and `wiki/`.
- Treat `swarmvault/cache/` as disposable.
- Keep Graphify reference imports under `graph_imports/` separate from canonical notes.
- Use `cache-clean` to delete old cache runs; use `--dry-run` before destructive cleanup.
