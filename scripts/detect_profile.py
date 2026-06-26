#!/usr/bin/env python3
"""Detect a GHFP LLM Wiki profile from source paths."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


KEYWORDS = {
    "research": {
        "paper", "papers", "doi", "abstract", "method", "methodology",
        "citation", "references", "thesis", "journal", "논문", "초록", "인용",
    },
    "trading": {
        "bitcoin", "btc", "trading", "trade", "strategy", "backtest",
        "ohlcv", "market", "risk", "portfolio", "kronos", "jutopia",
        "비트코인", "자동매매", "전략", "백테스트",
    },
    "codebase": {
        "src", "tests", "architecture", "api", "module", "class", "function",
        "package", "pyproject", "requirements", "dockerfile",
    },
}

EXTENSION_HINTS = {
    "research": {".pdf", ".bib", ".ris", ".docx"},
    "trading": {".csv", ".parquet", ".sqlite", ".db"},
    "codebase": {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".cpp", ".h"},
}


def iter_files(paths: list[Path], limit: int = 400):
    seen = 0
    for root in paths:
        if not root.exists():
            continue
        if root.is_file():
            yield root
            seen += 1
            continue
        for current, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", ".venv"}]
            for name in files:
                yield Path(current) / name
                seen += 1
                if seen >= limit:
                    return


def score_file(path: Path, scores: dict[str, int], max_bytes: int) -> None:
    lowered = str(path).lower()
    for profile, extensions in EXTENSION_HINTS.items():
        if path.suffix.lower() in extensions:
            scores[profile] += 3
    for profile, words in KEYWORDS.items():
        scores[profile] += sum(1 for word in words if word in lowered)

    if path.suffix.lower() in {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".py"}:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:max_bytes].lower()
        except OSError:
            return
        for profile, words in KEYWORDS.items():
            scores[profile] += sum(text.count(word) for word in words)


def detect_profile(paths: list[str], max_bytes: int = 16384) -> dict:
    roots = [Path(p).expanduser() for p in paths]
    scores = {"research": 0, "trading": 0, "codebase": 0}
    sampled = 0
    for path in iter_files(roots):
        sampled += 1
        score_file(path, scores, max_bytes)

    active = [name for name, value in scores.items() if value >= 3]
    if len(active) >= 2:
        profile = "mixed"
    elif active:
        profile = max(scores, key=scores.get)
    else:
        profile = "general"

    return {"profile": profile, "scores": scores, "sampled_files": sampled}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", default=["."], help="Source paths to scan.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    parser.add_argument("--max-bytes", type=int, default=16384)
    args = parser.parse_args()

    result = detect_profile(args.paths, max_bytes=args.max_bytes)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["profile"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

