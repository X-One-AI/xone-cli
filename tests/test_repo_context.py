from pathlib import Path

from xone_cli.repo_context import detect_default_base, is_remote_repo_url, validate_local_repo


def test_detect_default_base_reads_local_git_head(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")

    assert detect_default_base(str(repo)) == "master"


def test_detect_default_base_prefers_origin_head_when_available(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git = repo / ".git"
    git.mkdir()
    (git / "HEAD").write_text("ref: refs/heads/feature\n", encoding="utf-8")
    (git / "refs" / "remotes" / "origin").mkdir(parents=True)
    (git / "refs" / "remotes" / "origin" / "HEAD").write_text("ref: refs/remotes/origin/trunk\n", encoding="utf-8")

    assert detect_default_base(str(repo)) == "trunk"


def test_remote_repo_url_detection():
    assert is_remote_repo_url("https://github.com/openai/codex") is True
    assert is_remote_repo_url("git@github.com:X-One-AI/xone-cli.git") is True
    assert is_remote_repo_url("/tmp/repo") is False


def test_validate_local_repo_rejects_remote_url():
    valid, message = validate_local_repo("https://github.com/openai/codex")

    assert valid is False
    assert "Remote repository URLs are not supported by runbook yet" in message
    assert "git clone --depth 1 https://github.com/openai/codex" in message


def test_validate_local_repo_requires_git_metadata(tmp_path):
    valid, message = validate_local_repo(str(tmp_path))

    assert valid is False
    assert "not a local git repository" in message
