# TODO

> **Current phase**: Phase 0A - project boundary, business baseline, and data discovery.
>
> This file is the mutable project task queue. Long-lived requirements and decisions belong in
> [developer documentation](docs/dev/README.md); stage definitions and readiness evidence belong in
> [Project Inception and Readiness](docs/dev/project-inception-and-readiness.md).

## Completed Foundations

- [x] Establish documentation audiences, indexes, and routing rules.
- [x] Draft project positioning, system boundary, and success direction.
- [x] Draft logical Bronze/Silver/Gold responsibilities in ADR 0002.
- [x] Draft hybrid role-to-node topology and technology-selection boundary in ADR 0003.
- [x] Draft language admission, responsibility, and LTS runtime boundaries in ADR 0004.
- [x] Record the enterprise project-inception research and CMOP readiness method.
- [x] Split node responsibilities: MBP for backfill and full recompute, NAS for resident daily increments,
  a single orchestrator on OCI.
- [x] Correct the settlement cycle to T+1 across the documentation.

## Now: Complete Phase 0A Inputs

- [x] Provisionally rank BO-1, BO-2, and BO-3 as primary, supporting, or rejected candidates.
- [ ] Define the target personas, critical business flow, and at least one representative BQ.
- [x] Establish the initial raw-data source inventory: source class, owner, rights, format, arrival mode,
  expected history, quality risks, and sensitivity.
- [x] Adopt the ranking as the working BO hypothesis (loop step 1).
- [ ] Gather evidence for the hypothesis: minimum FIX order/execution/allocation subset, ISO 20022
  settlement and cash message families, and the semantics needed for corporate-action restatement.
- [ ] Probe whether ten years of corporate actions can actually be obtained. This is a go/no-go for the
  supporting BO, not a formatting detail.
- [ ] Revise or confirm the hypothesis against that evidence, then freeze the BO baseline.
- [ ] Decide the drill-down boundary for Silver: bounded demo capability or excluded from external scope.
- [ ] Settle the acquisition channel and licence terms for security master and corporate actions.
- [ ] Draft the minimum regulatory and industry data contracts for the selected BO.
- [ ] Test the leading BO against public-rule coverage, source feasibility, target scale, hardware limits,
  and an end-to-end acceptance story.
- [ ] Finalize the BO baseline: name the primary and supporting BOs, record rejected alternatives, and
  freeze the initial success measures and in-scope/out-of-scope boundary.
- [ ] Extend the workload baseline beyond capacity to cover velocity, freshness, access patterns,
  concurrency, retention, RPO/RTO, network limits, and operational constraints.
- [ ] Draft the synthetic-data generation contract: distributions, invariants, dirty-data cases, and
  reproducibility requirements.
- [ ] Draft the validation and reconciliation specification with measurable acceptance gates.

## Next: Enter Phase 0B

- [ ] Confirm that the BO baseline, source inventory, and workload envelope satisfy the entry gate in
  `docs/dev/project-inception-and-readiness.md`.
- [ ] Create the cross-cutting technology-selection evaluation requirement with scope, decision axes,
  evaluation criteria, representative workloads, and evidence requirements.
- [ ] Decide which product choices are independently reversible and therefore require separate ADRs.
- [ ] Run only risk-linked, time-boxed, disposable probes that cannot be resolved reliably from public
  documentation.
- [ ] Feed measured results into the capacity baseline, requirements, and Proposed ADRs.
- [ ] Finalize the component-to-language map and choose the supported LTS JDK from compatibility
  evidence; then define the minimum Java, Python, SQL, and Spark templates needed by Phase 1.
- [ ] Accept or supersede ADRs only when their open risks no longer threaten the first vertical slice.

## Later: Formal Implementation

- [ ] Build the reproducible one-million-row generator prototype.
- [ ] Implement the minimum Bronze to Silver to Gold vertical slice.
- [ ] Validate one late confirmation and one correction or cancellation end to end.
- [ ] Replace planning assumptions with measured bytes-per-row, compression, file-count, shuffle,
  runtime, memory, and storage results.
