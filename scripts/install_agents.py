#!/usr/bin/env python3
"""Install GHFP wiki skill entrypoints for local agents."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_SKILL = REPO_ROOT / ".skills" / "ghpf-wiki"


def copy_skill(target_root: Path) -> Path:
    target = target_root / "ghpf-wiki"
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(CANONICAL_SKILL, target)
    return target


def install(scope: str, agents: list[str]) -> list[str]:
    installed = []
    home = Path.home()
    for agent in agents:
        agent = agent.strip().lower()
        if not agent:
            continue
        if agent == "codex":
            roots = [REPO_ROOT / ".agents" / "skills"] if scope == "project" else [home / ".codex" / "skills"]
        elif agent == "claude":
            roots = [REPO_ROOT / ".claude" / "skills"] if scope == "project" else [home / ".claude" / "skills"]
        elif agent == "antigravity":
            roots = [REPO_ROOT / ".agents" / "skills"] if scope == "project" else [home / ".agents" / "skills"]
        else:
            raise SystemExit(f"Unsupported agent: {agent}")
        for root in roots:
            installed.append(str(copy_skill(root)))
    return installed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=["project", "user"], default="project")
    parser.add_argument("--agents", default="codex,claude,antigravity")
    args = parser.parse_args()
    installed = install(args.scope, args.agents.split(","))
    for path in installed:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

