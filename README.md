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

python3 scripts/setup_vault.py --vault ./my-vault --profile auto
python3 scripts/install_agents.py --scope project --agents codex,claude,antigravity
```

Then open `my-vault/` as an Obsidian vault and ask your agent to use the GHFP wiki workflow.

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

Extract PDF, web page, local HTML, or YouTube transcript sources into Markdown, then ingest them:

```bash
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest ./paper.pdf
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest https://example.com/article
python3 scripts/ghpf_wiki.py extract --vault ./my-vault --ingest https://www.youtube.com/watch?v=<id>
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

Keep `wiki/` as the human-readable canonical knowledge base. Use `graph_imports/` only as an imported Graphify reference layer. Let sidecar tools write only to `swarmvault/`, `graph_imports/`, `wiki/tasks/`, and explicit exports unless a human asks for canonical wiki edits.

## Quality Loop

The maintenance loop follows Karpathy's LLM Wiki idea while keeping the vault portable:

1. Put immutable source material in `raw/`.
2. Compile durable notes into `wiki/` with source coverage checklists and `[[wikilinks]]`.
3. Run `quality`, `lint`, and `link-audit` before relying on the wiki as context.
4. Use `link-strengthen` and manual review to add missing bidirectional links.
5. File reusable agent answers back into `wiki/syntheses/`.
6. Refresh `graph` and `context` exports for downstream agents.

For bulk material, put source articles in `raw/graphify_articles/`, run Graphify externally, then import the resulting `graph.json` with `graphify-import`. Durable findings should be promoted into `wiki/`; `graph_imports/` can be regenerated or pruned.

PDF extraction uses `pypdf` or `PyPDF2`. Web extraction uses Python's standard library. YouTube transcript extraction uses `youtube_transcript_api`, `yt-dlp`, or `uvx yt-dlp` when available. OCR, office parsing, and browser automation remain optional capabilities. `capabilities` reports what is available on the current machine so another user can clone the repo and let the workflow adapt to their environment.

## Cache Policy

- Preserve `raw/` and `wiki/`.
- Treat `swarmvault/cache/` as disposable.
- Keep Graphify reference imports under `graph_imports/` separate from canonical notes.
- Use `cache-clean` to delete old cache runs; use `--dry-run` before destructive cleanup.
