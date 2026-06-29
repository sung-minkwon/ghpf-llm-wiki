# GHFP LLM Wiki for Claude Code

This project supports Claude Code as an Obsidian-first LLM Wiki.

Use the same rules as `AGENTS.md`:

- New vaults use numbered physical folders by default, for example `300. wiki/310. sources`; use GHFP commands and `ghpf.config.json` to resolve logical paths.
- Logical `wiki/` is the canonical Markdown wiki.
- For an existing Obsidian vault, use the folder that directly contains `.obsidian`; run `python3 scripts/ghpf_wiki.py doctor --vault <path>` when the path is uncertain.
- Logical `_raw/` stores unprocessed source material; logical `raw/graphify_articles/` stores bulk Graphify intake.
- Logical `graph_imports/` stores non-canonical Graphify reference maps.
- Logical `swarmvault/` stores graph, context pack, cache, export, and task ledger artifacts.
- Add `[[wikilinks]]` when connecting concepts, papers, strategies, entities, and experiments.

Useful commands:

```bash
./install.sh
python3 scripts/setup_vault.py --vault <path> --profile auto
python3 scripts/ghpf_wiki.py extract --vault <path> --ingest --ocr-provider auto <pdf-or-url-or-youtube-or-image>
python3 scripts/ghpf_wiki.py extract --vault <path> --ingest --ocr-provider auto <docx-or-pptx-or-xlsx-or-hwp>
python3 scripts/ghpf_wiki.py video-frames --vault <path> --source <youtube-or-video-or-image> --ingest --figure-card
python3 scripts/ghpf_wiki.py card --vault <path> --type paper --all-sources
python3 scripts/ghpf_wiki.py index --vault <path>
python3 scripts/ghpf_wiki.py insight --vault <path> --type experiment --query "<topic>"
python3 scripts/ghpf_wiki.py figure-insight --vault <path> --domain trading --query "<figure topic>"
python3 scripts/ghpf_wiki.py figure-export --vault <path> --domain trading --name Figure_1 --run
python3 scripts/ghpf_wiki.py graphify-import --vault <path> --graph <graph.json>
python3 scripts/ghpf_wiki.py maintenance --vault <path>
python3 scripts/ghpf_wiki.py maintenance --vault <path> --threshold 20 --auto-graphify --graphify-graph <graph.json>
python3 scripts/ghpf_wiki.py cache-clean --vault <path> --dry-run
python3 scripts/ghpf_wiki.py graph --vault <path>
python3 scripts/ghpf_wiki.py context --vault <path> --query "<topic>"
python3 scripts/ghpf_wiki.py task start --vault <path> --title "<task>"
python3 scripts/ghpf_wiki.py task finish --vault <path> --title "<task>" --note "<result>"
```

Natural source trigger:

When the user says "이 문서를 LLM Wiki에 저장해줘", "이 PDF 위키화해줘", "이 웹주소를 LLM Wiki에 저장해줘", "이 유튜브를 위키에 저장해줘", "save this URL to the LLM Wiki", or similar, run the full intake automatically:

```bash
python3 scripts/ghpf_wiki.py extract --vault <path> --ingest --ocr-provider auto <pdf-or-url-or-youtube-or-office-doc-or-image>
python3 scripts/ghpf_wiki.py index --vault <path>
python3 scripts/ghpf_wiki.py lint --vault <path>
```

Use the explicit vault if provided; otherwise use the current known vault or `./my-vault` after setup. For existing Obsidian vaults, verify that the path contains `.obsidian`; if `doctor` reports nested Obsidian vaults, use the nested vault folder rather than the parent. If `wiki/research-profile.md` has focus axes, `ingest` automatically files matching candidate updates into `wiki/syntheses/auto-*.md`; report those paths as review candidates. For image sources, content-bearing web images, and scanned/text-poor PDFs, keep `--ocr-provider auto` so the active agent can use native vision OCR when available and record provider/status in the note and evidence index. For YouTube/video/image visual frames, also use `video-frames --ingest --figure-card` when the user asks for frame/image analysis. Report the created source note, preserved original or source URL, `evidence/index.jsonl`, evidence count, OCR status when attempted, auto-synthesis paths if any, and lint result.

For Claude Code slash-command style use, say:

- `/ghpf-setup` to initialize or repair a vault
- `/ghpf-extract` to extract PDF, web, local HTML, or YouTube transcript sources
- `/ghpf-video-frames` to sample YouTube/local-video/image frames into visual evidence notes
- `/ghpf-ingest` to turn sources into wiki notes
- `/ghpf-query` to answer from the wiki
- `/ghpf-context` to create an agent handoff pack
- `/ghpf-figure` to design and export manuscript or trading diagnostic figures
