import json
from datetime import date

from xone_cli.cli import main


def test_eval_open_source_json_outputs_sanitized_records(tmp_path, monkeypatch):
    repos = tmp_path / "repos.txt"
    repos.write_text("openai/codex\nhttps://github.com/docker/mcp-gateway\n", encoding="utf-8")
    output = tmp_path / "records.json"

    def fake_metadata(repo, snapshot_date):
        return {
            "source": repo,
            "source_url": f"https://github.com/{repo}",
            "snapshot_date": snapshot_date.isoformat(),
            "stars": 10,
            "forks": 2,
            "open_issues": 1,
            "default_branch": "main",
            "language": "Python",
        }

    monkeypatch.setattr("xone_cli.open_source_eval.fetch_github_metadata", fake_metadata)

    assert main(["eval", "open-source", "--repos", str(repos), "--output", str(output), "--format", "json"]) == 0

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "xone.open_source_evaluation_batch.v1"
    assert [record["source"] for record in payload["records"]] == ["openai/codex", "docker/mcp-gateway"]
    assert payload["records"][0]["sanitization"] == {
        "raw_logs_committed": False,
        "secrets_removed": True,
        "third_party_safety_label_used": False,
    }
    assert payload["records"][0]["commands_run"][0]["command"] == "xone doctor --json"
    assert payload["records"][0]["commands_run"][1]["result"] == "skipped"


def test_eval_open_source_with_clone_root_runs_local_runbook_dry_run(tmp_path, monkeypatch):
    repos = tmp_path / "repos.txt"
    repos.write_text("upstash/context7\n", encoding="utf-8")
    output = tmp_path / "records.md"
    clone_root = tmp_path / "clones"

    def fake_metadata(repo, snapshot_date):
        return {
            "source": repo,
            "source_url": f"https://github.com/{repo}",
            "snapshot_date": snapshot_date.isoformat(),
            "stars": 20,
            "forks": 3,
            "open_issues": 4,
            "default_branch": "master",
            "language": "TypeScript",
        }

    def fake_clone(record, root):
        repo = root / "upstash-context7"
        (repo / ".git").mkdir(parents=True)
        (repo / ".git" / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")
        return repo

    monkeypatch.setattr("xone_cli.open_source_eval.fetch_github_metadata", fake_metadata)
    monkeypatch.setattr("xone_cli.open_source_eval.clone_repo", fake_clone)

    assert main(
        [
            "eval",
            "open-source",
            "--repos",
            str(repos),
            "--clone-root",
            str(clone_root),
            "--output",
            str(output),
            "--format",
            "markdown",
        ]
    ) == 0

    markdown = output.read_text(encoding="utf-8")
    assert "# X-One Open-Source Adoption Evaluation" in markdown
    assert "upstash/context7" in markdown
    assert "runbook-dry-run" in markdown
    assert "--base master" in markdown


def test_eval_open_source_records_clone_failure_without_crashing(tmp_path, monkeypatch):
    repos = tmp_path / "repos.txt"
    repos.write_text("cline/cline\nopenai/codex\n", encoding="utf-8")
    output = tmp_path / "records.json"
    clone_root = tmp_path / "clones"

    def fake_metadata(repo, snapshot_date):
        return {
            "source": repo,
            "source_url": f"https://github.com/{repo}",
            "snapshot_date": snapshot_date.isoformat(),
            "stars": 10,
            "forks": 2,
            "open_issues": 1,
            "default_branch": "main",
            "language": "TypeScript",
        }

    def fake_clone(record, root):
        if record["source"] == "cline/cline":
            raise RuntimeError("clone failed")
        repo = root / "openai-codex"
        (repo / ".git").mkdir(parents=True)
        (repo / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        return repo

    monkeypatch.setattr("xone_cli.open_source_eval.fetch_github_metadata", fake_metadata)
    monkeypatch.setattr("xone_cli.open_source_eval.clone_repo", fake_clone)

    assert main(
        [
            "eval",
            "open-source",
            "--repos",
            str(repos),
            "--clone-root",
            str(clone_root),
            "--output",
            str(output),
            "--format",
            "json",
        ]
    ) == 0

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert [record["source"] for record in payload["records"]] == ["cline/cline", "openai/codex"]
    failed_command = payload["records"][0]["commands_run"][1]
    assert failed_command["name"] == "shallow-clone"
    assert failed_command["result"] == "fail"
    assert failed_command["mode"] == "read-only"
    assert payload["records"][1]["commands_run"][1]["name"] == "runbook-dry-run"
