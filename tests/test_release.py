from pathlib import Path

import xone_cli.release as release_module
from xone_cli.model import CommandResult
from xone_cli.release import required_files_status, verify_release


def test_required_files_status_reports_missing_files(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='xone-cli'\n", encoding="utf-8")

    status = required_files_status(tmp_path)

    assert status["pyproject.toml"] is True
    assert status["README.md"] is False


def test_verify_release_supports_metadata_only_mode():
    result = verify_release(project_root=Path("."), build=False, install=False, smoke=False)

    assert result["schema_version"] == "xone.release.verify.v1"
    assert result["required_files"]["pyproject.toml"] is True
    assert result["ok"] is True


def test_install_smoke_runs_before_temporary_venv_cleanup(tmp_path, monkeypatch):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "xone_cli-0.1.0-py3-none-any.whl").write_text("wheel", encoding="utf-8")
    for name in release_module.REQUIRED_RELEASE_FILES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ok", encoding="utf-8")

    class FakeTemporaryDirectory:
        active = False

        def __init__(self, prefix: str):
            self.path = tmp_path / "fake-temp"

        def __enter__(self):
            self.path.mkdir()
            FakeTemporaryDirectory.active = True
            return str(self.path)

        def __exit__(self, exc_type, exc, tb):
            FakeTemporaryDirectory.active = False

    def fake_run_command(command, *, dry_run=False, cwd=None, env=None):
        command_text = " ".join(str(part) for part in command)
        if "bin/xone" in command_text:
            assert FakeTemporaryDirectory.active is True
        assert not env or "PYTHONPATH" not in env
        return CommandResult(command=[str(part) for part in command], returncode=0, stdout="ok", stderr="", dry_run=dry_run)

    monkeypatch.setattr(release_module.tempfile, "TemporaryDirectory", FakeTemporaryDirectory)
    monkeypatch.setattr(release_module, "run_command", fake_run_command)

    result = verify_release(project_root=tmp_path, build=False, install=True, smoke=True)

    assert result["ok"] is True
    assert [check["name"] for check in result["checks"]] == ["venv", "wheel-install", "cli-version", "doctor-json"]
