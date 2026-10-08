# DRAFT — Claim-to-source ledger

Primary-source checks: 2026-10-08. Claims below are paraphrases; no quotations are used. Location descriptions permit verification without relying on search-result identifiers. A primary abstract supports only its stated mechanism; this check does not certify implementation equations, reproduce experiments, or establish applicability to this project.

## Checked references and exact support

| ID / reference | Primary URL and checked location | Supported manuscript claim | Boundary |
|---|---|---|---|
| R1. Oracle, *Virtual Threads*, Java Platform, Standard Edition 21 Core Libraries | https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html — “Don't Pool Virtual Threads,” semaphore example and following pool paragraph | Scarce-service access can be bounded with semaphores; a database connection pool already provides a concurrency boundary. | Guidance, not a benchmark or evidence that extra admission never helps in every system. |
| R2. Oracle, *JDK 24 Release Notes*, March 18, 2025 | https://www.oracle.com/java/technologies/javase/24-relnote-issues.html — Major New Functionality / Performance and Runtime / “Synchronize Virtual Threads without Pinning,” links JEP 491 | JDK24 allows virtual threads blocking in synchronized constructs to release underlying platform threads; the note says nearly all pinning cases are eliminated. | Does not establish zero pinning in every native/foreign path or observed behavior of our runtime. |
| R3. Matt Welsh and David Culler, “Adaptive Overload Control for Busy Internet Servers,” USITS, 2003 | https://www.usenix.org/conference/usits-03/adaptive-overload-control-busy-internet-servers — abstract and publisher BibTeX | Adaptive stage-level admission targets 90th-percentile response time, with request queues and extensions for service differentiation. | Does not certify a repository reimplementation or VT-specific behavior. |
| R4. Inho Cho, Ahmed Saeed, Joshua Fried, Seo Jin Park, Mohammad Alizadeh, and Adam Belay, “Overload Control for μs-scale RPCs with Breakwater,” OSDI, 2020, pp. 299–314 | https://www.usenix.org/conference/osdi20/presentation/cho — abstract and publisher BibTeX | Server-driven credits use queueing delay; demand speculation, piggybacking, and active queue management are distinct parts of the system. | Reduced equation checks omit system behavior. No published speedup/recovery number is transferred to this project. |
| R5. Inho Cho, Ahmed Saeed, Seo Jin Park, Mohammad Alizadeh, and Adam Belay, “Protego: Overload Control for Applications with Unpredictable Lock Contention,” NSDI, 2023, pp. 725–738 | https://www.usenix.org/conference/nsdi23/presentation/cho-inho — abstract and publisher BibTeX | Marginal-throughput credit admission addresses unpredictable lock contention; ASQM is a separate synchronization mechanism. | A marginal-throughput-only comparator is not all of Protego. |
| R6. Hao Xu and Juan A. Colmenares, “Admission Control with Response Time Objectives for Low-latency Online Data Systems,” arXiv:2312.15123v1, December 23, 2023 | https://arxiv.org/abs/2312.15123v1 — title/authors, submission history, abstract | Bouncer estimates percentile response times per incoming query, supports class objectives, and supplements admission with starvation-avoidance variants. | Cite this checked preprint version. Existing audit's SIGMOD 2024 venue/prefixed title needs publisher verification before a final venue citation. |
| R7. Jinwoo Park, Jaehyeong Park, Youngmok Jung, Hwijoon Lim, Hyunho Yeo, and Dongsu Han, “TopFull: An Adaptive Top-Down Overload Control for SLO-Oriented Microservices,” ACM SIGCOMM, 2024, DOI 10.1145/3651890.3672253 | https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final654-acmpaginated.pdf — p. 1 abstract and ACM Reference Format; §§4 and 6 | Global observations and per-API entry control target SLO-compliant goodput; topology affects the comparison. | No TopFull experimental numbers are reproduced or treated as VT evidence. |

JEP 444 and JEP 491 direct page retrieval returned HTTP 403 during this check; first-party indexed summaries were available, but the complete JEP text was not reverified. R1 and R2 supply the narrower claims actually used. Existing JEP URLs remain useful primary leads: https://openjdk.org/jeps/444 and https://openjdk.org/jeps/491. Native/foreign pinning coverage remains an explicit control requirement, not a freshly verified exhaustive taxonomy.

## Conditional project claims — none established

| ID | Proposed claim under investigation | Established explanation to exclude | Operational discriminator, pending approved protocol | Falsifier / narrowing condition |
|---|---|---|---|---|
| H1 | Residual execution-mode interaction with finite pools | Ordinary finite-capacity queueing, service demand, and pool sizing | Matched arrivals/demand/capacity; compare measured wait/service trajectories to a preregistered null model across execution modes. | Null model or matched platform/reactive controls explain the boundary within prespecified uncertainty/equivalence margins. |
| H2 | Mechanism persists beyond old monitor pinning | JDK21 monitor pinning, carrier starvation, framework/driver mismatch | Compare JDK21 with JDK24/25; observe JFR/carriers and separately isolate native/foreign paths and framework modes. | Effect disappears after JEP491, tracks pinning, or vanishes with matched frameworks. Narrow to that established explanation. |
| H3 | Added control value over established policies | Fixed/pool limits, percentile admission, credits, gradients, marginal throughput, class SLOs, global entry control | Preregister workload/capacity shifts, fair information/tuning budgets, held-out evaluation, SLO-goodput and recovery definitions. | A fixed or established controller is equivalent; gains require hindsight, unmatched information, or a single topology. |

A stability surface, early-warning signal, adaptive limiter, or pool sensitivity alone is not a contribution. The bounded search's failure to find a direct match is not evidence of originality. H1–H3 must remain conditional until an explicit gate decision and supporting experiments.

## Repository evidence anchors — provenance, not paper results

| Evidence anchor | What may be stated now | What must not be inferred |
|---|---|---|
| `artifact/results/baseline-validation/java17-native/validation.json` | Existing fixed/pool contract evidence is available. | VT performance or JDBC/reactive equivalence. |
| `artifact/results/baseline-validation/breakwater-inspired/validation.json`; `artifact/baselines/README.md` | Reduced paper-derived equations and declared deviations are recorded. | Author-artifact reproduction, distributed Breakwater behavior, or timing validity. |
| `artifact/results/baseline-validation/adaptive-controllers/validation.json`; `artifact/baselines/README.md` | Reduced source-derived Gradient2/Envoy checks preserve pinned upstream identity. | Official Envoy or complete Netflix behavior. |
| `artifact/review/VALIDATION_AUDIT_REPORT.md`; runtime review ZIP and companion checksum | Historical runtime correctness audit records emulated AMD64 on ARM64 and bounded JFR/held-batch evidence. | Native performance, JNI/FFM completion, or a new execution by the manuscript author. |
| `artifact/netflix-validation/REPORT.md`; Netflix review ZIP and companion checksum | Reported official core, frozen traces, and bounded adapter evidence; inspect package for raw evidence. | All-module certification, active-query cancellation, dynamic overload success, or aggregate readiness. |

These are repository-relative anchors; immutable commit URLs and raw-manifest hashes must accompany any future result. The two reports contain historical local/uncommitted wording and refer to raw directories not all present as loose repository files. Their compact review archives contain selected evidence with documented exclusions. This draft does not convert those narrative statements into newly observed facts. Package checksum verification does not verify omitted binaries or the complete original raw-hash set. Historical “uncommitted/no push” wording describes the execution snapshot, not current publication state. Distinguish newly observed package checks from inherited local validation. Reconcile superseding evidence through gate review, preserving old reduced/fixed/pool evidence.

## Unresolved bibliography and attribution work

- Reuse the broader audit and search log; verify primary full-text passage and final metadata before incorporating queueing-stability, WWW 2004, Quarkus/DEBS, pool-sizing, or DAGOR claims into manuscript prose.
- Before citing implementation formulas, read the exact pinned Netflix/Envoy blobs and map omissions; current mechanism-level draft does not quote or certify formulas.
- Verify current IEEE TPDS preparation requirements from the official venue before typesetting. No submission is authorized.
- Preserve exact publication titles, version, author order, and venue; do not infer an author's affiliation or invent manuscript authorship.
