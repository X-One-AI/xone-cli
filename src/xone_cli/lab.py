from __future__ import annotations

import tempfile
from pathlib import Path

from xone_cli.tooling import run_command


def render_evidence_loop_lab(*, output: Path, dry_run: bool = False) -> int:
    with tempfile.TemporaryDirectory(prefix="xone-lab-") as tmp:
        scenario_dir = Path(tmp) / "scenarios"
        init = run_command(["ai-incident-lab", "init", "--output", str(scenario_dir)], dry_run=dry_run)
        print(init.stdout, end="" if init.stdout.endswith("\n") else "\n")
        if init.stderr:
            print(init.stderr, end="" if init.stderr.endswith("\n") else "\n")
        if init.returncode != 0:
            return init.returncode

        scenario = scenario_dir / "agent-evidence-loop.yml"
        validate = run_command(["ai-incident-lab", "validate", "--scenarios", str(scenario_dir)], dry_run=dry_run)
        print(validate.stdout, end="" if validate.stdout.endswith("\n") else "\n")
        if validate.stderr:
            print(validate.stderr, end="" if validate.stderr.endswith("\n") else "\n")
        if validate.returncode != 0:
            return validate.returncode

        render = run_command(
            ["ai-incident-lab", "render", "--scenarios", str(scenario), "--format", "markdown"],
            dry_run=dry_run,
        )
        if render.returncode == 0 and not dry_run:
            output.write_text(render.stdout, encoding="utf-8")
        else:
            print(render.stdout, end="" if render.stdout.endswith("\n") else "\n")
        if render.stderr:
            print(render.stderr, end="" if render.stderr.endswith("\n") else "\n")
        return render.returncode

