# Install

## Local Development

```bash
python -m pip install -e '.[dev]'
xone --version
xone doctor
xone runbook --base main --head HEAD --dry-run
```

## User Install

```bash
python -m pip install xone-cli
xone doctor
xone runbook --base main --head HEAD --dry-run
```

`xone doctor` reports missing X-One tools and shows install guidance.

If `xone doctor` reports missing tools, install the suggested X-One packages and run it again before using `evidence`, `risk`, or `lab` commands.
