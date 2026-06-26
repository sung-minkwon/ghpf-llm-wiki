# GHFP LLM Wiki for Claude Code

This project supports Claude Code as an Obsidian-first LLM Wiki.

Use the same rules as `AGENTS.md`:

- `wiki/` is the canonical Markdown wiki.
- `_raw/` stores unprocessed source material; `raw/graphify_articles/` stores bulk Graphify intake.
- `graph_imports/` stores non-canonical Graphify reference maps.
- `swarmvault/` stores graph, context pack, cache, export, and task ledger artifacts.
- Add `[[wikilinks]]` when connecting concepts, papers, strategies, entities, and experiments.

Useful commands:

```bash
python3 scripts/setup_vault.py --vault <path> --profile auto
python3 scripts/ghpf_wiki.py extract --vault <path> --ingest <pdf-or-url-or-youtube>
python3 scripts/ghpf_wiki.py video-frames --vault <path> --source <youtube-or-video-or-image> --ingest --figure-card
python3 scripts/ghpf_wiki.py card --vault <path> --type paper --all-sources
python3 scripts/ghpf_wiki.py index --vault <path>
python3 scripts/ghpf_wiki.py insight --vault <path> --type experiment --query "<topic>"
python3 scripts/ghpf_wiki.py figure-insight --vault <path> --domain trading --query "<figure topic>"
python3 scripts/ghpf_wiki.py figure-export --vault <path> --domain trading --name Figure_1 --run
python3 scripts/ghpf_wiki.py graphify-import --vault <path> --graph <graph.json>
python3 scripts/ghpf_wiki.py cache-clean --vault <path> --dry-run
python3 scripts/ghpf_wiki.py graph --vault <path>
python3 scripts/ghpf_wiki.py context --vault <path> --query "<topic>"
python3 scripts/ghpf_wiki.py task start --vault <path> --title "<task>"
python3 scripts/ghpf_wiki.py task finish --vault <path> --title "<task>" --note "<result>"
```

For Claude Code slash-command style use, say:

- `/ghpf-setup` to initialize or repair a vault
- `/ghpf-extract` to extract PDF, web, local HTML, or YouTube transcript sources
- `/ghpf-video-frames` to sample YouTube/local-video/image frames into visual evidence notes
- `/ghpf-ingest` to turn sources into wiki notes
- `/ghpf-query` to answer from the wiki
- `/ghpf-context` to create an agent handoff pack
- `/ghpf-figure` to design and export manuscript or trading diagnostic figures
