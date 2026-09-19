"""Configuration validation and provenance bootstrap; no forecasting or execution."""

import argparse
import json
import tomllib
from pathlib import Path

from pydantic import ValidationError

from energy_surplus.config import ProjectConfig, load_config
from energy_surplus.logging import configure_logging
from energy_surplus.manifest import RunManifest, create_manifest, write_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="energy-surplus")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate-config", "init-run"):
        command = commands.add_parser(name)
        command.add_argument("--config", type=Path, required=True)
        if name == "init-run":
            command.add_argument("--project-root", type=Path, default=Path.cwd())
            command.add_argument("--output-dir", type=Path, default=Path("runs"))
    schema = commands.add_parser("schema")
    schema.add_argument("kind", choices=("config", "manifest"))
    args = parser.parse_args(argv)
    logger = configure_logging()
    try:
        if args.command == "schema":
            model = ProjectConfig if args.kind == "config" else RunManifest
            print(json.dumps(model.model_json_schema(), indent=2))
            return 0
        config = load_config(args.config)
        if args.command == "validate-config":
            print(json.dumps({"status": "valid", "schema_version": config.schema_version}))
            logger.info("configuration_validated")
        else:
            manifest = create_manifest(config, args.project_root.resolve())
            path = write_manifest(manifest, args.output_dir)
            print(json.dumps({"run_id": str(manifest.run_id), "manifest": str(path.resolve())}))
            logger.info("run_initialized", extra={"run_id": str(manifest.run_id)})
        return 0
    except ValidationError as exc:
        # Avoid reflecting raw input values (potentially credentials) in logs.
        details = [
            {"location": list(error["loc"]), "message": error["msg"]}
            for error in exc.errors(include_input=False, include_url=False)
        ]
        logger.error("validation_failed", extra={"details": details})
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        logger.error("command_failed", extra={"details": {"error_type": type(exc).__name__}})
    return 2
