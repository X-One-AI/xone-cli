import json
from pathlib import Path

from xone_cli.cli import main


def _fake_tool(bin_dir: Path, name: str, body: str = "echo tool") -> None:
    path = bin_dir / name
    path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    path.chmod(0o755)


def test_version_outputs_package_version(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == "xone 0.1.1"


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


def test_doctor_install_plan_outputs_scenario_commands(capsys):
    assert main(["doctor", "--install-plan"]) == 0

    output = capsys.readouterr().out
    assert "X-One install plan" in output
    assert "evidence-loop" in output
    assert "python -m pip install xone-agent-pr-evidence xone-agent-failure-packet xone-mcp-risk-index xone-ai-incident-lab" in output
    assert "mcp-review" in output
    assert "incident-lab" in output


def test_runbook_dry_run_is_available(capsys):
    assert main(["runbook", "--base", "main", "--head", "HEAD", "--dry-run"]) == 0
    assert "agent-pr-evidence collect" in capsys.readouterr().out


def test_runbook_rejects_remote_repo_url_instead_of_dry_run_false_positive(capsys):
    assert main(["runbook", "--repo", "https://github.com/openai/codex", "--head", "HEAD", "--dry-run"]) == 2

    output = capsys.readouterr().out
    assert "Remote repository URLs are not supported by runbook yet" in output
    assert "git clone --depth 1 https://github.com/openai/codex" in output
