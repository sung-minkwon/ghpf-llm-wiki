#!/usr/bin/env python3
"""Sidecar utilities for GHFP LLM Wiki vaults."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
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


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path, max_chars: int = 50000) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]


def manifest_path(vault: Path) -> Path:
    return vault / "wiki" / "manifest.json"


def load_manifest(vault: Path) -> dict:
    path = manifest_path(vault)
    if not path.exists():
        return {"sources": [], "generated_pages": [], "operations": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"sources": [], "generated_pages": [], "operations": [{"type": "manifest_recovered", "time": now_iso()}]}


def save_manifest(vault: Path, manifest: dict) -> None:
    path = manifest_path(vault)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def titleize_slug(slug: str) -> str:
    return re.sub(r"[-_]+", " ", slug).strip().title()


def append_log(vault: Path, message: str) -> None:
    log_path = vault / "wiki" / "log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("# GHFP LLM Wiki Log\n\n", encoding="utf-8")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {now_iso()}: {message}\n")


def ensure_index_entry(vault: Path, page_rel: str, title: str) -> None:
    index_path = vault / "wiki" / "index.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if not index_path.exists():
        index_path.write_text("# GHFP LLM Wiki Index\n\n## Pages\n\n", encoding="utf-8")
    text = index_path.read_text(encoding="utf-8")
    entry = f"- [[{title}]] - `{page_rel}`"
    if entry not in text:
        with index_path.open("a", encoding="utf-8") as handle:
            if not text.endswith("\n"):
                handle.write("\n")
            handle.write(entry + "\n")


def source_candidates(vault: Path) -> list[Path]:
    candidates = []
    for root_name in ("raw", "_raw"):
        root = vault / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".txt", ".csv", ".json", ".yaml", ".yml"}:
                candidates.append(path)
    return sorted(set(candidates))


def copy_to_raw(vault: Path, source: Path) -> Path:
    raw_root = vault / "raw" / "sources"
    raw_root.mkdir(parents=True, exist_ok=True)
    if source.resolve().is_relative_to((vault / "raw").resolve()):
        return source
    digest = sha256_file(source)[:12]
    target = raw_root / f"{slugify(source.stem)}-{digest}{source.suffix.lower() or '.txt'}"
    if not target.exists():
        shutil.copy2(source, target)
    return target


def summarize_text(text: str, max_lines: int = 12) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ["No readable text extracted."]
    return lines[:max_lines]


def extract_terms(text: str, limit: int = 12) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}|[가-힣]{2,}", text)
    stop = {"this", "that", "with", "from", "have", "will", "into", "wiki", "source", "paper", "data"}
    counts = {}
    for word in words:
        key = word.lower()
        if key in stop:
            continue
        counts[key] = counts.get(key, 0) + 1
    return [word for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def page_title_from_path(path: Path) -> str:
    return titleize_slug(slugify(path.stem))


def ingest_sources(vault: Path, sources: list[str], move: bool = False) -> dict:
    vault = vault.expanduser()
    selected = [Path(s).expanduser() for s in sources] if sources else source_candidates(vault)
    manifest = load_manifest(vault)
    known_hashes = {item.get("sha256") for item in manifest.get("sources", [])}
    ingested = []
    skipped = []

    for source in selected:
        if not source.exists() or not source.is_file():
            skipped.append({"source": str(source), "reason": "missing_or_not_file"})
            continue
        raw_path = copy_to_raw(vault, source)
        digest = sha256_file(raw_path)
        if digest in known_hashes:
            skipped.append({"source": str(source), "reason": "already_ingested"})
            continue

        text = read_text(raw_path)
        title = page_title_from_path(raw_path)
        source_rel = raw_path.relative_to(vault).as_posix()
        source_note = vault / "wiki" / "sources" / f"{slugify(raw_path.stem)}.md"
        terms = extract_terms(text)
        summary = summarize_text(text)
        term_links = " ".join(f"[[{titleize_slug(term)}]]" for term in terms[:8])

        source_note.parent.mkdir(parents=True, exist_ok=True)
        source_note.write_text(
            "\n".join(
                [
                    f"# {title}",
                    "",
                    f"Source: `{source_rel}`",
                    f"SHA256: `{digest}`",
                    "",
                    "## Summary",
                    "",
                    *[f"- {line}" for line in summary],
                    "",
                    "## Key Links",
                    "",
                    term_links or "No key terms extracted.",
                    "",
                    "## Open Questions",
                    "",
                    "- What should be merged into durable concept or entity pages?",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        concept_pages = []
        for term in terms[:8]:
            concept_title = titleize_slug(term)
            concept_path = vault / "wiki" / "concepts" / f"{slugify(term)}.md"
            if not concept_path.exists():
                concept_path.parent.mkdir(parents=True, exist_ok=True)
                concept_path.write_text(
                    f"# {concept_title}\n\n## Sources\n\n- [[{title}]]\n\n## Notes\n\n- Created from `{source_rel}`.\n",
                    encoding="utf-8",
                )
            else:
                current = concept_path.read_text(encoding="utf-8")
                source_link = f"- [[{title}]]"
                if source_link not in current:
                    with concept_path.open("a", encoding="utf-8") as handle:
                        handle.write(f"\n{source_link}\n")
            concept_pages.append(concept_path.relative_to(vault).as_posix())

        page_rel = source_note.relative_to(vault).as_posix()
        ensure_index_entry(vault, page_rel, title)
        for concept in concept_pages:
            ensure_index_entry(vault, concept, Path(concept).stem)

        manifest.setdefault("sources", []).append(
            {"path": source_rel, "sha256": digest, "ingested_at": now_iso(), "source_note": page_rel}
        )
        manifest.setdefault("generated_pages", []).append(page_rel)
        manifest.setdefault("generated_pages", []).extend(concept_pages)
        manifest.setdefault("operations", []).append({"type": "ingest", "time": now_iso(), "source": source_rel})
        append_log(vault, f"ingested `{source_rel}` into `{page_rel}`.")
        ingested.append({"source": source_rel, "source_note": page_rel, "concept_pages": concept_pages})

        if move and source.exists() and not source.resolve().is_relative_to((vault / "raw").resolve()):
            source.unlink()

    manifest["generated_pages"] = sorted(set(manifest.get("generated_pages", [])))
    save_manifest(vault, manifest)
    return {"ingested": ingested, "skipped": skipped}


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


def file_back(vault: Path, title: str, body: str, folder: str = "wiki/syntheses") -> Path:
    vault = vault.expanduser()
    folder_path = vault / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    page_path = folder_path / f"{slugify(title)}.md"
    if page_path.exists():
        with page_path.open("a", encoding="utf-8") as handle:
            handle.write(f"\n## Update {now_iso()}\n\n{body.strip()}\n")
    else:
        page_path.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")

    rel = page_path.relative_to(vault).as_posix()
    ensure_index_entry(vault, rel, title)
    append_log(vault, f"file-backed synthesis `{rel}`.")
    manifest = load_manifest(vault)
    manifest.setdefault("generated_pages", []).append(rel)
    manifest["generated_pages"] = sorted(set(manifest.get("generated_pages", [])))
    manifest.setdefault("operations", []).append({"type": "file_back", "time": now_iso(), "page": rel})
    save_manifest(vault, manifest)
    return page_path


def lint_wiki(vault: Path) -> dict:
    vault = vault.expanduser()
    pages = markdown_files(vault)
    page_by_title = {}
    for page in pages:
        page_by_title[page.stem.lower()] = page
        page_by_title[titleize_slug(page.stem).lower()] = page
    page_rels = {p.relative_to(vault).as_posix() for p in pages}
    broken_links = []
    orphan_pages = []
    index_missing = []
    manifest_missing = []

    linked_targets = set()
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="ignore")
        for target in WIKILINK_RE.findall(text):
            title = target.strip()
            linked_targets.add(title.lower())
            if title.lower() not in page_by_title:
                broken_links.append({"page": page.relative_to(vault).as_posix(), "target": title})

    for page in pages:
        rel = page.relative_to(vault).as_posix()
        if page.name in {"index.md", "log.md", "overview.md"}:
            continue
        if page.stem.lower() not in linked_targets and rel != "wiki/index.md":
            orphan_pages.append(rel)

    index_path = vault / "wiki" / "index.md"
    index_text = index_path.read_text(encoding="utf-8", errors="ignore") if index_path.exists() else ""
    for rel in sorted(page_rels):
        if rel.startswith("wiki/") and rel not in index_text and Path(rel).name not in {"index.md", "log.md", "overview.md"}:
            index_missing.append(rel)

    manifest = load_manifest(vault)
    for rel in manifest.get("generated_pages", []):
        if rel not in page_rels:
            manifest_missing.append(rel)

    required = ["raw", "wiki", "schema", "schema/AGENTS.md", "wiki/index.md", "wiki/log.md", "wiki/manifest.json"]
    missing_required = [item for item in required if not (vault / item).exists()]
    report = {
        "ok": not (broken_links or manifest_missing or missing_required),
        "pages": len(pages),
        "broken_links": broken_links,
        "orphan_pages": orphan_pages,
        "index_missing": index_missing,
        "manifest_missing": manifest_missing,
        "missing_required": missing_required,
    }
    report_path = vault / "swarmvault" / "exports" / "lint-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def doctor(vault: Path) -> dict:
    return {
        "vault": str(vault),
        "has_raw": (vault / "_raw").exists(),
        "has_karpathy_raw": (vault / "raw").exists(),
        "has_wiki": (vault / "wiki").exists(),
        "has_schema": (vault / "schema" / "AGENTS.md").exists(),
        "has_sidecar": (vault / "swarmvault").exists(),
        "markdown_pages": len(markdown_files(vault)),
        "has_config": (vault / "ghpf.config.json").exists(),
        "has_manifest": manifest_path(vault).exists(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    graph_p = sub.add_parser("graph")
    graph_p.add_argument("--vault", default=".")

    ingest_p = sub.add_parser("ingest")
    ingest_p.add_argument("--vault", default=".")
    ingest_p.add_argument("sources", nargs="*", help="Files to ingest. Defaults to raw/ and _raw/.")
    ingest_p.add_argument("--move", action="store_true", help="Delete original external source after copying to raw/.")

    lint_p = sub.add_parser("lint")
    lint_p.add_argument("--vault", default=".")

    file_back_p = sub.add_parser("file-back")
    file_back_p.add_argument("--vault", default=".")
    file_back_p.add_argument("--title", required=True)
    file_back_p.add_argument("--body", required=True)
    file_back_p.add_argument("--folder", default="wiki/syntheses")

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
    if args.command == "ingest":
        print(json.dumps(ingest_sources(Path(args.vault), args.sources, move=args.move), ensure_ascii=False, indent=2))
    elif args.command == "lint":
        report = lint_wiki(Path(args.vault))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if not report["ok"]:
            return 1
    elif args.command == "file-back":
        print(file_back(Path(args.vault), args.title, args.body, folder=args.folder))
    elif args.command == "graph":
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
