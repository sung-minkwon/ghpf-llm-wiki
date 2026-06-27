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
DEPENDENCY_TARGETS = {
    "none": None,
    "core": ".",
    "recommended": ".[recommended]",
    "all": ".[all]",
}


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


def skipped_step(name: str, reason: str) -> dict:
    return {"name": name, "cmd": [], "returncode": 0, "stdout": reason, "stderr": ""}


def venv_python(venv: Path) -> Path:
    if sys.platform.startswith("win"):
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def ensure_venv(venv: Path) -> dict:
    python = venv_python(venv)
    if python.exists():
        return skipped_step("create_venv", f"using existing virtualenv: {venv}")
    return run_step("create_venv", [sys.executable, "-m", "venv", str(venv)])


def install_dependencies(python: Path, dependency_set: str, upgrade_pip: bool = True) -> dict:
    target = DEPENDENCY_TARGETS[dependency_set]
    if target is None:
        return skipped_step("install_dependencies", "skipped dependency installation")

    commands = []
    stdout_parts = []
    stderr_parts = []
    if upgrade_pip:
        commands.append([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    commands.append([str(python), "-m", "pip", "install", "-e", target])

    for cmd in commands:
        completed = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        stdout_parts.append(completed.stdout.strip())
        stderr_parts.append(completed.stderr.strip())
        if completed.returncode != 0:
            return {
                "name": "install_dependencies",
                "cmd": cmd,
                "returncode": completed.returncode,
                "stdout": "\n".join(part for part in stdout_parts if part),
                "stderr": "\n".join(part for part in stderr_parts if part),
            }

    return {
        "name": "install_dependencies",
        "cmd": commands[-1],
        "returncode": 0,
        "stdout": "\n".join(part for part in stdout_parts if part),
        "stderr": "\n".join(part for part in stderr_parts if part),
    }


def print_step(step: dict) -> None:
    status = "OK" if step["returncode"] == 0 else "FAIL"
    print(f"[{status}] {step['name']}")
    if step["stdout"]:
        print(step["stdout"])
    if step["stderr"]:
        print(step["stderr"], file=sys.stderr)


def write_report(vault: Path, report: dict) -> Path:
    report_path = vault / "swarmvault" / "exports" / "install-report.json"
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
    parser.add_argument("--scope", choices=["project", "user"], default="project")
    parser.add_argument("--force", action="store_true", help="Pass --force to setup_vault.py.")
    parser.add_argument("--venv", default=".venv", help="Virtualenv path used for dependency installation.")
    parser.add_argument("--no-venv", action="store_true", help="Install dependencies into the current Python environment.")
    parser.add_argument(
        "--dependency-set",
        choices=sorted(DEPENDENCY_TARGETS),
        default="recommended",
        help="Python dependency set to install before running setup.",
    )
    parser.add_argument("--no-upgrade-pip", action="store_true", help="Do not upgrade pip before installing dependencies.")
    parser.add_argument("--json", action="store_true", help="Print the final install report as JSON.")
    args = parser.parse_args()

    vault_arg = Path(args.vault).expanduser()
    vault = vault_arg if vault_arg.is_absolute() else REPO_ROOT / vault_arg
    venv_arg = Path(args.venv).expanduser()
    venv = venv_arg if venv_arg.is_absolute() else REPO_ROOT / venv_arg
    python_executable = Path(sys.executable) if args.no_venv else venv_python(venv)

    results = []
    if args.no_venv:
        step = skipped_step("create_venv", "using current Python environment")
    else:
        step = ensure_venv(venv)
    results.append(step)
    if not args.json:
        print_step(step)

    if step["returncode"] == 0:
        step = install_dependencies(python_executable, args.dependency_set, upgrade_pip=not args.no_upgrade_pip)
        results.append(step)
        if not args.json:
            print_step(step)

    setup_cmd = [
        str(python_executable),
        "scripts/setup_vault.py",
        "--vault",
        str(vault),
        "--profile",
        args.profile,
    ]
    if args.force:
        setup_cmd.append("--force")

    steps = [
        ("setup_vault", setup_cmd),
        (
            "install_agent_skills",
            [
                str(python_executable),
                "scripts/install_agents.py",
                "--scope",
                args.scope,
                "--agents",
                args.agents,
            ],
        ),
        (
            "capabilities",
            [str(python_executable), "scripts/ghpf_wiki.py", "capabilities", "--vault", str(vault)],
        ),
        (
            "lint",
            [str(python_executable), "scripts/ghpf_wiki.py", "lint", "--vault", str(vault)],
        ),
    ]

    if all(step["returncode"] == 0 for step in results):
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
        "python": str(python_executable),
        "venv": None if args.no_venv else str(venv),
        "dependency_set": args.dependency_set,
        "profile": args.profile,
        "agents": [agent.strip() for agent in args.agents.split(",") if agent.strip()],
        "scope": args.scope,
        "ok": all(step["returncode"] == 0 for step in results) and len(results) == len(steps) + 2,
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
