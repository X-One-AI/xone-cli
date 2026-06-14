# Install

## Local Development

```bash
python -m pip install -e '.[dev]'
xone --version
xone doctor
xone doctor --install-plan
xone runbook --head HEAD --dry-run
xone eval open-source --repos repos.txt --output evaluation.md --format markdown
```

## User Install

```bash
python -m pip install xone-cli
xone doctor
xone doctor --install-plan
xone runbook --head HEAD --dry-run
xone eval open-source --repos repos.txt --output evaluation.md --format markdown
```

`xone doctor` reports missing X-One tools and shows install guidance.

If `xone doctor` reports missing tools, run `xone doctor --install-plan`. The install plan pins the current recommended X-One package versions and shows the first next command for each scenario.

Current scenario groups:

- `evidence-loop`: install `agent-pr-evidence 0.4.2`, `agent-failure-packet 0.4.2`, `mcp-risk-index 0.3.1`, and `ai-incident-lab 0.2.2`, then run `xone runbook --head HEAD --dry-run`.
- `mcp-review`: install `mcp-risk-index 0.3.1`, then run `xone risk context --catalog mcp-risk-index.catalog.yml --output mcp-risk-context.md`.
- `incident-lab`: install `ai-incident-lab 0.2.2`, then run `xone lab evidence-loop --output agent-evidence-loop.md`.

`xone runbook` expects a local git repository. To inspect a public repository, clone it first:

```bash
git clone --depth 1 https://github.com/owner/repo
xone runbook --repo repo --head HEAD --dry-run
```

## Open-Source Adoption Evaluation

Use `xone eval open-source` when you want a repeatable, sanitized surrogate feedback pass over public repositories.

Create a repo list:

```text
openai/codex
https://github.com/docker/mcp-gateway
```

Metadata-only evaluation:

```bash
xone eval open-source --repos repos.txt --output evaluation.json --format json
```

Public shallow-clone evaluation:

```bash
xone eval open-source --repos repos.txt --clone-root .xone-eval-clones --output evaluation.md --format markdown
```

Safety boundary:

- The command records public repository metadata and X-One command summaries.
- It does not label third-party repositories as safe or unsafe.
- It does not run third-party install scripts, test scripts, containers, or project commands.
- `--clone-root` performs `git clone --depth 1` only, then runs X-One dry-run commands against the local clones.
