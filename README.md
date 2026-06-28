# ghpf-llm-wiki

Obsidian-first LLM Wiki scaffold for research papers, trading strategy notes, codebase knowledge, and agent task memory.

The default pattern is:

- **Decimal Obsidian layout:** numbered physical folders such as `300. wiki/310. sources`
- **Canonical wiki writer:** logical Obsidian-style Markdown under `wiki/`
- **Raw source intake:** logical `raw/` with `_raw/` compatibility for Obsidian capture tools
- **Bulk graph reference layer:** Graphify intake in logical `raw/graphify_articles/` and imported maps under `graph_imports/`
- **Sidecar intelligence:** SwarmVault-inspired graph, context packs, exports, and task ledger under logical `swarmvault/`
- **Agent compatibility:** Codex via `AGENTS.md`, Claude Code via `CLAUDE.md`, and Antigravity via `.agent/`

## Quick Start

```bash
git clone https://github.com/sung-minkwon/ghpf-llm-wiki.git
cd ghpf-llm-wiki
./install.sh
```

`./install.sh` runs the default post-clone flow: create `./my-vault` with the decimal folder layout, install Codex/Claude Code/Antigravity project skills, print capabilities, run lint, and write the install report under the configured exports folder.

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

### Decimal Folder Layout

New vaults default to a Johnny.Decimal-style physical folder layout while preserving stable logical paths for commands and agents.

Examples:

- `001. evidence/` stores the evidence index.
- `100. graph_imports/` stores imported Graphify reference layers.
- `200. raw/210. originals/` preserves source artifacts.
- `300. wiki/310. sources/` stores source notes.
- `300. wiki/320. concepts/` stores durable concept notes.
- `300. wiki/340. cards/341. papers/` stores reusable paper cards.
- `300. wiki/400. domains/` stores recurring user-specific work areas created by LLM agents from `schema/folder-routing.md`.
- `003. swarmvault/090. exports/` stores sidecar reports and exports.

The CLI still accepts logical paths such as `wiki/sources` and resolves them through `ghpf.config.json`. Existing configured vaults keep their current layout when `--layout auto` is used. To force the old unnumbered layout for a new vault, run:

```bash
python3 scripts/setup_vault.py --vault ./my-vault --profile auto --layout classic
```

### Existing Obsidian Vaults

When connecting GHFP to an existing Obsidian vault, pass the folder that directly contains `.obsidian`:

```bash
python3 scripts/setup_vault.py --vault /path/to/your-vault --profile auto
python3 scripts/ghpf_wiki.py doctor --vault /path/to/your-vault
```

Do not pass a parent folder that merely contains an Obsidian vault as a child. `setup_vault.py` refuses that case and prints the nested vault path to use instead.

GHFP keeps canonical generated files under the configured wiki directory, for example `300. wiki/`. Some Obsidian helpers expect root-level `index.md` and `log.md`; setup and `index` create compatibility bridge files at the vault root without replacing an existing root `log.md`.

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

Each vault also gets `wiki/research-profile.md`. Edit that page once to define durable focus axes such as your main research question, experiment targets, trading strategy themes, or codebase concerns. After that, `ingest` automatically appends candidate updates to `wiki/syntheses/auto-*.md` when a new source matches the profile. Automatic updates stay as candidates by default and include confidence, evidence score, matched terms, evidence snippets, and review status.

## LLM-First Folder Routing

Each vault gets `schema/folder-routing.md`, a human-readable policy for filesystem-capable LLM agents. Agents should read it before creating new topic folders or moving canonical wiki notes.

The default rule is conservative:

- keep first-pass source notes in `wiki/sources/`
- keep cross-source answers in `wiki/syntheses/`
- create `wiki/domains/<domain-slug>/` only for recurring user-specific work areas
- create a domain when the user asks, or when the same subject appears across multiple sources, sessions, or tasks
- add a domain `index.md` and log the reason when a new domain is created

This lets different users grow different vault shapes without changing the distribution code. For example, one user may grow `wiki/domains/greenhouse-irrigation/`, while another grows `wiki/domains/automatic-trading/` or `wiki/domains/client-research/`.

## Sidecar Commands

Check installed optional capabilities:

```bash
python3 scripts/ghpf_wiki.py capabilities --vault ./my-vault
```

Ingest source files into the compiled wiki:

```bash
python3 scripts/ghpf_wiki.py ingest --vault ./my-vault ./paper-notes.md
```

Auto-synthesis is enabled by default but conservative:

```bash
# Default: write candidate updates only.
python3 scripts/ghpf_wiki.py ingest --vault ./my-vault ./paper-notes.md

# Disable all automatic synthesis for a sensitive import.
python3 scripts/ghpf_wiki.py ingest --vault ./my-vault --no-auto-synthesis ./private-notes.md

# Opt in to stable-note promotion only when evidence score passes the threshold.
python3 scripts/ghpf_wiki.py ingest --vault ./my-vault --auto-promote --min-evidence-score 0.8 ./paper-notes.md
```

Promotion creates or appends `wiki/syntheses/stable-*.md`. Use it for reviewed or high-trust pipelines; otherwise keep the default candidate workflow.

Extract PDF, web page, local HTML, Office/HWP documents, or YouTube transcript sources into Markdown, then ingest them:

```bash
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest ./paper.pdf
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest ./report.docx
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest ./korean-document.hwp
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest https://example.com/article
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest https://doi.org/10.xxxx/example
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest https://www.youtube.com/watch?v=<id>
```

For paper landing pages and DOI URLs, `extract` first tries the page itself. If the URL is not already a PDF, it looks for public PDF links in scholarly HTML metadata (`citation_pdf_url`, PDF anchors) and OpenAlex open-access locations. When a public PDF is found, GHFP downloads that PDF into `raw/sources/downloads/`, preserves it under `raw/originals/`, extracts page-level evidence, and ingests it with the source URL as provenance. It deliberately does not bypass paywalls or use piracy mirrors such as Sci-Hub, LibGen, or Z-Library; when no public PDF is available, it falls back to storing the web page content and discovery warnings.

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
python3 scripts/ghpf_wiki.py graph --vault ./my-vault --view semantic --write-obsidian-filter
```

Obsidian Graph View note: `wiki/index.md` is a navigation hub and intentionally links many pages, and auto-created concept notes can make the visual graph noisy. Use `--view semantic` for a source/card/synthesis/profile-centered graph. For a manual Obsidian filter:

```text
-path:wiki/index.md -path:wiki/log.md -path:wiki/overview.md -path:wiki/concepts
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

Refresh the human-readable overview, index, and domain entrypoints after adding or reorganizing knowledge:

```bash
python3 scripts/ghpf_wiki.py curate --vault ./my-vault
```

Regenerate older source notes that still look like extraction logs instead of concise source cards:

```bash
python3 scripts/ghpf_wiki.py source-curate --vault ./my-vault wiki/sources/paper-notes.md
python3 scripts/ghpf_wiki.py source-curate --vault ./my-vault --all-sources
```

Run cross-machine maintenance and Graphify threshold checks:

```bash
python3 scripts/ghpf_wiki.py maintenance --vault ./my-vault
python3 scripts/ghpf_wiki.py maintenance --vault ./my-vault --threshold 20 --auto-graphify --graphify-graph ./graphify-output/graph.json
```

`maintenance` refreshes the local index, link audit, graph export, and lint summary. It stores shared state in `swarmvault/state/maintenance-state.json`, so another computer using the same vault sees the same source count and last Graphify checkpoint. Graphify is recommended after the threshold is reached; when no `graph.json` is available, the command returns `graphify_next_steps` instead of guessing an external Graphify CLI command.

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

Keep the configured wiki directory as the human-readable canonical knowledge base. In the decimal layout this is `300. wiki/`; in the classic layout it is `wiki/`. Use the configured originals directory for preserved source artifacts, the configured evidence index for machine-readable evidence locators, and the configured graph imports directory only as an imported Graphify reference layer. Let sidecar tools write only to configured raw/evidence/sidecar/graph/task/export locations unless a human asks for canonical wiki edits. For recurring user-specific subject areas, follow `schema/folder-routing.md` and grow domain homes under `wiki/domains/`.

## Quality Loop

The maintenance loop follows Karpathy's LLM Wiki idea while keeping the vault portable:

1. Put immutable source material in `raw/`.
2. Compile durable notes into `wiki/` with source coverage checklists and `[[wikilinks]]`.
3. Run `quality`, `lint`, and `link-audit` before relying on the wiki as context.
4. Use `link-strengthen` and manual review to add missing bidirectional links.
5. Run `maintenance` periodically; it records shared Graphify threshold state in the vault, not in the local repo checkout.
6. File reusable agent answers back into `wiki/syntheses/`.
7. Refresh `graph` and `context` exports for downstream agents.

For bulk material, put source articles in `raw/graphify_articles/`, run Graphify externally, then import the resulting `graph.json` with `graphify-import`. Durable findings should be promoted into `wiki/`; `graph_imports/` can be regenerated or pruned.

For paper, experiment, and trading strategy insight, use cards first. `card` creates compact reusable structure, `index` builds a local hashed-vector/keyword index, `search` runs hybrid retrieval, `insight` writes evidence-backed synthesis, and `evaluate` records lightweight quality checks.

For figure work, use `figure-card` to capture reusable figure patterns, `figure-insight` to design panels from data goals and evidence, and `figure-export` to generate final-size Matplotlib code plus PDF/SVG/PNG outputs.

For video/image visual evidence, `video-frames` stores sampled frames in `raw/figures/video-frames/`, writes a frame-analysis Markdown source, can ingest it into `wiki/sources/`, and can create a figure card for later `figure-insight` work.

Extraction preserves ontology-ready evidence by default:

- Local original files and downloaded web/PDF assets are copied into `raw/originals/` with SHA256 hashes.
- Extracted evidence locations are indexed in `evidence/index.jsonl` with stable `evidence_id` / `chunk_id` values.
- PDF pages/tables, YouTube transcript timestamps, web image candidates, and video/image frames keep machine-readable location metadata for later OpenCrab promotion.
- Source notes in `wiki/sources/` link back to the preserved original and evidence index when `extract --ingest` is used.
- Paper landing pages and DOI URLs can promote to a downloaded open-access PDF when scholarly metadata or OpenAlex reports a public PDF URL; blocked or non-public PDFs are not bypassed.

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
