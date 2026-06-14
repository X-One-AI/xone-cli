import json
import os
from pathlib import Path

from xone_cli.cli import main


def _fake_tool(bin_dir: Path, name: str, body: str) -> None:
    path = bin_dir / name
    path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    path.chmod(0o755)


def test_evidence_collect_invokes_agent_pr_evidence(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    out = tmp_path / "evidence.json"
    _fake_tool(
        bin_dir,
        "agent-pr-evidence",
        "printf '%s\\n' '{\"handoff_decision\":{\"decision\":\"continue-review\"}}' > \"${13}\"",
    )
    monkeypatch.setenv("PATH", os.pathsep.join([str(bin_dir), os.environ.get("PATH", "")]))

    assert main(["evidence", "collect", "--repo", ".", "--base", "main", "--head", "HEAD", "--output", str(out)]) == 0

    assert json.loads(out.read_text(encoding="utf-8"))["handoff_decision"]["decision"] == "continue-review"


def test_evidence_packet_validates_and_builds_failure_packet(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    source = tmp_path / "run.json"
    packet = tmp_path / "packet.md"
    source.write_text("{}", encoding="utf-8")
    _fake_tool(
        bin_dir,
        "agent-failure-packet",
        "if [ \"$1\" = validate ]; then exit 0; fi\nprintf '# Packet\\n' > \"$7\"",
    )
    monkeypatch.setenv("PATH", os.pathsep.join([str(bin_dir), os.environ.get("PATH", "")]))

    assert main(["evidence", "packet", "--input", str(source), "--output", str(packet)]) == 0

    assert packet.read_text(encoding="utf-8").startswith("# Packet")


def test_runbook_dry_run_lists_underlying_command(capsys):
    assert main(["runbook", "--repo", ".", "--base", "main", "--head", "HEAD", "--dry-run"]) == 0

    output = capsys.readouterr().out
    assert "agent-pr-evidence collect" in output
    assert "--base main" in output


def test_runbook_auto_detects_default_branch_for_local_repo(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")

    assert main(["runbook", "--repo", str(repo), "--head", "HEAD", "--dry-run"]) == 0

    output = capsys.readouterr().out
    assert f"--repo {repo}" in output
    assert "--base master" in output
