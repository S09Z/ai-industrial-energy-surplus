# AI Energy Surplus & Capacity Optimization

**Core question:** How much energy can the industrial estate allocate, avoid purchasing, or potentially monetize tomorrow under an explicit reliability policy?

Phase 0 provides an installable Python package, strict configuration validation, run manifests, and local/CI checks. Forecasting, datasets, optimization, and the dashboard are not implemented yet; no measured model or financial results are claimed.

- [PoC specification](docs/poc-specification.md): data, ML, uncertainty, optimization, architecture, and acceptance criteria.
- [Management brief](docs/management-brief.md): business case, decision request, demonstration, and executive FAQ.
- [Implementation plan](PLAN.md): milestones and evidence required to complete each one.
- [Development guide](docs/development.md): environment setup, CLI commands, tests, and CI.
- [Decisions](docs/decisions.md): scope, operating assumptions, and foundation design choices.

Poetry uses the workspace `.venv` through the committed `poetry.toml`. Requires Python 3.12 and Poetry 2.2.1.

```sh
poetry sync --with dev
poetry run energy-surplus validate-config --config configs/poc.toml
poetry run energy-surplus init-run --config configs/poc.toml
poetry run pytest
```

Recommended first release: 20–50 proxy customers, hourly next-day forecasts, calibrated uncertainty, procurement and internal capacity recommendations, historical financial simulation, and a human approval dashboard. External sale is disabled by default. Battery optimization is a separately gated extension.

Real consumption data will come from [Building Data Genome 2](https://github.com/buds-lab/building-data-genome-project-2); these buildings are proxies, not evidence of performance on industrial factories. Supply, contracts, tariffs, network limits, and operating policies will initially be explicit simulation inputs.

All targets and financial examples in these documents are proposals or illustrations, not achieved results. The scope is decision support; there is no direct electrical equipment control.
