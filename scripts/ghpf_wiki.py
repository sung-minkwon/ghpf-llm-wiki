#!/usr/bin/env python3
"""Sidecar utilities for GHFP LLM Wiki vaults."""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


def slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9가-힣._-]+", "-", text.strip()).strip("-").lower()
    return slug or "untitled"


def markdown_files(vault: Path):
    wiki = vault / "wiki"
    if not wiki.exists():
        return []
    return sorted(p for p in wiki.rglob("*.md") if p.is_file())


def build_graph(vault: Path) -> dict:
    nodes = {}
    edges = []
    title_to_id = {}
    files = markdown_files(vault)

    for path in files:
        rel = path.relative_to(vault).as_posix()
        title = path.stem
        nodes[rel] = {"id": rel, "title": title, "path": rel, "kind": "page"}
        title_to_id[title.lower()] = rel

    for path in files:
        source = path.relative_to(vault).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in WIKILINK_RE.findall(text):
            target_title = match.strip()
            target = title_to_id.get(target_title.lower(), f"wiki/unresolved/{slugify(target_title)}.md")
            if target not in nodes:
                nodes[target] = {"id": target, "title": target_title, "path": target, "kind": "unresolved"}
            edges.append({"source": source, "target": target, "type": "wikilink"})

    graph = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": list(nodes.values()),
        "edges": edges,
    }

    state = vault / "swarmvault" / "state"
    exports = vault / "swarmvault" / "exports"
    state.mkdir(parents=True, exist_ok=True)
    exports.mkdir(parents=True, exist_ok=True)
    (state / "graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (exports / "graph.html").write_text(render_graph_html(graph), encoding="utf-8")
    return graph


def render_graph_html(graph: dict) -> str:
    data = html.escape(json.dumps(graph, ensure_ascii=False))
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>GHFP Wiki Graph</title>
<style>body{{font-family:system-ui;margin:2rem;line-height:1.5}}pre{{white-space:pre-wrap;background:#f6f8fa;padding:1rem}}</style></head>
<body>
<h1>GHFP Wiki Graph</h1>
<p>Nodes: {graph['node_count']} | Edges: {graph['edge_count']}</p>
<pre id="graph">{data}</pre>
</body></html>
"""


def build_context(vault: Path, query: str, limit: int = 8, max_chars: int = 1200) -> Path:
    terms = [t.lower() for t in re.findall(r"[\w가-힣]+", query) if len(t) > 1]
    scored = []
    for path in markdown_files(vault):
        text = path.read_text(encoding="utf-8", errors="ignore")
        haystack = f"{path.stem} {path.as_posix()} {text}".lower()
        score = sum(haystack.count(term) for term in terms)
        if score:
            scored.append((score, path, text))
    scored.sort(key=lambda item: (-item[0], item[1].as_posix()))

    out_dir = vault / "swarmvault" / "context-packs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{slugify(query)[:80]}.md"

    lines = [
        f"# Context Pack: {query}",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Included Pages",
        "",
    ]
    for score, path, text in scored[:limit]:
        rel = path.relative_to(vault).as_posix()
        excerpt = text.strip().replace("\n\n", "\n")[:max_chars]
        lines.extend([f"### {rel}", "", f"Score: {score}", "", "```md", excerpt, "```", ""])
    if not scored:
        lines.extend(["No matching wiki pages found.", ""])

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def record_task(vault: Path, status: str, title: str, note: str = "", target: str = "") -> Path:
    now = datetime.now(timezone.utc).isoformat()
    record = {"time": now, "status": status, "title": title, "target": target, "note": note}
    ledger = vault / "swarmvault" / "task-ledger"
    ledger.mkdir(parents=True, exist_ok=True)
    with (ledger / "tasks.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    task_dir = vault / "wiki" / "tasks"
    task_dir.mkdir(parents=True, exist_ok=True)
    task_path = task_dir / f"{slugify(title)}.md"
    if not task_path.exists():
        task_path.write_text(f"# {title}\n\n", encoding="utf-8")
    with task_path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {now} `{status}`")
        if target:
            handle.write(f" target={target}")
        if note:
            handle.write(f": {note}")
        handle.write("\n")
    return task_path


def doctor(vault: Path) -> dict:
    return {
        "vault": str(vault),
        "has_raw": (vault / "_raw").exists(),
        "has_wiki": (vault / "wiki").exists(),
        "has_sidecar": (vault / "swarmvault").exists(),
        "markdown_pages": len(markdown_files(vault)),
        "has_config": (vault / "ghpf.config.json").exists(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    graph_p = sub.add_parser("graph")
    graph_p.add_argument("--vault", default=".")

    context_p = sub.add_parser("context")
    context_p.add_argument("--vault", default=".")
    context_p.add_argument("--query", required=True)
    context_p.add_argument("--limit", type=int, default=8)

    task_p = sub.add_parser("task")
    task_sub = task_p.add_subparsers(dest="task_command", required=True)
    for name in ("start", "update", "finish"):
        p = task_sub.add_parser(name)
        p.add_argument("--vault", default=".")
        p.add_argument("--title", required=True)
        p.add_argument("--note", default="")
        p.add_argument("--target", default="")

    doctor_p = sub.add_parser("doctor")
    doctor_p.add_argument("--vault", default=".")

    args = parser.parse_args()
    if args.command == "graph":
        graph = build_graph(Path(args.vault).expanduser())
        print(json.dumps({"node_count": graph["node_count"], "edge_count": graph["edge_count"]}, indent=2))
    elif args.command == "context":
        path = build_context(Path(args.vault).expanduser(), args.query, limit=args.limit)
        print(path)
    elif args.command == "task":
        path = record_task(Path(args.vault).expanduser(), args.task_command, args.title, args.note, args.target)
        print(path)
    elif args.command == "doctor":
        print(json.dumps(doctor(Path(args.vault).expanduser()), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

