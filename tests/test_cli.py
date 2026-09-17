import json
import subprocess
import sys

import pytest

from energy_surplus.cli import main
from energy_surplus.config import ProjectConfig, load_config
from energy_surplus.manifest import RunManifest, create_manifest, digest, write_manifest


def test_validation_cli(root, capsys):
    assert main(["validate-config", "--config", str(root / "configs/poc.toml")]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["status"] == "valid"
    assert json.loads(captured.err)["event"] == "configuration_validated"


@pytest.mark.parametrize("content", ["[broken", 'schema_version = "unsupported"'])
def test_bad_config_returns_error_without_manifest(tmp_path, capsys, content):
    path = tmp_path / "bad.toml"
    path.write_text(content)
    output = tmp_path / "runs"
    assert main(["init-run", "--config", str(path), "--output-dir", str(output)]) == 2
    captured = capsys.readouterr()
    assert not captured.out
    assert json.loads(captured.err)["level"] == "ERROR"
    assert not output.exists()


def test_missing_config_is_controlled_error(tmp_path, capsys):
    assert main(["validate-config", "--config", str(tmp_path / "missing")]) == 2
    assert json.loads(capsys.readouterr().err)["details"]["error_type"] == "FileNotFoundError"


def test_validation_does_not_log_raw_values(tmp_path, capsys):
    path = tmp_path / "bad.toml"
    path.write_text('secret = "do-not-log-me"')
    assert main(["validate-config", "--config", str(path)]) == 2
    assert "do-not-log-me" not in capsys.readouterr().err


@pytest.mark.parametrize("kind", ["config", "manifest"])
def test_schema_export(kind, capsys):
    assert main(["schema", kind]) == 0
    schema = json.loads(capsys.readouterr().out)
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False


def test_run_manifest_roundtrip_and_provenance(root, tmp_path, capsys):
    args = [
        "init-run",
        "--config",
        str(root / "configs/poc.toml"),
        "--project-root",
        str(root),
        "--output-dir",
        str(tmp_path),
    ]
    assert main(args) == 0
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    manifest = RunManifest.model_validate_json(
        (tmp_path / result["run_id"] / "manifest.json").read_text()
    )
    assert json.loads(captured.err)["run_id"] == result["run_id"]
    assert manifest.environment_lock_sha256 == digest((root / "poetry.lock").read_bytes())
    assert manifest.config_sha256 == digest(manifest.config_snapshot.model_dump_json().encode())
    assert manifest.model is None and manifest.calibration is None and manifest.data == []
    assert manifest.issue_time is None
    assert manifest.created_at.utcoffset().total_seconds() == 0
    assert manifest.risk_policy_version == manifest.config_snapshot.risk.policy_version
    with pytest.raises(FileExistsError):
        write_manifest(manifest, tmp_path)
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)["run_id"] != result["run_id"]


def test_source_and_config_changes_affect_hashes(root, tmp_path, config_dict):
    (tmp_path / "poetry.lock").write_bytes((root / "poetry.lock").read_bytes())
    (tmp_path / "pyproject.toml").write_bytes((root / "pyproject.toml").read_bytes())
    source = tmp_path / "src/energy_surplus/__init__.py"
    source.parent.mkdir(parents=True)
    source.write_text('"""v1"""')
    config = ProjectConfig.model_validate(config_dict)
    before = create_manifest(config, tmp_path)
    source.write_text('"""v2"""')
    config_dict["risk"]["policy_version"] = "changed"
    after = create_manifest(ProjectConfig.model_validate(config_dict), tmp_path)
    assert before.code.source_sha256 != after.code.source_sha256
    assert before.config_sha256 != after.config_sha256
    assert before.code.git_commit is None and before.code.git_dirty is None


def test_missing_lock_is_not_fabricated(root, tmp_path):
    with pytest.raises(FileNotFoundError):
        create_manifest(load_config(root / "configs/poc.toml"), tmp_path)


def test_module_entrypoint_outside_repository(root, tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "energy_surplus",
            "validate-config",
            "--config",
            str(root / "configs/poc.toml"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)["status"] == "valid"
