#!/usr/bin/env python3
"""Sidecar utilities for GHFP LLM Wiki vaults."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
QUALITY_REQUIRED_FIELDS = ["tags", "source", "created", "aliases"]
QUALITY_WEIGHTS = {
    "completeness": 0.20,
    "connections": 0.20,
    "coverage": 0.25,
    "consistency": 0.20,
    "suggestions": 0.15,
}
PIPELINE_STEPS = ["setup", "ingest", "compile", "lint", "strengthen", "file-back", "graph", "context"]


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


def parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---\n"):
        return {}, content
    parts = content.split("\n---\n", 1)
    if len(parts) != 2:
        return {}, content
    frontmatter = {}
    for line in parts[0].splitlines()[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()]
            frontmatter[key] = items
        elif value:
            frontmatter[key] = value.strip("\"'")
    return frontmatter, parts[1]


def frontmatter_block(fields: dict) -> str:
    lines = ["---"]
    for key, value in fields.items():
        if isinstance(value, list):
            rendered = ", ".join(json.dumps(str(item), ensure_ascii=False) for item in value)
            lines.append(f"{key}: [{rendered}]")
        else:
            lines.append(f"{key}: {json.dumps(str(value), ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


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


def source_key_points(text: str, limit: int = 8) -> list[str]:
    lines = summarize_text(text, max_lines=limit)
    points = []
    for line in lines:
        cleaned = re.sub(r"^#+\s*", "", line).strip("-* \t")
        if cleaned:
            points.append(cleaned[:240])
    return points


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
        key_points = source_key_points(text)

        source_note.parent.mkdir(parents=True, exist_ok=True)
        source_note.write_text(
            frontmatter_block(
                {
                    "tags": ["ghpf/source"],
                    "source": source_rel,
                    "created": now_iso(),
                    "aliases": [title],
                    "sha256": digest,
                }
            )
            +
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
                    "## Source Coverage",
                    "",
                    *[f"- [x] {line}" for line in key_points],
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
                    frontmatter_block(
                        {
                            "tags": ["ghpf/concept"],
                            "source": source_rel,
                            "created": now_iso(),
                            "aliases": [concept_title],
                        }
                    )
                    + f"# {concept_title}\n\n## Sources\n\n- [[{title}]]\n\n## Notes\n\n- Created from `{source_rel}`.\n",
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
        title_to_id[titleize_slug(title).lower()] = rel

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
        page_path.write_text(
            frontmatter_block(
                {
                    "tags": ["ghpf/synthesis"],
                    "source": "file-back",
                    "created": now_iso(),
                    "aliases": [title],
                }
            )
            + f"# {title}\n\n{body.strip()}\n",
            encoding="utf-8",
        )

    rel = page_path.relative_to(vault).as_posix()
    ensure_index_entry(vault, rel, title)
    append_log(vault, f"file-backed synthesis `{rel}`.")
    manifest = load_manifest(vault)
    manifest.setdefault("generated_pages", []).append(rel)
    manifest["generated_pages"] = sorted(set(manifest.get("generated_pages", [])))
    manifest.setdefault("operations", []).append({"type": "file_back", "time": now_iso(), "page": rel})
    save_manifest(vault, manifest)
    return page_path


def quality_score(page: Path, source_text: str | None = None, consistency: float | None = None, suggestions: float | None = None, coverage: float | None = None) -> dict:
    content = page.read_text(encoding="utf-8", errors="ignore")
    frontmatter, body = parse_frontmatter(content)
    filled = sum(1 for field in QUALITY_REQUIRED_FIELDS if frontmatter.get(field))
    completeness = filled / len(QUALITY_REQUIRED_FIELDS)
    link_count = len(WIKILINK_RE.findall(body))
    if link_count == 0:
        connections = 0.2
    elif link_count <= 2:
        connections = 0.6
    elif link_count <= 8:
        connections = 1.0
    else:
        connections = 0.8

    coverage_value = coverage
    if coverage_value is None:
        checked = len(re.findall(r"- \[[xX]\]", body))
        unchecked = len(re.findall(r"- \[ \]", body))
        if checked or unchecked:
            coverage_value = checked / max(checked + unchecked, 1)
        elif source_text:
            source_terms = set(extract_terms(source_text, limit=20))
            body_terms = set(extract_terms(body, limit=80))
            coverage_value = len(source_terms & body_terms) / max(len(source_terms), 1)
        else:
            coverage_value = 0.5

    consistency_value = 0.5 if consistency is None else consistency
    suggestions_value = 0.5 if suggestions is None else suggestions
    breakdown = {
        "completeness": {"value": round(completeness, 3), "weight": QUALITY_WEIGHTS["completeness"], "filled": filled, "required": QUALITY_REQUIRED_FIELDS},
        "connections": {"value": round(connections, 3), "weight": QUALITY_WEIGHTS["connections"], "wikilinks": link_count, "target_range": "3-8"},
        "coverage": {"value": round(coverage_value, 3), "weight": QUALITY_WEIGHTS["coverage"]},
        "consistency": {"value": round(consistency_value, 3), "weight": QUALITY_WEIGHTS["consistency"]},
        "suggestions": {"value": round(suggestions_value, 3), "weight": QUALITY_WEIGHTS["suggestions"]},
    }
    score = round(sum(item["value"] * item["weight"] for item in breakdown.values()), 3)
    return {"page": str(page), "lint_score": score, "passed": score >= 0.7, "threshold": 0.7, "breakdown": breakdown}


def run_quality(vault: Path, pages: list[str], strict: bool = False, consistency: float | None = None, suggestions: float | None = None, coverage: float | None = None) -> dict:
    vault = vault.expanduser()
    selected = [vault / page for page in pages] if pages else [p for p in markdown_files(vault) if p.name not in {"index.md", "log.md", "overview.md"}]
    results = []
    for page in selected:
        if page.exists() and page.is_file():
            results.append(quality_score(page, consistency=consistency, suggestions=suggestions, coverage=coverage))
        else:
            results.append({"page": str(page), "error": "FILE_NOT_FOUND", "passed": False})
    report = {
        "ok": all(item.get("passed") for item in results) if strict else True,
        "strict": strict,
        "results": results,
        "average_score": round(sum(item.get("lint_score", 0.0) for item in results) / max(len(results), 1), 3),
    }
    out = vault / "swarmvault" / "exports" / "quality-report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def vault_relative_path(vault: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return vault.expanduser() / path


def extract_sections(content: str) -> dict[str, str]:
    _, body = parse_frontmatter(content)
    sections = {}
    current = "(intro)"
    lines = []
    for line in body.splitlines():
        if re.match(r"^##\s+", line):
            if lines:
                sections[current] = "\n".join(lines).strip()
            current = line.strip()
            lines = []
        else:
            lines.append(line)
    if lines:
        sections[current] = "\n".join(lines).strip()
    return sections


def section_diff(existing: Path, new: Path) -> dict:
    old_sections = extract_sections(existing.read_text(encoding="utf-8", errors="ignore"))
    new_sections = extract_sections(new.read_text(encoding="utf-8", errors="ignore"))
    results = []
    matched_new = set()

    for old_heading, old_body in old_sections.items():
        if old_heading == "(intro)":
            continue
        if old_heading in new_sections:
            matched_new.add(old_heading)
            similarity = SequenceMatcher(None, old_body, new_sections[old_heading]).ratio()
            if similarity < 1.0:
                results.append({"type": "CHANGED", "heading": old_heading, "similarity": round(similarity, 3)})
            continue
        best_heading = None
        best_score = 0.0
        for heading, body in new_sections.items():
            if heading in matched_new or heading == "(intro)":
                continue
            heading_score = SequenceMatcher(None, old_heading, heading).ratio()
            body_score = SequenceMatcher(None, old_body, body).ratio()
            score = max(heading_score, body_score * 0.8)
            if score >= 0.4 and body_score >= 0.5 and score > best_score:
                best_heading = heading
                best_score = score
        if best_heading:
            matched_new.add(best_heading)
            results.append({"type": "RENAMED", "old_heading": old_heading, "heading": best_heading, "similarity": round(best_score, 3)})
        else:
            results.append({"type": "REMOVED", "heading": old_heading})

    for heading, body in new_sections.items():
        if heading not in matched_new and heading != "(intro)":
            results.append({"type": "NEW", "heading": heading, "preview": body[:160].replace("\n", " ")})

    return {
        "summary": {
            "new": sum(1 for item in results if item["type"] == "NEW"),
            "changed": sum(1 for item in results if item["type"] == "CHANGED"),
            "removed": sum(1 for item in results if item["type"] == "REMOVED"),
            "renamed": sum(1 for item in results if item["type"] == "RENAMED"),
        },
        "sections": results,
    }


def state_path(vault: Path) -> Path:
    return vault / "swarmvault" / "state" / "pipeline-state.json"


def load_state(vault: Path) -> dict:
    path = state_path(vault)
    if not path.exists():
        return {"created_at": now_iso(), "completed": {}, "current": PIPELINE_STEPS[0], "errors": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(vault: Path, state: dict) -> None:
    path = state_path(vault)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def state_action(vault: Path, action: str, step: str | None = None) -> dict:
    vault = vault.expanduser()
    if action == "init":
        state = {"created_at": now_iso(), "completed": {}, "current": PIPELINE_STEPS[0], "errors": []}
        save_state(vault, state)
        return state
    state = load_state(vault)
    if action == "show":
        return {**state, "progress": f"{len(state.get('completed', {}))}/{len(PIPELINE_STEPS)}"}
    if step not in PIPELINE_STEPS:
        return {"error": "INVALID_STEP", "valid_steps": PIPELINE_STEPS}
    step_index = PIPELINE_STEPS.index(step)
    missing = [prior for prior in PIPELINE_STEPS[:step_index] if prior not in state.get("completed", {})]
    if action == "check":
        return {"step": step, "ready": not missing, "missing": missing, "completed": list(state.get("completed", {}).keys())}
    if action == "complete":
        if missing:
            error = {"error": "STEP_SKIP_DETECTED", "step": step, "missing": missing}
            state.setdefault("errors", []).append({**error, "time": now_iso()})
            save_state(vault, state)
            return error
        state.setdefault("completed", {})[step] = now_iso()
        state["current"] = PIPELINE_STEPS[step_index + 1] if step_index + 1 < len(PIPELINE_STEPS) else "done"
        save_state(vault, state)
        return state
    return {"error": "INVALID_ACTION"}


def graph_index(vault: Path) -> tuple[dict[str, Path], dict[str, set[str]], dict[str, set[str]]]:
    pages = markdown_files(vault)
    page_by_title = {}
    for page in pages:
        page_by_title[page.stem.lower()] = page
        page_by_title[titleize_slug(page.stem).lower()] = page
    outgoing = {p.relative_to(vault).as_posix(): set() for p in pages}
    incoming = {p.relative_to(vault).as_posix(): set() for p in pages}
    for page in pages:
        source_rel = page.relative_to(vault).as_posix()
        text = page.read_text(encoding="utf-8", errors="ignore")
        for target in WIKILINK_RE.findall(text):
            target_page = page_by_title.get(target.strip().lower())
            if target_page:
                target_rel = target_page.relative_to(vault).as_posix()
                outgoing[source_rel].add(target_rel)
                incoming.setdefault(target_rel, set()).add(source_rel)
    return page_by_title, outgoing, incoming


def link_audit(vault: Path) -> dict:
    lint = lint_wiki(vault)
    _, outgoing, incoming = graph_index(vault.expanduser())
    total_links = sum(len(v) for v in outgoing.values())
    one_way = []
    for source, targets in outgoing.items():
        for target in targets:
            if source not in outgoing.get(target, set()):
                one_way.append({"source": source, "target": target})
    report = {
        "pages": len(outgoing),
        "links": total_links,
        "average_links_per_page": round(total_links / max(len(outgoing), 1), 3),
        "broken_links": lint["broken_links"],
        "orphans": [page for page in outgoing if not outgoing.get(page) and not incoming.get(page)],
        "deadends": [page for page in outgoing if not outgoing.get(page) and incoming.get(page)],
        "hubs": sorted([page for page, links in outgoing.items() if len(links) + len(incoming.get(page, set())) >= 10]),
        "one_way_links": one_way,
    }
    out = vault.expanduser() / "swarmvault" / "exports" / "link-audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def page_terms(page: Path) -> set[str]:
    text = page.read_text(encoding="utf-8", errors="ignore")
    return set(extract_terms(text, limit=60))


def link_strengthen(vault: Path, page_rel: str, max_links: int = 5, backlink: bool = False) -> dict:
    vault = vault.expanduser()
    page = vault / page_rel
    if not page.exists():
        return {"error": "FILE_NOT_FOUND", "page": page_rel}
    target_terms = page_terms(page)
    existing_text = page.read_text(encoding="utf-8", errors="ignore")
    existing_links = {link.lower() for link in WIKILINK_RE.findall(existing_text)}
    candidates = []
    for other in markdown_files(vault):
        if other == page or other.name in {"index.md", "log.md"}:
            continue
        overlap = target_terms & page_terms(other)
        if not overlap or other.stem.lower() in existing_links or titleize_slug(other.stem).lower() in existing_links:
            continue
        candidates.append((len(overlap), other, sorted(overlap)[:8]))
    candidates.sort(key=lambda item: (-item[0], item[1].as_posix()))
    selected = candidates[:max_links]
    if selected:
        with page.open("a", encoding="utf-8") as handle:
            handle.write("\n## Related Notes\n\n")
            for score, other, overlap in selected:
                title = titleize_slug(other.stem)
                handle.write(f"- [[{title}]] - overlap: {', '.join(overlap)}\n")
        if backlink:
            source_title = titleize_slug(page.stem)
            for _, other, _ in selected:
                text = other.read_text(encoding="utf-8", errors="ignore")
                link = f"[[{source_title}]]"
                if link not in text:
                    with other.open("a", encoding="utf-8") as handle:
                        handle.write(f"\n## Backlinks\n\n- {link}\n")
    report = {
        "page": page_rel,
        "links_added": [{"page": other.relative_to(vault).as_posix(), "score": score, "overlap": overlap} for score, other, overlap in selected],
        "backlink": backlink,
    }
    out = vault / "swarmvault" / "exports" / "link-strengthen.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def command_available(command: str) -> bool:
    return shutil.which(command) is not None


def python_module_available(module: str) -> bool:
    result = subprocess.run(
        ["python3", "-c", f"import {module}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def capabilities(vault: Path | None = None) -> dict:
    modules = ["pypdf", "PyPDF2", "docx", "pptx", "openpyxl", "networkx", "youtube_transcript_api", "pytesseract", "playwright"]
    caps = {
        "commands": {name: command_available(name) for name in ["git", "node", "npx", "playwright", "yt-dlp", "tesseract", "obsidian"]},
        "python_modules": {name: python_module_available(name) for name in modules},
        "optional_modes": {
            "basic_wikilink_search": True,
            "graph_sidecar": True,
            "youtube_ingest_ready": command_available("yt-dlp") or python_module_available("youtube_transcript_api"),
            "ocr_ready": command_available("tesseract") or python_module_available("pytesseract"),
            "office_extract_ready": python_module_available("docx") or python_module_available("pptx") or python_module_available("openpyxl"),
            "playwright_ready": command_available("playwright") or python_module_available("playwright") or command_available("npx"),
        },
    }
    if vault is not None:
        caps["vault"] = doctor(vault)
    return caps


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
        "quality": run_quality(vault, [p.relative_to(vault).as_posix() for p in pages if p.name not in {"index.md", "log.md", "overview.md"}], strict=False),
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

    quality_p = sub.add_parser("quality")
    quality_p.add_argument("--vault", default=".")
    quality_p.add_argument("--strict", action="store_true")
    quality_p.add_argument("--coverage", type=float)
    quality_p.add_argument("--consistency", type=float)
    quality_p.add_argument("--suggestions", type=float)
    quality_p.add_argument("pages", nargs="*", help="Wiki page paths relative to the vault. Defaults to all wiki pages.")

    diff_p = sub.add_parser("diff")
    diff_p.add_argument("--vault", default=".")
    diff_p.add_argument("existing", help="Existing Markdown page path, absolute or vault-relative.")
    diff_p.add_argument("new", help="New Markdown page path, absolute or vault-relative.")

    state_p = sub.add_parser("state")
    state_p.add_argument("--vault", default=".")
    state_p.add_argument("action", choices=["init", "show", "check", "complete"])
    state_p.add_argument("step", nargs="?", choices=PIPELINE_STEPS)

    link_audit_p = sub.add_parser("link-audit")
    link_audit_p.add_argument("--vault", default=".")

    link_strengthen_p = sub.add_parser("link-strengthen")
    link_strengthen_p.add_argument("--vault", default=".")
    link_strengthen_p.add_argument("--page", required=True, help="Wiki page path relative to the vault.")
    link_strengthen_p.add_argument("--max-links", type=int, default=5)
    link_strengthen_p.add_argument("--backlink", action="store_true")

    capabilities_p = sub.add_parser("capabilities")
    capabilities_p.add_argument("--vault")

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
    elif args.command == "quality":
        report = run_quality(
            Path(args.vault),
            args.pages,
            strict=args.strict,
            consistency=args.consistency,
            suggestions=args.suggestions,
            coverage=args.coverage,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if not report["ok"]:
            return 1
    elif args.command == "diff":
        vault = Path(args.vault)
        report = section_diff(vault_relative_path(vault, args.existing), vault_relative_path(vault, args.new))
        out = vault.expanduser() / "swarmvault" / "exports" / "section-diff.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.command == "state":
        print(json.dumps(state_action(Path(args.vault), args.action, args.step), ensure_ascii=False, indent=2))
    elif args.command == "link-audit":
        print(json.dumps(link_audit(Path(args.vault)), ensure_ascii=False, indent=2))
    elif args.command == "link-strengthen":
        print(json.dumps(link_strengthen(Path(args.vault), args.page, max_links=args.max_links, backlink=args.backlink), ensure_ascii=False, indent=2))
    elif args.command == "capabilities":
        vault = Path(args.vault).expanduser() if args.vault else None
        print(json.dumps(capabilities(vault), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
