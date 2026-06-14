from __future__ import annotations

import shlex
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

from xone_cli.model import CommandResult, DoctorReport, ToolStatus

DOCTOR_SCHEMA_VERSION = "xone.doctor.v1"

REQUIRED_TOOLS = (
    "agent-pr-evidence",
    "agent-failure-packet",
    "mcp-risk-index",
    "ai-incident-lab",
)

PACKAGE_BY_TOOL = {
    "agent-pr-evidence": "xone-agent-pr-evidence",
    "agent-failure-packet": "xone-agent-failure-packet",
    "mcp-risk-index": "xone-mcp-risk-index",
    "ai-incident-lab": "xone-ai-incident-lab",
}

INSTALL_PLAN_GROUPS = {
    "evidence-loop": (
        "agent-pr-evidence",
        "agent-failure-packet",
        "mcp-risk-index",
        "ai-incident-lab",
    ),
    "mcp-review": ("mcp-risk-index",),
    "incident-lab": ("ai-incident-lab",),
    "all": REQUIRED_TOOLS,
}


def find_tool(name: str) -> str | None:
    return shutil.which(name)


def install_hint(name: str) -> str:
    package = PACKAGE_BY_TOOL.get(name, name)
    return f"python -m pip install {package}"


def install_plan(profile: str = "all") -> list[tuple[str, str]]:
    if profile == "all":
        groups = ("evidence-loop", "mcp-review", "incident-lab")
    else:
        groups = (profile,)
    plan = []
    for group in groups:
        packages = [PACKAGE_BY_TOOL[name] for name in INSTALL_PLAN_GROUPS[group]]
        plan.append((group, f"python -m pip install {' '.join(packages)}"))
    return plan


def run_command(
    command: Sequence[str],
    *,
    dry_run: bool = False,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> CommandResult:
    command_list = [str(part) for part in command]
    if dry_run:
        return CommandResult(
            command=command_list,
            returncode=0,
            stdout=f"DRY RUN: {_format_command(command_list)}",
            stderr="",
            dry_run=True,
        )

    try:
        completed = subprocess.run(
            command_list,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=dict(env) if env is not None else None,
        )
    except FileNotFoundError as error:
        return CommandResult(
            command=command_list,
            returncode=127,
            stdout="",
            stderr=str(error),
        )
    return CommandResult(
        command=command_list,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def doctor_status() -> DoctorReport:
    tools = [_tool_status(name) for name in REQUIRED_TOOLS]
    return DoctorReport(schema_version=DOCTOR_SCHEMA_VERSION, tools=tools)


def _tool_status(name: str) -> ToolStatus:
    executable = find_tool(name)
    if not executable:
        return ToolStatus(
            name=name,
            executable=None,
            available=False,
            version=None,
            install_hint=install_hint(name),
        )
    version_result = run_command([name, "--version"])
    version = version_result.stdout.strip() if version_result.returncode == 0 else None
    return ToolStatus(
        name=name,
        executable=executable,
        available=True,
        version=version,
        install_hint=install_hint(name),
    )


def _format_command(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)
