"""Checksummed provenance for configuration-only runs and future artifacts."""

import hashlib
import subprocess
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import AwareDatetime, Field

from energy_surplus.config import Name, ProjectConfig, Schema

Sha256 = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]


class ArtifactRef(Schema):
    path: Name
    version: Name
    sha256: Sha256


class CodeRef(Schema):
    package_version: Name
    git_commit: str | None
    git_dirty: bool | None
    source_sha256: Sha256


class RunManifest(Schema):
    schema_version: Literal["1"] = "1"
    run_id: UUID
    created_at: AwareDatetime
    status: Literal["configuration_validated"] = "configuration_validated"
    config_sha256: Sha256
    config_snapshot: ProjectConfig
    environment_lock_sha256: Sha256
    code: CodeRef
    feature_schema_version: Name
    risk_policy_version: Name
    commercial_policy_version: Name
    data: list[ArtifactRef] = Field(default_factory=list)
    model: ArtifactRef | None = None
    calibration: ArtifactRef | None = None
    # Phase 0 does not issue a forecast or consume a data availability snapshot.
    issue_time: AwareDatetime | None = None
    input_availability_cutoff: AwareDatetime | None = None


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def git_value(root: Path, *args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def create_manifest(config: ProjectConfig, project_root: Path) -> RunManifest:
    """Require local project/lock evidence; never invent a revision for missing artifacts."""
    lock = (project_root / "poetry.lock").read_bytes()
    paths = [project_root / "pyproject.toml"]
    sources = sorted((project_root / "src" / "energy_surplus").rglob("*.py"))
    if not sources:
        raise ValueError("project root must contain src/energy_surplus Python sources")
    paths.extend(sources)
    source_hash = hashlib.sha256()
    for path in paths:
        source_hash.update(path.relative_to(project_root).as_posix().encode() + b"\0")
        source_hash.update(path.read_bytes() + b"\0")
    git_status = git_value(project_root, "status", "--porcelain", "--untracked-files=all")
    return RunManifest(
        run_id=uuid4(),
        created_at=datetime.now(UTC),
        config_sha256=digest(config.model_dump_json().encode()),
        config_snapshot=config,
        environment_lock_sha256=digest(lock),
        code=CodeRef(
            package_version=version("energy-surplus"),
            git_commit=git_value(project_root, "rev-parse", "HEAD"),
            git_dirty=None if git_status is None else bool(git_status),
            source_sha256=source_hash.hexdigest(),
        ),
        feature_schema_version=config.forecast.feature_schema_version,
        risk_policy_version=config.risk.policy_version,
        commercial_policy_version=config.commercial.policy_version,
    )


def write_manifest(manifest: RunManifest, output_dir: Path) -> Path:
    """A unique run directory prevents overwriting a previous audit record."""
    run_dir = output_dir / str(manifest.run_id)
    run_dir.mkdir(parents=True, exist_ok=False)
    path = run_dir / "manifest.json"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(manifest.model_dump_json(indent=2) + "\n")
    return path
