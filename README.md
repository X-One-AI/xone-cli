# xone-cli

Languages: English | [中文](./README.zh-CN.md)

`xone-cli` is the unified local entry point for X-One Agent Evidence Loop workflows.

It helps developers move from scattered tools to one clear path:

```text
collect PR evidence
-> decide handoff
-> create failure packet when needed
-> attach MCP risk context when useful
-> run safe-local training scenarios
```

## Install

```bash
python -m pip install xone-cli
xone --version
xone doctor
```

## First Run

```bash
xone doctor
xone doctor --install-plan
xone runbook --head HEAD --dry-run
```

`xone runbook` auto-detects the local repository default branch. Remote GitHub URLs are not accepted yet; clone the repository first, then pass the local path with `--repo`.

`xone-cli` orchestrates these X-One tools:

- `agent-pr-evidence`
- `agent-failure-packet`
- `mcp-risk-index`
- `ai-incident-lab`

## Boundary

- It does not replace the underlying tools.
- It does not post GitHub comments.
- It does not modify repositories automatically.
- It does not make allow/deny runtime enforcement decisions.
- It does not make hidden network calls.

## Docs

- [Product Foundation](./docs/product-foundation.md)
- [Install](./docs/install.md)
- [Release](./docs/release.md)
- [Open-source Feedback Ledger](./docs/feedback/open-source-feedback-ledger.md)
