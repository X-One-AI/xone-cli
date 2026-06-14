from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse


def is_remote_repo_url(repo: str) -> bool:
    parsed = urlparse(repo)
    return parsed.scheme in {"http", "https", "ssh", "git"} or bool(re.match(r"^[^/@\s]+@[^:\s]+:.+", repo))


def validate_local_repo(repo: str) -> tuple[bool, str]:
    if is_remote_repo_url(repo):
        return (
            False,
            "Remote repository URLs are not supported by runbook yet. "
            f"Clone first, then pass the local path: git clone --depth 1 {repo}",
        )
    path = Path(repo)
    if not (path / ".git").exists():
        return False, f"{repo} is not a local git repository. Run xone runbook from a git repo or pass --repo /path/to/repo."
    return True, ""


def detect_default_base(repo: str) -> str:
    remote_default = _git_symbolic_ref(repo, "refs/remotes/origin/HEAD")
    if remote_default and remote_default.startswith("origin/"):
        return remote_default.removeprefix("origin/")
    local_default = _git_symbolic_ref(repo, "HEAD")
    if local_default:
        return local_default
    git_dir = Path(repo) / ".git"
    origin_head = _read_ref_name(git_dir / "refs" / "remotes" / "origin" / "HEAD", "refs/remotes/origin/")
    if origin_head:
        return origin_head
    local_head = _read_ref_name(git_dir / "HEAD", "refs/heads/")
    return local_head or "main"


def _git_symbolic_ref(repo: str, ref: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", repo, "symbolic-ref", "--quiet", "--short", ref],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _read_ref_name(path: Path, prefix: str) -> str | None:
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8").strip()
    if not content.startswith("ref: "):
        return None
    ref = content.removeprefix("ref: ").strip()
    if ref.startswith(prefix):
        return ref.removeprefix(prefix)
    return None
