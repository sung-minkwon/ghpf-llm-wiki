import json
from pathlib import Path

from scripts.detect_profile import detect_profile
from scripts.setup_vault import setup_vault


def test_setup_vault_creates_general_layout(tmp_path: Path):
    result = setup_vault(tmp_path, "general", [], force=False)

    assert result["profile"] == "general"
    assert (tmp_path / "wiki" / "index.md").exists()
    assert (tmp_path / "wiki" / "manifest.json").exists()
    assert (tmp_path / "schema" / "AGENTS.md").exists()
    assert (tmp_path / "raw" / "originals").is_dir()
    assert (tmp_path / "swarmvault" / "state" / "hybrid-index").is_dir()

    config = json.loads((tmp_path / "ghpf.config.json").read_text(encoding="utf-8"))
    assert config["profile"] == "general"
    assert config["evidence_index"] == "evidence/index.jsonl"


def test_detect_profile_identifies_mixed_sources(tmp_path: Path):
    (tmp_path / "paper.md").write_text("abstract methodology citation thesis", encoding="utf-8")
    (tmp_path / "strategy.md").write_text("bitcoin trading strategy backtest risk", encoding="utf-8")

    result = detect_profile([str(tmp_path)])

    assert result["profile"] == "mixed"
    assert result["scores"]["research"] >= 3
    assert result["scores"]["trading"] >= 3


def test_setup_vault_auto_reuses_existing_profile(tmp_path: Path):
    setup_vault(tmp_path, "general", [], force=False)
    (tmp_path / "wiki" / "sources" / "strategy.md").write_text(
        "bitcoin trading strategy backtest risk abstract methodology citation",
        encoding="utf-8",
    )

    result = setup_vault(tmp_path, "auto", [], force=False)

    assert result["profile"] == "general"
    assert result["detected"]["source"] == "existing_config"
