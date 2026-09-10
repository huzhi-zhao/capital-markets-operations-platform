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
- [x] Define the target personas, critical business flow, and at least one representative BQ.
  Operations analyst is primary, the T+1 morning exception workflow is the one flow that must run
  end to end, and BQ-2 is representative because it constrains grain, keys and lineage.
- [x] Establish the initial raw-data source inventory: source class, owner, rights, format, arrival mode,
  expected history, quality risks, and sensitivity.
- [x] Adopt the ranking as the working BO hypothesis (loop step 1).
- [ ] Gather evidence for the hypothesis: minimum FIX order/execution/allocation subset, ISO 20022
  settlement and cash message families, and the semantics needed for corporate-action restatement.
- [x] Probe whether ten years of corporate actions can actually be obtained. Answer: yes, from the SEC
  structured endpoints, which are free, cover ten years, and are explicitly redistributable.
- [x] Decide the corporate-action sourcing method: extract real splits, dividends, name changes and
  delistings from SEC, and anchor the generator's event distributions to them.
- [x] Settle the daily market-data question: prices become synthetic, because synthetic instruments make
  real prices meaningless. FX and rate curves stay real.
- [x] Decide the SEC extraction scope. Answer: all forty quarters, no pilot subset, because a subset
  cannot expose the cross-period definition drift that matters most here.
- [x] Write the validation rule that separates forward splits, reverse splits, and unrelated conversion
  ratios in the SEC split-ratio concept. Adopted the standard reference-data practice: context filter
  first, single normalized adjustment factor, corroboration against shares outstanding, plausibility
  bands as alarms only, and a three-way pass/reject/quarantine outcome.
- [x] Decide how extracted real events map onto synthetic instruments. Answer: one-to-one alias binding,
  which preserves the real event calendar's clustering and cross-event correlation for free, and fixes
  the instrument universe at roughly ten thousand.
- [x] Pick the FIX version before filling in any field table. Answer: FIX 4.4, single version, no
  mixing. It is the earliest version carrying the confirmation and allocation semantics BO-1's
  chain needs, and FIX 5.0's session-layer split buys nothing for a batch generator.
- [x] Run the forty-quarter SEC extraction and replace the planning estimates with measurements.
  Instrument universe is 12505, extracted volume is 6 MB, split-ratio adjudication rate is ten percent,
  and twenty-nine percent of reverse-split filers were later delisted.
- [x] Run the second SEC pass for name changes. 49 percent of the universe has former names, at five
  times the split rate, but the formerNames date fields are EDGAR name-appearance windows rather than
  legal change dates, so counts are usable and dates are not.
- [ ] Decide whether the generator needs accurate name-change dates. If so, they must be recovered from
  the filings themselves, which is separate work.
- [x] Decide where extraction output lives in the repo and in what format. Answer: scripts under
  tools/sec-extract, pinned raw responses plus a manifest under data/reference/sec, committed rather
  than regenerated because SEC data drifts as filers amend.
- [ ] Freeze the BO baseline. Blocked only on the FIX and ISO 20022 field evidence; the hypothesis itself
  is confirmed and needs no revision.
- [x] Decide the drill-down boundary for Silver. Answer: excluded from external scope. The difference
  explanation chain is materialized into Gold during the batch, the interactive path never crosses the
  tunnel, and per-event Silver drill-down stays a LAN-only engineering capability.
- [ ] Fill the regulatory data-contract skeleton, starting with the FIX order lifecycle batch.
- [x] Test the leading BO against public-rule coverage, source feasibility, target scale, hardware limits,
  and an end-to-end acceptance story. Three of five criteria pass, two lack evidence rather than failing,
  and the ranking needs no change. See business-objectives.md section 5.1.
- [ ] Finalize the BO baseline: name the primary and supporting BOs, record rejected alternatives, and
  freeze the initial success measures and in-scope/out-of-scope boundary.
- [x] Extend the workload baseline beyond capacity to cover velocity, freshness, access patterns,
  concurrency, retention, RPO/RTO, network limits, and operational constraints. Written as the
  workload envelope in workload-baseline.md section 5, and renamed that file from
  data-volume-baseline.md to match its content.
- [x] Draft the synthetic-data generation contract: reproducibility, instrument dimension, measured
  corporate-action distributions, and the dirty-data contract. The trade-lifecycle distributions and
  three of the invariants stay blank until the FIX field evidence lands.
- [ ] Fill the trade-lifecycle distributions and the FIX-dependent invariants in the generation spec
  once the field tables are verified.
- [x] Draft the validation and reconciliation specification: four reconciliation pairs, per-pair date
  basis, the difference taxonomy, rerun assertions and gate semantics. Thresholds and tolerances stay
  open until Phase 1 measures them.

## Next: Enter Phase 0B

- [ ] Confirm that the BO baseline, source inventory, and workload envelope satisfy the entry gate in
  `docs/dev/project-inception-and-readiness.md`.
- [x] Create the cross-cutting technology-selection evaluation requirement with scope, decision axes,
  evaluation criteria, representative workloads, and evidence requirements. Evaluation depth is tied to
  reversal cost, and the workloads come from the workload envelope rather than generic benchmarks.
- [ ] Confirm the first-pass reversal-cost ranking in the evaluation requirement, which decides which
  choices get their own ADR.
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
