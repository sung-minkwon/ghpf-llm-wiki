from pathlib import Path

from ghpf_wiki_support.dependencies import capabilities, command_available, python_module_available


def test_python_module_available_uses_current_interpreter():
    assert python_module_available("json") is True
    assert python_module_available("definitely_missing_ghpf_module") is False


def test_command_available_reports_boolean():
    assert isinstance(command_available("python3"), bool)


def test_capabilities_can_include_vault_status(tmp_path: Path):
    report = capabilities(tmp_path, vault_status=lambda vault: {"vault": str(vault), "ok": True})

    assert report["optional_modes"]["basic_wikilink_search"] is True
    assert report["vault"] == {"vault": str(tmp_path), "ok": True}
    assert "python_modules" in report
