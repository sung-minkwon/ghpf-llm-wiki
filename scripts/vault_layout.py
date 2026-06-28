"""Vault folder layout helpers for GHFP.

The public command surface keeps logical paths such as ``wiki/sources``.
Physical vaults may use numbered folders such as ``300. wiki/310. sources``.
"""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_LAYOUT_SCHEME = "decimal"

CLASSIC_LAYOUT_PATHS = {
    "_raw": "_raw",
    "evidence": "evidence",
    "graph_imports": "graph_imports",
    "raw": "raw",
    "raw/originals": "raw/originals",
    "raw/figures": "raw/figures",
    "raw/figures/video-frames": "raw/figures/video-frames",
    "raw/graphify_articles": "raw/graphify_articles",
    "raw/sources": "raw/sources",
    "raw/sources/extracted": "raw/sources/extracted",
    "raw/sources/downloads": "raw/sources/downloads",
    "schema": "schema",
    "swarmvault": "swarmvault",
    "swarmvault/state": "swarmvault/state",
    "swarmvault/state/hybrid-index": "swarmvault/state/hybrid-index",
    "swarmvault/cache": "swarmvault/cache",
    "swarmvault/context-packs": "swarmvault/context-packs",
    "swarmvault/task-ledger": "swarmvault/task-ledger",
    "swarmvault/evaluations": "swarmvault/evaluations",
    "swarmvault/exports": "swarmvault/exports",
    "swarmvault/exports/figures": "swarmvault/exports/figures",
    "swarmvault/exports/video-frames": "swarmvault/exports/video-frames",
    "wiki": "wiki",
    "wiki/sources": "wiki/sources",
    "wiki/papers": "wiki/papers",
    "wiki/methods": "wiki/methods",
    "wiki/citations": "wiki/citations",
    "wiki/trading": "wiki/trading",
    "wiki/trading/strategies": "wiki/trading/strategies",
    "wiki/trading/backtests": "wiki/trading/backtests",
    "wiki/trading/market-data": "wiki/trading/market-data",
    "wiki/trading/risk-rules": "wiki/trading/risk-rules",
    "wiki/codebase": "wiki/codebase",
    "wiki/codebase/architecture": "wiki/codebase/architecture",
    "wiki/codebase/modules": "wiki/codebase/modules",
    "wiki/codebase/experiments": "wiki/codebase/experiments",
    "wiki/concepts": "wiki/concepts",
    "wiki/entities": "wiki/entities",
    "wiki/cards": "wiki/cards",
    "wiki/cards/papers": "wiki/cards/papers",
    "wiki/cards/experiments": "wiki/cards/experiments",
    "wiki/cards/strategies": "wiki/cards/strategies",
    "wiki/cards/figures": "wiki/cards/figures",
    "wiki/figure-designs": "wiki/figure-designs",
    "wiki/syntheses": "wiki/syntheses",
    "wiki/domains": "wiki/domains",
    "wiki/projects": "wiki/projects",
    "wiki/open-questions": "wiki/open-questions",
    "wiki/tasks": "wiki/tasks",
}

DECIMAL_LAYOUT_PATHS = {
    "_raw": "000. _raw",
    "evidence": "001. evidence",
    "schema": "002. schema",
    "swarmvault": "003. swarmvault",
    "swarmvault/state": "003. swarmvault/010. state",
    "swarmvault/state/hybrid-index": "003. swarmvault/010. state/011. hybrid-index",
    "swarmvault/cache": "003. swarmvault/020. cache",
    "swarmvault/context-packs": "003. swarmvault/030. context-packs",
    "swarmvault/task-ledger": "003. swarmvault/040. task-ledger",
    "swarmvault/evaluations": "003. swarmvault/050. evaluations",
    "swarmvault/exports": "003. swarmvault/090. exports",
    "swarmvault/exports/figures": "003. swarmvault/090. exports/091. figures",
    "swarmvault/exports/video-frames": "003. swarmvault/090. exports/092. video-frames",
    "graph_imports": "100. graph_imports",
    "raw": "200. raw",
    "raw/originals": "200. raw/210. originals",
    "raw/figures": "200. raw/220. figures",
    "raw/figures/video-frames": "200. raw/220. figures/221. video-frames",
    "raw/graphify_articles": "200. raw/230. graphify_articles",
    "raw/sources": "200. raw/240. sources",
    "raw/sources/extracted": "200. raw/240. sources/241. extracted",
    "raw/sources/downloads": "200. raw/240. sources/242. downloads",
    "wiki": "300. wiki",
    "wiki/sources": "300. wiki/310. sources",
    "wiki/papers": "300. wiki/311. papers",
    "wiki/methods": "300. wiki/312. methods",
    "wiki/citations": "300. wiki/313. citations",
    "wiki/concepts": "300. wiki/320. concepts",
    "wiki/entities": "300. wiki/330. entities",
    "wiki/cards": "300. wiki/340. cards",
    "wiki/cards/papers": "300. wiki/340. cards/341. papers",
    "wiki/cards/experiments": "300. wiki/340. cards/342. experiments",
    "wiki/cards/strategies": "300. wiki/340. cards/343. strategies",
    "wiki/cards/figures": "300. wiki/340. cards/344. figures",
    "wiki/figure-designs": "300. wiki/350. figure-designs",
    "wiki/syntheses": "300. wiki/360. syntheses",
    "wiki/domains": "300. wiki/400. domains",
    "wiki/projects": "300. wiki/370. projects",
    "wiki/open-questions": "300. wiki/380. open-questions",
    "wiki/tasks": "300. wiki/390. tasks",
    "wiki/trading": "300. wiki/410. trading",
    "wiki/trading/strategies": "300. wiki/410. trading/411. strategies",
    "wiki/trading/backtests": "300. wiki/410. trading/412. backtests",
    "wiki/trading/market-data": "300. wiki/410. trading/413. market-data",
    "wiki/trading/risk-rules": "300. wiki/410. trading/414. risk-rules",
    "wiki/codebase": "300. wiki/420. codebase",
    "wiki/codebase/architecture": "300. wiki/420. codebase/421. architecture",
    "wiki/codebase/modules": "300. wiki/420. codebase/422. modules",
    "wiki/codebase/experiments": "300. wiki/420. codebase/423. experiments",
}

CONFIG_DIR_FIELDS = {
    "raw_dir": "raw",
    "originals_dir": "raw/originals",
    "evidence_dir": "evidence",
    "evidence_index": "evidence/index.jsonl",
    "figures_raw_dir": "raw/figures",
    "video_frames_raw_dir": "raw/figures/video-frames",
    "graphify_raw_dir": "raw/graphify_articles",
    "capture_dir": "_raw",
    "wiki_dir": "wiki",
    "sources_dir": "wiki/sources",
    "concepts_dir": "wiki/concepts",
    "entities_dir": "wiki/entities",
    "cards_dir": "wiki/cards",
    "paper_cards_dir": "wiki/cards/papers",
    "experiment_cards_dir": "wiki/cards/experiments",
    "strategy_cards_dir": "wiki/cards/strategies",
    "figure_cards_dir": "wiki/cards/figures",
    "figure_designs_dir": "wiki/figure-designs",
    "syntheses_dir": "wiki/syntheses",
    "domains_dir": "wiki/domains",
    "projects_dir": "wiki/projects",
    "open_questions_dir": "wiki/open-questions",
    "tasks_dir": "wiki/tasks",
    "graph_imports_dir": "graph_imports",
    "schema_dir": "schema",
    "sidecar_dir": "swarmvault",
    "hybrid_index_dir": "swarmvault/state/hybrid-index",
    "evaluations_dir": "swarmvault/evaluations",
    "figure_exports_dir": "swarmvault/exports/figures",
    "video_frame_exports_dir": "swarmvault/exports/video-frames",
    "cache_dir": "swarmvault/cache",
}


def normalize_rel(path: str | Path) -> str:
    return str(path).replace("\\", "/").strip("/")


def layout_paths(scheme: str = DEFAULT_LAYOUT_SCHEME) -> dict[str, str]:
    if scheme == "classic":
        return dict(CLASSIC_LAYOUT_PATHS)
    if scheme == "decimal":
        return dict(DECIMAL_LAYOUT_PATHS)
    raise ValueError(f"Unknown layout scheme: {scheme}")


def config_for_layout(scheme: str = DEFAULT_LAYOUT_SCHEME) -> dict[str, str]:
    paths = layout_paths(scheme)
    config = {"layout_scheme": scheme, "layout_paths": paths}
    for field, logical in CONFIG_DIR_FIELDS.items():
        if logical == "evidence/index.jsonl":
            evidence_dir = paths.get("evidence", "evidence")
            config[field] = f"{evidence_dir}/index.jsonl"
        else:
            config[field] = paths.get(logical, logical)
    return config


def load_vault_config(vault: Path) -> dict:
    config_path = vault / "ghpf.config.json"
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_error": "invalid_json"}


def paths_from_config(config: dict) -> dict[str, str]:
    if isinstance(config.get("layout_paths"), dict):
        return {normalize_rel(k): normalize_rel(v) for k, v in config["layout_paths"].items()}
    paths = dict(CLASSIC_LAYOUT_PATHS)
    for field, logical in CONFIG_DIR_FIELDS.items():
        if field in config and logical != "evidence/index.jsonl":
            paths[logical] = normalize_rel(config[field])
    return paths


def actual_rel_for(vault: Path, logical_rel: str | Path, config: dict | None = None) -> str:
    logical = normalize_rel(logical_rel)
    config = load_vault_config(vault) if config is None else config
    paths = paths_from_config(config)
    for logical_prefix in sorted(paths, key=len, reverse=True):
        actual_prefix = paths[logical_prefix]
        if logical == logical_prefix:
            return actual_prefix
        if logical.startswith(logical_prefix + "/"):
            return actual_prefix + logical[len(logical_prefix) :]
    return logical


def resolve_vault_path(vault: Path, logical_rel: str | Path, config: dict | None = None) -> Path:
    return vault / actual_rel_for(vault, logical_rel, config=config)


def to_logical_rel(vault: Path, path: Path, config: dict | None = None) -> str:
    try:
        actual = normalize_rel(path.relative_to(vault))
    except ValueError:
        actual = normalize_rel(path)
    config = load_vault_config(vault) if config is None else config
    paths = paths_from_config(config)
    for logical_prefix, actual_prefix in sorted(paths.items(), key=lambda item: len(item[1]), reverse=True):
        if actual == actual_prefix:
            return logical_prefix
        if actual.startswith(actual_prefix + "/"):
            return logical_prefix + actual[len(actual_prefix) :]
    return actual


def path_is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False
