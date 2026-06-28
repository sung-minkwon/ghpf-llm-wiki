from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import ghpf_wiki  # noqa: E402


class _BodyHandler(BaseHTTPRequestHandler):
    body = b""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, *args):
        pass


class GhpfWikiTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "ghpf_wiki.py"), *args],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_fetch_url_reports_truncation(self):
        _BodyHandler.body = b"0123456789END"
        server = ThreadingHTTPServer(("127.0.0.1", 0), _BodyHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_address[1]}/large.txt"
            body, content_type, truncated = ghpf_wiki.fetch_url(url, max_bytes=10)
        finally:
            server.shutdown()
            server.server_close()

        self.assertEqual(body, b"0123456789")
        self.assertIn("text/plain", content_type)
        self.assertTrue(truncated)

    def test_fetch_web_content_warns_when_truncated(self):
        with mock.patch.object(ghpf_wiki, "fetch_url", return_value=(b"abc", "text/html", True)):
            body, content_type, warnings = ghpf_wiki.fetch_web_content("https://example.test/large")

        self.assertEqual(body, b"abc")
        self.assertEqual(content_type, "text/html")
        self.assertTrue(any("truncated" in warning for warning in warnings))

    def test_extract_missing_source_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.pdf"
            completed = self.run_cli("extract", "--vault", str(Path(temp_dir) / "vault"), str(missing))

        self.assertNotEqual(completed.returncode, 0)
        result = json.loads(completed.stdout)
        self.assertEqual(result["skipped"][0]["reason"], "missing_or_not_file")

    def test_ingest_duplicate_hash_in_same_run_skips_second_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            src = root / "src"
            src.mkdir()
            first = src / "a.md"
            second = src / "b.md"
            first.write_text("same content\n", encoding="utf-8")
            second.write_text("same content\n", encoding="utf-8")

            completed = self.run_cli("ingest", "--vault", str(root / "vault"), str(first), str(second))

        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(len(result["ingested"]), 1)
        self.assertEqual(len(result["skipped"]), 1)
        self.assertEqual(result["skipped"][0]["reason"], "already_ingested")


if __name__ == "__main__":
    unittest.main()
