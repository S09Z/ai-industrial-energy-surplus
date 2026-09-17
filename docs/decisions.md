# Phase 0 decisions and operating assumptions

Status: implemented foundation, not an approved operating policy. The sample configuration is a simulation fixture and makes no production reliability or economic claim.

| Decision | Rationale and boundary |
|---|---|
| Daily issue cutoff at 12:00 estate local time | Plan tomorrow's local calendar day using only inputs available at issue time. Delivery is hourly; lead times are roughly 12–36 hours. Cutoff is configurable. |
| UTC storage with a named local timezone | Calendar features and business reporting use the source site's local clock. The sample uses Asia/Bangkok only as a demonstration clock; BDG2 timezone must be resolved from selected site metadata in Phase 1. Never relabel foreign observations as Thai measurements. |
| Local calendar day, not always 24 elapsed hours | The Thai demonstration has 24 hours. Sites observing daylight saving may have 23/25 intervals; Phase 2 must handle this explicitly rather than discard or duplicate energy. |
| BDG2 electricity, initially 20 proxy customers | Select using development-only completeness of at least 95%, preferably one coherent site. Buildings are proxies for factories; no meter IDs have been selected or data downloaded yet. |
| Development through June 2017; calibration July–September; holdout October–December | Boundaries are half-open dates in source-local calendar. Final holdout labels remain untouched during development. Selection and fitted preprocessing must never use holdout outcomes. |
| Explicit energy and power units | Meter intervals use kWh; power limits use MW; future cost ledgers use MWh and THB/MWh. Configuration rejects missing/wrong units rather than guessing conversion. |
| Separate physical energy and capacity entitlement | Sample supply is 40 MW deliverable generation plus 60 MW committed grid import. The 80 MW grid import limit is a ceiling, not an extra source. The 100 MW transformer limit refers to the grid interface, not total estate generation. All are synthetic. |
| Risk P90 and 3 MW reserve are illustrative | P90 is a marginal demand quantile, not a daily reliability guarantee. Excess reserve may create a valid shortage scenario; it is not rejected as a malformed configuration. Later risk/optimizer stages expose it. |
| Exports and execution disabled | Phase 0 cannot configure an export or execution permission. Internal reassignment is unknown/prohibited until effective-dated eligibility is implemented. A later schema revision must introduce reviewed eligibility rather than casually flip a boolean. |
| Scenario definitions are inputs, not executed simulations | Normal, shutdown, production surge, and supply reduction are typed. Factory IDs are placeholders pending Phase 1 mapping. Hot-day is disabled because the initial forecast uses no issue-time weather. |
| Python 3.12, TOML, Pydantic, Poetry | TOML avoids an additional parser dependency. Strict validation rejects typo fields and numeric strings. A committed Poetry lock records exact dependency versions/hashes; the committed `poetry.toml` creates/reuses the workspace `.venv`. Current runtime scope is configuration and provenance only. |
| Baseline plus pooled LightGBM planned | Seasonal Naive establishes the benchmark; boosting is the first nonlinear challenger. ML dependencies are added when those phases begin, not installed speculatively. |
| CLI before services | Small offline commands establish reproducibility without Kafka, Kubernetes, databases, or an external LLM. FastAPI/dashboard remain later work. |
| UUID per run and checksummed manifest | A validation run snapshots typed config, source digest, lock digest, package/Git versions and policy versions. Data/model/calibration references remain explicitly absent until those artifacts exist. |
| No direct equipment or trade integration | This foundation has no execution interfaces. Later recommendations require human approval and separate operating authorization. |

The manifest's config hash covers the normalized JSON snapshot, not TOML comments/formatting. Its source hash covers relative paths and bytes of `pyproject.toml` and package Python files; lock and config have separate hashes. Git dirty status records uncommitted work. Outside Git, commit and dirty status are null rather than invented. These identifiers support traceability, not artifact storage or cryptographic signing; retain source and artifacts for reproducibility.

Dependencies use the [Pydantic model/validation API](https://docs.pydantic.dev/latest/concepts/models/) and [Poetry environment configuration](https://python-poetry.org/docs/configuration/#virtualenvsin-project). Phase 0 validates configuration structure and consistency; it cannot validate a physical grid, an actual dataset, or contractual permission.
