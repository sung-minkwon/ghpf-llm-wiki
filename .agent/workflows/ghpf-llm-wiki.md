# GHFP LLM Wiki Workflows

## /ghpf-setup

Initialize or repair a vault:

```bash
python3 scripts/setup_vault.py --vault <path> --profile auto
```

## /ghpf-ingest

Read files in `_raw/`, create or update source/concept/entity/project notes in `wiki/`, and add `[[wikilinks]]`.

## /ghpf-query

Answer from `wiki/index.md`, page summaries, and relevant linked notes. Cite page paths.

## /ghpf-context

Create a compact agent handoff:

```bash
python3 scripts/ghpf_wiki.py context --vault <path> --query "<task>"
```

## /ghpf-graph

Refresh graph artifacts:

```bash
python3 scripts/ghpf_wiki.py graph --vault <path>
```

