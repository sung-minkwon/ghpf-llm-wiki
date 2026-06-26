# GHFP LLM Wiki Rule

When a task mentions GHFP, Obsidian wiki, LLM Wiki, papers, research notes, trading strategies, backtests, context packs, or agent memory:

1. Read `AGENTS.md`.
2. Prefer `wiki/` Markdown as the source of truth.
3. Use `_raw/` for normal intake, `raw/graphify_articles/` for Graphify bulk intake, and `swarmvault/` for sidecar artifacts.
4. Use `graph_imports/` as a non-canonical reference layer; promote durable findings into `wiki/`.
5. Preserve user notes and make focused wiki edits.
6. Refresh graph/context outputs with `scripts/ghpf_wiki.py` when the wiki changes.
7. Prune temporary cache only through `cache-clean`.
