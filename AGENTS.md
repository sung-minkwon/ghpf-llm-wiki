# GHFP LLM Wiki Agent Guide

Use this repository as an Obsidian-first LLM Wiki with a sidecar graph and task-memory layer.

## Operating Rules

- For a fresh clone, run `./install.sh` first. It creates `.venv/`, installs the recommended Python dependency set, creates `./my-vault`, installs project skills for Codex/Claude Code/Antigravity, checks capabilities, runs lint, and writes an install report.
- Treat `wiki/` as the canonical, human-readable Markdown wiki.
- Treat `graph_imports/` as non-canonical Graphify reference material. Promote durable findings into `wiki/` before relying on them as maintained knowledge.
- Treat `wiki/cards/` as the reusable structure for paper, experiment, and strategy insight work.
- Treat `wiki/cards/figures/` and `wiki/figure-designs/` as the reusable structure for manuscript, experiment, and trading chart figure design.
- Treat `raw/originals/` as preserved original source artifacts and `evidence/index.jsonl` as the machine-readable evidence locator index.
- Treat `raw/figures/video-frames/` as preserved visual evidence sampled from YouTube, local videos, and image files.
- Use `[[wikilinks]]` for durable cross-references.
- Put immutable source copies in `raw/`; `_raw/` is supported for Obsidian capture compatibility.
- Put bulk Graphify intake in `raw/graphify_articles/`; normal `ingest` skips that folder.
- Keep wiki operating rules in `schema/AGENTS.md`.
- Put graph, retrieval, context-pack, cache, export, and task-ledger artifacts under `swarmvault/`.
- Do not rewrite user notes broadly. Merge focused changes and preserve provenance.
- For setup, run `./install.sh` for the default install or `python3 scripts/setup_vault.py --vault <path> --profile auto` for manual setup.
- For extract/video-frames/ingest/card/index/search/insight/evaluate/figure-card/figure-insight/figure-export/lint/quality/diff/state/link-audit/link-strengthen/graphify-import/cache-clean/file-back/graph/context/task sidecar work, run `python3 scripts/ghpf_wiki.py --help`.
- Treat advanced PDF parsing, HWP/HWPX conversion, YouTube transcript metadata, OCR, office document parsing, and browser/DeepCloak fallback as optional environment capabilities. `./install.sh` installs recommended Python packages, but system tools such as `ffmpeg`, `tesseract`, Graphify, Obsidian, and Playwright browser binaries may still need separate installation. Check `python scripts/ghpf_wiki.py capabilities --vault <path>` from the activated `.venv` before assuming they are installed.

## Expected Workflow

### Natural Source LLM Wiki Trigger

When the user says a short natural-language request such as "이 문서를 LLM Wiki에 저장해줘", "이 PDF 위키화해줘", "이 웹주소를 LLM Wiki에 저장해줘", "이 유튜브를 위키에 저장해줘", "save this URL to the LLM Wiki", or "ingest this paper/video/page into the wiki":

1. Treat it as the full source intake workflow, not a request for a manual plan.
2. Resolve the source from the provided attachment/path/URL, or from the only plausible PDF/Office/HTML source in the current working directory. If multiple sources are plausible, ask which one.
3. Resolve the vault from the user's explicit path, the current project/vault context, an existing `./my-vault`, or create `./my-vault` via `./install.sh` when needed.
4. Run `python3 scripts/ghpf_wiki.py extract --vault <vault> --ingest <source>` for PDF, web page, local HTML, Office/HWP, or YouTube transcript intake.
5. If the user explicitly asks for YouTube/video/image visual frames, also run `python3 scripts/ghpf_wiki.py video-frames --vault <vault> --source <source> --ingest --figure-card`.
6. Run `python3 scripts/ghpf_wiki.py index --vault <vault>` and `python3 scripts/ghpf_wiki.py lint --vault <vault>`.
7. Report the source note path, preserved original path or source URL, `evidence/index.jsonl`, evidence record count, and lint result.

1. Detect or select a profile: `research`, `trading`, `codebase`, `mixed`, or `general`.
2. Create missing vault folders.
3. Extract PDF, web, local HTML, Office/HWP, YouTube transcript, and video/image frame sources into Markdown when needed.
4. Ingest sources into concise source notes and update `wiki/manifest.json`.
5. Track the pipeline with `state` so setup, ingest, compile, lint, strengthen, file-back, graph, and context work are not skipped.
6. Extract durable concepts, entities, methods, strategies, claims, and open questions.
7. Create `paper`, `experiment`, or `strategy` cards before deep insight work.
8. Build `index`, run `search`, and use `insight` for evidence-backed synthesis.
9. Use `video-frames` before `figure-card`, `figure-insight`, and `figure-export` when the task depends on chart screenshots, slides, or video frames.
10. Link notes with `[[wikilinks]]`.
11. Run `quality`, `lint`, `link-audit`, and `evaluate`; use `link-strengthen` when a note needs more useful cross-links.
12. For bulk Graphify maps, import `graph.json` into `graph_imports/` and search it as broad context, not as canonical truth.
13. File reusable query results back into `wiki/syntheses/`, then refresh graph/context packs when the wiki changes.
14. Prune `swarmvault/cache/` with `cache-clean`; never use cache cleanup to remove `raw/` or `wiki/`.

For Codex, use the skill in `.skills/ghpf-wiki/SKILL.md` when the task mentions GHFP, LLM Wiki, Obsidian wiki, research papers, trading strategy notes, context packs, or agent task memory.
