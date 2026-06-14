from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from xone_cli import __version__
from xone_cli.tooling import doctor_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="xone")
    parser.add_argument("--version", action="store_true", help="show version and exit")
    subparsers = parser.add_subparsers(dest="command")

    doctor = subparsers.add_parser("doctor", help="check local X-One tool availability")
    doctor.add_argument("--json", action="store_true", help="write machine-readable status")
    doctor.add_argument("--dry-run", action="store_true", help="show checks without running them")

    runbook = subparsers.add_parser("runbook", help="assemble a local X-One evidence runbook")
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
        report = doctor_status()
        payload = report.to_dict()
        payload["dry_run"] = args.dry_run
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_doctor(report)
        return 0

    if args.command == "runbook":
        payload = {"schema_version": "xone.runbook.v1", "status": "not-implemented", "dry_run": args.dry_run}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print("xone runbook: not implemented")
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
