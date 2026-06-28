# GHFP LLM Wiki Agent Guide

Use this repository as an Obsidian-first LLM Wiki with a sidecar graph and task-memory layer.

## Operating Rules

- For a fresh clone, run `./install.sh` first. It creates `./my-vault`, installs user-level skills for Codex/Claude Code/Antigravity so GHFP Wiki can trigger outside this repo, checks capabilities, runs lint, and writes an install report. Use `./install.sh --scope project` only for repo-local skill entrypoints.
- New vaults use a Johnny.Decimal-style physical layout by default, such as `300. wiki/310. sources`. Commands and docs may still refer to logical paths such as `wiki/sources`; resolve them through `ghpf.config.json` or the GHFP CLI.
- Treat logical `wiki/` as the canonical, human-readable Markdown wiki.
- Read logical `schema/folder-routing.md` before creating new topic/domain folders or moving canonical wiki notes.
- Treat logical `graph_imports/` as non-canonical Graphify reference material. Promote durable findings into `wiki/` before relying on them as maintained knowledge.
- Treat logical `wiki/cards/` as the reusable structure for paper, experiment, and strategy insight work.
- Treat logical `wiki/cards/figures/` and `wiki/figure-designs/` as the reusable structure for manuscript, experiment, and trading chart figure design.
- Treat logical `raw/originals/` as preserved original source artifacts and logical `evidence/index.jsonl` as the machine-readable evidence locator index.
- Treat logical `raw/figures/video-frames/` as preserved visual evidence sampled from YouTube, local videos, and image files.
- Use `[[wikilinks]]` for durable cross-references.
- Put immutable source copies in logical `raw/`; `_raw/` is supported for Obsidian capture compatibility.
- Put bulk Graphify intake in logical `raw/graphify_articles/`; normal `ingest` skips that folder.
- Keep wiki operating rules in logical `schema/AGENTS.md`.
- Let recurring user-specific work areas grow under logical `wiki/domains/<domain-slug>/` after checking `schema/folder-routing.md`.
- Put graph, retrieval, context-pack, cache, export, and task-ledger artifacts under logical `swarmvault/`.
- Do not rewrite user notes broadly. Merge focused changes and preserve provenance.
- For setup, run `./install.sh` for the default install or `python3 scripts/setup_vault.py --vault <path> --profile auto` for manual setup.
- For an existing Obsidian vault, use the folder that directly contains `.obsidian` as `<path>`. If a user gives a parent folder, run `python3 scripts/ghpf_wiki.py doctor --vault <path>` and use the reported nested Obsidian vault path instead of writing to the parent.
- For extract/video-frames/ingest/source-curate/card/index/search/insight/evaluate/figure-card/figure-insight/figure-export/lint/quality/diff/state/link-audit/link-strengthen/curate/maintenance/graphify-import/cache-clean/file-back/graph/context/task sidecar work, run `python3 scripts/ghpf_wiki.py --help`.
- Treat advanced PDF parsing, HWP/HWPX conversion, YouTube transcript metadata, OCR, office document parsing, and browser/DeepCloak fallback as optional environment capabilities. Check `python3 scripts/ghpf_wiki.py capabilities --vault <path>` before assuming they are installed.

## Expected Workflow

### Natural Source LLM Wiki Trigger

When the user says a short natural-language request such as "이 문서를 LLM Wiki에 저장해줘", "이 PDF 위키화해줘", "이 웹주소를 LLM Wiki에 저장해줘", "이 유튜브를 위키에 저장해줘", "save this URL to the LLM Wiki", or "ingest this paper/video/page into the wiki":

1. Treat it as the full source intake workflow, not a request for a manual plan.
2. Resolve the source from the provided attachment/path/URL, or from the only plausible PDF/Office/HTML source in the current working directory. If multiple sources are plausible, ask which one.
3. Resolve the vault from the user's explicit path, the current project/vault context, an existing `./my-vault`, or create `./my-vault` via `./install.sh` when needed. For an existing Obsidian vault, verify that the selected path directly contains `.obsidian`; if it only contains a nested Obsidian vault, use the nested folder or ask before writing.
4. Run `python3 scripts/ghpf_wiki.py extract --vault <vault> --ingest <source>` for PDF, web page, local HTML, Office/HWP, or YouTube transcript intake.
5. If `wiki/research-profile.md` exists, `ingest` also files matching candidate updates into `wiki/syntheses/auto-*.md`; report those paths when created and treat them as review candidates, not final conclusions.
6. If the user explicitly asks for YouTube/video/image visual frames, also run `python3 scripts/ghpf_wiki.py video-frames --vault <vault> --source <source> --ingest --figure-card`.
7. Run `python3 scripts/ghpf_wiki.py index --vault <vault>` and `python3 scripts/ghpf_wiki.py lint --vault <vault>`.
8. Report the source note path, preserved original path or source URL, `evidence/index.jsonl`, evidence record count, auto-synthesis paths if any, and lint result.

1. Detect or select a profile: `research`, `trading`, `codebase`, `mixed`, or `general`.
2. Create missing vault folders.
3. Extract PDF, web, local HTML, Office/HWP, YouTube transcript, and video/image frame sources into Markdown when needed.
4. Ingest sources into concise source notes and update logical `wiki/manifest.json`.
5. Track the pipeline with `state` so setup, ingest, compile, lint, strengthen, file-back, graph, and context work are not skipped.
6. Extract durable concepts, entities, methods, strategies, claims, and open questions.
7. Create `paper`, `experiment`, or `strategy` cards before deep insight work.
8. Let `ingest` update logical `wiki/syntheses/auto-*.md` from `wiki/research-profile.md` when focus axes match.
9. Build `index`, run `search`, and use `insight` for evidence-backed synthesis.
10. Use `video-frames` before `figure-card`, `figure-insight`, and `figure-export` when the task depends on chart screenshots, slides, or video frames.
11. Link notes with `[[wikilinks]]`.
12. Run `quality`, `lint`, `link-audit`, and `evaluate`; use `link-strengthen` when a note needs more useful cross-links.
13. Run `source-curate` when older source notes still read like extraction logs instead of concise human source cards.
14. Run `curate` after substantial ingest or reorganization so `overview.md`, `index.md`, and `wiki/domains/index.md` remain useful human entrypoints.
15. Run `maintenance` for periodic cross-machine cleanup and Graphify threshold checks. Its source-count checkpoint lives in `swarmvault/state/maintenance-state.json`.
16. For bulk Graphify maps, import `graph.json` into `graph_imports/` and search it as broad context, not as canonical truth.
17. File reusable query results back into `wiki/syntheses/`, then refresh graph/context packs when the wiki changes.
18. Prune `swarmvault/cache/` with `cache-clean`; never use cache cleanup to remove `raw/` or `wiki/`.

For Codex, use the skill in `.skills/ghpf-wiki/SKILL.md` when the task mentions GHFP, LLM Wiki, Obsidian wiki, research papers, trading strategy notes, context packs, or agent task memory.
