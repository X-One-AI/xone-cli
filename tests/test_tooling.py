import os
from pathlib import Path

from xone_cli.tooling import REQUIRED_TOOLS, doctor_status, find_tool, run_command


def _fake_tool(bin_dir: Path, name: str, body: str = "echo tool") -> Path:
    path = bin_dir / name
    path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def test_find_tool_returns_present_executable(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    tool = _fake_tool(bin_dir, "agent-pr-evidence", "echo agent-pr-evidence 0.4.1")
    monkeypatch.setenv("PATH", str(bin_dir))

    assert find_tool("agent-pr-evidence") == str(tool)


def test_doctor_status_reports_present_and_missing_tools(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_tool(bin_dir, "agent-pr-evidence", "echo agent-pr-evidence 0.4.1")
    monkeypatch.setenv("PATH", str(bin_dir))

    report = doctor_status()
    tools = {tool.name: tool for tool in report.tools}

    assert set(tools) == set(REQUIRED_TOOLS)
    assert tools["agent-pr-evidence"].available is True
    assert tools["agent-failure-packet"].available is False
    assert "python -m pip install" in tools["agent-failure-packet"].install_hint


def test_run_command_supports_dry_run():
    result = run_command(["agent-pr-evidence", "--version"], dry_run=True)

    assert result.returncode == 0
    assert result.dry_run is True
    assert "agent-pr-evidence --version" in result.stdout


def test_run_command_captures_output(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_tool(bin_dir, "xone-fake", "echo ok")
    monkeypatch.setenv("PATH", os.pathsep.join([str(bin_dir), os.environ.get("PATH", "")]))

    result = run_command(["xone-fake"])

    assert result.returncode == 0
    assert result.stdout.strip() == "ok"
    assert result.stderr == ""

