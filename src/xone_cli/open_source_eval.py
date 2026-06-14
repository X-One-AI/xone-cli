from __future__ import annotations

import json
import subprocess
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from xone_cli.evidence import collect_for_runbook
from xone_cli.tooling import doctor_status


BATCH_SCHEMA_VERSION = "xone.open_source_evaluation_batch.v1"
RECORD_SCHEMA_VERSION = "xone.open_source_evaluation.v1"


@dataclass(frozen=True)
class EvalRecord:
    source: str
    source_url: str
    snapshot_date: str
    stars: int
    forks: int
    open_issues: int
    default_branch: str
    language: str | None
    commands_run: list[dict]
    sanitization: dict
    decision: str

    def to_dict(self) -> dict:
        return {
            "schema_version": RECORD_SCHEMA_VERSION,
            "source": self.source,
            "source_url": self.source_url,
            "snapshot_date": self.snapshot_date,
            "stars": self.stars,
            "forks": self.forks,
            "open_issues": self.open_issues,
            "default_branch": self.default_branch,
            "language": self.language,
            "categories": [],
            "xone_tools_used": ["xone-cli"],
            "commands_run": self.commands_run,
            "role_findings": [],
            "sanitization": self.sanitization,
            "decision": self.decision,
        }


def evaluate_open_source(
    *,
    repos_file: Path,
    output: Path,
    output_format: str,
    clone_root: Path | None = None,
    snapshot_date: date | None = None,
) -> int:
    snapshot = snapshot_date or date.today()
    sources = read_repo_refs(repos_file)
    records = []
    for source in sources:
        metadata = fetch_github_metadata(source, snapshot)
        commands = [
            {
                "name": "doctor-json",
                "command": "xone doctor --json",
                "mode": "read-only",
                "result": "pass" if doctor_status().ok else "needs-install",
            }
        ]
        if clone_root is None:
            commands.append(
                {
                    "name": "runbook-dry-run",
                    "command": "xone runbook --repo <local-clone> --head HEAD --dry-run",
                    "mode": "read-only",
                    "result": "skipped",
                    "reason": "clone-root not provided",
                }
            )
        else:
            try:
                local_repo = clone_repo(metadata, clone_root)
            except Exception as exc:
                commands.append(
                    {
                        "name": "shallow-clone",
                        "command": f"git clone --depth 1 {metadata['source_url']} <clone-root>",
                        "mode": "read-only",
                        "result": "fail",
                        "output_summary": str(exc),
                    }
                )
            else:
                code, _report, message = collect_for_runbook(
                    repo=str(local_repo),
                    base=None,
                    head="HEAD",
                    test_logs=[],
                    profile="strict",
                    dry_run=True,
                )
                commands.append(
                    {
                        "name": "runbook-dry-run",
                        "command": "xone runbook --repo <local-clone> --head HEAD --dry-run",
                        "mode": "read-only",
                        "result": "pass" if code == 0 else "fail",
                        "output_summary": message.strip(),
                    }
                )
        records.append(_record_from_metadata(metadata, commands).to_dict())

    batch = {
        "schema_version": BATCH_SCHEMA_VERSION,
        "snapshot_date": snapshot.isoformat(),
        "records": records,
    }
    if output_format == "json":
        output.write_text(json.dumps(batch, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        output.write_text(render_markdown(batch), encoding="utf-8")
    print(f"Wrote {len(records)} open-source evaluation records to {output}")
    return 0


def read_repo_refs(path: Path) -> list[str]:
    refs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        refs.append(normalize_repo_ref(value))
    return refs


def normalize_repo_ref(value: str) -> str:
    parsed = urlparse(value)
    if parsed.netloc == "github.com":
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1].removesuffix('.git')}"
    return value.removesuffix(".git")


def fetch_github_metadata(repo: str, snapshot_date: date) -> dict:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "xone-cli-open-source-eval"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.load(response)
    return {
        "source": payload["full_name"],
        "source_url": payload["html_url"],
        "snapshot_date": snapshot_date.isoformat(),
        "stars": payload["stargazers_count"],
        "forks": payload["forks_count"],
        "open_issues": payload["open_issues_count"],
        "default_branch": payload["default_branch"],
        "language": payload.get("language"),
    }


def clone_repo(record: dict, root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    target = root / record["source"].replace("/", "-")
    if (target / ".git").exists():
        return target
    subprocess.run(
        ["git", "clone", "--depth", "1", record["source_url"], str(target)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return target


def render_markdown(batch: dict) -> str:
    lines = [
        "# X-One Open-Source Adoption Evaluation",
        "",
        f"Snapshot date: {batch['snapshot_date']}",
        "",
        "| Source | Stars | Forks | Issues | Default Branch | Decision |",
        "|---|---:|---:|---:|---|---|",
    ]
    for record in batch["records"]:
        lines.append(
            f"| {record['source']} | {record['stars']} | {record['forks']} | "
            f"{record['open_issues']} | {record['default_branch']} | {record['decision']} |"
        )
    lines.extend(["", "## Command Evidence", ""])
    for record in batch["records"]:
        lines.append(f"### {record['source']}")
        for command in record["commands_run"]:
            lines.append(f"- {command.get('name', command['command'])}: {command['result']}")
            lines.append(f"  - command: `{command['command']}`")
            if command.get("output_summary"):
                lines.append(f"  - summary: `{command['output_summary']}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _record_from_metadata(metadata: dict, commands: list[dict]) -> EvalRecord:
    return EvalRecord(
        source=metadata["source"],
        source_url=metadata["source_url"],
        snapshot_date=metadata["snapshot_date"],
        stars=metadata["stars"],
        forks=metadata["forks"],
        open_issues=metadata["open_issues"],
        default_branch=metadata["default_branch"],
        language=metadata.get("language"),
        commands_run=commands,
        sanitization={
            "raw_logs_committed": False,
            "secrets_removed": True,
            "third_party_safety_label_used": False,
        },
        decision="defer-with-reason",
    )
