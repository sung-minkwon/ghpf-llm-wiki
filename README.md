# ghpf-llm-wiki

Obsidian-first LLM Wiki scaffold for research papers, trading strategy notes, codebase knowledge, and agent task memory.

The default pattern is:

- **Canonical wiki writer:** Obsidian-style Markdown under `wiki/`
- **Raw source intake:** `raw/` with `_raw/` compatibility for Obsidian capture tools
- **Sidecar intelligence:** SwarmVault-inspired graph, context packs, exports, and task ledger under `swarmvault/`
- **Agent compatibility:** Codex via `AGENTS.md`, Claude Code via `CLAUDE.md`, and Antigravity via `.agent/`

## Quick Start

```bash
git clone https://github.com/sung-minkwon/ghpf-llm-wiki.git
cd ghpf-llm-wiki

python3 scripts/setup_vault.py --vault ./my-vault --profile auto
python3 scripts/install_agents.py --scope project --agents codex,claude,antigravity
```

Then open `my-vault/` as an Obsidian vault and ask your agent to use the GHFP wiki workflow.

## Profiles

`setup_vault.py` can create folders from a profile:

- `research`: papers, methods, citations, thesis notes
- `trading`: strategies, backtests, market data, risk rules
- `codebase`: architecture, modules, experiments
- `mixed`: combined research + trading + code workflow
- `auto`: scan source material and choose the profile

Example:

```bash
python3 scripts/setup_vault.py --vault ~/obsidian/ghpf --source ~/papers --source ~/trading-notes --profile auto
```

## Sidecar Commands

Ingest source files into the compiled wiki:

```bash
python3 scripts/ghpf_wiki.py ingest --vault ./my-vault ./paper-notes.md
```

Lint wiki health:

```bash
python3 scripts/ghpf_wiki.py lint --vault ./my-vault
```

File a reusable answer back into the wiki:

```bash
python3 scripts/ghpf_wiki.py file-back --vault ./my-vault --title "BTC regime filter" --body "Reusable synthesis with [[wikilinks]]."
```

Build a wikilink graph:

```bash
python3 scripts/ghpf_wiki.py graph --vault ./my-vault
```

Create a compact context pack for an agent:

```bash
python3 scripts/ghpf_wiki.py context --vault ./my-vault --query "bitcoin regime filter strategy"
```

Record an agent task:

```bash
python3 scripts/ghpf_wiki.py task start --vault ./my-vault --title "Test BTC strategy candidate"
python3 scripts/ghpf_wiki.py task finish --vault ./my-vault --title "Test BTC strategy candidate" --note "Rejected after walk-forward drawdown."
```

## Design Rule

Keep `wiki/` as the human-readable canonical knowledge base. Let sidecar tools write only to `swarmvault/`, `wiki/tasks/`, and explicit exports unless a human asks for wiki edits.
