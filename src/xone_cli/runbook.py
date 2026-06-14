from __future__ import annotations

import json
from pathlib import Path


def render_runbook(report: dict) -> str:
    decision = report.get("handoff_decision") or {}
    lines = [
        "# X-One Evidence Runbook",
        "",
        "## Handoff Decision",
        "",
        f"- Decision: `{decision.get('decision', 'unknown')}`",
        f"- Reason: {decision.get('reason', 'not provided')}",
        f"- Evidence source: {decision.get('evidence_source', 'not provided')}",
        f"- Handoff target: {decision.get('handoff_target', 'not provided')}",
        f"- Revisit trigger: {decision.get('revisit_trigger', 'not provided')}",
        "",
        "## Next Action",
        "",
        _next_action(decision.get("decision")),
        "",
        "## Raw Summary",
        "",
        "```json",
        json.dumps(report.get("summary", {}), indent=2, sort_keys=True),
        "```",
        "",
    ]
    return "\n".join(lines)


def write_runbook(report: dict, output: Path) -> None:
    output.write_text(render_runbook(report), encoding="utf-8")


def _next_action(decision: str | None) -> str:
    if decision == "create-failure-packet":
        return "- Build a redacted failure packet with `xone evidence packet`."
    if decision == "block-before-merge":
        return "- Add passing tests, an accountable owner, or a remediation plan before merge."
    if decision == "baseline-review":
        return "- Review the baseline before accepting new or existing risk."
    if decision == "request-test-evidence":
        return "- Provide test logs or explain why tests are not required."
    return "- Continue normal review."

