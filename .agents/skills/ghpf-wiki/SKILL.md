---
name: ghpf-wiki
description: Set up, maintain, query, and export a GHFP Obsidian-first LLM Wiki for research papers, trading strategy notes, codebase knowledge, graph/context sidecar artifacts, and agent task memory. Use when the task mentions GHFP, LLM Wiki, Obsidian vaults, paper ingestion, Bitcoin/trading strategy synthesis, backtest notes, Codex/Claude/Antigravity wiki setup, context packs, wikilinks, or SwarmVault-style sidecar features.
---

# GHFP Wiki

Use this skill to create and operate a portable LLM Wiki.

## Core Model

- Use `wiki/` as the canonical human-readable Markdown wiki.
- Use `raw/` as the immutable source intake folder.
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

For PDF, web page, local HTML, or YouTube transcript sources, extract and ingest in one step:

```bash
python3 scripts/ghpf_wiki.py extract --vault <path> --ingest <pdf-or-url-or-youtube>
```

For each source in `raw/` or `_raw/`:

1. Create a source note under `wiki/sources/`.
2. Add frontmatter, source provenance, a source coverage checklist, and key `[[wikilinks]]`.
3. Extract durable concepts, entities, claims, methods, strategies, experiments, and open questions.
4. Merge into existing `wiki/concepts/`, `wiki/entities/`, project, paper, trading, or code notes.
5. Add source references and `[[wikilinks]]`.
6. Append the operation to `wiki/log.md`.

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
3. `ingest` to compile raw material into source notes.
4. `card`, `index`, `search`, and `insight` for paper, experiment, or strategy insight.
5. `quality` and `lint` to check metadata, coverage, broken links, and manifest drift.
6. `link-audit` and `link-strengthen` to improve graph connectivity.
7. `evaluate` before relying on generated insight.
8. `graphify-import` when a bulk Graphify map should become searchable reference context.
9. `file-back` to save reusable answers.
10. `graph` and `context` to export sidecar artifacts for agents.
11. `cache-clean --dry-run` before deleting disposable cache.
