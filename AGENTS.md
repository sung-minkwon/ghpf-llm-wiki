# GHFP LLM Wiki Agent Guide

Use this repository as an Obsidian-first LLM Wiki with a sidecar graph and task-memory layer.

## Operating Rules

- Treat `wiki/` as the canonical, human-readable Markdown wiki.
- Treat `graph_imports/` as non-canonical Graphify reference material. Promote durable findings into `wiki/` before relying on them as maintained knowledge.
- Use `[[wikilinks]]` for durable cross-references.
- Put immutable source copies in `raw/`; `_raw/` is supported for Obsidian capture compatibility.
- Put bulk Graphify intake in `raw/graphify_articles/`; normal `ingest` skips that folder.
- Keep wiki operating rules in `schema/AGENTS.md`.
- Put graph, retrieval, context-pack, cache, export, and task-ledger artifacts under `swarmvault/`.
- Do not rewrite user notes broadly. Merge focused changes and preserve provenance.
- For setup, run `python3 scripts/setup_vault.py --vault <path> --profile auto`.
- For extract/ingest/lint/quality/diff/state/link-audit/link-strengthen/graphify-import/cache-clean/file-back/graph/context/task sidecar work, run `python3 scripts/ghpf_wiki.py --help`.
- Treat YouTube transcript, OCR, office document, and browser automation support as optional environment capabilities. Check `python3 scripts/ghpf_wiki.py capabilities --vault <path>` before assuming they are installed.

## Expected Workflow

1. Detect or select a profile: `research`, `trading`, `codebase`, `mixed`, or `general`.
2. Create missing vault folders.
3. Extract PDF, web, local HTML, and YouTube transcript sources into Markdown when needed.
4. Ingest sources into concise source notes and update `wiki/manifest.json`.
5. Track the pipeline with `state` so setup, ingest, compile, lint, strengthen, file-back, graph, and context work are not skipped.
6. Extract durable concepts, entities, methods, strategies, claims, and open questions.
7. Link notes with `[[wikilinks]]`.
8. Run `quality`, `lint`, and `link-audit`; use `link-strengthen` when a note needs more useful cross-links.
9. For bulk Graphify maps, import `graph.json` into `graph_imports/` and search it as broad context, not as canonical truth.
10. File reusable query results back into `wiki/syntheses/`, then refresh graph/context packs when the wiki changes.
11. Prune `swarmvault/cache/` with `cache-clean`; never use cache cleanup to remove `raw/` or `wiki/`.

For Codex, use the skill in `.skills/ghpf-wiki/SKILL.md` when the task mentions GHFP, LLM Wiki, Obsidian wiki, research papers, trading strategy notes, context packs, or agent task memory.
