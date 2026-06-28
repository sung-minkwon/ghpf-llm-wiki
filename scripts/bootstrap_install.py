#!/usr/bin/env python3
"""Run the default GHFP LLM Wiki post-clone installation flow."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import vault_layout as layout  # noqa: E402


def run_step(name: str, cmd: list[str]) -> dict:
    completed = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "name": name,
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def print_step(step: dict) -> None:
    status = "OK" if step["returncode"] == 0 else "FAIL"
    print(f"[{status}] {step['name']}")
    if step["stdout"]:
        print(step["stdout"])
    if step["stderr"]:
        print(step["stderr"], file=sys.stderr)


def write_report(vault: Path, report: dict) -> Path:
    report_path = layout.resolve_vault_path(vault, "swarmvault/exports") / "install-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default="./my-vault", help="Vault directory to create or repair.")
    parser.add_argument(
        "--profile",
        default="auto",
        choices=["auto", "general", "research", "trading", "codebase", "mixed"],
    )
    parser.add_argument("--agents", default="codex,claude,antigravity")
    parser.add_argument("--scope", choices=["project", "user"], default="user", help="Install agent skills globally by default; use project for repo-local skill entrypoints.")
    parser.add_argument("--force", action="store_true", help="Pass --force to setup_vault.py.")
    parser.add_argument("--layout", choices=["auto", "decimal", "classic"], default="auto", help="Folder layout passed to setup_vault.py.")
    parser.add_argument("--json", action="store_true", help="Print the final install report as JSON.")
    args = parser.parse_args()

    vault_arg = Path(args.vault).expanduser()
    vault = vault_arg if vault_arg.is_absolute() else REPO_ROOT / vault_arg
    setup_cmd = [
        sys.executable,
        "scripts/setup_vault.py",
        "--vault",
        str(vault),
        "--profile",
        args.profile,
        "--layout",
        args.layout,
    ]
    if args.force:
        setup_cmd.append("--force")

    steps = [
        ("setup_vault", setup_cmd),
        (
            "install_agent_skills",
            [
                sys.executable,
                "scripts/install_agents.py",
                "--scope",
                args.scope,
                "--agents",
                args.agents,
            ],
        ),
        (
            "capabilities",
            [sys.executable, "scripts/ghpf_wiki.py", "capabilities", "--vault", str(vault)],
        ),
        (
            "lint",
            [sys.executable, "scripts/ghpf_wiki.py", "lint", "--vault", str(vault)],
        ),
    ]

    results = []
    for name, cmd in steps:
        step = run_step(name, cmd)
        results.append(step)
        if not args.json:
            print_step(step)
        if step["returncode"] != 0:
            break

    report = {
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
        "vault": str(vault),
        "profile": args.profile,
        "layout": args.layout,
        "agents": [agent.strip() for agent in args.agents.split(",") if agent.strip()],
        "scope": args.scope,
        "ok": all(step["returncode"] == 0 for step in results) and len(results) == len(steps),
        "steps": results,
    }
    report_path = write_report(vault, report)
    report["report_path"] = str(report_path)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"install_report: {report_path}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
