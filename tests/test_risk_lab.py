import os
from pathlib import Path

from xone_cli.cli import main


def _fake_tool(bin_dir: Path, name: str, body: str) -> None:
    path = bin_dir / name
    path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    path.chmod(0o755)


def test_risk_context_prepends_review_boundary(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    catalog = tmp_path / "catalog.yml"
    output = tmp_path / "risk.md"
    catalog.write_text("schema_version: test\n", encoding="utf-8")
    _fake_tool(
        bin_dir,
        "mcp-risk-index",
        "if [ \"$1\" = validate ]; then exit 0; fi\nprintf '# MCP Risk Index\\n'",
    )
    monkeypatch.setenv("PATH", os.pathsep.join([str(bin_dir), os.environ.get("PATH", "")]))

    assert main(["risk", "context", "--catalog", str(catalog), "--output", str(output)]) == 0

    rendered = output.read_text(encoding="utf-8")
    assert "review context, not an allow/deny decision" in rendered
    assert "# MCP Risk Index" in rendered


def test_lab_evidence_loop_renders_scenario(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    output = tmp_path / "lab.md"
    _fake_tool(
        bin_dir,
        "ai-incident-lab",
        "if [ \"$1\" = init ]; then mkdir -p \"$3\"; touch \"$3/agent-evidence-loop.yml\"; exit 0; fi\nif [ \"$1\" = validate ]; then exit 0; fi\nprintf 'This scenario teaches the evidence loop. It does not execute the other X-One tools.\\n'",
    )
    monkeypatch.setenv("PATH", os.pathsep.join([str(bin_dir), os.environ.get("PATH", "")]))

    assert main(["lab", "evidence-loop", "--output", str(output)]) == 0

    assert "This scenario teaches the evidence loop" in output.read_text(encoding="utf-8")

