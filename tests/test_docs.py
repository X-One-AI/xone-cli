from pathlib import Path


def test_docs_and_package_metadata_stay_aligned():
    english = Path("README.md").read_text(encoding="utf-8")
    chinese = Path("README.zh-CN.md").read_text(encoding="utf-8")
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    ci = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    publish = Path(".github/workflows/publish.yml").read_text(encoding="utf-8")
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")
    production = Path("ops/constraints/production.md").read_text(encoding="utf-8")
    main_entry = Path("ops/constraints/main-entry.md").read_text(encoding="utf-8")
    evolution = Path("ops/skills/evolution.md").read_text(encoding="utf-8")

    assert "README.zh-CN.md" in english
    assert "README.md" in chinese
    assert "xone doctor" in english
    assert "xone doctor --install-plan" in english
    assert "xone runbook --head HEAD --dry-run" in english
    assert "Remote GitHub URLs are not accepted yet" in english
    assert "xone doctor" in chinese
    assert "xone doctor --install-plan" in chinese
    assert "xone runbook --head HEAD --dry-run" in chinese
    assert "远程 GitHub URL" in chinese
    assert "git clone --depth 1 https://github.com/owner/repo" in Path("docs/install.md").read_text(encoding="utf-8")
    assert "xone release verify --build --install --smoke" in Path("docs/release.md").read_text(encoding="utf-8")
    assert 'name = "xone-cli"' in pyproject
    assert 'xone = "xone_cli.cli:entrypoint"' in pyproject
    assert "python -m pytest -q" in ci
    assert "xone runbook --base HEAD~1 --head HEAD --dry-run" in ci
    assert "environment: testpypi" in publish
    assert "startsWith(github.ref, 'refs/tags/v')" in publish
    assert "doctor --install-plan" in changelog
    assert "auto-detect the local repository default branch" in changelog
    assert "Do not make hidden network calls" in production
    assert "Keep top-level commands small" in main_entry
    assert "Delete or weaken" in evolution
