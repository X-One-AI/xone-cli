from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from xone_cli.tooling import run_command

RELEASE_VERIFY_SCHEMA_VERSION = "xone.release.verify.v1"

REQUIRED_RELEASE_FILES = (
    "pyproject.toml",
    "README.md",
    "README.zh-CN.md",
    "CHANGELOG.md",
    "LICENSE",
    ".github/workflows/ci.yml",
    ".github/workflows/publish.yml",
)


def required_files_status(project_root: Path) -> dict[str, bool]:
    return {name: (project_root / name).exists() for name in REQUIRED_RELEASE_FILES}


def verify_release(
    *,
    project_root: Path,
    build: bool,
    install: bool,
    smoke: bool,
) -> dict:
    project_root = project_root.resolve()
    required_files = required_files_status(project_root)
    checks: list[dict] = []
    release_env = _release_subprocess_env()
    smoke_commands: list[list[str]] = [
        ["python", "-m", "xone_cli", "--version"],
        ["python", "-m", "xone_cli", "doctor", "--json"],
    ]

    if build:
        result = run_command(["python", "-m", "build"], dry_run=False, cwd=project_root, env=release_env)
        checks.append(_check("build", result.returncode, result.stdout, result.stderr))

    if install:
        with tempfile.TemporaryDirectory(prefix="xone-release-venv-") as tmp:
            venv_dir = Path(tmp) / "venv"
            venv = run_command(["python", "-m", "venv", str(venv_dir)])
            checks.append(_check("venv", venv.returncode, venv.stdout, venv.stderr))
            if venv.returncode == 0:
                wheel = _latest_wheel(project_root)
                if wheel:
                    pip = venv_dir / "bin" / "pip"
                    installed = run_command([str(pip), "install", str(wheel)], env=release_env)
                    checks.append(_check("wheel-install", installed.returncode, installed.stdout, installed.stderr))
                    xone = venv_dir / "bin" / "xone"
                    smoke_commands = [
                        [str(xone), "--version"],
                        [str(xone), "doctor", "--json"],
                    ]
                else:
                    checks.append({"name": "wheel-install", "returncode": 1, "stdout": "", "stderr": "No wheel found in dist/"})

            if smoke:
                for name, command in (("cli-version", smoke_commands[0]), ("doctor-json", smoke_commands[1])):
                    result = run_command(command, cwd=project_root, env=release_env)
                    checks.append(_check(name, result.returncode, result.stdout, result.stderr))
    elif smoke:
        for name, command in (("cli-version", smoke_commands[0]), ("doctor-json", smoke_commands[1])):
            result = run_command(command, cwd=project_root, env=release_env)
            checks.append(_check(name, result.returncode, result.stdout, result.stderr))

    ok = all(required_files.values()) and all(check["returncode"] == 0 for check in checks)
    return {
        "schema_version": RELEASE_VERIFY_SCHEMA_VERSION,
        "ok": ok,
        "required_files": required_files,
        "checks": checks,
    }


def print_release_report(report: dict, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    print("X-One release verification")
    print(f"ok: {str(report['ok']).lower()}")
    print("required files:")
    for name, exists in report["required_files"].items():
        print(f"- {name}: {'ok' if exists else 'missing'}")
    if report["checks"]:
        print("checks:")
        for check in report["checks"]:
            print(f"- {check['name']}: {'ok' if check['returncode'] == 0 else 'failed'}")


def _check(name: str, returncode: int, stdout: str, stderr: str) -> dict:
    return {"name": name, "returncode": returncode, "stdout": stdout[-2000:], "stderr": stderr[-2000:]}


def _latest_wheel(project_root: Path) -> Path | None:
    wheels = sorted((project_root / "dist").glob("*.whl"), key=lambda path: path.stat().st_mtime, reverse=True)
    return wheels[0] if wheels else None


def _release_subprocess_env() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    return env
