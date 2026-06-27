"""Dependency and capability detection for GHFP LLM Wiki."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

COMMANDS = [
    "git",
    "node",
    "npx",
    "uv",
    "uvx",
    "graphify",
    "playwright",
    "yt-dlp",
    "ffmpeg",
    "ffprobe",
    "tesseract",
    "obsidian",
    "opendataloader-pdf",
    "marker_single",
    "hwpjs",
    "deepcloak",
]

PYTHON_MODULES = [
    "pypdf",
    "PyPDF2",
    "pdfplumber",
    "docx",
    "pptx",
    "openpyxl",
    "networkx",
    "youtube_transcript_api",
    "pytesseract",
    "playwright",
    "matplotlib",
    "numpy",
    "PIL",
]


def command_available(command: str) -> bool:
    return shutil.which(command) is not None


def python_module_available(module: str, python: str | None = None) -> bool:
    executable = python or sys.executable
    result = subprocess.run(
        [executable, "-c", f"import {module}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def capabilities(
    vault: Path | None = None,
    vault_status: Callable[[Path], dict] | None = None,
    python: str | None = None,
) -> dict:
    commands = {name: command_available(name) for name in COMMANDS}
    modules = {name: python_module_available(name, python=python) for name in PYTHON_MODULES}
    report = {
        "commands": commands,
        "python_modules": modules,
        "optional_modes": {
            "basic_wikilink_search": True,
            "graph_sidecar": True,
            "graphify_import_ready": True,
            "graphify_cli_ready": commands["graphify"] or commands["uv"],
            "youtube_ingest_ready": commands["yt-dlp"] or commands["uvx"] or modules["youtube_transcript_api"],
            "ocr_ready": commands["tesseract"] or modules["pytesseract"],
            "advanced_pdf_extract_ready": commands["opendataloader-pdf"] or commands["marker_single"] or modules["pdfplumber"],
            "hwp_extract_ready": commands["hwpjs"] or commands["npx"],
            "office_extract_ready": modules["docx"] or modules["pptx"] or modules["openpyxl"] or commands["npx"],
            "playwright_ready": commands["playwright"] or modules["playwright"],
            "deepcloak_ready": commands["deepcloak"],
            "web_fallback_ready": modules["playwright"] or commands["deepcloak"],
            "figure_export_ready": modules["matplotlib"] and modules["numpy"],
            "image_frame_analysis_ready": modules["PIL"],
            "video_frame_extract_ready": commands["ffmpeg"],
            "youtube_frame_extract_ready": commands["ffmpeg"] and (commands["yt-dlp"] or commands["uvx"]),
        },
    }
    if vault is not None and vault_status is not None:
        report["vault"] = vault_status(vault)
    return report
