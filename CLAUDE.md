# GHFP LLM Wiki for Claude Code

This project supports Claude Code as an Obsidian-first LLM Wiki.

Use the same rules as `AGENTS.md`:

- `wiki/` is the canonical Markdown wiki.
- `_raw/` stores unprocessed source material.
- `swarmvault/` stores graph, context pack, export, and task ledger artifacts.
- Add `[[wikilinks]]` when connecting concepts, papers, strategies, entities, and experiments.

Useful commands:

```bash
python3 scripts/setup_vault.py --vault <path> --profile auto
python3 scripts/ghpf_wiki.py graph --vault <path>
python3 scripts/ghpf_wiki.py context --vault <path> --query "<topic>"
python3 scripts/ghpf_wiki.py task start --vault <path> --title "<task>"
python3 scripts/ghpf_wiki.py task finish --vault <path> --title "<task>" --note "<result>"
```

For Claude Code slash-command style use, say:

- `/ghpf-setup` to initialize or repair a vault
- `/ghpf-ingest` to turn sources into wiki notes
- `/ghpf-query` to answer from the wiki
- `/ghpf-context` to create an agent handoff pack

