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
        vault / "ghpf.config.json",
        json.dumps(
            {
                "profile": profile,
                "profile_description": spec["description"],
                "vault_root": str(vault.resolve()),
                "raw_dir": "_raw",
                "wiki_dir": "wiki",
                "sidecar_dir": "swarmvault",
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

