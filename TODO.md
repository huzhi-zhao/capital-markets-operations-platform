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

- [x] Gather the remaining hypothesis evidence, applying the matrix and frozen-lifecycle method batch
  one established. All four batches are done. Seven allocation and confirmation messages against
  Volume 5, the securities settlement family against its schemas and report, the cash families
  against their schemas and the external code sets. Six segments, six frozen lifecycles: order,
  allocation, confirmation, settlement with its failure variant, and the cash leg.
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
- [x] Freeze the BO baseline. The one blocking criterion was the chain evidence, and all six segments
  now have a frozen minimal lifecycle sourced to a page or a schema element. Reconciliation and
  difference attribution stay primary, restatement stays supporting, regulatory reporting stays
  demoted. Rejected alternatives, the scope boundary, and what would justify unfreezing are recorded
  with the decision rather than left implicit.
- [x] Finalize the initial success measures. Five of the seven are binary and judgeable today, on
  purpose: the baseline should not hang on a number nobody has measured. The two that need
  measurement are the batch deadline and the restatement window, and both constrain the
  implementation rather than the objective, so neither can unfreeze the baseline.

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
- [ ] Execute the shared-host enablement plan. All four remaining items land on the same machine,
  which the sibling project also uses, so they are written up as a staged launch plan in the design
  doc dated 2026-09-12 rather than tracked as loose tasks. Two stages need no downtime and can be
  done any time: adding the host to the SSH configuration, and a read-only version inventory. Two
  need a restart window the owner does not currently have: the Iceberg runtime on the shared Spark,
  and a separate Trino catalog. Every stage gates on the sibling project's smoke test passing before
  this project's own check counts. The owner will run the whole plan in one sitting on a date not yet
  fixed, so nothing here is to be split off or chased separately. Anything else that can only be
  settled on that machine goes into the same design doc rather than becoming its own task.
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
- [x] Establish whether the REST catalog backing store can be rebuilt from the metadata files in object
  storage. A registration procedure exists that adopts an existing metadata file into a catalog, so
  per-table recovery is real. Three gaps make it not yet a recovery method. The list of which tables
  exist lives only in the catalog that was lost. Nothing in object storage says which metadata file is
  current, and picking wrongly rolls silently back to an older snapshot. And the procedure carries an
  explicit warning that registering one metadata file in two catalogs can corrupt the table, so it is
  not idempotent.
- [ ] Keep a table inventory outside the catalog backing store, at least names and locations. It is
  small enough to sit with the reference data the recovery objectives already treat as irreplaceable,
  and without it the rebuild path cannot start.
- [ ] Time a catalog rebuild drill and check whether the newest-metadata-file rule holds in practice.
  Until measured, catalog recovery stays an assumption.
- [x] Verify DuckDB and Polars Iceberg write maturity. The question was posed slightly wrong: writing
  exists, maintenance is what is missing. DuckDB writes full DML through a REST catalog including
  keyed merges, but only as merge-on-read positional deletes, and its extension offers no compaction,
  no snapshot expiry and no orphan cleanup, so it cannot run the compaction workload. Polars offers
  only append and overwrite, both flagged unstable, and delegates to the Python library underneath,
  which has an upsert but likewise no data-file compaction. Spark with the table format's own
  procedures covers all seven workloads. Spark is therefore the evidence-backed choice, which is the
  distinction the evaluation asked to be written into the decision record.
- [ ] Implement the write-path admission checks. The plan is written up in the design doc dated
  2026-09-12; only the implementation is left. Three layers: static configuration rules in CI, a
  property assertion on the create-table path, and an online sweep of actual table properties. The
  first two need nothing that does not already exist. The third reads the catalog and therefore waits
  for the enablement window. Acceptance is stated as seven negative and positive CI cases.
- [ ] Schedule the delete-file cleanup that mixed-engine writing implies. If DuckDB writes these
  tables, Spark has to run the position-delete rewrite and the data-file rewrite on a cadence,
  because the engine producing the delete files cannot consume them. The admission-check design makes
  the cadence a mandatory field on every dual-write table, so this item now has a place to live; what
  is still missing is the cadence itself, which needs the accumulation rate measured on the host.
- [ ] Produce the evaluation matrix and risk list, and open Proposed ADRs for the high and medium
  reversal-cost decisions only.
## Next: Phase 0B-2 and 0B-3

- [ ] Run only risk-linked, time-boxed, disposable probes that cannot be resolved reliably from public
  documentation.
- [ ] Feed measured results into the capacity baseline, requirements, and Proposed ADRs.
- [ ] Finalize the component-to-language map, then define the minimum Java, Python, SQL and Spark
  templates needed by Phase 1. The runtime-boundaries record already scopes its long-term-release rule
  to self-written Java modules and already allows third-party components their own runtimes, so that
  part needs no revision. What the map must now fix is a concrete runtime per component, using the
  measured versions rather than the newest releases.
- [x] Add the measured Java evidence for both engines to the runtime boundaries record. Done as an
  amendment dated 2026-09-12. The two supported ranges do not overlap, which turns that record's
  permission to run components on their own runtimes into a necessity without changing the principle.
  It also carries the risk the record was missing: the query engine requires exactly Java 22 and
  refuses Java 21 and below, so that component may have no long-term release available at all. Two
  responses are recorded and neither is chosen, because choosing belongs to the candidate re-ranking.
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
- [x] Read the Message Definition Report for the Settlement and Reconciliation message set, Part 1.
  It confirms every one of S-1's field choices through its own worked examples, supplies the two
  business roles, and adds two fields S-1 had missed: the safekeeping account, which is where the
  account dimension attaches to the settlement leg, and the credit-debit indicator, whose sign flips
  with direction the same way the allocation net money does. S-1 is frozen.
- [x] Recover the status transition ordering. The decision diagram is an image inside the report, read
  block by block. It organises status by which party performed the step rather than by kind of status,
  and it settles the rule S-2 needs: the settlement branch first asks whether the current moment is
  before or after the instructed settlement date, and pending becomes failing at the end of that date.
  It also shows that matching status is not monotonic, that the two matching axes differ by who issued
  them, and that an unmatched trade carries only the account owner's reason.
- [ ] Follow the diagram's one external pointer, a chapter reference that is not in this report and
  points at the market practice group's own document. It affects boundary detail on the
  before-or-after judgement, not the main rule.
- [ ] Read Parts 2 and 3 of the same report for the per-element definitions and usage rules. S-1 does
  not depend on them; S-3 and S-4 do. S-2 turned out not to need them: its rule came from the
  decision diagram and its value ranges from the schema.
- [x] Freeze S-2, the failed-then-late settlement scenario. It reuses S-1's instruction rather than
  issuing a new one, and adds two status advices carrying the same reason code on two different
  axes, pending before the settlement date ends and failing after it. Counting the two enumerations
  from the schema settles which codes S-2 may use: sixty-one pending, sixty-four failing, fifty-seven
  shared, and only the shared ones can appear on both steps. All five reasons the main business flow
  cares about are in the shared set. The confirmation's effective settlement date is mandatory while
  the instructed one is optional, so both are now always written and the delay is measurable as their
  difference.
- [x] Write a business validation layer for the settlement leg. Written into the validation and
  reconciliation spec as a new section, three tiers split by how much a check needs to see: one
  message, one transaction identifier's worth of messages, then the scenario contract. Every check
  says whether it comes from the specification or from this project's own choice, because only the
  second kind may be revised as scenarios expand, and every check carries its applicability. Output
  is contract violation rather than a reconciliation break, so failing chains stay out of the queue
  instead of showing up there as fake quantity mismatches.
- [ ] Write the same layer for the cash leg. The three-tier split should carry over, but the payment
  messages have even fewer mandatory fields than the settlement ones and the status report has none
  at all, so that has to be checked before assuming the structure transfers.
- [ ] Decide where the account servicer and account owner roles live in the generation spec. S-1
  introduces both and the two-level client and account structure has neither.

- [x] Verify the ISO 20022 cash families from their schemas. Twelve messages across the two cash
  message sets, identifiers, roots and cardinality all taken from the registration authority's own
  XSD. Three findings matter beyond bookkeeping. The payments family is batch-oriented where the
  securities family is one instruction per message, so Bronze needs a group table and a transaction
  table rather than one row per message. The status report's transaction level has no mandatory
  element at all, an even weaker guarantee than the settlement leg's. And the end-to-end identifier
  is the only mandatory identifier in the payment identification block, which makes it the single
  anchor that ties the cash leg back to the securities leg.
- [x] Obtain the External Code Sets. Version 2Q2026, one hundred sixty-three types and three thousand
  three hundred forty-seven codes, read in the browser and not saved. The cash leg's vocabulary gap is
  closed. Two things came out of it that the schema alone would never have shown. Thirty-three codes
  are marked obsolete in an annotation while remaining ordinary enumerations, so a generator that
  treats the enumeration list as its value pool will emit withdrawn codes and no validator will catch
  it; the annotation has to be read alongside the values. And the bank transaction codes are not in
  the code sets either, only a second pointer to a separate spreadsheet published a quarter earlier,
  whose domain, family and subfamily form a table of about fifteen hundred valid combinations rather
  than three independent enumerations.
- [ ] Snapshot the code sets and the bank transaction combination table as one versioned artifact that
  the generator and the validation layer both read. They must not fetch independently: different
  versions on the two sides produce data that is legal and a validator that says it is not, with
  neither side wrong.
- [x] Freeze P-1, the minimal cash-leg lifecycle, and with it close the six-segment chain. The
  financial-institution credit transfer is chosen over the customer one for a single structural
  reason: only it carries an underlying-allocation list, whose five fields are all mandatory and are
  exactly the allocation table the chain already produces. One message carries the block and splits
  it internally, the same shape as every earlier segment.
- [x] Correct the claim that the end-to-end identifier is the only key tying the cash leg back to the
  securities leg. It is the only mandatory one. The related-references choice on each underlying
  allocation opens with a securities settlement transaction identifier, a field the standard provided
  for precisely this join. All three levels are now written rather than only the mandatory one.
- [ ] Read the Message Definition Reports for both cash message sets. Business flows, roles and
  worked examples are there, the same position they occupied for the settlement leg.
- [x] Decide how the batch-oriented payment messages land in Bronze. Settled in the design doc dated
  2026-09-12. Five tables rather than two, because the repeating structure goes deeper than the
  transaction list: the underlying allocations carry the link back to the securities leg, and the
  status report has two independently repeating levels of its own. Primary keys are technical, parent
  key plus physical ordinal, so that a rerun is idempotent while a genuine re-delivery survives as the
  duplicate it is. Partitioning follows the ingest batch, not the business date, because every late
  message would otherwise rewrite a committed history partition and late messages are the main flow.
