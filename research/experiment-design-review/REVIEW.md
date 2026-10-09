# Skeptical review of the VT experiment draft

**Decision: FAIL for freeze readiness; PASS as a clearly bounded draft.** This is a source-text review, not a preregistration, benchmark, implementation, new literature review, or authorization to execute. No raw experimental results exist in this review. All numerical examples below are planning arithmetic, not observations.

Reviewed immutable source: `ae30dacddc765ceb98037ac8cf3bf9b5531afea7`, specifically `research/experiment-design/{README,PROTOCOL,MEASUREMENTS,NATIVE_PLAN}.md`. The existing draft is unchanged. Section references below refer to those files at that commit. Proposed amendments are recommendations for independent review, not applied changes.

## Decision register

PASS means the source states an adequate draft-level safeguard. FAIL means a definition or inference needs correction before freeze. OPEN means an explicit prospective choice, calibration result or external gate is still needed; it is not a failed experiment.

| Item | Decision | Source anchor | Reason / minimum action |
|---|---|---|---|
| DRAFT and baseline/execution boundary | PASS | README: Gate before approval or execution | Explicitly gates approval, implementation and confirmatory data; preserve this boundary. |
| Pool versus offered-load estimand | FAIL | PROTOCOL: Questions, estimands and rejection rules | Pool-specific capacity normalization changes absolute offered rate with pool. The contrast identifies a joint pool/load policy interaction, not an isolated pool intervention. Define the target and add a common-absolute-rate contrast before claiming a causal pool effect. |
| Calibration capacity definition | OPEN | PROTOCOL: Matched workload and matrix | Independent and common-across-modes is necessary but does not specify how capacity is measured, its uncertainty, or saturation criterion. Freeze those choices before workload selection. |
| Mode-blind residual discriminator | FAIL | PROTOCOL: Questions; Queueing null ladder | Identical mode-blind predictions cancel from the stated within-pool mode contrast. The residual contrast alone is not an additional test of the queueing explanation. Require a separate, quantitative held-out model adequacy and intervention decision. |
| Pool-wait endpoint population | FAIL | PROTOCOL: primary endpoint; MEASUREMENTS: Raw records and accounting | Mean pool wait is undefined for work never entering/acquiring the pool; completion-only measurement selects survivors. Define the population, censoring and treatment of non-entry before computing the primary contrast. |
| Simultaneous interval decision | FAIL | PROTOCOL: H1 decision; MEASUREMENTS: Uncertainty and decisions | Family-level 95% versus per-contrast 97.5% wording can be compatible but is not operationally reconciled. Holm tests and fixed Bonferroni intervals are different procedures; choose one authoritative confirmation rule and exact direction handling. |
| Ten-block uncertainty | OPEN | PROTOCOL: Repeats; MEASUREMENTS: Uncertainty | Ten independent paired blocks is a proposal, not demonstrated precision or calibrated coverage. 10,000 resamples do not create independent blocks. Require prospective precision assessment and specify the resampling hierarchy. |
| Tail and censoring reporting | PASS / FAIL | MEASUREMENTS: Offered load and tails | Conditional-tail labels, outcome denominators and unresolved reporting are good. A 1% unresolved cutoff alone does not define identification of all-offered completion p99 when rejection/error/noncompletion are present. Amend the estimand. |
| Tail sample-size floor | OPEN | MEASUREMENTS: Offered load and tails | 100,000 successes implies about 100 observations above p99.9, not a precision guarantee. Clarify cell aggregation and run-level uncertainty; retain conditional descriptive reporting below the floor. |
| Native resource and wall-time proposal | PASS / OPEN | NATIVE_PLAN: Proposed future performance allocation | 1,800 trials / 135 h and 240 trials / 18 h arithmetic is correct for 270 s per trial; runtime feasibility, calibration, storage and overhead remain unmeasured. |
| Runtime and comparator falsifiers | PASS | PROTOCOL: RQ2, Controller fairness, causal checks | JEP491/monitor boundary, native/foreign isolation, framework differences and conventional-controller explanations are retained. No new novelty follows from the draft. |

## 1. Separate a pool intervention from a normalized-load intervention

The draft sets the primary load to 1.0 times separately calibrated capacity for each pool, common across modes. Thus the small-pool comparison runs at one absolute arrival rate and the large-pool comparison generally runs at another. Sharing arrivals within each pool makes the VT/PT comparison fair at that pool; it does not hold arrivals fixed across the pool contrast.

This need not invalidate a useful question about behavior near each pool's nominal saturation. It changes the estimand. A mode-by-pool contrast across those cells can also reflect a mode-by-arrival-rate effect or differing calibration errors. Randomizing pool/run order does not remove a deliberately co-varying offered rate.

**Minimal proposed amendment:** name the current primary contrast the "mode interaction with pool-specific normalized-load policy." State that it cannot isolate pool size alone. Before a causal finite-pool claim, add a preregistered paired comparison using exactly the same absolute arrival schedule at pool 2 and pool 16; choose its rate using calibration only. Retain the normalized-load contrast as a distinct estimand. Do not silently substitute this new contrast after seeing outcomes.

If that additional contrast is infeasible, narrow RQ1 to the joint policy question rather than claiming that matching normalized utilization removes confounding. A common rate may leave one pool lightly loaded and another saturated; that is a feature of the fixed-arrival pool intervention, not a reason to retune each arm.

**Capacity choices still OPEN:** define calibration workload, reference execution path, capacity statistic, stationarity criterion, duration, repeats, service-demand measurement boundary, and handling of CPU/DB saturation. Prefer a declared external service-capacity reference or an explicitly chosen reference arm; do not average execution-mode outcomes without defining the resulting target. Record uncertainty in capacity and thus in the selected absolute rates. Equal numerical load ratios need not mean equal actual utilization under mode-dependent service demand. Do not use confirmatory overloaded outcomes to revise the calibration denominator.

## 2. The residual contrast needs a separate model-discrimination rule

The stated residual is observed log(mean pool wait + 1 ms) minus its mode-blind prediction. If that prediction is identical for VT and PT within a pool, then it cancels:

`r_VT,c - r_PT,c = y_VT,c - y_PT,c`.

Consequently the proposed difference-in-differences D is algebraically the same as the raw transformed-wait interaction. Calling it a residual does not, by itself, establish that GI/G/c or a stronger conventional explanation failed. The draft separately requires failure of conventional alternatives, but that requirement lacks a frozen quantitative decision.

If predictions instead use mode-specific calibrated service demands, worker capacities or driver overhead, cancellation need not occur. Then the null is not fully mode-blind and the inputs, calibration uncertainties and interpretation must be explicit. Post-treatment overloaded occupancy/service measurements must not be fed back into the null as if exogenous.

**Minimal proposed amendment:** keep D as the descriptive/confirmatory interaction estimand, define the null's inputs and prediction equality conditions, and specify an independent held-out predictive check with declared outcomes, discrepancy statistic, prediction intervals and decision threshold. Choose the conventional model ladder with calibration data. A failed predictive check is evidence against that specified model, not automatically evidence for a VT mechanism. Require a targeted intervention and independent prediction of its effect before applying that stronger label. No simulator is implemented or validated by this review.

## 3. Define pool wait for failures and non-entry

The raw contract records every scheduled request, which is a strong safeguard. It does not yet define which of those requests contribute to mean pool wait. An admission-rejected request never enters the pool queue. A queued request that times out before acquisition has no acquire timestamp. A client timeout can also precede later server acquisition. Discarding any of these cases can reverse an arm comparison through selection.

**Minimal proposed amendment:** specify separate quantities rather than giving invented wait values:

1. Among requests that enter the pool queue, measure time from enqueue to acquisition or terminal departure from that queue. Distinguish acquisition, abandonment/cancellation, error and unresolved queue residence at the cutoff. This is queue residence, not necessarily wait-to-acquisition.
2. Report the population fraction reaching pool enqueue, acquisition probability and all scheduled terminal outcomes beside that conditional estimand. State that entry is treatment-dependent, so the conditional contrast alone is not an all-offered causal effect.
3. If the primary endpoint remains wait-to-acquisition, define treatment of competing departures and unresolved work; do not treat abandoned requests as observed acquisitions or apply an unqualified survival estimator. If acquisition is never reached, a finite acquisition time is not observed.
4. Define run-level means, any fixed truncation horizon, zero-entry cells, offsets and aggregation before computing D. A change from acquisition wait to queue residence changes the target and must precede freeze.

The existing every-request goodput/outcome denominators should remain an unconditional companion decision. No single replacement primary endpoint is imposed here; the scientific target requires coordinator choice.

## 4. Make interval and replication decisions executable

PROTOCOL asks for a simultaneous 95% CI outside the practical band and same-direction replication in a second distribution. MEASUREMENTS proposes Holm tests at family alpha .05 plus 97.5% per-contrast intervals. Two 97.5% marginal intervals can provide at least 95% simultaneous coverage by Bonferroni if their marginal coverage is valid; they are not generally the inversion of Holm tests. The current wording leaves unclear which outcome wins if tests and intervals disagree.

**Minimal proposed amendment:** use one authoritative confirmation rule, for example: for each of the two JDK25 demand-distribution contrasts, construct the prespecified 97.5% two-sided interval; declare the joint confirmation only when both lie wholly above +log(1.10), or both wholly below -log(1.10). Label this a Bonferroni family-coverage rule, conditional on valid marginal intervals. Treat Holm results, if retained, as explicitly secondary. This is a proposed conservative rule, not a claim that its small-sample bootstrap coverage is established.

State whether direction is prespecified or either common direction is acceptable, what the JDK21 comparison contributes, and which result constitutes H2 confirmation. Specify paired uncertainty for any direct JDK interaction; two separate significance decisions are not a test of a difference. Keep equivalence, absence of evidence and inconclusive precision distinct. These clarifications do not turn exploratory carrier/driver/heap checks into additional confirmatory findings.

## 5. Ten blocks and calibration uncertainty need prospective assessment

The source correctly chooses independent runs/blocks as experimental units and preserves pairing. However, a nonparametric bootstrap from ten blocks has only ten observed independent units; extra resamples improve numerical evaluation of that empirical distribution, not coverage or representativeness. Rare host/day effects and heavy-tailed block contrasts can remain poorly characterized. Neither ten blocks nor the 100,000-request floor demonstrates power for a 10% practical band.

**Minimal proposed amendment:** specify whether a block spans both pools, both modes and both demand distributions; specify how JDK/day order is balanced. Resample complete paired vectors, not the four arms independently. For estimated null predictions, nest calibration resampling outside confirmation-block resampling and preserve the shared calibration across affected cells; freeze how each refit/prediction propagates uncertainty. If the mode-blind prediction cancels from D, acknowledge that cancellation rather than adding independent model noise to each arm.

Before freeze, use a separate pilot only to assess precision and choose a fixed prospective number of independent blocks or a narrower claim. Document the interval method and sensitivity to individual blocks. Pilot outcomes cannot also serve as the supposedly untouched confirmatory dataset. If ten blocks are all that can be afforded, report the precision limitations and allow an inconclusive result. No deadline or limited compute justifies treating individual requests as replacement independent replicates, omitting valid poor trials, or lowering the evidence standard after observations.

## 6. Completion tails require a population definition

Successful-only latency percentiles are correctly labeled conditional in the draft. The proposed rule "where >1% unresolved, an all-offered p99 completion time is not identifiable" is incomplete: rejected, permanently cancelled or errored requests may never complete successfully even when none is unresolved. Conversely, unresolved outcomes can sometimes yield a quantile bound depending on their censoring times. The unresolved fraction alone is not a universal identification rule.

**Minimal proposed amendment:** distinguish conditional successful-response latency, time to any terminal disposition, and time to successful completion for all offered requests. Do not rank them as interchangeable. For all-offered successful completion, explicitly represent non-success/never-completion mass and report whether a finite quantile is supported, bounded, or not estimable under the declared definition. Do not assign zero latency or a timeout value as a successful completion. Retain outcome proportions, scheduled-arrival goodput and raw cutoff/censoring times. No invented values or unqualified noninformative-censoring assumption.

Clarify whether the 100,000-success floor is per run or pooled cell. Pooling requests across ten blocks is permissible for a descriptive mixture percentile if labeled, but uncertainty must still respect blocks; it cannot silently become 100,000 independent experimental units. With 100,000 successes, the upper 0.1% contains roughly 100 observations by arithmetic, not a guarantee of narrow intervals under dependence or heterogeneity.

## 7. Feasibility arithmetic is correct but execution remains blocked

The proposed 1,800 trials at 270 s each total 486,000 s = 135 h. The reduced 240 trials total 64,800 s = 18 h. Both exclude startup, calibration, JDK/DB resets, tuning, instrumentation checks, failed technical runs, mechanism ablations and replication. The 12-config by 3-seed tuning budget also needs trace durations and per-controller totals before its cost is known.

A planning bound illustrates why the tail floor needs clarification: if a pool of two connections each holds a connection for exactly 10 ms and all other overhead is zero, at most about 200 acquisitions/s, or 36,000 over 180 s, fit in that measurement interval. Real overhead can reduce this. This is a simple assumed-capacity calculation, not a predicted or measured result for the proposed PostgreSQL workload. It shows that 100,000 successes per run would conflict with that illustrative cell, while pooled-cell counts may be adequate and still require block-aware uncertainty.

**Minimal proposed amendment:** retain native performance as BLOCKED until an owned suitable runner and observed architecture/resource limits are documented. Before any approved run, require a manifest with the actual reduced matrix, per-phase durations, calibration/tuning cost, independent-block target, storage estimate and expected total wall time. Validate instrumentation/generator capability under the approved correctness gates; do not reinterpret emulated smoke as native performance. If a smaller design is needed, choose it prospectively and identify the claims it drops. Missing hardware is not an experimental failure.

## Closure conditions and preserved boundaries

Before a future freeze, resolve the five FAIL definitions above (joint pool/load estimand, model-discrimination rule, pool-wait population, interval rule, completion-tail population), and close or explicitly narrow the OPEN calibration, precision and feasibility choices. A corrected text still requires independent baseline/design approval; no gate is closed by this review.

Preserve the draft's JDK21 versus post-JEP491 boundary and separate native/foreign mechanisms; standard queueing, driver differences and established controllers can falsify the stronger claim. Baseline status remains aggregate OPEN. The official/reduced comparator distinction remains material. Package checks cover included bytes only, not omitted binaries or inherited full raw evidence. Historical uncommitted/no-push reports describe their execution snapshot. Citation identity/version/venue are separate verification tasks; none were newly verified here. Expected oracle values must precede future implementation outputs. No manuscript, baseline, benchmark, simulator or candidate code was changed.
