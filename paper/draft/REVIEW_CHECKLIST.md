# DRAFT — Reproducibility and skeptical-review checklist

Unchecked boxes are requirements or unresolved decisions, not assertions of work completed. No item here opens the selected-baseline gate. This checklist extends the repository's reproducibility contract without replacing historical evidence.

## Editorial checks completed for this skeleton

- [x] DRAFT, unverified novelty, proposed-only methods, and pending results are explicit.
- [x] No author/affiliation, data point, outcome figure, or performance gain is invented.
- [x] Seven primary-source references have a checked location and bounded supported claim.
- [x] Source-retrieval limitations and pending bibliography are disclosed.
- [x] H1–H3 each state an excluded established explanation, discriminator, and falsifier.
- [x] Fixed/pool, Breakwater-inspired, and reduced Gradient2/Envoy evidence remain separately identified.
- [x] JEP491 and correctness-only emulation limits are explicit.

## Before approving experiments

- [ ] Coordinator records aggregate selected-baseline decision with immutable evidence, required comparators, accepted deviations, and remaining exclusions.
- [ ] Each selected comparator has pinned sources/license, resolved dependency/tool closure, build/smoke evidence, and matched workload-interface checks.
- [ ] Independent expected traces and tolerances are frozen and hashed before actual outputs. Oracle provenance and any common-author limitations are disclosed.
- [ ] Official artifacts and reduced reimplementations are named accurately; failures and unavailable checks remain visible.
- [ ] Native measurement environment is available under the authorized zero-cost constraint; architecture, virtualization/emulation, actual JDK outputs, CPU/memory/kernel/container settings, and resource limits are observed. Registry labels alone are insufficient.
- [ ] JDK21 and post-JEP491 comparisons, carrier settings, JFR event configuration, native/JNI/foreign coverage or explicit exclusions, and framework/driver differences are decided.
- [ ] Approved protocol fixes arrivals, downstream semantics, capacities, timeout/cancellation/retry behavior, workload shifts, tuning budgets, warmup, repetitions/seeds, order, duration, and stop rules.
- [ ] Stability/collapse/recovery/SLO-goodput definitions, queueing null model, equivalence margin, uncertainty method, censoring policy, and held-out evaluation are specified before outcomes.

## Before accepting a result into the manuscript

- [ ] Exact source/config/dependency/runtime hashes and command/exit/log records resolve to each run.
- [ ] Raw outputs are retained unchanged; exclusions, missing samples, crashes, retries, and transient failures are reported.
- [ ] Offered/accepted/completed/rejected/timed-out/cancelled accounting reconciles; cancelled or rejected work is not hidden from outcome denominators.
- [ ] Admission wait, pool wait, service time, and end-to-end time are separated with justified instrumentation.
- [ ] Load generator has demonstrated spare capacity; arrival scheduling avoids coordinated omission; statistical unit is an independent run where appropriate.
- [ ] All derived tables/figures regenerate from committed scripts and raw inputs; uncertainty and relevant negative results are included.
- [ ] Timing evidence comes from the declared native measurement environment. AMD64-on-ARM64 smoke supports only correctness.
- [ ] Review copies map to original hashes with redaction/transformation/exclusion records; packaged checksums are not confused with omitted raw-file checksums.
- [ ] Second review checks actual evidence, not just a worker status, report summary, or successful exit.

## Skeptical reviewer questions

1. Does ordinary queueing plus a finite pool explain everything? If so, H1 fails; retain that finding without claiming a new stability phenomenon.
2. Does the effect disappear after JEP491, track native/foreign pinning or carrier starvation, or disappear when frameworks match? If so, narrow H2 accordingly.
3. Would a fixed limit chosen without hindsight or an established controller do as well within the prespecified equivalence margin? If so, H3 fails.
4. Is the apparent gain caused by shedding more work, relaxing SLOs, changing information or tuning budgets, selecting only successes, or changing downstream semantics?
5. Are reduced equations being mistaken for a full baseline, or deterministic held-batch behavior for adaptation under load?
6. Does the evidence span enough workloads/capacities/topologies for the stated scope, and are omissions and unsuccessful configurations visible?
7. Does every factual related-work sentence have primary support? Have all outcome/novelty sentences survived claim-to-source review?

## Before publication preparation

- [ ] Confirm authorship, affiliations, contributions, acknowledgments/funding, disclosures, and artifact availability from supplied facts.
- [ ] Verify current official TPDS format, length, review/anonymity, and artifact requirements; typeset and visually check the complete manuscript.
- [ ] Replace every pending placeholder using approved evidence or remove it; refresh literature within the documented scope.
- [ ] Obtain explicit publication/submission authorization. This draft grants none.
