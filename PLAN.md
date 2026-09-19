# Implementation Plan

Phase 0 is implemented and locally verified; the following milestones remain pending. Complete the acceptance evidence before marking one done. Estimate: 6–8 full-time-equivalent engineering weeks, conditional on public-data usability; real enterprise access and approvals are separate dependencies.

| Milestone | Indicative effort | Deliverable and completion evidence |
|---|---|---|
| M1 — Data readiness | Week 1 | Reproducible BDG2 download manifest, license/attribution, 20 selected electricity customers, units/timezone validation, quality report, frozen splits, synthetic-input register. Reject leakage in selection and preprocessing. |
| M2 — Forecast benchmark | Weeks 2–3 | Issue-time feature table, Seasonal Naive and pooled LightGBM, chronological folds, customer/estate metrics, peak report, saved models and run manifest. Availability assertions pass for every feature. |
| M3 — Uncertainty and surplus | Week 4 | Factory quantiles, separately calibrated estate quantiles, coverage/pinball/width report, signed shortages and safe envelope, policy comparison. Do not sum customer quantiles. |
| M4 — Decision and value | Week 5 | LP procurement model, eligible entitlement allocation, baseline/candidate actual-demand replay, net-cost ledger, hard-constraint checks, infeasibility behavior. Unknown export permission produces zero export. |
| M5 — Executive demo | Week 6 | FastAPI and dashboard, scenario suite, explanation waterfall, approval simulation, traceable KPI cards, management walkthrough. No direct execution integration. |
| M6 — Reproducibility and review | Weeks 7–8 buffer | Containerized run, CI, failure injection, runtime measurement, untouched holdout report and go/no-go decision. Optional coherent joint scenario work only if core gates are complete. |

## Phase 0 — Implementation status

### Phase 0 — Project foundation

**Dependency:** drafted specification. **Budget:** 2 days, within M1/M6.

- [x] P0.1 Record scope and assumptions in `docs/decisions.md`: next-day hourly delivery, issue-time cutoff, timezone, proxy customers, external export disabled, and no control integration.
- [x] P0.2 Create Python packaging and the directory structure below; add environment locking and ignore generated data, models, credentials, and local run artifacts.
- [x] P0.3 Define typed configuration for dataset selection, forecasting, supply, risk, commercial eligibility, and scenarios; reject missing units or inconsistent limits.
- [x] P0.4 Add a CLI entry point, structured logging, run IDs, and a run-manifest schema covering data, code, model, calibration, and policy versions.
- [x] P0.5 Establish linting, focused test execution, and a minimal GitLab CI pipeline; document local setup.

**Deliverables:** installable project skeleton, configuration schema, development instructions, initial CI.

**Exit gate:** a clean environment can install the package, validate a sample configuration, and run the initial checks. No model or performance claims are required.

**Evidence:** [Phase 0 verification](docs/phase-0-verification.md). Clean locked installation, 40 passing tests, Ruff lint/format checks, sample validation and manifest creation, source/wheel builds, and installed-wheel execution outside the checkout passed locally. GitLab runner execution remains unverified; the CI definition and equivalent local commands are provided.

## Proposed implementation layout

Phase 0 creates this directory structure. Future domain packages contain only package markers; notebooks and runtime data/model directories contain directory markers until their phases begin.

```text
notebooks/               # learning narrative; imports reusable src code
src/energy_surplus/
  data/                  # validation, snapshots, provenance
  features/              # issue-time availability and transformations
  forecasting/           # baseline, pooled model, quantiles, calibration
  risk/                  # supply headroom, shortages, scenarios
  optimization/          # procurement and entitlement constraints
  evaluation/            # rolling backtests and financial replay
  api/                   # typed read and approval endpoints
  dashboard/             # control tower
tests/                   # units, leakage, balances, failures, integration
configs/                 # versioned data/model/policy/scenario settings
data/{raw,interim,processed}/ # generated, excluded from Git
models/                  # generated artifacts, excluded from Git
docs/                    # design, model/data cards, runbook, results
infra/                   # Docker and deployment examples
```

Notebook sequence: 01 data understanding, 02 data quality, 03 EDA, 04 baseline, 05 LightGBM, 06 probabilistic forecast, 07 hierarchical analysis, 08 surplus, 09 optimization, 10 scenarios, 11 business KPI, 12 executive demo. Notebook 07 initially demonstrates why marginal quantiles do not add; full probabilistic reconciliation is an extension.

## Required engineering checks

- Unit conversion and interval duration; duplicate and daylight-saving handling.
- Feature source timestamps no later than issue-time availability cutoff; no random time splits.
- Missing-label exclusion and coverage reporting; preprocessing fitted on training data only.
- Quantile nonnegativity/ordering and calibration evaluated after postprocessing.
- Capacity transfers conserve estate entitlement and never create generation.
- Energy balance, source deliverability, reserve, import/export, and network caps.
- External export remains zero for unknown, prohibited, or expired eligibility.
- Cost ledger counts each action once and includes identical recourse rules for both policies.
- Stale supply/meter inputs, infeasibility, timeouts, and expired approvals suppress action.
- Optional ESS tests include efficiency, terminal SOC, simultaneous-flow prevention, and reserve duration.

## Pilot progression

Public-data PoC → actual-data retrospective validation → read-only shadow operation → manually approved limited pilot → measured-value review. A provisional shadow period is 4–8 weeks, extended until relevant operating regimes are represented. Progress depends on calibrated risk and operator/commercial sign-off, not merely dashboard completion. External sales, ESS, LLM/RAG, and additional horizons get separate scope decisions.
