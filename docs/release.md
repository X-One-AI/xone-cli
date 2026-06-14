# Release

`xone-cli` uses a release candidate gate before public publishing.

Required checks:

```bash
python -m pytest -q
python -m build
python -m venv /tmp/xone-cli-release-venv
/tmp/xone-cli-release-venv/bin/python -m pip install dist/*.whl
/tmp/xone-cli-release-venv/bin/xone --version
/tmp/xone-cli-release-venv/bin/xone doctor --json
```

PyPI publishing must be tag-gated. TestPyPI publishing must use the `testpypi` environment.

