# DRAFT — Virtual Threads and Finite Downstream Capacity: A Controlled Investigation

Intended venue: IEEE Transactions on Parallel and Distributed Systems. Editorial skeleton only. Authors and affiliations: pending confirmation. Novelty: UNVERIFIED. Methods: PROPOSED, pending selected-baseline gate approval. Results: PENDING.

## Abstract — draft problem statement

Java virtual threads support highly concurrent blocking applications, while finite downstream resources still constrain service capacity [R1]. This proposed investigation asks whether a runtime-dependent interaction with finite downstream pools remains after accounting for ordinary queueing, workload demand, framework behavior, and version-dependent pinning. Existing overload controllers already address latency objectives, queue-delay feedback, contention, and global service dependencies [R3–R7]. The intended comparison would therefore test explanatory and control equivalence against those established mechanisms before considering a contribution claim. No experimental outcomes, improvements, or novelty conclusions are reported in this draft.

Index terms: virtual threads; admission control; queueing; reproducibility.

## 1. Introduction

Oracle's Java 21 guidance recommends explicit concurrency boundaries for scarce services and describes database connection pools as such boundaries [R1]. Consequently, observing a saturated pool behind many virtual threads would not by itself establish a new mechanism. Adaptive admission and overload recovery likewise have substantial prior art [R3–R7].

The research question is conditional: after matching offered work and downstream capacity, is any remaining execution-mode effect unexplained by established queueing and admission mechanisms? A second question is whether any proposed control adds value over properly tuned established comparators. These are questions, not findings or promised contributions.

Any eventual contribution paragraph must identify an excluded established explanation, an operational discriminator, and a falsifier. Candidate claim slots are listed in the ledger. A null or equivalent result would require narrowing the paper to a reproducibility/negative-result account if that account is independently justified; it would not support relabeling ordinary queueing as novelty.

## 2. Background and related work

### 2.1 Concurrency boundaries and runtime versions

Virtual-thread availability does not eliminate finite database capacity. Pool-only and fixed-semaphore policies are essential controls rather than novel proposals [R1]. Runtime-version comparisons are necessary: JDK 24 changed blocking within `synchronized` constructs to release the underlying platform thread, eliminating nearly all pinning cases described by that release note [R2]. A JDK 21 observation therefore cannot be generalized unchanged to JDK 24/25. Remaining native/foreign-call paths must be isolated and observed, not assumed covered by a monitor fixture.

### 2.2 Established overload mechanisms

Welsh and Culler adapt stage-level admission to bound a response-time percentile [R3]. Breakwater uses server-side queue-delay credits and additional overload mechanisms [R4]. Protego uses marginal-throughput feedback under unpredictable lock contention and a separate synchronization mechanism [R5]. Bouncer estimates percentile response time per query and supports class-specific objectives and starvation safeguards [R6]. TopFull uses global observations and per-API entry control for SLO-compliant goodput [R7]. These mechanisms preclude claims that adaptive limiting, a contention-sensitive signal, or SLO-aware shedding alone is new.

Netflix Gradient2 and Envoy are engineering comparator families; the repository distinguishes source-derived reduced equations from official artifacts. Their exact implementation/version claims must follow pinned source and validation evidence, not a mutable product overview. The broader queueing, multi-tier admission, Quarkus, and pool-sizing references already inventoried in `research/CLOSEST_PRIOR_ART.md` remain required related-work expansion before submission; entries not freshly checked here are not represented as newly verified citations.

## 3. Problem definition and hypotheses — PROPOSED

The conceptual system has arrivals, an admission boundary, an execution mode, and a finite downstream pool. Waiting before admission, waiting for a connection, and downstream service are separate quantities. Offered, accepted, completed, rejected, timed-out, and cancelled requests require separate counts. SLO-compliant goodput counts successful completions meeting the specified end-to-end deadline per measurement interval; rejected requests must not disappear from the load denominator.

Candidate hypotheses and rejection conditions are H1–H3 in the ledger. Stability, collapse, recovery, the measurement window, and practical equivalence margins require preregistered operational definitions. A latency plateau or a rising queue alone will not be called a new phase transition. Little's Law, if used, is an accounting relationship under its applicable conditions, not proof of causation or a stationary model for transient overload.

## 4. Methods — PROPOSED; NOT APPROVED OR EXECUTED

This section reserves the eventual protocol structure. It does not freeze parameters, authorize sweeps, or implement a candidate controller. After gate approval, link the approved versioned protocol rather than silently promoting these notes.

### 4.1 Matched execution and runtime controls

Compare virtual-thread, bounded platform-thread, and genuine reactive execution with matched request semantics, downstream fixture, transaction/isolation behavior, capacity, timeout/cancellation policy, and offered arrival schedule. Compare JDK 21 with JDK 24/25; distinguish an observed JDK 25 run from unexecuted JDK 24 coverage. Record carrier parallelism, JFR configuration/events, CPU allocation, heap/GC, native/foreign paths, and instrumentation overhead. Driver/framework differences are confounders requiring explicit bounds.

### 4.2 Comparator qualification

Retain no-extra-admission/pool-only and fixed-limit controls. Qualify USITS-style, Breakwater-inspired, Gradient2/Envoy, Protego-style, Bouncer-style, and topology-appropriate TopFull comparators before their use. For each, identify official artifact versus reduced reimplementation, immutable source, build/dependency closure, frozen independent expected traces, behavior omissions, and matched workload compatibility. Any infeasible comparator requires an explicit scope decision before execution; omission cannot imply superiority. Tuning budgets and observations available to controllers must be comparable and fixed before held-out evaluation.

### 4.3 Workload, null models, and analysis

Reserve fields for arrival-process generation and load-generator capacity, service-demand distributions, capacity shifts, pool sizes, warmup, run duration, independent repetitions/seeds, run-order randomization, uncertainty estimation, and treatment of timeouts/censoring. Avoid coordinated omission and selection of only successful-response latency. Fit/check an ordinary finite-capacity queueing explanation before introducing a virtual-thread-specific effect. Reserve held-out workloads for prediction and controller assessment. No numerical choices, power calculation, or statistical significance is claimed here.

## 5. Evidence status — correctness only

At preparation, the repository contains fixed/pool contracts, a reduced Breakwater-inspired comparator, reduced Gradient2/Envoy equations, a runtime-smoke audit, and an official Netflix core/integration report. Their source locations and evidence limits appear in the ledger. Historical preparation-only documents coexist with later audit reports; their old environment availability statements must not overwrite later bounded observations.

The runtime-smoke audit records AMD64 execution on an ARM64 host. This is correctness evidence under emulation, not native performance evidence. Official Netflix core/adapter validation does not certify all Netflix modules, official Envoy, dynamic overload control, active-query cancellation, JNI/foreign coverage, or aggregate scientific readiness. Counts in validation reports are test outcomes, not paper benchmarks. This draft performs no new runtime execution and does not independently recertify those packages.

## 6. Results — PENDING

No data, numerical comparison, figure, or result table is supplied. Future subsections, only after approved execution and provenance review: null-model fit; runtime/pool interaction; JDK/pinning controls; comparator equivalence; workload-shift recovery; sensitivity and negative results. Each subsection must cite immutable configuration/raw-output/analysis provenance and report uncertainty and failures. Remove a subsection if no justified evidence supports it.

## 7. Discussion and threats to validity — PENDING

Required topics include queueing explanations; framework/driver mismatch; JDK-version attribution; load-generator saturation; warmup/JIT/GC; instrumentation effects; emulation versus native execution; finite sampling of tails; tuning leakage; censoring and retries; workload and topology scope; omitted comparator behavior; and the difference between equation conformance and system equivalence. No generalization beyond observed native environments is warranted.

## 8. Conclusion — PENDING

A conclusion will be written from approved evidence, including null results. There is presently no supported claim of a novel mechanism, superior controller, or performance gain.

## Reproducibility statement — DRAFT

Follow `artifact/REPRODUCIBILITY.md` and the additional review checklist. All reported evidence must resolve to immutable source/configuration and raw artifacts with processing commands; record transformations of review copies and exclusions. Authorship, acknowledgments, funding, data availability, and publication disclosures remain unfilled pending factual confirmation.

## References

Use verified entries R1–R7 in `CLAIM_SOURCE_LEDGER.md`. Other prior-art citations remain expansion tasks, not fabricated bibliography records.
