# TODO

> **Current phase**: Phase 0B-1 - solution evaluation, with two Phase 0A items running in parallel.
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

## Done: Phase 0A Inputs

- [x] Provisionally rank BO-1, BO-2, and BO-3 as primary, supporting, or rejected candidates.
- [x] Define the target personas, critical business flow, and at least one representative BQ.
  Operations analyst is primary, the T+1 morning exception workflow is the one flow that must run
  end to end, and BQ-2 is representative because it constrains grain, keys and lineage.
- [x] Establish the initial raw-data source inventory: source class, owner, rights, format, arrival mode,
  expected history, quality risks, and sensitivity.
- [x] Adopt the ranking as the working BO hypothesis (loop step 1).
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
- [x] Decide where extraction output lives in the repo and in what format. Answer: scripts under
  tools/sec-extract, pinned raw responses plus a manifest under data/reference/sec, committed rather
  than regenerated because SEC data drifts as filers amend.
- [x] Decide the drill-down boundary for Silver. Answer: excluded from external scope. The difference
  explanation chain is materialized into Gold during the batch, the interactive path never crosses the
  tunnel, and per-event Silver drill-down stays a LAN-only engineering capability.
- [x] Read the FIX 4.4 field tables and state machine, and upgrade the candidate field list into a
  contract matrix organised by message and scenario, with a frozen minimal lifecycle L-1.
- [x] Fill the contract matrix: per-message obligation levels, conditional-required conditions, the
  L-1 transition table and per-step values, each carrying a volume and section citation. Transitions
  outside the matrices are recorded as L-1 scenario violations rather than FIX violations, because the
  specification warns its own matrices are not exhaustive.
- [x] Answer whether CumQty plus LeavesQty equals OrderQty unconditionally. It does not. It holds on
  L-1's New, Partially Filled and Filled reports, and must not be asserted on terminal states.
- [x] Test the leading BO against public-rule coverage, source feasibility, target scale, hardware limits,
  and an end-to-end acceptance story. Three of five criteria pass, two lack evidence rather than failing,
  and the ranking needs no change. See business-objectives.md section 5.1.
- [x] Extend the workload baseline beyond capacity to cover velocity, freshness, access patterns,
  concurrency, retention, RPO/RTO, network limits, and operational constraints. Written as the
  workload envelope in workload-baseline.md section 5, and renamed that file from
  data-volume-baseline.md to match its content.
- [x] Draft the synthetic-data generation contract: reproducibility, instrument dimension, measured
  corporate-action distributions, and the dirty-data contract. The trade-lifecycle distributions and
  three of the invariants stay blank until the FIX field evidence lands.
- [x] Draft the validation and reconciliation specification: four reconciliation pairs, per-pair date
  basis, the difference taxonomy, rerun assertions and gate semantics. Thresholds and tolerances stay
  open until Phase 1 measures them.

## Parallel: Close the Remaining Phase 0A Items

These block freezing the BO baseline and therefore Phase 1. They do not block 0B-1, because every
representative workload in the evaluation requirement comes from the workload envelope rather than
from any message specification, so no amount of further message reading changes which candidate
handles keyed rewrites of historical partitions.

- [ ] Gather the remaining hypothesis evidence: FIX allocation and confirmation, then the ISO 20022
  settlement and cash message families, applying the matrix and frozen-lifecycle method that batch one
  established.
- [ ] Confirm or replace the five proposed L-1 distribution parameters in generation spec section 6.2.
  Two carry real consequences: the quantity split must not round to a zero fill or the derived quantity
  fields stop reconciling, and fill prices must come from the same series used for valuation or
  reconciliation R1 carries a permanent difference that has nothing to do with the pipeline.
- [ ] Decide whether the generator needs accurate name-change dates. If so, they must be recovered from
  the filings themselves, which is separate work.
- [ ] Freeze the BO baseline. Blocked only on the FIX and ISO 20022 field evidence; the hypothesis itself
  is confirmed and needs no revision.
- [ ] Finalize the BO baseline: name the primary and supporting BOs, record rejected alternatives, and
  freeze the initial success measures and in-scope/out-of-scope boundary.

## Now: Phase 0B-1 Solution Evaluation

- [x] Create the cross-cutting technology-selection evaluation requirement with scope, decision axes,
  evaluation criteria, representative workloads, and evidence requirements. Evaluation depth is tied to
  reversal cost, and the workloads come from the workload envelope rather than generic benchmarks.
- [x] Confirm that the source inventory and workload envelope satisfy the entry gate. They do. The gate
  is the five conditions in the readiness document, all of which hold, and that section states that
  technology evaluation requires neither a permanently frozen BO nor every raw field settled.
- [x] Correct the evaluation requirement's own entry condition, which said it waited on a BO freeze and
  contradicted the readiness gate. It waits on the workload envelope, which is ready.
- [x] Build the candidate slate. Every decision previously listed one preferred answer, and an
  evaluation with one candidate is not an evaluation. Also split catalog implementation out of the
  table-format row, since only the interface shape was ever decided and the two differ in reversal cost.
- [x] Re-check the reversal-cost ranking. Batch compute moves to medium, because replacing the engine
  means rewriting all processing code. Object storage's S3 risk may be lower than assumed, since an
  independent REST catalog owns commit atomicity.
- [x] Screen the OCI memory budget on paper, using each project's own published requirements. Trino at
  the eight gigabytes typical of its Kubernetes deployment plus Airflow at its documented four gigabyte
  minimum already consume half the box, before streaming, BI, lineage, two databases and the operating
  system. The roughly twenty-one gigabyte estimate in the architecture document is withdrawn.
- [ ] Decide whether the 2026 no-pipeline-components boundary in the roadmap is relaxed for disposable
  probes. Deploying components to measure resident memory conflicts with it, so probe P-1b cannot run
  until this is answered. The paper screen needed no such deployment and is already done.
- [ ] Run probe P-1b once that boundary is settled: per-candidate idle and peak resident memory under
  the interactive query workload, deployed one component at a time, stopping any candidate that exceeds
  six gigabytes idle.
- [ ] Re-rank the candidates so the lighter combinations are evaluated alongside the heavy ones rather
  than after them. The default stack is no longer the assumed starting point.
- [x] Verify whether an independent REST catalog removes the conditional-write requirement on object
  storage. It does. The table specification requires only in-place write, seekable reads and deletes,
  and states outright that tables do not require rename except where rename itself implements the
  commit. The REST catalog performs the compare-and-swap server-side through its requirement
  assertions. The candidate set widens, and the leading compatibility question becomes multipart
  upload, which no vendor statement covers for third-party stores.
- [ ] Decide the configuration gate that forbids filesystem and Hadoop catalogs. The specification's own
  exception is exactly this case, and a single job configured that way silently reintroduces the rename
  requirement, failing by dropping commits under concurrency rather than by erroring.
- [ ] Establish whether the REST catalog backing store can be rebuilt from the metadata files in object
  storage, and how long that takes. It now sits on the commit path as a single point, and an unverified
  rebuild is an assumption rather than a recovery method.
- [ ] Verify DuckDB and Polars Iceberg write maturity, not read. Read support is long settled; write is
  the precondition for the keyed-merge and restatement workloads. A negative result makes Spark the
  evidence-backed choice rather than the default one.
- [ ] Produce the evaluation matrix and risk list, and open Proposed ADRs for the high and medium
  reversal-cost decisions only.
## Next: Phase 0B-2 and 0B-3

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
