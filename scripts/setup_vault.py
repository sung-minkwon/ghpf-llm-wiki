#!/usr/bin/env python3
"""Create a portable GHFP LLM Wiki vault structure."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from detect_profile import detect_profile  # noqa: E402
from vault_layout import (  # noqa: E402
    DEFAULT_LAYOUT_SCHEME,
    actual_rel_for,
    config_for_layout,
    load_vault_config,
    resolve_vault_path,
)


def load_profile(profile: str) -> dict:
    path = REPO_ROOT / "templates" / "profiles" / f"{profile}.json"
    if not path.exists():
        valid = sorted(p.stem for p in (REPO_ROOT / "templates" / "profiles").glob("*.json"))
        raise SystemExit(f"Unknown profile {profile!r}. Valid profiles: {', '.join(valid)}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_if_missing(path: Path, content: str, force: bool = False) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def select_layout(vault: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    existing = load_vault_config(vault)
    if existing.get("layout_scheme"):
        return str(existing["layout_scheme"])
    if existing:
        return "classic"
    return DEFAULT_LAYOUT_SCHEME


def ensure_index_entry(vault: Path, layout_config: dict, title: str, page_rel: str) -> None:
    index_path = resolve_vault_path(vault, "wiki/index.md", config=layout_config)
    if not index_path.exists():
        return
    text = index_path.read_text(encoding="utf-8")
    entry = f"- [[{title}]] - `{page_rel}`"
    if entry not in text:
        with index_path.open("a", encoding="utf-8") as handle:
            if not text.endswith("\n"):
                handle.write("\n")
            handle.write(entry + "\n")


def root_index_bridge_content(
    index_rel: str = "wiki/index.md",
    log_rel: str = "wiki/log.md",
    manifest_rel: str = "wiki/manifest.json",
    profile_rel: str = "wiki/research-profile.md",
) -> str:
    return f"""<!-- GHFP_ROOT_INDEX_BRIDGE -->
# GHFP LLM Wiki Root Index

This root file exists for compatibility with Obsidian helpers that expect `index.md` at the vault root.

Canonical GHFP files:

- [{index_rel}]({index_rel})
- [{log_rel}]({log_rel})
- [{manifest_rel}]({manifest_rel})
- [{profile_rel}]({profile_rel})

Use `{index_rel}` as the canonical generated index. This bridge intentionally uses Markdown links instead of wikilinks so it does not add noisy graph edges.
"""


def root_log_bridge_content(log_rel: str = "wiki/log.md") -> str:
    return f"""# GHFP LLM Wiki Root Log

This root file exists for compatibility with helpers that expect `log.md` at the vault root.

Canonical GHFP log: [{log_rel}]({log_rel})
"""


def ensure_root_compatibility(vault: Path, layout_config: dict) -> dict:
    root_index = vault / "index.md"
    root_log = vault / "log.md"
    index_rel = actual_rel_for(vault, "wiki/index.md", config=layout_config)
    log_rel = actual_rel_for(vault, "wiki/log.md", config=layout_config)
    manifest_rel = actual_rel_for(vault, "wiki/manifest.json", config=layout_config)
    profile_rel = actual_rel_for(vault, "wiki/research-profile.md", config=layout_config)
    created = []
    preserved = []
    if root_index.exists():
        text = root_index.read_text(encoding="utf-8", errors="ignore")
        if "<!-- GHFP_ROOT_INDEX_BRIDGE -->" in text:
            root_index.write_text(root_index_bridge_content(index_rel, log_rel, manifest_rel, profile_rel), encoding="utf-8")
        else:
            preserved.append("index.md")
    else:
        root_index.write_text(root_index_bridge_content(index_rel, log_rel, manifest_rel, profile_rel), encoding="utf-8")
        created.append("index.md")
    if root_log.exists():
        preserved.append("log.md")
    else:
        root_log.write_text(root_log_bridge_content(log_rel), encoding="utf-8")
        created.append("log.md")
    return {"root_index": root_index.exists(), "root_log": root_log.exists(), "created": created, "preserved": sorted(set(preserved))}


def find_obsidian_vaults(root: Path, max_depth: int = 3) -> list[Path]:
    if not root.exists() or not root.is_dir():
        return []
    found = []
    skip_names = {".git", ".obsidian", "__pycache__", "node_modules", ".venv", "venv"}
    stack = [(root, 0)]
    while stack:
        current, depth = stack.pop()
        if (current / ".obsidian").is_dir():
            found.append(current)
        if depth >= max_depth:
            continue
        try:
            children = list(current.iterdir())
        except OSError:
            continue
        for child in children:
            if child.is_dir() and child.name not in skip_names:
                stack.append((child, depth + 1))
    return sorted(set(found))


def validate_vault_target(vault: Path) -> list[str]:
    warnings = []
    nested_vaults = [path for path in find_obsidian_vaults(vault) if path != vault]
    if not (vault / ".obsidian").is_dir() and nested_vaults:
        suggestions = "\n".join(f"  - {path}" for path in nested_vaults[:5])
        raise SystemExit(
            "Refusing to initialize this path because it contains nested Obsidian vaults, "
            "but the selected path is not itself an Obsidian vault.\n"
            "Use the folder that contains `.obsidian` as --vault instead:\n"
            f"{suggestions}"
        )
    if vault.exists() and not (vault / ".obsidian").is_dir():
        warnings.append("selected path has no .obsidian folder; this is fine for a new vault, but existing Obsidian vaults should point at the folder containing .obsidian")
    return warnings


def schema_agents_content(profile: str, layout_config: dict) -> str:
    paths = layout_config.get("layout_paths", {})
    layout_lines = "\n".join(f"- `{logical}` -> `{actual}`" for logical, actual in sorted(paths.items()))
    return f"""# GHFP Wiki Schema

Profile: `{profile}`
Layout: `{layout_config.get("layout_scheme", "classic")}`

## Decimal Folder Layout

GHFP commands use logical paths such as `wiki/sources`; the physical Obsidian vault can use numbered folders for stable sorting.

{layout_lines}

## Canonical Layout

- `raw/`: immutable source copies and intake material.
- `raw/originals/`: preserved original files and downloaded assets with SHA256-backed names.
- `raw/figures/`: copied or extracted figure image assets and chart references.
- `raw/figures/video-frames/`: sampled YouTube/local-video frames for visual evidence.
- `raw/graphify_articles/`: bulk Graphify intake; normal `ingest` skips this folder.
- `_raw/`: compatibility intake folder for Obsidian-style capture tools.
- `evidence/index.jsonl`: machine-readable evidence locations for OpenCrab promotion.
- `wiki/`: compiled Markdown knowledge maintained by agents and humans.
- `wiki/sources/`: one note per source.
- `wiki/concepts/`: durable ideas, methods, claims, and reusable patterns.
- `wiki/entities/`: people, projects, organizations, assets, instruments, and code systems.
- `wiki/cards/`: reusable paper, experiment, and strategy cards for insight workflows.
- `wiki/cards/figures/`: reusable figure design cards.
- `wiki/figure-designs/`: proposed figure layouts and export plans for manuscripts or strategy reports.
- `wiki/syntheses/`: query answers and cross-source summaries filed back into the wiki.
- `schema/`: wiki operating rules and validation expectations.
- `graph_imports/`: imported Graphify reference layers. Treat these as useful maps, not canonical notes.
- `swarmvault/`: graph, hybrid index, context-pack, task-ledger, evaluation, and export sidecar artifacts.
- `swarmvault/exports/video-frames/`: frame-analysis manifests.
- `swarmvault/cache/`: temporary sidecar cache. Safe to prune with `cache-clean`.

## Operating Rules

1. Preserve raw sources. Do not overwrite source files in `raw/`.
2. Preserve original files and downloaded assets under `raw/originals/`; do not use that folder as normal ingest input.
3. Keep `evidence/index.jsonl` as the machine-readable evidence locator index.
4. Compile source material into stable wiki pages instead of answering only from raw chunks.
5. Merge new facts into existing concept/entity/source pages when possible.
6. Use `[[wikilinks]]` for durable relationships.
7. Keep `wiki/index.md`, `wiki/log.md`, and `wiki/manifest.json` current.
8. When a query produces reusable knowledge, file it back under `wiki/syntheses/`.
9. Run lint after ingest or file-back work.
10. Search `graph_imports/` for broad map context, then promote durable findings into `wiki/`.
11. Preserve `raw/`, `evidence/`, and `wiki/`; prune only cache/export artifacts with explicit cache commands.
12. Prefer cards and hybrid search for insight work; avoid rereading full sources unless needed.
13. For figure work, store reusable design evidence in `wiki/cards/figures/` and exported code/output in `swarmvault/exports/figures/`.
14. For video or image frame work, preserve sampled frames under `raw/figures/video-frames/` and analysis manifests under `swarmvault/exports/video-frames/`.
15. Use `maintenance` for cross-machine periodic cleanup and Graphify threshold checks. It stores shared state in `swarmvault/state/maintenance-state.json`.
16. Keep `wiki/research-profile.md` current. When it has focus axes, `ingest` automatically files candidate updates into `wiki/syntheses/auto-*.md`.
"""


def research_profile_content(profile: str) -> str:
    now = datetime.now(timezone.utc).date().isoformat()
    return f"""---
tags: ["ghpf/research-profile"]
source: "setup-vault"
created: "{now}"
aliases: ["Research Profile"]
---

# Research Profile

Profile: `{profile}`

Use this page to teach GHFP what "relevant to my work" means. After this file contains focus axes, `ingest` automatically appends candidate updates to `wiki/syntheses/auto-*.md`. Automatic updates remain candidates unless an explicit promotion policy is used.

## Research Questions

- Main question: replace this with your core research, product, trading, or codebase question.
- Secondary question: replace this with a second durable question if needed.

## Focus Areas

- Evidence quality: source provenance, direct quotes or evidence pointers, limitations, missing data.
- Method and workflow: methods, architecture, tools, experiments, benchmarks, evaluation.
- Reusable insight: claims, design patterns, failure modes, action items, next experiments.

## Auto-Synthesis Rules

- Keep automatic updates as candidates until reviewed.
- Prefer concrete method, metric, limitation, or decision impact over broad summary.
- Mark weak or metadata-only evidence as `needs_review`.
- Treat `ready_for_promotion` as a review queue, not as final truth.
"""


def setup_vault(vault: Path, profile: str, sources: list[str], force: bool = False, layout: str = "auto") -> dict:
    vault = vault.expanduser()
    warnings = validate_vault_target(vault)
    layout = select_layout(vault, layout)
    layout_config = config_for_layout(layout)
    if profile == "auto":
        detected = detect_profile(sources or [str(vault)])
        profile = detected["profile"]
    else:
        detected = {"profile": profile, "scores": {}, "sampled_files": 0}

    spec = load_profile(profile)
    created_dirs = []
    for folder in spec["folders"]:
        path = resolve_vault_path(vault, folder, config=layout_config)
        path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(path.relative_to(vault)))
    for folder in ("raw", "schema"):
        path = resolve_vault_path(vault, folder, config=layout_config)
        path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(path.relative_to(vault)))

    now = datetime.now(timezone.utc).isoformat()
    write_if_missing(
        resolve_vault_path(vault, "wiki/index.md", config=layout_config),
        f"# GHFP LLM Wiki Index\n\nProfile: `{profile}`\n\n## Core Areas\n\n",
        force=force,
    )
    write_if_missing(
        resolve_vault_path(vault, "wiki/log.md", config=layout_config),
        f"# GHFP LLM Wiki Log\n\n- {now}: initialized profile `{profile}`.\n",
        force=False,
    )
    write_if_missing(
        resolve_vault_path(vault, "wiki/overview.md", config=layout_config),
        "# GHFP LLM Wiki Overview\n\nSummarize the living knowledge base here.\n",
        force=False,
    )
    write_if_missing(resolve_vault_path(vault, "wiki/research-profile.md", config=layout_config), research_profile_content(profile), force=False)
    ensure_index_entry(vault, layout_config, "Research Profile", actual_rel_for(vault, "wiki/research-profile.md", config=layout_config))
    write_if_missing(
        resolve_vault_path(vault, "wiki/manifest.json", config=layout_config),
        json.dumps({"sources": [], "generated_pages": [], "operations": []}, ensure_ascii=False, indent=2) + "\n",
        force=False,
    )
    write_if_missing(resolve_vault_path(vault, "schema/AGENTS.md", config=layout_config), schema_agents_content(profile, layout_config), force=force)
    root_compatibility = ensure_root_compatibility(vault, layout_config)
    config_payload = {
        "profile": profile,
        "profile_description": spec["description"],
        "vault_root": str(vault.resolve()),
        **layout_config,
        "cache_policy": {"max_age_days": 30, "keep_latest": 10},
        "created_at": now,
    }
    write_if_missing(
        vault / "ghpf.config.json",
        json.dumps(config_payload, ensure_ascii=False, indent=2)
        + "\n",
        force=force,
    )

    return {
        "vault": str(vault),
        "profile": profile,
        "layout": layout,
        "detected": detected,
        "created_dirs": created_dirs,
        "root_compatibility": root_compatibility,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default=".", help="Vault directory to create or repair.")
    parser.add_argument("--source", action="append", default=[], help="Source path used for auto profile detection.")
    parser.add_argument(
        "--profile",
        default="auto",
        choices=["auto", "general", "research", "trading", "codebase", "mixed"],
    )
    parser.add_argument("--force", action="store_true", help="Overwrite generated index/config files.")
    parser.add_argument("--layout", choices=["auto", "decimal", "classic"], default="auto", help="Folder layout. New vaults default to decimal; existing configured vaults keep their layout.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    result = setup_vault(Path(args.vault).expanduser(), args.profile, args.source, force=args.force, layout=args.layout)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"vault: {result['vault']}")
        print(f"profile: {result['profile']}")
        print(f"layout: {result['layout']}")
        print(f"created_dirs: {len(result['created_dirs'])}")
        for warning in result.get("warnings", []):
            print(f"warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
