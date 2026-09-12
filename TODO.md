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
- [x] Add a confirmation-layer assertion to the validation spec. Done as a section covering the whole
  allocation and confirmation segment, not just that one assertion, since the same discipline applies
  across it. Every assertion now carries three things: whether it comes from the specification, from
  this project, or is inferred from two others; the condition under which it holds; and the scenario
  that will retire it. The inferred one turned out to matter most. Total confirmed quantity equalling
  instructed quantity is composed from two assertions, so it dies together with the narrow one, and
  nothing in its own wording reveals that. The R1 and R2 comparisons were extended to the allocation
  layer at the same time, where both sides share a date basis because allocation does not cross the
  settlement date, unlike the trade-to-cash comparison one section earlier.
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
- [x] Re-rank the candidates so the lighter combinations are evaluated alongside the heavy ones rather
  than after them. Recorded as section 2.7 of the technology selection evaluation. Three findings had
  each removed one leg of the old ordering: the measured residency leaves the memory budget with room
  to spare, so it stops being a screen; single-node engines can write but cannot maintain, so a light
  combination can only redivide the work rather than replace the engine; and the query engine's exact
  Java requirement is not a long-term release, so the heaviest component now carries a cost that shows
  up in no performance number. Candidates are now six whole combinations rather than nine rows of
  single decisions, each of which must cover the full workload set on its own. Test order goes by how
  much a failure would eliminate, which puts the default stack last and demotes its numbers to a
  reference baseline. Six binary elimination criteria, and the residency threshold is kept as a guard
  rail rather than a screen.
- [x] Settle how evaluation results map onto proposed records. Five records for five questions that
  can each be overturned on their own, not one per combination and not one per decision row. The
  combination labels are scaffolding for the evaluation and stay out of the record titles.
- [x] Draft the compute division-of-labour record, which is the one unit whose conclusion needs no
  performance measurement. It rules out a single-node engine owning a set of tables outright, because
  compaction and snapshot expiry are the two columns those engines leave empty and the deferred
  deletes only accumulate. It pairs that with the two configuration constraints that make shared
  writing safe, both already expressed as admission checks. It deliberately leaves resident-versus
  on-demand open, and it records that the light combinations rest on one untested premise.
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
  reversal-cost decisions only. Partitioning is settled and the compute unit is drafted; the other
  four units wait on measurement.
- [x] Promote the two decisions that were already made but had no record of their own. The protocol
  version is one: it constrains every field table across phases and rolling it back means rewriting
  every generated message, which is the admission bar. The drill-down boundary is the other: the
  architecture section that held it said outright it was not yet a record and named the condition for
  promoting it, and that condition has since come true, because the decision produced a named
  exception to the Gold budget rule and is now relied on in four places. Both records add what a
  decision section does not carry: the options that lost, the price being paid, and the conditions
  under which the decision should be revisited.
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

- [x] Unlock two more settlement scenarios instead of the one that was queued. The queued fourth
  scenario was the reversal, which needs the restatement path working first; the cancellation refusal
  needs only the two scenarios already frozen and lands directly on the main business flow, since the
  first thing an operator does with a morning exception is ask whether it can be pulled back. The
  specification answers that with a code of its own, denied-since-settled. So cancellation-executed
  and cancellation-refused are frozen and the reversal moves down one slot.
  Three structural findings came out of it. The cancellation status advice has a mandatory status,
  unlike its settlement counterpart where every status is optional, so one of the checks written for
  the settlement leg is simply unnecessary here and the validation layer must stop treating a message
  family as one shape. A cancellation chain has two anchors pointing in opposite directions, one from
  the request back to the original instruction and one from the status back to the request, so they
  have to be checked separately. And the two scenarios differ in a way that is itself a contract:
  a successful cancellation must change the original instruction's processing status while a refused
  one must not touch it, and writing only one of those two leaves both unenforced.
  Bilateral cancellation is a real branch in the specification, where a matched instruction needs the
  counterparty's consent. It is out of reach because the party model has no market counterparty, and
  that is recorded as a boundary with its price rather than passed over.

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
- [x] Write the same layer for the cash leg. Checked before assuming, and the structure does not
  transfer. Written as section 2C of the validation and reconciliation specification. Four
  differences each moved a piece of the skeleton. A payment message carries many transactions, so
  the single-message tier splits into group header and transaction row, which must go to different
  queues because a bad header voids the whole batch while a bad row voids only itself. The status
  report has no mandatory field at all, so that whole table is CMOP with nothing behind it, unlike
  its settlement look-alike which named constraints now back. Code vocabularies live outside the
  schema, so an entire class of checks carries a vocabulary version and can change answer across
  quarters, and obsolete codes are ordinary enumerations with no formal marker. A statement entry
  can batch twenty payments, so counting rows to reconcile is wrong on the specification's own
  terms. Four tiers, one orthogonal versioned dimension, and three injections, two of them paired to
  prove the tier split itself rather than any single check.
- [x] Decide where the account servicer and account owner roles live in the generation spec.
  Neither of the two options on the table, and the settlement pair is handled together with the two
  agent roles the cash leg adds, rather than one segment at a time. Written as section 3B. Roles are
  where a fact points, not a kind of entity: the same custodian is a servicing party in one message
  and an agent in another, so building a table per role would store one institution four times with
  nothing keeping the copies consistent. The account owner needs nothing new at all, because it
  follows from the account, which the two-level structure already pins to exactly one client; that
  only works because the earlier decision refused to flatten those two levels, and the payoff lands
  here two months later. What genuinely has no source is which institution holds an account, so that
  becomes one small dimension shared by three roles. One simplification is taken and priced: all of a
  client's accounts sit at one institution, because otherwise a single allocation splits into several
  batches of instructions aimed at different servicers, which changes the chain's shape rather than
  adding a column. Identifiers must not be business identifier codes, and this time it is the
  specification saying so rather than us: those codes are issued by a registration authority and
  synthetic institutions have none, while the schema checks only their shape.

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
- [x] Read the Message Definition Reports for both cash message sets, and Parts 2 and 3 of the
  settlement one. Recorded as section 4C of the regulatory data contracts. The payoff is in Part 2's
  named constraints, which state cross-element conditions the schema cannot express and which no XML
  validator executes, so the business validation layer is their only enforcer. Two checks recorded as
  CMOP decisions are in fact specification requirements: a security identification must carry at
  least one of its three children, and a status advice must carry at least one of its four status
  axes. The pending-to-failing moment that S-2 rests on is now a numbered constraint rather than only
  a transcribed diagram, and it names the two status codes. Part 3 turns partial settlement into a
  per-instruction flag, so the "exactly one confirmation" condition hangs on a field rather than on a
  scenario. On the payments side the status report is optional in every described flow, which narrows
  invariant P1-8 to a generator-side convention; on the cash management side one statement entry can
  batch twenty payments, which rules out a one-to-one reconciliation for P-4.
- [x] Decide how the batch-oriented payment messages land in Bronze. Settled in the design doc dated
  2026-09-12. Five tables rather than two, because the repeating structure goes deeper than the
  transaction list: the underlying allocations carry the link back to the securities leg, and the
  status report has two independently repeating levels of its own. Primary keys are technical, parent
  key plus physical ordinal, so that a rerun is idempotent while a genuine re-delivery survives as the
  duplicate it is. Partitioning follows the ingest batch, not the business date, because every late
  message would otherwise rewrite a committed history partition and late messages are the main flow.
- [x] Freeze P-2, and in doing so correct the scenario as it was originally sketched. It was written
  as "cash leg late, securities leg normal", on the reasoning that this would test the two legs
  coming apart. Under delivery versus payment the two legs cannot come apart: payment not happening
  is delivery not happening. A cash-only delay is possible only under free-of-payment settlement,
  which no frozen scenario uses. The original wording would have produced a batch of data that
  violates the chain's own contract quietly, because every message is individually legal and the
  invariant tying the two dates together is conditioned on delivery versus payment and so would never
  have been evaluated against it. The coherent scenario is both legs late together, paired with S-2,
  which tests the same thing the original wording was reaching for: the effective settlement date
  separating from the instructed one. The instructed date is deliberately left unchanged, since a
  delay does not rewrite the original instruction.
- [x] Lift the cross-segment check that a failing securities leg forbids a completed cash leg out of
  its not-evaluated state. It was recorded that way because the only scenario that could exercise it
  was locked. Freezing P-2 gives it test data for the first time, and brings two checks with it: the
  two legs' effective settlement dates must be equal, and the cash leg must not reach a terminal
  state while the securities leg is still pending. The equality check cannot be merged into the
  existing one comparing instructed dates, because separating those two date pairs is the entire
  point of the scenario.
- [x] Freeze P-4, the end-of-day statement. Its whole difficulty is that one entry is not one
  payment: the report's own example batches twenty. Reconciliation therefore never runs on row
  counts, only on the end-to-end identifier echoed per transaction inside the entry. That echo is
  optional in the schema and mandatory in CMOP, because without it a broken reconciliation can only
  report a wrong total and never say which payment caused it, and saying which payment is the whole
  content of the primary business objective. Five invariants follow, of which exactly one is
  decidable from the statement alone; that one is run as its own batch, matching the real operational
  window where the bank's statement arrives before the internal ledger does.
- [x] Read the named constraints of the reversal advice, the cancellation-request status advice and
  the transaction notification, which was the last outstanding item from the report reading. The
  method used in the previous batch turns out to be unsound and one of its conclusions is now
  overturned. That batch searched the three settlement messages for a constraint by name, found it
  absent from the confirmation, and concluded the confirmation carries no such rule, leaving the
  matching check recorded as a CMOP decision. The confirmation does carry it, under a different name:
  the constraint tracks the element name, and the element is called settled amount rather than
  settlement amount. The rule text is otherwise identical. Names cannot be used to probe for absence;
  the whole list has to be taken and read. Every earlier "verified this message does not carry that
  rule" conclusion is now suspect and flagged as such.
- [x] Record the three constraints that turn out to apply to every securities message rather than to
  one. The settlement parties are a chain, not five independent slots: each one present requires its
  predecessor present, which means the generator must choose the depth first and then fill from the
  first slot, and the party-dimension section was written on the opposite assumption. An account
  owner reference that is unavailable is written as a sentinel string rather than left absent, which
  never affects generation because CMOP always has a reference, but which forbids writing the
  join-back check as an unconditional assertion and forbids joining on that field at all. And a
  linkage number, if given at all, must carry the linked message's own identifier.
- [x] Rerun the whole-list method over the three already-frozen settlement messages, on the reasoning
  that if "searched by name and found nothing" is unreliable, then so is "searched by name and
  concluded I was done". Seventy-one, thirty-one and fifty-five named entries respectively. It found
  a missing mandatory block in the frozen minimal scenario: when no standing settlement instruction
  applies, the counterparty side's depository and first settlement party are both required, and CMOP
  never produces standing settlement instructions, so every instruction and every confirmation needs
  that block. The schema marks it optional, so no XML validator would ever have caught it. The frozen
  status sequences are unchanged; the block is added, dated, and sourced.
- [x] Settle the first case where a rule and a guideline point different ways. The same passage that
  makes the depository mandatory also says to populate it with a real central securities depository's
  registered code, which the project forbids itself from inventing. The rule is satisfied and the
  guideline is deliberately not: the depository carries a proprietary identifier, the deviation is
  recorded where it happens, and the price is stated, which is that the identifier corresponds to no
  real market. Generalized into a standing rule for the project: wherever a guideline asks for a
  real-world registered identifier, use a proprietary one and record the deviation, because inventing
  something that looks registered is worse than saying plainly that it is not.
- [x] Record that an absent status axis carries meaning. A status advice bearing only the settlement
  status means the transaction is matched, not that its matching status is unknown, so the downstream
  mapping must not fill it with a null and read that as unmatched. This is the second constraint of
  its kind after the no-reference sentinel, and together they say that absence in these messages is
  not the database's null. The Bronze-to-Silver mapping has to declare, per field, what absence means.
- [x] Apply the whole-list method to the payment messages as well, since the earlier pass over them
  used the discredited search-by-name approach. Seventy-one named entries on the credit transfer,
  twenty-five on the status report. One check is overturned outright and two move from CMOP decision
  to specification requirement. The interbank settlement date is an exclusive or across two levels:
  present in the group header forbids it on the transaction, absent from the group header requires it
  on the transaction. The validation layer asked for it on the transaction unconditionally, which
  under the values CMOP actually generates would have passed violating data and failed compliant
  data, wrong in both directions. The date now sits in the group header by an explicit choice whose
  price is written down: a block whose transactions ever need different settlement dates forces the
  date down a level and the header cleared in the same change, because the exclusive or forbids
  keeping both.
- [x] Resolve the open question about pairing the clearing settlement method with a clearing system
  element, which was left as a puzzle when the payments report was first read. The settlement method
  rules are all prohibitions: clearing forbids a settlement account and the reimbursement agents, and
  says nothing about requiring a clearing system. The example filled it because the example describes
  a specific clearing system. CMOP's values are compliant, and the same passage yields a prohibition
  CMOP must now honour, since all four of those elements are optional in the schema and no validator
  would catch them.
- [x] Sweep the cash management messages the same way. The three report messages carry nearly
  identical constraint lists, which confirms from the specification side what had only been inferred
  from the schemas, that they share one entry structure. The most consequential find is not in these
  messages at all but in the payment message, stated identically in both: the underlying allocation
  list may only be present where the two parties have agreed bilaterally to carry it. That element is
  the sole structural reason the whole cash leg was built on the financial-institution credit
  transfer, and five separate checks rest on it. Nothing about the generated values changes, but an
  unstated premise is now stated: CMOP declares the agreement to hold, and any outward claim that the
  cash leg reconciles back to the securities leg has to carry that condition, because in a market
  without the agreement the transfer message simply does not carry the list. It also explains why the
  real-world problem is hard, which is the thing the primary objective exists to show.
- [x] Split the bank transaction code check in two. The specification does constrain those three
  levels, but only by generality: a non-generic sub-family is not allowed under a generic family. It
  says nothing about whether a given combination exists in the roughly sixteen-hundred-row table.
  Those are different claims with different overturn conditions, so they are now different checks.
- [x] Record three constraints whose wording invites a damaging misreading. Each says one of two
  elements "must be absent", which reads as a prohibition until the following sentence, that both may
  be absent, makes clear it means not-both. Misreading one turns an optional element into a forbidden
  one, and the symptom is a field that is silently always empty, which no check would ever flag. They
  are also a different shape from the settlement-date rule, which is a true exclusive or requiring
  exactly one, so the two shapes are written up separately rather than under one name.
- [x] Freeze the reversal scenario, and drop the dependency that was blocking it. It had been
  recorded as waiting on the corporate-action restatement path, which is wrong: the two interact, but
  the reversal's own values need nothing from restatement. The interaction is now its own scenario,
  and that one genuinely does depend on restatement. Three structural facts came out of the report.
  The reversal must name the confirmation it voids, and that reference is mandatory, which makes it a
  stronger anchor than the cancellation chain's, where the pointer to the original instruction sits
  in an optional block. The reversal carries no reason at all: not an optional one, no such element
  exists, which is worth stating next to the cancellation advice that does carry a reason and the
  payment return that is required to. Any design claiming to explain automatically why something was
  reversed would be inventing information the standard does not carry. And the reversal is a separate
  message that restates the voided leg in full rather than editing the original, so current state is
  the product of two messages.
- [x] Record that the one hard part of the reversal is not in the message. Four of its five checks
  are decidable on the message itself; the fifth is that every aggregate summing settled
  confirmations has to subtract the reversed one. That is the only place a reversal produces a wrong
  number, and it fails silently, since the sum always computes, just over one leg too many.
- [x] Note a new category of element: one whose every branch is a real-world registered identifier,
  with no proprietary alternative. The cash settlement system place is a three-way choice between a
  digital ledger identifier, a bank identifier code and a legal entity identifier. Elsewhere the
  project's answer to a registered identifier is to use a proprietary one and record the deviation;
  here there is no such option, so the element is left out entirely.
- [x] Freeze the payment return, paired with the securities reversal. The first question was which of
  two undo messages to use, and the deciding evidence was not the messages' definitions but their
  reason code lists. The reversal message's eleven reasons are all payment-side operational faults,
  wrong account number, duplication, missed cut-off, and not one of them can say that the securities
  delivery was undone; using it would force the not-specified code and throw away the only
  informative field in the scenario. The return message's list has a code meaning the payment is no
  longer justified, which is exactly the situation. Verified against the current external code sets
  rather than assumed.
- [x] Record the asymmetry the pairing exposes. The securities reversal carries no reason at all,
  while the cash return is required to carry one, so CMOP has to state on the cash side a reason the
  securities side never gave it. That is forced by the two message families' designs, not chosen. The
  handling is to use the single most non-committal valid code, add no free text, and say plainly in
  any outward description that the reason is supplied by CMOP rather than inherited, so that nobody
  reads the chain as evidence that causes can be traced.
- [x] Note the one trap avoided only by reading. The return message may carry an underlying credit
  transfer, but a rule allows it only when the original transaction carried one, and CMOP's original
  carries the allocation list instead. Filling it because the schema permits it would be a violation
  no validator would catch. This is a conditional prohibition on an element that is perfectly
  legitimate elsewhere, which is the shape a generator built on "fill what you can" walks straight
  into.
- [x] Check the two distribution formats of the external code sets against each other, since the
  validation layer already requires every vocabulary verdict to carry a version. Of a hundred and
  forty enumerated code sets in release 2Q2026 v3, a hundred and thirty-seven match code for code and
  three do not. The local instrument set carries a hundred and fifteen codes in the schema
  distribution and ninety in the JSON one; the two clearing system sets differ by four codes and one.
  Every difference runs the same way, with the schema as the superset. This is worse than a version
  mismatch, because both files call themselves the same version: a generator built on one and a
  checker built on the other produce data that is legal, a checker that says it is not, and matching
  version strings on both sides. The schema distribution is now the project's source of record, on
  the grounds that the data is XML and that a superset cannot reject compliant values, and the JSON
  gap is recorded as a known divergence. The verdict now has to carry the format, not just the
  version.
- [x] Correct the code-set decision made an hour earlier, which was right about the facts and wrong
  about what to do with them. The three sets where the schema and JSON distributions disagree turn
  out to differ by exactly the obsolete codes, and checking all hundred and forty enumerated sets
  confirms the JSON membership equals the registered-only membership code for code. So the schema
  distribution is a superset whose extra content is precisely what the validation rule exists to
  reject, and choosing it because a superset cannot reject compliant data would have quietly disabled
  that rule. The judgement table is now built from the spreadsheet filtered on registration status,
  with the JSON as a cross-check that must agree; a disagreement means the release itself is wrong
  and is a reason to stop rather than to pick one. The schema keeps its role for schema validity,
  which is not the same question as business validity.
- [x] Record the one recycled code value in the whole inventory. A local instrument code was made
  obsolete in 2018 under one name by one requester and re-registered in 2021 under a different name
  and meaning by another. It is the only such pair among three thousand three hundred and
  forty-seven, checked pairwise. Nothing needs to change now, since CMOP neither generates that code
  nor spans those years, but it is the only hard evidence for the claim that a code set is a
  slowly-changing dimension keyed by value and validity period rather than an enumeration, and that
  claim decides where reference data has to live.
- [x] Record a spreadsheet-parsing requirement for reference-data ingestion. Empty cells are simply
  absent from the file, so reading values in order of appearance rather than by column coordinate
  shifts every affected row left. It happened on the first parse here and produced a status column
  full of dates, which looks exactly like dirty source data and is not. The failure mode is the
  dangerous kind: every field is individually well-formed, so nothing downstream can catch it.
- [x] Turn the bank transaction code requirement from "take a valid combination from the table" into
  three named codes, because the former cannot be executed by a generator. The table has one thousand
  five hundred and sixty-seven combinations, counted rather than estimated, across eleven domains; the
  two the project uses account for eight hundred and twenty-nine of them. The payment side resolves
  to issued and received financial institution credit transfer, differing only in the family level,
  and the securities side to settlement trade. All three were checked row by row in the published
  table.
- [x] Add a check the combination table cannot make. Since issued and received are both valid
  combinations, putting the issued code on a credit entry passes the table lookup while being wrong,
  so direction against family is now its own check with its own injection, and the table lookup is
  expected to stay silent on it.
- [x] Freeze the allocation-reject scenario, and correct the sketch that defined it. The sketch called
  for multiple versions of one allocation identifier. FIX forbids that: the identifier must be unique
  across every allocation instruction sent as new, so the response to a block-level reject is required
  to carry a new one. Version linkage runs through the reference-identifier chain instead, which turns
  the alignment the scenario exists to test from a group-by on a single key into a backward traversal.
  The goal survives; only the mechanism was wrong. The chain form is also the harder and more realistic
  one, since downstream receives a run of identifiers that are all different.
- [x] Read the field dictionary rather than the message page for the allocation status field, and find
  two values the documentation had missed. The message page lists four; the dictionary lists six,
  adding incomplete and rejected-by-intermediary. Neither is generated here, but writing the legal
  domain as four values would reject compliant data the day fragmentation or the intermediary flow
  arrives. This is the same lesson as the ISO 20022 constraint lists reached from a different
  direction: the message page and the field dictionary are two documents and the message page can be
  incomplete, so searching one of them is not evidence of absence.
- [x] Record that the account-level reject code carries the same value domain as the block-level one
  but is declared in FIXML without any enumeration, so only the project's own validation layer can
  check it. A second instance turned up on the confirmation side, where one Boolean field carries an
  enumeration and another does not. Strictness in FIXML is decided per field, not per datatype, which
  means the validation layer cannot infer from a field's type whether the schema already covers it.
- [x] Freeze the confirmation-reject scenario, and overturn the claim it rested on. The documentation
  said all three confirmation models end in an affirmed state, which is what the specification's own
  summary sentence says. The same page draws two of the three models stopping at received, and states
  that the recipient of a copy confirmation has no power to affirm at all. Only the first model
  reaches affirmed. Since ready-to-settle hangs on that state, the interface between the confirmation
  segment and the settlement segment holds for one model out of three. This is the first registered
  inconsistency where a summary sentence contradicts a diagram on the same page rather than two
  provisions contradicting each other; the diagram is more specific and wins, and the reasoning is
  recorded because the next reader of that sentence will raise the same objection.
- [x] Split the confirmation-reject scenario into three. Copy confirmations and status broadcasts had
  been folded in on the grounds that all three share one recovery path. They share the recovery path
  but not the terminal state, and no terminal assertion can be written for a scenario whose three
  branches end in different places.
- [x] Record that a rejection on a copy confirmation means a transmission or processing failure rather
  than disagreement with the content, so the same status value carries two unrelated meanings and the
  only field separating them is the copy indicator. Any reject-rate figure must be stratified by it
  first; an unstratified rate adds transport faults to business disputes and gets less meaningful as
  the sample grows. The stratification key is itself one of the fields the schema does not constrain.
- [x] Close the question of whether the confirmation side can support reason-code analysis. It cannot.
  The vocabulary has three values and none of them covers a money mismatch, which is what
  confirmations actually get rejected for, so real rejections land on "other" with free text. This is
  a property of the vocabulary rather than of the sample size, and it is written down to block the
  natural next step of collecting more data.
- [x] Record the three copy-paste defects in the confirmation acknowledgement field table, all of them
  inherited from the allocation acknowledgement: a condition naming a field the message does not have,
  a text note referring to an allocation-side code, and a timestamp described as belonging to a
  different message. The errata release did not fix them, so they are the current state of the version
  this project uses, and the reading to be implemented is written down rather than left to whoever
  implements it.
- [x] Settle what "late" measures before freezing the two late-arrival scenarios. The obvious reading
  is impossible: the session layer requires the sending timestamp to be within two minutes of atomic
  clock time and requires the receiver to reject and disconnect otherwise, so no message can be late
  in transit. What this project calls late is a business event that happened before the nightly
  cut-off carried in a message that arrived after it, and the only place that is observable is batch
  membership, which has no field in the protocol at all.
- [x] Record the two duplicate mechanisms and the fact that their dedupe keys are opposite. A possible
  duplicate keeps its sequence number and is mechanically removable; a possible resend carries a new
  sequence number with a byte-identical body, and the specification hands that case to the application
  rather than solving it. That turns "Bronze keeps the session header" from a principle into a
  requirement with a named failure, because a resend and its original agree on every business field
  including the event timestamp.
- [x] Record the trap in the original-sending-time field. It is set equal to the sending time when the
  real value is unknown, so a zero difference means either an instant retransmit or no information at
  all. Averaging them together skews the retransmit-delay distribution while every individual sample
  stays legal.
- [x] Freeze the late-allocation scenario. Its acceptance criterion is not the reconciliation result:
  the first batch reporting a missing allocation is correct behaviour and the next batch clearing it
  is easy. What the scenario exists to prove is that the first batch's published result is restated
  with both versions kept, which is the main business objective itself. An implementation that
  overwrites in place passes every equation check and fails only that, so the injection is paired with
  a second one that differs only in overwriting.
- [x] Record the inversion found while freezing it. The allocation instruction makes the trade date
  mandatory and the event timestamp optional, and the acknowledgement does the reverse, so neither
  message carries both. On the instruction the only guaranteed time information is a date with no time
  of day, which means allocation-side lateness can only be measured in business days. That is the same
  conclusion the session-layer reading reached by an unrelated route. The confirmation pair makes both
  mandatory, so that side can be measured to the second, and the two scenarios must not share a
  threshold.
- [x] Freeze the late-confirmation scenario, the first one crossing both contracts. Because
  ready-to-settle hangs on the affirmation, an affirmation arriving after the settlement date forces a
  choice; the branch that settles without waiting leaves no trace in the data and is excluded on the
  grounds that it cannot be verified, and the other lands on the already-frozen failed-then-late
  settlement scenario. That gives the six-segment chain its first cross-contract causal link rather
  than a mere join. It also introduces a third shape of check: dwell time in a half-finished state,
  which is neither an equation nor a reachability question, and which looks normal in every single
  batch taken alone.
- [ ] Build the chain-traversal check that the reference-identifier chains need. It is the first
  assertion in the catalogue that is not an equation, and the cost is not in the assertion but in the
  validation layer having no such shape. Two scenarios are waiting on it, the two-hop allocation
  correction and its confirmation-side twin, and they should be unlocked together since they share it.
- [ ] Decide whether to build the combination scenarios where a late message is also rejected. Both are
  registered and both are deferred for the same reason: the restatement path and the correction path
  look alike from downstream, so each can mask the other's failure. They are only worth building once
  the two component checks pass on their own.
- [x] Freeze the unbooked-entry reconciliation scenario, and correct the message it was registered
  against. The registered sketch put pending and future-dated entries into the end-of-day statement,
  but that message's own scope paragraph says it carries booked entries only, while the intraday
  report's scope says it carries pending and booked items. The scenario therefore crosses two
  messages rather than living in one, which makes it the second cross-document scenario after the
  late-confirmation one.
- [x] Record that nothing enforces that scope. The statement's complete constraint list runs to
  thirty-one entries and not one of them mentions the entry status, so a message carrying a pending
  entry passes schema validation and passes every constraint while contradicting the paragraph that
  defines what the message is for. This is a fourth distinct shape of gap, after prose disagreeing
  with formalisation, constraints hanging off optional elements, and vocabularies living outside the
  schema.
- [x] Note the fifth way searching a specification by name goes wrong. Searching the report for the
  booked-entry code finds two hits and both are a clearing-channel code that happens to share the
  spelling; the pending and future codes appear nowhere at all, because that vocabulary is an
  external code set. So a name search can miss what is there and also find something else entirely.
- [x] Record that the booking date changes meaning with the status. It is the expected date while the
  entry is pending and the actual date once it is booked, and the value date behaves the same way.
  An assertion that the two dates agree across the two messages therefore looks obviously right and
  is false; the difference is forecast error, which is an output. The generation mix deliberately
  keeps that difference non-zero for part of the population, because otherwise the assertion
  forbidding the comparison would never have any data to prove it works.
- [x] Record how much weaker this anchor is than the group-return one. Every one of the five levels
  from the entry down to the end-to-end identifier is optional, and the transaction detail component
  has twenty-nine elements with not a single mandatory one, which is the second zero-mandatory block
  found. The only pressure the specification applies is a guideline that uses "should". Unlike the
  group return, where the structure forbids per-payment identification outright, here it is permitted
  and simply never required, so a generation convention can fix it. That produces a fourth shape of
  check, structural existence, which asserts the anchor is present before anything asserts it matches.
- [x] Record the prose prohibition with no constraint behind it. Where availability information is
  given the value date must not be used, stated with "must not" and absent from all thirty-one
  constraints. The injection for it expects silence from the schema and from the constraint set, and
  a finding only from this project's own checks.
- [x] Record the reversal direction, which will be needed for the reversal scenario later. The credit
  or debit indicator on a reversing entry describes that entry, not the one being reversed, so signed
  summation over entries is correct and counting entries as payments double-counts.
- [ ] Build the pending-then-rejected variant. It needs the intraday report to be driven by the
  payment status report, so that a payment rejected after being reported as pending disappears from
  the statement rather than appearing as booked. It is the negative twin of the frozen scenario and
  shares its anchor.
- [ ] Build the future-dated variant together with the case where the value date differs from the
  booking date. Both pull the scenario across a day boundary, which is why the frozen version uses
  only the pending status and keeps the two dates equal.
- [x] Take the complete constraint list for all four messages in the cash management family and
  compare them side by side, the first time the whole-list method has been applied across sibling
  messages rather than within one. The intraday report and the end-of-day statement carry thirty-one
  constraints with identical names except one, and that one differs only because the element it
  governs is named differently in each message, so the rule is renamed to match. That is exactly the
  reason the method exists, now confirmed by an independent route. The notification carries thirty,
  missing the balance-availability rule because it has no balances at all, which the structure tables
  say too.
- [x] Record that no constraint in the entire family mentions the entry status, so the split between
  which message may carry unbooked entries and which may not is enforced nowhere.
- [x] Expand the reporting-request message, closing the last open item from the fourth batch. Its
  nine constraints are all generic datatype checks with no business rule at all. The name of the
  report being requested is free text rather than a code, so a request for a message that does not
  exist passes everything. The account is optional while the account owner is mandatory, and the
  reporting period may be left open-ended.
- [x] Record the inverse of the optional-block pattern. Three earlier cases had a whole group of
  constraints go dormant when an optional element was absent; here an optional block makes two of its
  children mandatory the moment it appears. Filtering by entry status therefore forces you to pin the
  direction too, and since the status is a non-repeating choice, asking for both unbooked and booked
  in both directions needs four separate requests or no filter at all.
- [x] Record that the identifier pairing a report back to the request that asked for it is optional
  on the report side, the same shape as the entry-level anchor: permitted, never required.
- [ ] Freeze the request-and-response scenario, registered as the first message in the chain sent by
  the account holder rather than pushed by the servicer. It is blocked on the intraday report
  generator that the unbooked-entry scenario introduces, and its three assertions stay unevaluated
  until then.
- [x] Take the complete constraint lists for the two cancellation messages, which the two frozen
  cancellation scenarios had used without doing so. Twenty-five and twenty-six entries, differing in
  only three places, and one of those has the word "Information" misspelled in the specification
  itself. That is a sixth way searching a specification by name fails, and the hardest to guard
  against.
- [x] Correct the justification in the executed-cancellation scenario. It said the success reason was
  chosen over two alternatives, citing the eleven-value vocabulary. Following the type chain shows
  that branch resolves to a two-value vocabulary whose members are "cancelled by yourself" and
  "other", so the two alternatives do not exist there at all. The chosen value stands; the reasoning
  is void. This is the second time a success-side reason vocabulary has turned out too small to
  support any analysis, after the confirmation reject codes, which promotes it to a reading habit:
  count the vocabulary before promising analysis on it.
- [x] Record that one distribution carries four numbered variants of the cancellation reason
  vocabulary and four of the denial vocabulary, with heavily overlapping code letters and differing
  definitions. Searching by code letters lands on the wrong set. The denied-because-settled code used
  by the frozen scenario has been traced to the specific set that branch actually references.
- [x] Record the asymmetry along the cancellation chain. The requester has eleven reasons available,
  the servicer refusing has ten, and the servicer succeeding has two. So why a cancellation happened
  can only be answered from the request, and the request's reason field is optional, which forces a
  generation convention and an injection for its absence.
- [x] Record the sentinel value. When no reference exists the account-owner transaction identifier
  must literally be the string NONREF, and a formalised rule then requires one of three alternative
  references. That makes a third point on the anchor-strength scale, between an always-present
  identifier and one that is merely permitted: degraded but not gone. Any join on that field has to
  exclude the sentinel first, or every unreferenced transaction matches every other one.
- [x] Narrow what the reversal-and-corporate-action scenario is waiting on. The cancellation request
  carries a corporate-action event identifier alongside a code meaning the original transaction was
  cancelled and replaced because of a corporate action. That is a different model from restatement:
  restatement is a new version of one fact, this is two distinct transactions. So the scenario no
  longer waits on the restatement path, only on corporate-action event identifiers being available.
- [x] Record the second instance this session of the inverse optional-block pattern, in the
  cancellation request's transaction detail block, which makes three of its children mandatory the
  moment the optional parent appears.
- [ ] Follow up the split-and-partial-settlement code found alongside the corporate-action one. It
  names the mechanism by which a transaction is cancelled and replaced to permit partial settlement,
  which is the interface the deferred partial-settlement ordering check needs.
- [x] Open the corporate actions family, an item that had sat unstarted for several batches, reading
  only the part the reversal scenario needs rather than trying to cover thirteen messages.
- [x] Record that the corporate-action event identifier is mandatory, the first strong anchor found
  anywhere in this project. The market-wide official reference is the optional one, and the only
  constraint on it points at an external market-practice document. Since this project has a single
  account servicer, the mandatory servicer-assigned identifier is enough and the official one is not
  generated.
- [x] Record that the specification's own definitions of the two split event types confirm the
  business invariant this project derived independently from accounting consistency: quantity changes,
  unit price moves the other way, aggregate value unchanged. Worth noting because it is a genuine
  independent check rather than two documents copying one source.
- [x] Record the second and worse case of prose disagreeing with formalisation. The prose names an
  element that does not exist anywhere in that message's structure, while the formalisation names one
  that does, and the prose carries a trailing reference to the equivalent rule in the older telex
  standard, which is where the wrong name came from. The reading rule already adopted is strengthened:
  element names appearing in prose must be checked against the structure table.
- [x] Discover that the reversal scenario was registered as one thing when it is three. The
  corporate-action movement reversal has nine reason codes and every one of them is a detail of the
  posting being wrong, not the event being withdrawn, so that message reverses a posting rather than
  an event. Withdrawing an event is a different message entirely, and cancelling-and-replacing a
  settlement instruction is a third path. Only the middle one actually depends on the restatement
  path. The old scenario number is retired and three replace it.
- [x] Record a third same-letters-different-meaning collision in one session, which promotes the
  vocabulary check from three rules to five: results must carry the code set name, not just the code
  value, exactly as they must carry the vocabulary version. Also record that the vocabulary check is
  no longer unique to the payment segment.
- [ ] Take the constraint lists for the remaining twelve corporate-action messages and compare them
  the way the cash family was compared. Only the movement reversal's twenty-four were taken.
- [ ] Decide whether option-bearing events are in scope. The notification and instruction messages
  were left unopened because the only corporate actions generated so far are splits and reverse
  splits, neither of which offers the holder a choice.
- [x] Take the constraint lists for all thirteen corporate-action messages, closing the item opened
  an hour earlier. Four hundred and ninety-six constraints across the family, of which fifty-one are
  formalised, and the notification alone accounts for more than half the formalisations.
- [x] Record that constraint count does not track how consequential a message is. The notification
  carries one hundred and eighteen; the advice that withdraws an already-announced event carries
  fourteen, every one of them a generic datatype or presence check, and not one formalised. So the
  entire meaning of withdrawing an event, that every adjustment derived from it must be rolled back,
  has no basis in the specification at all. That is weaker than the earlier case where a scope
  paragraph said something no constraint enforced: here there is not even a scope sentence.
- [x] Record the three structural facts that shape the event-withdrawal scenario. Its reason code is
  mandatory with exactly two values, issuer withdrawal and servicer processing error, and the two
  differ downstream because only the second permits re-announcing the same event. Its account block
  is a choice between all accounts and a named list, so withdrawing an event for a subset of accounts
  is legal and the check must be per account rather than per event. And it still requires the event's
  completeness and confirmation statuses, so withdrawn-and-confirmed differs from
  withdrawn-and-unconfirmed.
- [x] Draft six invariants for that scenario without freezing it, since it needs the corporate-action
  replay to materialise adjustment factors first. One of them ties the corporate-action path back to
  the main business objective through the same acceptance criterion the late-allocation scenario uses:
  published results are restated with both versions kept. Two unrelated paths demanding the same
  criterion is stronger evidence for it than one.
- [x] Add a corporate-action segment to the validation layer, the fourth segment. It differs from the
  other three in that almost every check is this project's own rather than the specification's, and
  that ratio has to be stated in any outward claim: saying the segment passes validation means it
  passes checks written here, not ISO 20022's.
- [x] Pair the two reversal checks deliberately. The movement reversal and the event withdrawal are
  named alike and look alike, and their consequences are opposite: one rewinds every adjustment the
  event produced, the other corrects a single posting. Writing only the first lets a generator treat
  a bookkeeping correction as a full restatement across every account, which is the most expensive
  error available in this segment.
- [x] Freeze the corporate-action posting reversal. It sits on a fifth shape of anchor, different in
  direction from the four already catalogued: the reversal must say which confirmation it reverses,
  while the confirmation need not give itself an identifier at all unless it is paginated. So a
  reversal can point at something never declared, and both messages are perfectly compliant. The
  generation convention makes the identifier mandatory and the missing case becomes an injection.
- [x] Record the reason-code reasoning. Of the nine reversal reasons, five are cash concepts and a
  split is a pure securities posting with no cash leg, one would change which holdings are affected
  and therefore belongs to a different scenario, leaving two, of which one is "other".
- [x] Pair the invariant that the reversal must not roll back adjustment factors with the one saying
  the event still exists and is still confirmed. They say the same thing from two sides and both are
  kept, because the likely generator error is merging the two messages' handling paths, and that
  error trips both at once. Both firing together is the signal.
- [x] Record that the constraint whose prose names a non-existent element appears word for word in
  two different messages, so it is an error at the source distributed to every message that
  references it, not a typesetting accident.
- [x] Record the strongest evidence yet for name search failing: a correctly spelled rule and a
  misspelled rule with nearly identical prose coexist in one constraint list as two distinct
  constraints, so searching either name finds half the rules.
- [ ] Build the follow-on where a corrected confirmation is resent after a reversal. The check has to
  tell "resent after reversal" apart from "posted twice", which needs the reversal-versus-withdrawal
  check passing first.
- [x] Promote the anchor-strength list to the project's classification baseline and add the column
  saying how each shape's check must be written. Every future reference key gets filed under one of
  the five. The fifth is the easiest to miss because the pointer side looks entirely normal.
- [x] Set the corporate-action sampling mix. The reversal rate is deliberately far above what a real
  market produces, because three of that scenario's six invariants only have data when a reversal
  happens, and sampling at the real rate would leave them permanently unverified. Event withdrawal is
  generated at zero, because producing it would give the roll-back check and the must-not-roll-back
  check data at the same time and let each mask the other.
- [x] Freeze the pending-then-rejected variant. Its whole check is an absence, which makes it the
  legal counter-example to the frozen scenario's main assertion, so that assertion now needs a
  condition. The condition lives on a third message, which is a fourth source of applicability after
  unconditional, a field on the message being judged, and another message on the same chain.
- [x] Record why that fourth source is dangerous. The specification does not require the status
  report at all, so an absent rejection means either the payment was not rejected or it was and
  nobody said so, and the data cannot tell those apart. The new check therefore has to sit alongside
  the existing one that catches this project failing to emit its own status reports; without that
  pairing a generator can make any payment vanish by dropping one message.
- [x] Record that a payment that never booked produces no reversal entry, because the reversal
  indicator describes an entry that undoes a posting and there was no posting. Simply disappearing is
  the correct representation, and appearing as a reversal is an injection.
- [x] Pair this scenario with the denied-cancellation one in the settlement segment. Both ask a
  question an operator asks on the morning after, both are answered by a code in a third message, and
  both have assertions whose satisfied state is that nothing happened. Assertions of that kind look
  permanently green without a paired injection, so both get two injections: one producing a violation
  and one producing legitimate silence.
- [ ] Build the multiple-intraday-reports variant alongside the changed-since-last-query filter. The
  frozen scenario emits one intraday report because the disappearance is already judgeable from the
  statement, and a second report adds volume without adding a check.
