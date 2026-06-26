# GHFP LLM Wiki Agent Guide

Use this repository as an Obsidian-first LLM Wiki with a sidecar graph and task-memory layer.

## Operating Rules

- Treat `wiki/` as the canonical, human-readable Markdown wiki.
- Use `[[wikilinks]]` for durable cross-references.
- Put immutable source copies in `raw/`; `_raw/` is supported for Obsidian capture compatibility.
- Keep wiki operating rules in `schema/AGENTS.md`.
- Put graph, retrieval, context-pack, export, and task-ledger artifacts under `swarmvault/`.
- Do not rewrite user notes broadly. Merge focused changes and preserve provenance.
- For setup, run `python3 scripts/setup_vault.py --vault <path> --profile auto`.
- For ingest/lint/file-back/graph/context/task sidecar work, run `python3 scripts/ghpf_wiki.py --help`.

## Expected Workflow

1. Detect or select a profile: `research`, `trading`, `codebase`, `mixed`, or `general`.
2. Create missing vault folders.
3. Ingest sources into concise source notes and update `wiki/manifest.json`.
4. Extract durable concepts, entities, methods, strategies, claims, and open questions.
5. Link notes with `[[wikilinks]]`.
6. Run lint, file reusable query results back into `wiki/syntheses/`, and refresh graph/context packs when the wiki changes.

For Codex, use the skill in `.skills/ghpf-wiki/SKILL.md` when the task mentions GHFP, LLM Wiki, Obsidian wiki, research papers, trading strategy notes, context packs, or agent task memory.
