# Differentiation — Virtual-Thread Cascading Backpressure

Review date: 2026-09-30  
Evidence base before this reconciliation: `968ba03d21c49091354b60343a9a501f1fc6f31e`  
Status: **PROVISIONAL — NOVELTY UNVERIFIED**

## Research question

Under workload shifts, can a measurable stability-transition surface across offered load, virtual-thread concurrency, and finite downstream capacity predict collapse early enough for adaptive admission control to preserve throughput and tail latency better than fixed limits?

## Closest established work and exact boundary

| Established result or mechanism | Overlap | Not our contribution | Candidate differentiation |
|---|---|---|---|
| JEP 444 / virtual threads | FOUNDATIONAL | Virtual threads, high-concurrency throughput, Little's-Law framing | Stability-transition characterization for virtual-thread services with finite downstream capacity |
| Oracle Java 21 guidance | SUBSTANTIAL | Semaphores for scarce resources; connection pools as concurrency boundaries | Online estimation and adaptation of the safe operating region |
| Fixed concurrency limits and pool sizing | SUBSTANTIAL | Limiting callers to downstream capacity | Controller response to workload/capacity shifts rather than a manually selected fixed limit |
| General backpressure and overload control | SUBSTANTIAL | Queues, rejection, load shedding, or downstream saturation | A virtual-thread-specific empirical map only if results show behavior not explained by generic queueing alone |
| USITS 2003, WWW 2004, and Leskelä 2006 | DIRECT | Percentile-response admission, stable multi-tier overload behavior, measured queueing stability regions, and feedback sensitivity | A runtime-specific mechanism only if established queueing predictions fail under controlled platform/reactive comparisons |
| Breakwater, Gradient2/Envoy, Protego, Bouncer, and TopFull | DIRECT | Credit-, gradient-, marginal-throughput-, SLO-, and global-observation overload control | Non-equivalence requires direct comparator behavior, not a renamed adaptive limiter |
| JEP 491 and DEBS 2023 Quarkus study | DIRECT | JDK 24 removes Java 21 monitor pinning; resource-constrained virtual-thread/framework comparisons already exist | A finite-pool interaction that persists beyond removed pinning and framework mismatch |
| Database CPU/pool guidance and microservice pool-size studies | FOUNDATIONAL / PARTIAL | Finite downstream capacity and workload-specific pool tuning | Hold arrival process, database capacity, pool size, and demand constant across execution modes |

## Candidate contributions

1. A reproducible **stability-transition surface** parameterized by arrival process, service-time distribution, virtual-thread concurrency, pool capacity, and queue/admission policy.
2. Observable early-warning signals—such as queue growth, wait/service-time separation, rejection rate, and tail-latency slope—that predict transition before sustained collapse.
3. An adaptive admission controller compared against:
   - no explicit admission limit;
   - connection-pool-only limiting;
   - fixed semaphore limits;
   - USITS-style percentile control;
   - Breakwater-inspired credit control;
   - Netflix Gradient2 or Envoy adaptive concurrency;
   - Protego-style marginal-throughput signaling;
   - Bouncer-style SLO admission;
   - TopFull where topology permits.
4. Evidence separating virtual-thread effects from ordinary finite-capacity queueing.

## Operational discriminator matrix

| Candidate contribution | Established mechanism explicitly excluded | Operational discriminator | Result that falsifies or substantially weakens it |
|---|---|---|---|
| Residual runtime/pool interaction after a queueing null model | Ordinary finite-capacity pool queueing, pool sizing, and generic stability regions | With arrival process, service demand, database capacity, and pool size held constant, an execution-mode × pool-occupancy interaction remains after comparing predicted and observed queue/wait/service-time trajectories. | Platform-thread and reactive controls follow the same boundary and recovery within uncertainty, or a standard queueing model explains the residuals without a virtual-thread variable. |
| JDK-version-persistent virtual-thread mechanism | Java 21 monitor pinning and framework integration mismatch | The effect persists on JDK 24/25, while JFR pinning events, carrier parallelism, native/foreign calls, and framework mode are recorded and controlled. | The effect disappears after JEP 491, tracks JFR pinning/native calls, or vanishes under matched framework modes. |
| Added control value beyond established admission algorithms | Generic adaptive limiting, queue-delay credits, Gradient2/Envoy, marginal-throughput control, query-class SLO admission, and global TopFull-style control | On preregistered workload/capacity shifts, the candidate improves recovery and SLO-goodput against every feasible mandatory comparator without merely changing its target or tuning budget. | A fixed limit chosen without hindsight or an established controller is equivalent within uncertainty, or gains occur only with post hoc tuning or one topology. |

## Claims this paper must not make

- Virtual threads, Little's Law, semaphores, connection pools, backpressure, or downstream bottlenecks are new.
- Fixed admission limiting is a novel controller.
- A throughput plateau or rising latency alone proves a new stability phenomenon.
- Better results in one configuration establish generality.

## Falsifiers

The candidate contribution is weakened or rejected if:

- the transition is fully predicted by a standard queueing model with no material virtual-thread-specific effect;
- a fixed limit selected without hindsight performs equivalently across tested workload shifts;
- controller gains disappear outside one database, pool, or service-time distribution;
- the proposed warning signal detects collapse only after tail latency is already unacceptable;
- scholarly search finds a prior system that maps the same transition surface and applies equivalent adaptive control.

## Evidence required to pass this gate

- [x] Closest adaptive-concurrency, overload-control, database-admission, queueing, runtime-version, framework, and finite-pool evidence is tabulated with workload, metrics, and artifacts.
- [x] Candidate contributions are classified using the repository overlap taxonomy.
- [x] Mandatory adaptive-concurrency and admission baselines are named and justified.
- [x] Generic queueing, pool-sizing, framework, and pinning explanations are explicit falsifiers.
- [x] Public artifact availability and initial environment/license constraints are inventoried.
- [x] Backward/forward citation chains for Breakwater, Protego, Bouncer, and TopFull are complete for the bounded audit.
- [x] Bounded direct-intersection and comparable-pool searches are documented; no verified peer-reviewed direct match was identified as of 2026-09-30, without treating absence as proof of novelty.
- [ ] Selected baselines pass pinned build, smoke, behavioral, and workload-compatibility checks.
- [x] Candidate claims remain labeled unverified.

## Gate decision

**NOT COMPLETE.** Citation chains, the bounded direct-intersection search, the operational discriminator, and falsifiers are reconciled. The remaining blocker is executable-baseline evidence: pinned build, smoke, behavioral conformance, and workload compatibility for the selected artifacts or explicit reimplementations. No experiment-design or implementation gate may start until that evidence is committed and read back.

## Executability evidence boundary

Isolated fixed-semaphore and pool-only contracts passed ten Java 17 checks; see `artifact/results/baseline-validation/java17-native/validation.json`. These are not VT, JDBC, reactive-framework, Gradient2, Envoy, or Breakwater validation. The executable-baseline checklist remains unchecked. External controller conformance, a pinned dependency closure, JDK 21/24/25 availability, and workload-interface evidence are still missing. Candidate design/implementation remains blocked.



## Breakwater comparator evidence boundary

A reduced Breakwater-inspired, paper-derived comparator now passes 11/11 independent deterministic equation fixtures. The mapping covers OSDI 2020 §3.2.1 Eqs. (1)–(2) and §3.2.2 Eqs. (3)–(6), with all omissions and safety deviations recorded in `artifact/baselines/README.md`. This is not the author artifact, an exact reproduction, a workload adapter, or performance evidence.

The executable-baseline checklist remains unchecked. Netflix/Gradient2 and Envoy still lack completed build/smoke/conformance evidence; JDK 21 versus 24/25, reactive-framework, JDBC, and workload-interface validation remain blocked. The differentiation gate therefore remains **NOT COMPLETE**, and no downstream experiment or candidate implementation is unblocked by this scoped result.


## Adaptive-controller equation evidence boundary

Reduced source-derived comparators now pass 17/17 independent deterministic fixtures: 12 stateful Netflix Gradient2-derived decisions and five Envoy gradient-derived decisions. Exact upstream revisions/source blobs, raw commands, exit codes, runtime facts, hashes, inputs, expected outputs, actual outputs, and declared deviations are captured in `artifact/results/baseline-validation/adaptive-controllers/validation.json`.

This evidence closes only the reduced equation/state-conformance sub-item. It is not an official Gradle/Bazel build, an exact reproduction, a proxy or library integration, a workload adapter, or performance evidence. Official builds were unattempted because the captured free environment lacks Gradle/Maven/Bazel/Bazelisk/Docker; JDK 21/24/25 were also unavailable. Reactive-framework, JDBC, virtual-thread/version, and shared-workload compatibility remain unresolved.

The executable-baseline checklist remains unchecked and the differentiation gate remains **NOT COMPLETE**. Downstream experiment design and candidate implementation remain blocked until the missing runtime and workload-interface evidence is committed and independently read back.


## Local Docker runtime bundle preparation (2026-10-05 UTC)

A prepared bundle is now available at `artifact/runtime-validation/README.md`. From repository root run `bash artifact/scripts/validate-runtime.sh` on Linux/WSL with Python 3 and a local Docker daemon. It uses immutable linux/amd64 image manifests (registry-declared Temurin 21.0.12.1+1 and 25.0.4.1+1, PostgreSQL 16.15), a 29-JAR SHA-256 dependency lock, matched finite-pool JDBC/platform/virtual and genuine R2DBC cases, deterministic held-batch request assertions, preserved reduced-control adapters, and separate monitor/JNI JFR fixtures. JNI runs only if the pinned image has a native compiler; foreign-call coverage remains unattempted.

**PREPARED / RUNTIME UNATTEMPTED.** Java17 compilation and five constant-signal adapter checks passed; the actual missing-Docker command emitted an UNATTEMPTED manifest, logs and hashes under `artifact/results/runtime-validation/preparation`. Docker, JDK21/25, database/interface equivalence and JFR cases have not run here. Registry version metadata is not an observed runtime. The constant-capacity adapters do not validate dynamic controller behavior. Existing 17/17 reduced Gradient2/Envoy conformance is not an official upstream build or performance result. No existing baseline evidence was replaced.

The exact command, artifact layout, immutable pins, workload semantics and limitations are documented in the bundle README. Raw user-local results must be inspected before closing runtime/interface gates. **Aggregate scientific/selected-baseline gate remains NOT COMPLETE.**
