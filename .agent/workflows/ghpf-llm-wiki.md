# GHFP LLM Wiki Workflows

## /ghpf-install

Run the default post-clone install:

```bash
./install.sh
```

## /ghpf-setup

Initialize or repair a vault:

```bash
python3 scripts/setup_vault.py --vault <path> --profile auto
```

## /ghpf-ingest

Read files in `_raw/`, create or update source/concept/entity/project notes in `wiki/`, and add `[[wikilinks]]`.

## /ghpf-extract

Extract PDF, web page, local HTML, Office/HWP, or YouTube transcript sources and ingest them:

```bash
python3 scripts/ghpf_wiki.py extract --vault <path> --ingest <pdf-or-url-or-youtube>
python3 scripts/ghpf_wiki.py extract --vault <path> --ingest <docx-or-pptx-or-xlsx-or-hwp>
```

## /ghpf-video-frames

Sample YouTube, local video, or image frames into visual evidence, ingest them, and create a figure card:

```bash
python3 scripts/ghpf_wiki.py video-frames --vault <path> --source <youtube-or-video-or-image> --ingest --figure-card
```

## /ghpf-query

Answer from `wiki/index.md`, page summaries, and relevant linked notes. Cite page paths.

## /ghpf-context

Create a compact agent handoff:

```bash
python3 scripts/ghpf_wiki.py context --vault <path> --query "<task>"
```

## /ghpf-insight

Create reusable cards, build the hybrid index, and synthesize insight:

```bash
python3 scripts/ghpf_wiki.py card --vault <path> --type paper --all-sources
python3 scripts/ghpf_wiki.py index --vault <path>
python3 scripts/ghpf_wiki.py insight --vault <path> --type experiment --query "<task>"
python3 scripts/ghpf_wiki.py evaluate --vault <path> --type experiment --target <insight-page>
```

## /ghpf-figure

Create figure design cards, propose a panel layout, and export Matplotlib outputs:

```bash
python3 scripts/ghpf_wiki.py figure-card --vault <path> --domain auto --all-sources
python3 scripts/ghpf_wiki.py figure-insight --vault <path> --domain trading --query "<figure task>"
python3 scripts/ghpf_wiki.py figure-export --vault <path> --domain trading --name Figure_1 --run
```

## /ghpf-graph

Refresh graph artifacts:

```bash
python3 scripts/ghpf_wiki.py graph --vault <path>
```

## /ghpf-graphify-import

Import a Graphify `graph.json` as non-canonical reference notes:

```bash
python3 scripts/ghpf_wiki.py graphify-import --vault <path> --graph <graph.json>
```

## /ghpf-cache-clean

Preview and prune temporary sidecar cache:

```bash
python3 scripts/ghpf_wiki.py cache-clean --vault <path> --dry-run
python3 scripts/ghpf_wiki.py cache-clean --vault <path>
```
