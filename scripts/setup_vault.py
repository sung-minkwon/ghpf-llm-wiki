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


def schema_agents_content(profile: str) -> str:
    return f"""# GHFP Wiki Schema

Profile: `{profile}`

## Canonical Layout

- `raw/`: immutable source copies and intake material.
- `raw/graphify_articles/`: bulk Graphify intake; normal `ingest` skips this folder.
- `_raw/`: compatibility intake folder for Obsidian-style capture tools.
- `wiki/`: compiled Markdown knowledge maintained by agents and humans.
- `wiki/sources/`: one note per source.
- `wiki/concepts/`: durable ideas, methods, claims, and reusable patterns.
- `wiki/entities/`: people, projects, organizations, assets, instruments, and code systems.
- `wiki/syntheses/`: query answers and cross-source summaries filed back into the wiki.
- `schema/`: wiki operating rules and validation expectations.
- `graph_imports/`: imported Graphify reference layers. Treat these as useful maps, not canonical notes.
- `swarmvault/`: graph, context-pack, task-ledger, and export sidecar artifacts.
- `swarmvault/cache/`: temporary sidecar cache. Safe to prune with `cache-clean`.

## Operating Rules

1. Preserve raw sources. Do not overwrite source files in `raw/`.
2. Compile source material into stable wiki pages instead of answering only from raw chunks.
3. Merge new facts into existing concept/entity/source pages when possible.
4. Use `[[wikilinks]]` for durable relationships.
5. Keep `wiki/index.md`, `wiki/log.md`, and `wiki/manifest.json` current.
6. When a query produces reusable knowledge, file it back under `wiki/syntheses/`.
7. Run lint after ingest or file-back work.
8. Search `graph_imports/` for broad map context, then promote durable findings into `wiki/`.
9. Preserve `raw/` and `wiki/`; prune only cache/export artifacts with explicit cache commands.
"""


def setup_vault(vault: Path, profile: str, sources: list[str], force: bool = False) -> dict:
    if profile == "auto":
        detected = detect_profile(sources or [str(vault)])
        profile = detected["profile"]
    else:
        detected = {"profile": profile, "scores": {}, "sampled_files": 0}

    spec = load_profile(profile)
    created_dirs = []
    for folder in spec["folders"]:
        path = vault / folder
        path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(path.relative_to(vault)))
    for folder in ("raw", "schema"):
        path = vault / folder
        path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(path.relative_to(vault)))

    now = datetime.now(timezone.utc).isoformat()
    write_if_missing(
        vault / "wiki" / "index.md",
        f"# GHFP LLM Wiki Index\n\nProfile: `{profile}`\n\n## Core Areas\n\n",
        force=force,
    )
    write_if_missing(
        vault / "wiki" / "log.md",
        f"# GHFP LLM Wiki Log\n\n- {now}: initialized profile `{profile}`.\n",
        force=False,
    )
    write_if_missing(
        vault / "wiki" / "overview.md",
        "# GHFP LLM Wiki Overview\n\nSummarize the living knowledge base here.\n",
        force=False,
    )
    write_if_missing(
        vault / "wiki" / "manifest.json",
        json.dumps({"sources": [], "generated_pages": [], "operations": []}, ensure_ascii=False, indent=2) + "\n",
        force=False,
    )
    write_if_missing(vault / "schema" / "AGENTS.md", schema_agents_content(profile), force=force)
    write_if_missing(
        vault / "ghpf.config.json",
        json.dumps(
            {
                "profile": profile,
                "profile_description": spec["description"],
                "vault_root": str(vault.resolve()),
                "raw_dir": "raw",
                "graphify_raw_dir": "raw/graphify_articles",
                "capture_dir": "_raw",
                "wiki_dir": "wiki",
                "graph_imports_dir": "graph_imports",
                "schema_dir": "schema",
                "sidecar_dir": "swarmvault",
                "cache_dir": "swarmvault/cache",
                "cache_policy": {"max_age_days": 30, "keep_latest": 10},
                "created_at": now,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        force=force,
    )

    return {
        "vault": str(vault),
        "profile": profile,
        "detected": detected,
        "created_dirs": created_dirs,
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
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    result = setup_vault(Path(args.vault).expanduser(), args.profile, args.source, force=args.force)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"vault: {result['vault']}")
        print(f"profile: {result['profile']}")
        print(f"created_dirs: {len(result['created_dirs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
