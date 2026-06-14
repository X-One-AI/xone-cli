import json

from xone_cli.cli import main


def test_version_outputs_package_version(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == "xone 0.1.0"


def test_doctor_json_has_schema(capsys):
    assert main(["doctor", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "xone.doctor.v1"


def test_runbook_dry_run_is_available(capsys):
    assert main(["runbook", "--dry-run"]) == 0
    assert "xone runbook" in capsys.readouterr().out

