import json
from pathlib import Path

from xone_cli.cli import main


def _fake_tool(bin_dir: Path, name: str, body: str = "echo tool") -> None:
    path = bin_dir / name
    path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    path.chmod(0o755)


def test_version_outputs_package_version(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == "xone 0.1.0"


def test_doctor_json_reports_required_tools(tmp_path, monkeypatch, capsys):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_tool(bin_dir, "agent-pr-evidence", "echo agent-pr-evidence 0.4.1")
    monkeypatch.setenv("PATH", str(bin_dir))

    assert main(["doctor", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "xone.doctor.v1"
    assert payload["tools"][0]["name"] == "agent-pr-evidence"
    assert payload["tools"][0]["available"] is True
    assert payload["tools"][1]["available"] is False


def test_runbook_dry_run_is_available(capsys):
    assert main(["runbook", "--dry-run"]) == 0
    assert "xone runbook" in capsys.readouterr().out
