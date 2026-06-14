from pathlib import Path


def test_docs_and_package_metadata_stay_aligned():
    english = Path("README.md").read_text(encoding="utf-8")
    chinese = Path("README.zh-CN.md").read_text(encoding="utf-8")
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    ci = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    publish = Path(".github/workflows/publish.yml").read_text(encoding="utf-8")
    production = Path("ops/constraints/production.md").read_text(encoding="utf-8")
    main_entry = Path("ops/constraints/main-entry.md").read_text(encoding="utf-8")
    evolution = Path("ops/skills/evolution.md").read_text(encoding="utf-8")

    assert "README.zh-CN.md" in english
    assert "README.md" in chinese
    assert "xone doctor" in english
    assert "xone runbook" in english
    assert "xone doctor" in chinese
    assert "xone runbook" in chinese
    assert 'name = "xone-cli"' in pyproject
    assert 'xone = "xone_cli.cli:entrypoint"' in pyproject
    assert "python -m pytest -q" in ci
    assert "environment: testpypi" in publish
    assert "startsWith(github.ref, 'refs/tags/v')" in publish
    assert "Do not make hidden network calls" in production
    assert "Keep top-level commands small" in main_entry
    assert "Delete or weaken" in evolution

