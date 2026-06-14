from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    dry_run: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ToolStatus:
    name: str
    executable: str | None
    available: bool
    version: str | None
    install_hint: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DoctorReport:
    schema_version: str
    tools: list[ToolStatus]

    @property
    def ok(self) -> bool:
        return all(tool.available for tool in self.tools)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["ok"] = self.ok
        return data

