# Virtual-thread experiment design — DRAFT

This is a reviewable proposal, not an approved preregistration, implementation authorization, or experimental result. Source evidence reviewed at `b059710efe659e5b56f092a48a654b685326053b`. The independent selected-baseline gate remains open. No benchmark was executed to prepare this draft.

## Reading order

1. [Protocol](PROTOCOL.md): claims, falsifiers, workload matrix and analysis decisions.
2. [Measurement contract](MEASUREMENTS.md): raw accounting, censoring, uncertainty and validity rules.
3. [Native execution prerequisites](NATIVE_PLAN.md): zero-cost local correctness invocation and proposed performance resources.

## Gate before approval or execution

The coordinator must independently read back the selected baseline source, hashes, build, smoke, behavioral oracle and matched-workload evidence. A commit or worker PASS alone does not close this gate. Resolve active-query cancellation, timeout/error ownership, dynamic-controller workload integration, and the selected Envoy-style scope; distinguish official core versus reduced controller validation. Any unsupported mandatory comparator must remain explicitly blocked or motivate a reviewed narrower claim, not disappear from the comparison.

The official Netflix core report supports its scoped tests and bounded adapters; it does not establish overload performance or whole-repository build coverage. Existing emulated AMD64-on-ARM64 runtime results are correctness evidence only. A newly checked review-package checksum proves only the packaged bytes; it does not verify omitted toolchain binaries, dependency caches or the full original raw-hash set. Historical report wording such as “uncommitted/no push” describes its execution snapshot, not the current repository publication state. This draft reads inherited reports and does not relabel their executions as new local validation. Prior 10/10 native fixed/pool, 11/11 Breakwater-inspired and 17/17 reduced adaptive fixtures remain intact and retain their narrow scope.

After the gate passes, resolve the explicitly provisional numerical choices below with calibration-only evidence; independently review and freeze source/config hashes, tuning grid, randomization schedule, null predictions, analysis script specification and exclusions **before** confirmatory measurements. New observations cannot retroactively alter a frozen claim; amendments precede a new independent dataset and preserve earlier outcomes. A baseline-gate failure leaves this folder DRAFT.

## Scientific decision

Pool sensitivity, a stability map, and adaptive admission alone are established mechanisms. A new VT-specific claim requires a material held-out residual mode × pool effect beyond queueing, driver/framework differences, pinning, carrier capacity, GC and resource contention. If conventional explanations suffice, report the negative or narrowed result; do not implement a candidate controller merely to continue the project.

## Sources and evidence boundary

- [JEP 444](https://openjdk.org/jeps/444) and [JEP 491](https://openjdk.org/jeps/491); [Oracle JDK24 migration changes](https://docs.oracle.com/en/java/javase/24/migrate/significant-changes-jdk-24.html) independently confirms the synchronized-unmounting change. JEP491 direct retrieval was unavailable during this review; no new direct-read claim is made.
- [Official Netflix source](https://github.com/Netflix/concurrency-limits/tree/78a74b9878d38c4c048b0304ce12a162ab7b7222), repository `artifact/netflix-validation/REPORT.md` and frozen trace/lock evidence.
- [Envoy adaptive-concurrency documentation](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/adaptive_concurrency_filter.html); execution must pin the repository revision in `research/BASELINE_ARTIFACTS.md`, not mutable latest docs.
- Repository `research/DIFFERENTIATION.md`, `research/CLOSEST_PRIOR_ART.md`, `artifact/baselines/README.md`, `artifact/review/VALIDATION_AUDIT_REPORT.md` and `artifact/runtime-validation/README.md` establish prior-art, reduced-equation and correctness boundaries. This proposal does not modify them.

## Draft definition amendment

This text amendment responds to the source-text review at `research/experiment-design-review/REVIEW.md` (review commit `074842a940fe8f5353e7696574408445a14e4c1a`; reviewed draft `ae30dacddc765ceb98037ac8cf3bf9b5531afea7`). It separates the joint normalized-load estimand from a fixed-arrival pool intervention, acknowledges mode-blind prediction cancellation, proposes a separate held-out predictive decision, defines restricted queue residence and censoring, selects one Bonferroni common-direction rule, and accounts for permanent noncompletion in all-offered tails. These are prospective draft changes, not retrospective preregistration or verified coverage. Earlier definitions remain available at the reviewed source commit. Calibration capacity definitions/uncertainty, null validation, fixed-arrival rate/family, independent-block precision and native feasibility remain OPEN; baseline/design gates remain OPEN. No pilot, candidate, calibration or benchmark was performed for this amendment.
