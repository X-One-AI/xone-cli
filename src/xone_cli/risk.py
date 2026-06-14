from __future__ import annotations

from pathlib import Path

from xone_cli.tooling import run_command

RISK_CONTEXT_BOUNDARY = "This is review context, not an allow/deny decision."


def render_risk_context(*, catalog: Path, output: Path, dry_run: bool = False) -> int:
    validate = run_command(["mcp-risk-index", "validate", "--catalog", str(catalog), "--strict"], dry_run=dry_run)
    print(validate.stdout, end="" if validate.stdout.endswith("\n") else "\n")
    if validate.stderr:
        print(validate.stderr, end="" if validate.stderr.endswith("\n") else "\n")
    if validate.returncode != 0:
        return validate.returncode

    rendered = run_command(["mcp-risk-index", "render", "--catalog", str(catalog), "--format", "markdown"], dry_run=dry_run)
    if rendered.returncode == 0 and not dry_run:
        output.write_text(f"> {RISK_CONTEXT_BOUNDARY}\n\n{rendered.stdout}", encoding="utf-8")
    else:
        print(rendered.stdout, end="" if rendered.stdout.endswith("\n") else "\n")
    if rendered.stderr:
        print(rendered.stderr, end="" if rendered.stderr.endswith("\n") else "\n")
    return rendered.returncode

