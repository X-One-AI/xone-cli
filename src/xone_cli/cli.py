from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections.abc import Sequence

from xone_cli import __version__
from xone_cli.evidence import build_failure_packet, collect_evidence, collect_for_runbook, gate_evidence
from xone_cli.lab import render_evidence_loop_lab
from xone_cli.risk import render_risk_context
from xone_cli.runbook import write_runbook
from xone_cli.release import print_release_report, verify_release
from xone_cli.tooling import doctor_status, install_plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="xone")
    parser.add_argument("--version", action="store_true", help="show version and exit")
    subparsers = parser.add_subparsers(dest="command")

    doctor = subparsers.add_parser("doctor", help="check local X-One tool availability")
    doctor.add_argument("--json", action="store_true", help="write machine-readable status")
    doctor.add_argument("--dry-run", action="store_true", help="show checks without running them")
    doctor.add_argument(
        "--install-plan",
        nargs="?",
        const="all",
        choices=("all", "evidence-loop", "mcp-review", "incident-lab"),
        help="show scenario-based install commands",
    )

    evidence = subparsers.add_parser("evidence", help="work with PR evidence and failure packets")
    evidence_subparsers = evidence.add_subparsers(dest="evidence_command")
    collect = evidence_subparsers.add_parser("collect", help="collect PR evidence")
    _add_evidence_collection_args(collect)
    collect.add_argument("--output", type=Path, required=True, help="JSON evidence output path")
    collect.add_argument("--dry-run", action="store_true")

    gate = evidence_subparsers.add_parser("gate", help="run baseline gate")
    _add_evidence_collection_args(gate)
    gate.add_argument("--baseline", type=Path, required=True)
    gate.add_argument("--dry-run", action="store_true")

    packet = evidence_subparsers.add_parser("packet", help="build a redacted failure packet")
    packet.add_argument("--input", type=Path, required=True)
    packet.add_argument("--output", type=Path, required=True)
    packet.add_argument("--profile", choices=("incident", "issue"), default="issue")
    packet.add_argument("--dry-run", action="store_true")

    risk = subparsers.add_parser("risk", help="work with MCP risk context")
    risk_subparsers = risk.add_subparsers(dest="risk_command")
    context = risk_subparsers.add_parser("context", help="render risk context")
    context.add_argument("--catalog", type=Path, required=True)
    context.add_argument("--output", type=Path, required=True)
    context.add_argument("--dry-run", action="store_true")

    lab = subparsers.add_parser("lab", help="work with safe-local lab scenarios")
    lab_subparsers = lab.add_subparsers(dest="lab_command")
    evidence_loop = lab_subparsers.add_parser("evidence-loop", help="render Agent Evidence Loop scenario")
    evidence_loop.add_argument("--output", type=Path, required=True)
    evidence_loop.add_argument("--dry-run", action="store_true")

    release = subparsers.add_parser("release", help="verify local release readiness")
    release_subparsers = release.add_subparsers(dest="release_command")
    verify = release_subparsers.add_parser("verify", help="run release/package checks")
    verify.add_argument("--project-root", type=Path, default=Path("."))
    verify.add_argument("--build", action="store_true")
    verify.add_argument("--install", action="store_true")
    verify.add_argument("--smoke", action="store_true")
    verify.add_argument("--json", action="store_true")

    runbook = subparsers.add_parser("runbook", help="assemble a local X-One evidence runbook")
    _add_evidence_collection_args(runbook, require_base=False)
    runbook.add_argument("--output", type=Path)
    runbook.add_argument("--dry-run", action="store_true", help="show underlying commands without running them")
    runbook.add_argument("--json", action="store_true", help="write machine-readable summary")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"xone {__version__}")
        return 0

    if args.command == "doctor":
        if args.install_plan:
            _print_install_plan(args.install_plan)
            return 0
        report = doctor_status()
        payload = report.to_dict()
        payload["dry_run"] = args.dry_run
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_doctor(report)
        return 0

    if args.command == "evidence":
        if args.evidence_command == "collect":
            return collect_evidence(
                repo=args.repo,
                base=args.base,
                head=args.head,
                output=args.output,
                test_logs=args.test_log,
                profile=args.profile,
                dry_run=args.dry_run,
            )
        if args.evidence_command == "gate":
            return gate_evidence(
                repo=args.repo,
                base=args.base,
                head=args.head,
                baseline=args.baseline,
                profile=args.profile,
                dry_run=args.dry_run,
            )
        if args.evidence_command == "packet":
            return build_failure_packet(
                input_path=args.input,
                output=args.output,
                profile=args.profile,
                dry_run=args.dry_run,
            )

    if args.command == "risk" and args.risk_command == "context":
        return render_risk_context(catalog=args.catalog, output=args.output, dry_run=args.dry_run)

    if args.command == "lab" and args.lab_command == "evidence-loop":
        return render_evidence_loop_lab(output=args.output, dry_run=args.dry_run)

    if args.command == "release" and args.release_command == "verify":
        report = verify_release(
            project_root=args.project_root,
            build=args.build,
            install=args.install,
            smoke=args.smoke,
        )
        print_release_report(report, as_json=args.json)
        return 0 if report["ok"] else 1

    if args.command == "runbook":
        code, report, message = collect_for_runbook(
            repo=args.repo,
            base=args.base,
            head=args.head,
            test_logs=args.test_log,
            profile=args.profile,
            dry_run=args.dry_run,
        )
        if code != 0:
            print(message)
            return code
        if args.dry_run:
            print(message)
            return 0
        payload = {
            "schema_version": "xone.runbook.v1",
            "handoff_decision": (report or {}).get("handoff_decision"),
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        if args.output and report is not None:
            write_runbook(report, args.output)
        elif report is not None:
            print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    parser.print_help(sys.stderr)
    return 2


def entrypoint() -> None:
    raise SystemExit(main())


def _print_doctor(report) -> None:
    print("X-One toolchain")
    for tool in report.tools:
        status = "ok" if tool.available else "missing"
        print(f"- {tool.name}: {status}")
        if tool.version:
            print(f"  version: {tool.version}")
        if not tool.available:
            print(f"  install: {tool.install_hint}")


def _print_install_plan(profile: str) -> None:
    print("X-One install plan")
    for item in install_plan(profile):
        print(f"- {item['name']}: {item['command']}")
        print(f"  when: {item['when']}")
        print(f"  next: {item['next']}")


def _add_evidence_collection_args(parser: argparse.ArgumentParser, *, require_base: bool = True) -> None:
    parser.add_argument("--repo", default=".", help="git repository path")
    parser.add_argument("--base", required=require_base, help="base git ref; runbook can auto-detect when omitted")
    parser.add_argument("--head", required=True, help="head git ref")
    parser.add_argument("--test-log", action="append", default=[], help="test log path; repeatable")
    parser.add_argument("--profile", choices=("default", "strict"), default="strict")
