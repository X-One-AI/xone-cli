# Open-Source Feedback Ledger

This ledger substitutes early real-user feedback with public, sanitized open-source samples.

Rules:

- Record source URL and observation, not raw sensitive configuration.
- Do not label third-party projects as safe or unsafe.
- Classify observations as false-positive, false-negative, adapter-request, scenario-request, catalog-update, config-discovery, default-branch, install-friction, agent-instruction-signal, runtime-capability-risk, or cli-ux-improvement.

## Samples

The first ledger entries live in `fixtures/open-source-samples/`.

Use `xone eval open-source --repos repos.txt --output evaluation.json --format json` to refresh sanitized evaluation records. Add `--clone-root <dir>` only when shallow public clones are acceptable for the review.

| Source | Stars | Forks | Type | Feedback |
| --- | ---: | ---: | --- | --- |
| modelcontextprotocol/servers | 87186 | 10998 | mcp-server-examples | catalog-update |
| github/github-mcp-server | 30650 | 4381 | mcp-server-examples | catalog-update |
| microsoft/playwright-mcp | 33878 | 2798 | mcp-server-examples | scenario-request |
| upstash/context7 | 57304 | 2706 | mcp-server-examples | catalog-update |
| wonderwhy-er/DesktopCommanderMCP | 6165 | 729 | security-sensitive | scenario-request |
| cline/cline | 63235 | 6677 | ai-coding-tool | adapter-request |
| continuedev/continue | 33683 | 4654 | ai-coding-tool | adapter-request |
| Aider-AI/aider | 46171 | 4580 | ai-coding-tool | scenario-request |
| openai/codex | 90890 | 13410 | ai-coding-tool | scenario-request |
| OpenHands/OpenHands | 76929 | 9771 | agent-workflow | adapter-request |
| docker/mcp-gateway | 1452 | 246 | security-sensitive | catalog-update |
| anthropics/claude-code | 132258 | 21413 | ai-coding-tool | scenario-request |
