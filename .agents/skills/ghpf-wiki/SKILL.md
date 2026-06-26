---
name: ghpf-wiki
description: Set up, maintain, query, and export a GHFP Obsidian-first LLM Wiki for research papers, trading strategy notes, codebase knowledge, graph/context sidecar artifacts, and agent task memory. Use when the task mentions GHFP, LLM Wiki, Obsidian vaults, paper ingestion, Bitcoin/trading strategy synthesis, backtest notes, Codex/Claude/Antigravity wiki setup, context packs, wikilinks, or SwarmVault-style sidecar features.
---

# GHFP Wiki

Use this skill to create and operate a portable LLM Wiki.

## Core Model

- Use `wiki/` as the canonical human-readable Markdown wiki.
- Use `_raw/` as the source intake folder.
- Use `swarmvault/` for sidecar graph, context-pack, export, and task-ledger artifacts.
- Preserve existing notes. Merge targeted updates instead of rewriting broad folders.
- Add `[[wikilinks]]` between papers, methods, claims, entities, strategies, experiments, and code modules.

## Setup

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

For each source in `_raw/`:

1. Create a source note under `wiki/sources/`.
2. Extract durable concepts, entities, claims, methods, strategies, experiments, and open questions.
3. Merge into existing `wiki/concepts/`, `wiki/entities/`, project, paper, trading, or code notes.
4. Add source references and `[[wikilinks]]`.
5. Append the operation to `wiki/log.md`.

## Sidecar Features

Refresh graph artifacts:

```bash
python3 scripts/ghpf_wiki.py graph --vault <path>
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

## Query

Answer from the wiki first:

1. Read `wiki/index.md`.
2. Search titles, headings, tags, and summaries.
3. Open the smallest set of relevant pages.
4. Cite page paths.
5. If the answer should compound, save it under `wiki/syntheses/` or an appropriate domain folder.

