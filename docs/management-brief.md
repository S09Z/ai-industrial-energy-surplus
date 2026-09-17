# Management Brief — Energy Optimization Control Tower

**Decision requested:** sponsor a 6–8 engineering-week PoC to test whether better next-day demand and uncertainty forecasts improve procurement and internal capacity planning. Assign an operations sponsor and commercial/finance reviewer. No purchase, external sale, or equipment automation is authorized by this proposal.

The dashboard tells us what happened. Forecasting estimates what will happen. Optimization recommends what to do and makes the cost and risk of that choice visible.

## Business outcome

At a daily planning cutoff, provide 24 hourly forecasts, the supply headroom after uncertainty and reserve, a recommended action, and its modeled THB value. Begin with avoidable procurement and eligible internal capacity reassignment. External sale is a future opportunity contingent on physical surplus and documented commercial permission.

The key distinction is that 3 MW of unused contracted capacity is not automatically 3 MW of electricity available for sale. It creates value only when a permitted action changes cost, utilization, or reliability.

## Demonstration

Use real historical electricity consumption from 20–50 non-residential proxy customers, paired with clearly labeled simulated supply, tariffs, and contracts. This proves the workflow and measures performance on the proxy population; an industrial production claim requires actual factory data.

Show a normal plan, a factory production surge, a supply reduction, and a stale-data failure. The audience sees recommendations change, the reasons, and when the system declines to recommend an action. Every screen labels the issue time, units, modeled assumptions, risk policy, and approval status.

An illustrative hour has 100 MW deliverable supply, 89 MW P90 demand, and 3 MW operating reserve, leaving an 8 MW planning envelope. That is an uncertainty-adjusted estimate, not a guaranteed sale quantity. Commercial and network restrictions may reduce eligible export to zero.

## Success and economics

Proposed success criteria: 10% relative estate WAPE improvement over a seasonal baseline; P90 coverage near 90% with transparent uncertainty; no increase in replay unmet energy; no accepted plan violating modeled hard constraints; and at least 3% lower controllable procurement cost in the agreed simulated base case. Report peak error, emergency purchases, and sensitivity as well. These are targets, not results or promised ROI.

For illustration, avoiding a cancellable 4 MW purchase for 3 hours saves 12 MWh. A synthetic tariff of THB 2,500/MWh implies THB 30,000 gross avoided spend before fees and imbalance costs. Fixed commitments may yield no savings. Finance verifies realized benefit against a frozen counterfactual after execution, avoiding double counting between procurement, reallocation, and storage.

## Executive questions

| Question | Proposed answer |
|---|---|
| Do we need to write code? | Yes for data contracts, eligibility, constraints, replay, and integrations. Existing model and solver libraries handle the algorithms. |
| Can we use AutoML? | Yes as a challenger after fixing chronological splits, availability rules, and business evaluation. It cannot decide contract eligibility or the reliability policy. |
| Are there off-the-shelf platforms? | Forecasting, energy management, and optimization products can be evaluated against the same replay harness. Run a build-versus-buy review after data and constraint discovery; no vendor selection is needed for this PoC. |
| Can the pipeline be automated? | Ingestion, training experiments, forecasts, validation, and recommendations can be scheduled. Commercial approval and operational execution stay with authorized people. |
| Do operators need coding skills? | No. Operators review plans, assumptions, explanations, alerts, and approval screens. Engineers maintain the system. |
| Do we need GPUs? | Not for the proposed seasonal and tree-model PoC. Size CPU and memory after profiling; do not purchase GPU infrastructure first. |
| Can it run on-prem, cloud, or hybrid? | Yes. The proposed batch/API design is portable. Hybrid can retain raw meter data on-prem and share only approved aggregates. |
| Does company data leave the company? | Only if deployment and integration choices allow it. Forecasting and optimization can run locally without an external LLM. |
| What if the forecast is wrong? | Reserve, calibrated uncertainty, stress tests, and emergency recourse reduce exposure. We measure realized replay breaches; forecasts cannot guarantee reliability. |
| How does it know it is uncertain? | Quantile models estimate a range; held-out calibration and observed coverage test it. Drift and missing-data checks can invalidate a recommendation. |
| What is the fallback? | Use the approved conservative planning procedure with verified inputs; suppress new actions when critical inputs or constraints are untrusted. |
| Can it explain high demand? | Show historical comparisons, schedule inputs, and model feature contributions. Explanations are evidence-linked and not causal proof. |
| Can AI control the grid? | This project provides recommendations only. Any future control integration is a separate engineering and governance project. |
| How do we avoid lock-in? | Use open data schemas, portable files, versioned APIs, reproducible models, and replaceable solver/model interfaces. |
| How many people are needed? | One primary engineer, with recurring input from operations and a commercial/finance owner. A live pilot also needs the OT/integration and security owners. |
| How much history? | Prefer 12–24 months to observe seasonality; BDG2 provides two years. Less history supports a narrower claim and more conservative planning. |
| What if data quality is poor? | First deliver a quality report and repair plan. Missing meters must not look like shutdowns or create phantom surplus. |
| How does it differ from BI? | It evaluates future actions under uncertainty and constraints, then compares their costs and realized outcomes. |
| How do we measure ROI without sales? | Avoidable procurement and imbalance costs, verified charge reductions, and planning hours saved; value only what the action actually changes. |
| How does it scale to 100 factories? | Pooled forecasting and batch inference scale by customer-hours. Benchmark runtime and topology/contract complexity before adding infrastructure. |
| What happens after success? | Validate on factory data, operate in shadow mode, then run a limited human-approved pilot and measure realized value. |

## Sponsorship assumptions

The PoC is useful even if export is prohibited, but only commercially flexible costs can become savings. Management should provide an operating baseline, identify who owns the risk policy, and nominate the reviewer for tariff and contract assumptions before a real-data pilot. Actual licensing, wheeling, PPA, and trading eligibility remain a separate commercial/legal determination.
