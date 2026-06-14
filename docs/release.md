# Release

`xone-cli` uses a release candidate gate before public publishing.

Required checks:

```bash
python -m pytest -q
python -m pip install -e '.[dev]'
xone release verify --build --install --smoke
```

`xone release verify` builds the package, installs the wheel into a temporary virtual environment, and runs smoke checks from the installed `xone` entry point.

PyPI publishing must be tag-gated. TestPyPI publishing must use the `testpypi` environment.
