# GHFP LLM Wiki Rule

When a task mentions GHFP, Obsidian wiki, LLM Wiki, papers, research notes, trading strategies, backtests, context packs, or agent memory:

1. Read `AGENTS.md`.
2. Prefer `wiki/` Markdown as the source of truth.
3. Use `_raw/` for normal intake, `raw/graphify_articles/` for Graphify bulk intake, and `swarmvault/` for sidecar artifacts.
4. Use `graph_imports/` as a non-canonical reference layer; promote durable findings into `wiki/`.
5. Preserve user notes and make focused wiki edits.
6. Refresh graph/context outputs with `scripts/ghpf_wiki.py` when the wiki changes.
7. Prune temporary cache only through `cache-clean`.

If the task says "이 문서를 LLM Wiki에 저장", "PDF 위키화", "웹주소를 LLM Wiki에 저장", "유튜브를 위키에 저장", "save this URL to the LLM Wiki", or equivalent, run the automatic source intake workflow: extract with `--ingest`, build `index`, run `lint`, and report source note, preserved original or source URL, evidence index, evidence count, and lint status. For explicit video/frame/image analysis requests, also run `video-frames --ingest --figure-card`.
