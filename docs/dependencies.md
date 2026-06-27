# GHFP LLM Wiki Dependencies

`./install.sh` creates `.venv/` by default and installs the `recommended` Python dependency set:

```bash
python3 scripts/bootstrap_install.py --dependency-set recommended
```

## Python Dependency Sets

- `core`: editable install of this repository only.
- `recommended`: PDF, Office, YouTube transcript/download helpers, OCR bridge, figure export, image analysis, and graph helper packages.
- `all`: everything in `recommended`, plus the Playwright Python package.
- `none`: skip Python dependency installation.

Equivalent manual commands:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[recommended]
```

For development:

```bash
python -m pip install -r requirements-dev.txt
pytest
```

## System Tools

These capabilities may still require non-Python binaries:

- Video frame extraction: `ffmpeg` and `ffprobe`
- OCR engine: `tesseract`
- HWP fallback: Node.js plus `npx`/`hwpjs` or `kordoc`
- Browser fallback: Playwright browser binaries after installing the Python package
- Graphify CLI: external `graphify` command when you want to run Graphify itself
- Obsidian desktop app: only needed to open the generated vault interactively

macOS examples:

```bash
brew install ffmpeg tesseract node
python -m playwright install chromium
```

Check the final state:

```bash
python scripts/ghpf_wiki.py capabilities --vault ./my-vault
```
