from __future__ import annotations

import json
import tempfile
from pathlib import Path

from xone_cli.tooling import run_command


def collect_evidence(
    *,
    repo: str,
    base: str,
    head: str,
    output: Path | None,
    test_logs: list[str],
    profile: str,
    dry_run: bool = False,
) -> int:
    command = [
        "agent-pr-evidence",
        "collect",
        "--repo",
        repo,
        "--base",
        base,
        "--head",
        head,
        "--profile",
        profile,
        "--format",
        "json",
    ]
    for test_log in test_logs:
        command.extend(["--test-log", test_log])
    if output:
        command.extend(["--output", str(output)])
    result = run_command(command, dry_run=dry_run)
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n")
    return result.returncode


def gate_evidence(
    *,
    repo: str,
    base: str,
    head: str,
    baseline: Path,
    profile: str,
    dry_run: bool = False,
) -> int:
    command = [
        "agent-pr-evidence",
        "gate",
        "--repo",
        repo,
        "--base",
        base,
        "--head",
        head,
        "--profile",
        profile,
        "--baseline",
        str(baseline),
        "--format",
        "json",
    ]
    result = run_command(command, dry_run=dry_run)
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n")
    return result.returncode


def build_failure_packet(*, input_path: Path, output: Path, profile: str, dry_run: bool = False) -> int:
    validate = run_command(["agent-failure-packet", "validate", "--input", str(input_path)], dry_run=dry_run)
    print(validate.stdout, end="" if validate.stdout.endswith("\n") else "\n")
    if validate.stderr:
        print(validate.stderr, end="" if validate.stderr.endswith("\n") else "\n")
    if validate.returncode != 0:
        return validate.returncode

    build = run_command(
        [
            "agent-failure-packet",
            "build",
            "--input",
            str(input_path),
            "--profile",
            profile,
            "--output",
            str(output),
        ],
        dry_run=dry_run,
    )
    print(build.stdout, end="" if build.stdout.endswith("\n") else "\n")
    if build.stderr:
        print(build.stderr, end="" if build.stderr.endswith("\n") else "\n")
    return build.returncode


def collect_for_runbook(
    *,
    repo: str,
    base: str,
    head: str,
    test_logs: list[str],
    profile: str,
    dry_run: bool,
) -> tuple[int, dict | None, str]:
    command = [
        "agent-pr-evidence",
        "collect",
        "--repo",
        repo,
        "--base",
        base,
        "--head",
        head,
        "--profile",
        profile,
        "--format",
        "json",
    ]
    for test_log in test_logs:
        command.extend(["--test-log", test_log])
    if dry_run:
        result = run_command(command, dry_run=True)
        return result.returncode, None, result.stdout
    with tempfile.TemporaryDirectory(prefix="xone-runbook-") as tmp:
        output = Path(tmp) / "evidence.json"
        result = run_command([*command, "--output", str(output)])
        if result.returncode != 0:
            return result.returncode, None, result.stderr or result.stdout
        return 0, json.loads(output.read_text(encoding="utf-8")), ""

