# Local development

Prerequisites: Python 3.12 and Poetry 2.2.1 (also pinned in CI). Run the following from the repository root. No GPU, database, dataset, cloud account, or credentials are required for Phase 0.

```sh
poetry check --lock --strict
poetry sync --with dev
poetry run energy-surplus validate-config --config configs/poc.toml
poetry run energy-surplus init-run --config configs/poc.toml
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
poetry build
```

`validate-config` reads and validates without writing artifacts. `init-run` performs the same validation, then writes `runs/<uuid>/manifest.json`. This is a configuration validation run, not a forecast. It requires `poetry.lock`, `pyproject.toml`, and Python package sources at `--project-root` (default: current directory). Use `--output-dir` to choose an artifact location. Running it twice creates separate run IDs; writing over an existing run is rejected.

Command results are JSON on stdout and structured JSON-line logs are on stderr. Exit code 0 means success; 2 means invalid command/input or an I/O failure. Validation errors identify field locations without reflecting raw values. Non-validation failures report an error type; inspect file paths and permissions if a command cannot read or write.

Export the schemas from the implemented types rather than maintain separate hand-written copies:

```sh
poetry run energy-surplus schema config
poetry run energy-surplus schema manifest
python -m energy_surplus --help
```

The last command assumes the environment is activated; otherwise use `poetry run python -m energy_surplus --help`. The installed console entry point also works outside the checkout when passed an absolute config path. `init-run` additionally requires an explicit project root outside the checkout.

Configuration is strict TOML: date/time values use native TOML syntax, numeric values must not be quoted, and every power quantity has `value` and `unit = "MW"`. Unknown keys are errors. See `configs/poc.toml` and `docs/decisions.md` for sample scope and assumptions. Never put secrets into versioned configuration; future integrations must resolve credentials separately.

## Dependency changes and CI

Commit `pyproject.toml` and `poetry.lock` together. To intentionally update dependencies, edit/add the requirement, run `poetry lock`, then repeat synchronization, lint, tests, and packaging checks. `poetry check --lock --strict` fails if the lock is missing or stale; do not silently regenerate it in CI. The build backend is pinned separately in `pyproject.toml`.

GitLab CI uses Python 3.12, installs the pinned Poetry CLI, synchronizes the lock, runs lint/format/tests, validates the sample, initializes a manifest, and builds the distribution. It retains manifests and distributions as short-lived job artifacts. A remote GitLab runner is not required for local development; remote execution is a separate verification step once this repository is connected to GitLab.

## Workspace environment

The committed `poetry.toml` sets `virtualenvs.create = true` and `virtualenvs.in-project = true`, so the environment lives at `<repository>/.venv`. Poetry reuses an existing compatible `.venv`. Start in a shell without an unrelated virtual environment activated, since Poetry respects an active environment. Environment variables can override local settings.

```sh
poetry env use python3.12
poetry env info --path
poetry run python -c "import sys; print(sys.executable)"
```

Both paths should point inside this repository's `.venv`. Configure your editor to use `.venv/bin/python` (Windows: `.venv/Scripts/python.exe`). `poetry run` does not require shell activation. Optional activation on macOS/Linux is `source .venv/bin/activate`.

For a fresh-install check, copy the project source, configuration, tests, `pyproject.toml`, `poetry.lock`, and `poetry.toml` to a temporary checkout without an environment, then run the setup/check commands there. Its environment should also be created at that checkout's `.venv`. Avoid maintaining alternate environment directories in the working project.

Generated data, models, run records, environments, caches, and common credential files are ignored by Git. Directory markers preserve the planned structure. Notebooks and later domain packages are intentionally empty until their implementation phase; there are no model results yet.
