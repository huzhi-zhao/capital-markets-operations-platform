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
  settlement and cash families, applying the matrix and frozen-lifecycle method batch one established.
  Allocation instruction, allocation instruction acknowledgement, confirmation, confirmation
  acknowledgement, confirmation request, allocation report and allocation report acknowledgement are
  all verified against Volume 5, and A-1 and C-1 are frozen. The securities settlement family is
  verified from the normative schemas and S-1 is structurally settled. The cash families remain.
- [x] Decide that A-1 continues from L-1 rather than starting beside it, and freeze the binding
  contract: order identifier, filled quantity and average price are inherited, never regenerated,
  because regenerating any of them puts two unrelated order identities in Bronze and breaks the
  per-event traceability the project claims. Message-level values still wait on the volumes.
- [x] Add an account dimension to the generation spec. Two levels, client and account, because the
  accounts in one allocation must belong to one client and a flat set cannot express that. Unlike the
  instrument dimension it has no real source to inherit from, so every size figure is a setting rather
  than a measurement, and the outward claim has to say so. Three of its four lifecycle events match the
  instrument dimension; account merges do not, because they move positions across keys and a
  single-key version chain cannot represent that. The contract is that a merge never rewrites history.
- [ ] Decide how the merge chain is materialised in Silver: walk the chain per query, or pre-expand to
  the chain tail in the dimension. A performance and correctness trade-off, not a design question, so
  it waits for Phase 1 measurements.
- [x] Settle the version claim, and correct half of it. The specification states in its own words that
  confirmation and allocation report are new to 4.4, so no comparison against 4.2 is needed. But the
  same page records that allocation existed before under a different message name, so the original
  wording, that 4.4 is the earliest carrying allocation semantics, was wrong. What 4.4 adds is
  confirmation, plus moving fees and expenses out of the allocation instruction.
- [x] Verify the confirmation messages and freeze C-1, using the same method. Three messages checked
  against Volume 5 pages 45 to 56 with enumerations from Volume 6. The specification contradicts itself
  in three places where field rows were copied from the allocation side without editing, so the matrix
  records the specification wording and the conditional table records the project's reading separately.
  A third scaffold invariant proved to be the same class of error as the previous two, treating an
  equation that holds in a narrow case as universal.
- [x] Verify the allocation report and its acknowledgement, the last two unchecked messages in batch two.
  They look like the allocation instruction but differ in four ways, including one trap where the
  acknowledgement requires an identifier the report itself may omit. Neither has a scenario in this
  project, so they are filed as A-5 at low priority rather than pushed into A-1.
- [x] Read the specification's own example flows and rejection scenarios for allocation, Volume 5
  pages 33 to 38. This reversed A-1's step count: every one of the six flows lists the interim
  received acknowledgement as its own row, so A-1 goes from two steps to three.
- [ ] Add a confirmation-layer assertion to the validation spec: at least one confirmation per allocated
  account, exactly one within C-1's narrow conditions. The applicability condition has to ship with it,
  or it starts producing false alarms as soon as C-2 lands.
- [x] Settle the five L-1 distribution parameters. Adopted, with the scalars marked openly as arbitrary:
  what is justified is the constraints and the shape of each distribution, not the specific numbers,
  which are placeholders to be revisited once Phase 1 measures row width. Order size and fill count
  jointly drive rows per instrument-day, so changing either is cheap in itself but forces the capacity
  estimate to be redone.
- [x] Decide whether the generator needs accurate name-change dates. It does not, for the same reason
  prices are synthetic: a real date on a synthetic instrument is no truer than a generated one. What
  the extraction contributes is counts and ordering, which set the length distribution of the dimension
  version chains, and that is the part under test.
- [x] Decide how name changes are placed in time. Anchored to corporate actions rather than uniform,
  because clustering produces short version intervals and same-day changes, exactly where the
  no-overlap-no-gap invariant breaks, and because it puts restatement and dimension change in the same
  batch, which is the hardest case to reconcile.
- [ ] Choose the anchor window width and the share of name changes that anchor rather than falling back
  to uniform sampling. These set the difficulty of the test, not its correctness.
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
- [x] Screen the OCI memory budget on paper, then discard the screen's conclusion. Measurement showed
  it overstated Trino threefold and the others by comparable factors, because published figures are
  capacity recommendations for production throughput rather than idle footprints. The lesson is kept in
  the document: a paper screen can raise a risk, it cannot eliminate a candidate.
- [x] Decide whether the 2026 no-pipeline-components boundary is relaxed for disposable probes. It is,
  within four conditions recorded in the roadmap. The generator, the pipeline itself and the ordering
  of full backfill after the baseline freeze are untouched.
- [x] Locate and inventory the four-core instance. It exists and matches its stated specification, but
  it is not idle: 26 containers of the sibling project and personal services occupy 16 GB of memory and
  143 GB of disk, leaving roughly 7.9 GB and 32 GB for this project.
- [x] Resolve the storage and memory question. The owner reports both are reclaimable, over 100 GB of
  disk and enough memory by removing unused containers and relocating two personal services, provided
  the architecture does not change. Recorded as a plan rather than a measurement, to be re-measured
  before deployment.
- [x] Decide reuse versus independent deployment. Full reuse on the OCI side, catalog excepted,
  recorded as an amendment to the topology ADR. The deciding argument is that the heavy work already
  sits on the laptop, so the OCI engine is idle most of the time and a second deployment earns nothing.
  Blast radius is accepted explicitly, as availability risk only.
- [ ] Add the Iceberg runtime to the shared Spark, matching 3.5.1 and Scala 2.12. It currently has no
  Iceberg support at all, and this modifies a container the sibling project uses.
- [ ] Add a separate Trino catalog for this project rather than altering the existing one, which points
  at the sibling project's Hive metastore. Two projects then share one engine while their tables stay
  invisible to each other. Adding a catalog generally needs a restart, which interrupts the sibling
  project, so it needs a window.
- [ ] Gather the JDK and compatibility evidence against the versions actually running, not the latest
  releases. The shared Spark image runs JDK 11, which constrains the runtime boundaries ADR.
- [ ] Add a host block for the four-core instance to the SSH configuration so it is addressable by name.
- [x] Run probe P-1b. No deployment was needed: the host already runs the entire stack CMOP planned to
  install, so the figures come from real running instances. The default combination occupies about
  7.6 GB, comfortably inside 24 GB.
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

- [x] Verify the ISO 20022 securities settlement family. Identifiers, versions, element cardinality and
  enumerations for the instruction, status advice and confirmation come from the registration
  authority's own schemas, which are normative. S-1 is structurally settled and continues from C-1's
  affirmed confirmations.
- [ ] Read the Message Definition Report for the Settlement and Reconciliation message set. The schemas
  give cardinality and enumerations but not usage rules, so S-1's structure is settled while its field
  choices are not. Until this is read, S-1 is not frozen.
- [ ] Write a business validation layer for the settlement leg. Schema validity proves almost nothing
  here: an instruction that names no security passes the schema, because the security identification
  branch is mandatory while all three of its children are optional.
- [ ] Decide where the account servicer and account owner roles live in the generation spec. S-1
  introduces both and the two-level client and account structure has neither.
