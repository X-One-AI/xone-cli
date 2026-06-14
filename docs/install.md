# Install

## Local Development

```bash
python -m pip install -e '.[dev]'
xone --version
xone doctor
xone doctor --install-plan
xone runbook --head HEAD --dry-run
```

## User Install

```bash
python -m pip install xone-cli
xone doctor
xone doctor --install-plan
xone runbook --head HEAD --dry-run
```

`xone doctor` reports missing X-One tools and shows install guidance.

If `xone doctor` reports missing tools, install the suggested X-One packages and run it again before using `evidence`, `risk`, or `lab` commands.

`xone runbook` expects a local git repository. To inspect a public repository, clone it first:

```bash
git clone --depth 1 https://github.com/owner/repo
xone runbook --repo repo --head HEAD --dry-run
```
