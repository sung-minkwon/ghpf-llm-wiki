from pathlib import Path

from scripts.bootstrap_install import DEPENDENCY_TARGETS, skipped_step, venv_python


def test_dependency_targets_expose_install_modes():
    assert DEPENDENCY_TARGETS["none"] is None
    assert DEPENDENCY_TARGETS["core"] == "."
    assert DEPENDENCY_TARGETS["recommended"] == ".[recommended]"
    assert DEPENDENCY_TARGETS["all"] == ".[all]"


def test_skipped_step_is_successful():
    step = skipped_step("example", "not needed")

    assert step["returncode"] == 0
    assert step["stdout"] == "not needed"


def test_venv_python_points_inside_venv(tmp_path: Path):
    path = venv_python(tmp_path / ".venv")

    assert ".venv" in path.parts
    assert path.name.startswith("python")
