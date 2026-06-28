"""Human-readable entrypoint curation for GHFP LLM Wiki vaults."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

try:
    import vault_layout as layout
except ModuleNotFoundError:  # pragma: no cover - used when installed as a package entry point.
    from . import vault_layout as layout


INDEX_MARKER_BEGIN = "<!-- GHFP_HUMAN_ENTRYPOINTS_BEGIN -->"
INDEX_MARKER_END = "<!-- GHFP_HUMAN_ENTRYPOINTS_END -->"
OVERVIEW_PLACEHOLDER = "Summarize the living knowledge base here."


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _actual(vault: Path, logical_rel: str, config: dict | None = None) -> str:
    return layout.actual_rel_for(vault, logical_rel, config=config)


def _frontmatter(tags: list[str], source: str, aliases: list[str]) -> str:
    aliases_rendered = ", ".join(f'"{alias}"' for alias in aliases)
    tags_rendered = ", ".join(f'"{tag}"' for tag in tags)
    return "\n".join(
        [
            "---",
            f"tags: [{tags_rendered}]",
            f'source: "{source}"',
            f'created: "{_today()}"',
            f"aliases: [{aliases_rendered}]",
            "---",
            "",
        ]
    )


def index_start_here_block(vault: Path, profile: str, config: dict | None = None) -> str:
    overview_rel = _actual(vault, "wiki/overview.md", config=config)
    domains_rel = _actual(vault, "wiki/domains/index.md", config=config)
    profile_rel = _actual(vault, "wiki/research-profile.md", config=config)
    syntheses_rel = _actual(vault, "wiki/syntheses", config=config)
    sources_rel = _actual(vault, "wiki/sources", config=config)
    concepts_rel = _actual(vault, "wiki/concepts", config=config)
    entities_rel = _actual(vault, "wiki/entities", config=config)
    return f"""{INDEX_MARKER_BEGIN}
## Start Here

This index is the navigation hub for the compiled, human-readable wiki. Start with these pages before opening raw source notes or auto-created concept stubs.

1. [[GHFP LLM Wiki Overview]] - current scope, reading order, and maintenance rules.
2. [[Domain Index]] - recurring subject areas such as research projects, trading systems, manuscripts, or codebases.
3. [[Research Profile]] - what this vault should treat as relevant and worth synthesizing.

## Human-Readable Layers

- `{syntheses_rel}/`: cross-source summaries and reusable conclusions.
- `{_actual(vault, "wiki/domains", config=config)}/`: domain homes for recurring user-specific work streams.
- `{entities_rel}/`: people, organizations, assets, projects, instruments, and other durable entities.
- `{sources_rel}/`: source-level notes with provenance and evidence pointers.
- `{concepts_rel}/`: concept pages; review before treating short auto-created stubs as final summaries.

## Current Entry Files

- [{overview_rel}]({overview_rel})
- [{domains_rel}]({domains_rel})
- [{profile_rel}]({profile_rel})

{INDEX_MARKER_END}
"""


def index_content(vault: Path, profile: str, config: dict | None = None) -> str:
    return (
        _frontmatter(["ghpf/index"], "setup-vault", ["GHFP LLM Wiki Index"])
        + f"# GHFP LLM Wiki Index\n\nProfile: `{profile}`\n\n"
        + index_start_here_block(vault, profile, config=config)
        + "\n## Auto-Generated Page Catalog\n\n"
    )


def overview_content(vault: Path, profile: str, config: dict | None = None) -> str:
    sources_rel = _actual(vault, "wiki/sources", config=config)
    concepts_rel = _actual(vault, "wiki/concepts", config=config)
    entities_rel = _actual(vault, "wiki/entities", config=config)
    syntheses_rel = _actual(vault, "wiki/syntheses", config=config)
    domains_rel = _actual(vault, "wiki/domains", config=config)
    raw_rel = _actual(vault, "raw", config=config)
    evidence_rel = _actual(vault, "evidence/index.jsonl", config=config)
    return (
        _frontmatter(["ghpf/overview"], "setup-vault", ["GHFP LLM Wiki Overview", "Vault Overview"])
        + f"""# GHFP LLM Wiki Overview

Profile: `{profile}`

This vault is meant to be a compiled LLM wiki: raw material is preserved separately, while `wiki/` contains Markdown that a human and an LLM can read as maintained knowledge.

## Start Here

- [[GHFP LLM Wiki Index]]: navigation hub and page catalog.
- [[Domain Index]]: recurring subject areas and where new domain homes should grow.
- [[Research Profile]]: the user's current questions, focus areas, and auto-synthesis rules.

## What Belongs Where

- `{raw_rel}/`: preserved intake material and immutable source copies.
- `{evidence_rel}`: machine-readable evidence locator index.
- `{sources_rel}/`: one note per source, with provenance and evidence pointers.
- `{concepts_rel}/`: durable concepts, methods, claims, and patterns.
- `{entities_rel}/`: entities such as people, projects, organizations, assets, instruments, and code systems.
- `{syntheses_rel}/`: human-readable cross-source summaries and reusable conclusions.
- `{domains_rel}/`: topic homes for recurring user-specific work streams.

## Maintenance Rule

After ingesting or extracting sources, update this overview, the index, and any relevant domain home when the new material changes what a reader should look at first. Source notes and concept stubs are not enough by themselves; durable knowledge should be promoted into syntheses, entity pages, or domain homes.
"""
    )


def domain_index_content(vault: Path, profile: str, config: dict | None = None) -> str:
    sources_rel = _actual(vault, "wiki/sources", config=config)
    syntheses_rel = _actual(vault, "wiki/syntheses", config=config)
    domains_rel = _actual(vault, "wiki/domains", config=config)
    return (
        _frontmatter(["ghpf/domain-index"], "setup-vault", ["Domain Index", "Wiki Domains"])
        + f"""# Domain Index

Profile: `{profile}`

This page lists recurring subject areas that deserve their own readable home. Use domain homes for user-specific work streams such as research projects, trading systems, manuscripts, datasets, clients, or codebases.

## Domains

- Add domain homes under `{domains_rel}/<domain-slug>/index.md` as recurring areas emerge.

## When To Create A Domain

Create a domain when the same subject appears across several sources or sessions, has its own workflow, or needs a stable place for decisions, syntheses, experiments, or strategy notes.

## Default Flow

1. Preserve source-level material in `{sources_rel}/`.
2. Promote reusable conclusions into `{syntheses_rel}/`.
3. Link the relevant synthesis, source notes, cards, and entities from the matching domain home.
4. Keep the domain home short enough to act as a reading map.
"""
    )


def _is_default_index(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("# GHFP LLM Wiki Index") and "## Start Here" not in stripped and "## Auto-Generated Page Catalog" not in stripped


def _insert_index_block(text: str, block: str) -> str:
    if INDEX_MARKER_BEGIN in text:
        before, rest = text.split(INDEX_MARKER_BEGIN, 1)
        current_body, after = rest.split(INDEX_MARKER_END, 1)
        current_block = f"{INDEX_MARKER_BEGIN}{current_body}{INDEX_MARKER_END}"
        if current_block.strip() == block.strip():
            return text
        separator = "" if after.startswith("\n") else "\n"
        return before.rstrip() + "\n\n" + block.rstrip() + separator + after
    if "## Start Here" in text:
        return text
    lines = text.splitlines()
    insert_at = 0
    for idx, line in enumerate(lines[:12]):
        if line.startswith("## "):
            insert_at = idx
            break
    else:
        insert_at = min(len(lines), 3)
    merged = lines[:insert_at] + ["", block.rstrip(), ""] + lines[insert_at:]
    return "\n".join(merged).rstrip() + "\n"


def _write_or_preserve(path: Path, content: str, force: bool, placeholder: str | None = None) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    if force or not existed:
        path.write_text(content, encoding="utf-8")
        return "updated" if existed else "created"
    text = path.read_text(encoding="utf-8", errors="ignore")
    if placeholder and placeholder in text:
        path.write_text(content, encoding="utf-8")
        return "updated"
    return "preserved"


def curate_entrypoints(vault: Path, profile: str = "general", force: bool = False, config: dict | None = None) -> dict:
    vault = vault.expanduser()
    config = layout.load_vault_config(vault) if config is None else config
    if not config:
        config = layout.config_for_layout()
    result = {"created": [], "updated": [], "preserved": []}

    overview_path = layout.resolve_vault_path(vault, "wiki/overview.md", config=config)
    index_path = layout.resolve_vault_path(vault, "wiki/index.md", config=config)
    domain_index_path = layout.resolve_vault_path(vault, "wiki/domains/index.md", config=config)

    overview_status = _write_or_preserve(overview_path, overview_content(vault, profile, config=config), force, OVERVIEW_PLACEHOLDER)
    result[overview_status].append(overview_path.relative_to(vault).as_posix())

    domain_status = _write_or_preserve(domain_index_path, domain_index_content(vault, profile, config=config), force)
    result[domain_status].append(domain_index_path.relative_to(vault).as_posix())

    index_path.parent.mkdir(parents=True, exist_ok=True)
    if force or not index_path.exists() or _is_default_index(index_path.read_text(encoding="utf-8", errors="ignore")):
        existed = index_path.exists()
        index_path.write_text(index_content(vault, profile, config=config), encoding="utf-8")
        result["updated" if existed else "created"].append(index_path.relative_to(vault).as_posix())
    else:
        original = index_path.read_text(encoding="utf-8", errors="ignore")
        merged = _insert_index_block(original, index_start_here_block(vault, profile, config=config))
        if merged != original:
            index_path.write_text(merged, encoding="utf-8")
            result["updated"].append(index_path.relative_to(vault).as_posix())
        else:
            result["preserved"].append(index_path.relative_to(vault).as_posix())

    return result
