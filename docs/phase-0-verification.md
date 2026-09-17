# Phase 0 verification

Verified locally on 17 September 2026 using macOS arm64, CPython 3.12.13, and Poetry 2.2.1. This records foundation verification, not forecasting or financial performance.

| Requirement | Implemented evidence | Verification |
|---|---|---|
| P0.1 — Scope and operating assumptions | `docs/decisions.md`, `configs/poc.toml` | Cutoff, local/UTC clock rules, proxy customers, conservative commercial defaults, and no execution are explicit. DST and source-site timezone selection remain assigned to the data/forecast phases. |
| P0.2 — Package, structure, environment | `pyproject.toml`, `.python-version`, `poetry.lock`, `.gitignore`, package/domain directories | Fresh temporary-checkout installation into its own `.venv` succeeded. Source distribution and wheel built. Wheel installed as a regular package and successfully invoked from outside the checkout. Distribution contents exclude environments, cache, and run artifacts. |
| P0.3 — Typed configuration | `src/energy_surplus/config.py`, `configs/poc.toml` | Tests cover missing/wrong units, negative/nonfinite/nonnumeric values, import/transformer limits, disabled export/execution, quantiles, split order, timezone, and invalid scenarios. |
| P0.4 — CLI/logs/manifests | `cli.py`, `logging.py`, `manifest.py` | Sample validation and `init-run` passed. Tests verify stdout/stderr JSON, UUID correlation, exact config/lock hashes, source-change hashes, schema exports, empty data/model references, failure exits, and overwrite rejection. |
| P0.5 — Checks, CI, setup | `tests/`, `.gitlab-ci.yml`, `docs/development.md` | 40 tests passed in both working and fresh environments. Ruff check and format check passed. Git diff whitespace check passed. CI commands were exercised locally; no remote runner result is claimed. |

Commands exercised:

```sh
poetry check --lock --strict
poetry sync --with dev
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
poetry run energy-surplus validate-config --config configs/poc.toml
poetry run energy-surplus init-run --config configs/poc.toml
poetry build
git diff --check
```

Migration verification uses `poetry.lock` and the committed `poetry.toml` (`virtualenvs.in-project = true`). `poetry env info --path` resolves to the workspace `.venv`. A separate temporary checkout started without an environment; Poetry created its `.venv` and installed the locked dependencies. Both working and temporary environments passed all 40 tests. The sample CLI and manifest generation passed with the manifest hash checked against `poetry.lock`.

Source and wheel distributions were rebuilt with Poetry. The wheel was installed into the temporary environment and validated from outside the checkout. Both distribution archives were inspected for unwanted environments, caches, data, models, and run files. Remote GitLab execution remains unverified; its definition now uses Poetry 2.2.1 and checks lock consistency before synchronization.

Dependency downloads required network access. This demonstrates a clean environment install, not an air-gapped bootstrap. The previous dependency-manager lockfile has been removed; existing ignored caches and old run records are historical local artifacts, not inputs to the Poetry workflow.

No Phase 1 data has been acquired. Scenario definitions are validated but not executed. No model, forecast, optimizer, API server, dashboard, or live integration is included in Phase 0.
