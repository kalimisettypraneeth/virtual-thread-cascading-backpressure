# Mandatory baseline artifact inventory

Review date: 2026-09-30

## Status

**INVENTORY COMPLETE FOR DISCOVERED PUBLIC ARTIFACTS; EXECUTION NOT YET VERIFIED.**

This document records whether each mandatory comparison has a discoverable public implementation, the implementation's initial license and environment constraints, and the resulting experiment-design decision. Repository presence and README/license metadata were checked. No entry is considered buildable, runnable, or behaviorally equivalent to its paper until a pinned revision has passed build, smoke, and paper-behavior checks in a recorded environment.

## Evidence rule

Artifact presence is not baseline reproducibility. A public or official repository is only discovery evidence. Mark a baseline executable only after recording:

1. repository and pinned commit;
2. usable license or explicit permission;
3. build commands and successful build;
4. environment manifest, including hardware and external services;
5. smoke-test output; and
6. a behavioral check against the paper's reported mechanism, not necessarily its numeric results.

If an artifact cannot be verified, any implementation derived from prose must be labeled a reimplementation and must not be represented as the authors' artifact or an exact reproduction.

## Inventory

| Mandatory baseline or null explanation | Artifact evidence checked | Initial reproducibility classification | Experiment decision |
|---|---|---|---|
| JDK 21 versus JDK 24/25; fixed semaphore; pool-only limit | Official JDK behavior and local harness components; no external research artifact required | Harness implementation required | Implement directly, pin JDK builds, record carrier settings and JFR pinning evidence, and validate each control independently. |
| USITS 2003 adaptive percentile-response admission | Paper identified; no author implementation verified in this search | Paper/specification only | If used, label it paper-inspired and validate its response-time control law on synthetic traces before comparison. |
| WWW 2004 stable multi-tier admission/scheduling | Paper/record identified; no author implementation verified in this search | Paper/specification only | Use as a null explanation or carefully documented reimplementation, not as an exact artifact reproduction. |
| Leskelä 2006 measurement-based stability regions | Analytical work; no software artifact expected or verified | Analytical null model | Implement the published model/equations with unit tests and compare predicted versus observed boundaries. |
| DAGOR | Paper identified; GitHub search found only third-party gRPC implementations, not a verified author artifact | Unverified third-party implementations | Do not treat a third-party repository as canonical. Reimplement from the paper only with an explicit conformance test and limitation note. |
| Breakwater | Public paper artifact at `inhocho89/breakwater-artifact`; README verified on branch `osdi2020` | Official-looking artifact with substantial environment dependency | README's quick start requires a CloudLab profile and eleven xl170 machines. No top-level license was verified. Do not vendor or claim reproducibility until license and a feasible isolated environment are confirmed. |
| Protego | Paper identified; no public author repository verified in targeted searches | Paper/specification only | A signal-inspired ablation may be used, but it must not be called Protego unless the algorithm and behavior are validated against the paper. |
| Bouncer | Paper/preprint identified; no public author repository verified in targeted searches | Paper/specification only | Implement from the paper only if needed, disclose it as a reimplementation, and validate the decision rule separately. |
| Netflix Concurrency Limits / Gradient2 | Public official repository `Netflix/concurrency-limits`; README and Apache-2.0 license verified | Licensed official implementation; execution unverified | Strong runnable-baseline candidate. Pin a commit, build it, smoke test Gradient2, and record integration changes. |
| Envoy adaptive concurrency | Public official repository `envoyproxy/envoy`; README and Apache-2.0 license verified | Licensed official implementation; execution unverified and heavyweight | Prefer an external-proxy deployment. A simplified controller is acceptable only if trace-level decisions are shown equivalent over a preregistered validation workload. |
| TopFull | Public official repository `kaist-ina/TopFull`; README identifies the SIGCOMM 2024 implementation | Official artifact; execution and license unverified | Inspect its topology and dependencies before use. No top-level license was verified, so reuse requires a license decision. |
| Quarkus virtual-thread versus worker-pool/reactive comparison | Peer-reviewed study identified; no accompanying public experiment artifact verified in this search | Paper-only comparison | Recreate only the required framework modes with pinned versions and report deviations from the paper's setup. |

## Pinned compatibility decision

| Baseline | Observed revision | License/build readback | Current executable status | Exact next evidence |
|---|---|---|---|---|
| Harness-native fixed semaphore, pool-only limit, JDK and platform/reactive controls | Isolated native controls now present; version/framework integration absent | No external license dependency | **JAVA 17 NATIVE CONTRACT PASS; VT/JDBC/FRAMEWORK BLOCKED** | See isolated validation below; candidate design remains blocked. |
| Netflix Concurrency Limits / Gradient2 | `Netflix/concurrency-limits@78a74b9878d38c4c048b0304ce12a162ab7b7222` | Apache-2.0 `LICENSE` and Gradle build file read back | **PINNED; BUILD/SMOKE NOT RUN** | Build the pinned Java modules, run tests, integrate a minimal adapter, and verify decisions on a fixed latency trace. |
| Envoy adaptive concurrency | `envoyproxy/envoy@0ac73c8f38e5c1c875103980b0979ef536cd7573` | Apache-2.0 `LICENSE`; Bazel/Bazelisk build instructions read back | **PINNED; BUILD/SMOKE NOT RUN; HEAVYWEIGHT** | Prefer a pinned binary/container only after provenance verification; validate controller decisions against the experiment trace. |
| TopFull | `kaist-ina/TopFull@0c7af21fb48765ec13da9b2b478dd850c0ef6cf8` | Official README read back; no top-level `LICENSE` at the pinned revision | **LICENSE BLOCKED; NOT EXECUTED** | Obtain a usable license or use a clearly labeled paper-derived comparator with conformance tests. |
| Breakwater | `inhocho89/breakwater-artifact@e8a284b9f20a62c8d4146ab076595a19970943ce` | Official artifact README read back; no top-level `LICENSE`; quick start requires eleven CloudLab xl170 nodes | **LICENSE/ENVIRONMENT BLOCKED; NOT EXECUTED** | Resolve license and topology feasibility, or preregister a reduced paper-inspired credit controller and validate its control law. |
| Protego, Bouncer, USITS/WWW controllers, Leskelä model | Primary papers/specifications | No verified author artifact selected | **REIMPLEMENTATION REQUIRED** | Specify equations/state transitions, unit-test them, and record deviations; never label as author artifacts. |

This table is a compatibility decision, not execution evidence. Zero mandatory external baselines are currently reproduced.

## Readiness classes

- **Class A — official and licensed, execution pending:** Netflix Concurrency Limits; Envoy.
- **Class B — public paper artifact with unresolved environment or license constraints:** Breakwater; TopFull.
- **Class C — paper/specification or unverified implementation only:** USITS 2003 controller; WWW 2004 controller; Leskelä model; DAGOR; Protego; Bouncer; Quarkus DEBS setup.
- **Harness-native controls:** fixed semaphore, pool-only limiting, JDK-version and platform/reactive controls.

None of these classes means “reproduced.” Class A only means the next build/smoke gate can proceed without an immediately visible license blocker.

## Completion gate for experiment design

The artifact-discovery checklist item is complete. The executable-baseline gate remains open until every baseline selected for the experiment matrix has either:

- a pinned, licensed, build- and smoke-verified artifact with a behavioral check; or
- a preregistered, explicitly labeled reimplementation with conformance tests and documented deviations.

A missing or incompatible artifact is a design constraint, not permission to silently substitute a weaker baseline.

## Isolated native validation

The Java 17 source-launcher run in `artifact/results/baseline-validation/java17-native/validation.json` exited zero with ten deterministic contract checks. Source and validator SHA-256 values, actual commands, standard output/error, OS/kernel, CPU/memory, runtime build, and available executables are captured by `artifact/scripts/validate_baselines.py`. This is not benchmark data or candidate implementation.

| Comparator | Executed status | Evidence / blocker |
|---|---|---|
| Fixed semaphore | **PASS: isolated Java 17 contract only** | Capacity rejection, exactly-once permit release, invalid capacity: `artifact/baselines/NativeControls.java`; raw validation JSON above. No JDBC or VT interface tested. |
| Pool-only | **PASS: isolated Java 17 contract only** | Platform-thread handoff and interruption accounting in the same test. No JDBC pool, fairness, timeout, or cancellation policy compatibility claim. |
| Netflix Gradient2, pinned `78a74b9…` | **BLOCKED: build/smoke/conformance not executed** | No local Gradle/Maven executable or resolved dependency closure. Pinned root `build.gradle` uses dynamic JUnit 5.+/4.+, Mockito 4.+, SLF4J 1.7.+, Spectator 1.+ and Spring 5.+ ranges. Core requests SLF4J and JUnit; pin resolved dependencies/checksums before claiming reproducibility. |
| Envoy, pinned `0ac73c8…` | **BLOCKED: not executed; no substitute validated** | No verified pinned binary/image or local container runtime. A simplified comparator cannot establish trace equivalence by comparing against its own implementation; an independent pinned reference trace/oracle is required. |
| Breakwater-inspired credit | **PASS: reduced paper-derived equation conformance only** | Original Java 17 comparator maps §3.2 Eqs. (1)–(6); 11/11 independent deterministic fixtures passed. No author code was copied. Distributed messaging, AQM, fairness, workload integration, and performance remain unvalidated. |
| JDK 21 and 24/25, VT/platform/reactive controls | **PARTIAL / BLOCKED** | Available build is OpenJDK 17.0.20+8-1-24.04-Ubuntu only. Platform-thread and CompletionStage plumbing passed; CompletionStage is not a tested reactive framework. VT/version-comparison smoke was not run. |
| TopFull | **LICENSE BLOCKED; NOT EXECUTED** | No code copied; earlier artifact classification preserved. |

Absence of a `javac` executable did not imply absence of compilation: the installed runtime exposes `jdk.compiler`, and the Java source launcher compiled and ran the native checks. Conversely, Java 17 success cannot certify JDK 21/24/25 behavior. No external baseline build was attempted in this validation and no dependency download or image launch occurred. Local executable absence is not evidence that an upstream artifact is defective.

**Gate remains NOT COMPLETE.** Next evidence must include the Netflix resolved build/dependency closure and deterministic decisions; an independent Envoy reference plus smoke/conformance; a specified Breakwater-inspired credit comparator; JDK 21 and 24/25 smoke paths; and workload-interface validation. Retain JFR pinning events, carrier parallelism/settings, native/foreign-call isolation, platform-thread and matched reactive/framework controls as requirements, not observations.



## Breakwater-inspired comparator evidence

The original comparator in `artifact/baselines/BreakwaterInspired.java` maps OSDI 2020 §3.2.1 Eqs. (1)–(2) and §3.2.2 Eqs. (3)–(6). Its independent validator passed 11/11 fixtures and captured raw evidence at `artifact/results/baseline-validation/breakwater-inspired/validation.json`. Source SHA-256 is `f6bc04f7e7cd307e2ad8b1aeb7f2758f0cdeee222907509e8b9cc1c8bfba6f48`; validator SHA-256 is `55763a79381529c9163d74de059231250324bc7a1bbb714a7ee54c758fcc7d0b`.

This closes only the reduced credit-equation conformance item. The implementation is explicitly **Breakwater-inspired and paper-derived**, not the authors' artifact or an exact reproduction. It excludes Shenango queue sensing, RTT-driven distributed operation, demand/credit piggybacking, random explicit-credit selection, lazy max-min distribution across live clients, AQM, client expiration, and the eleven-node artifact topology. Its Eq. (4) uses integer credit division and its Eq. (6) adds a documented non-negative clamp.

The author artifact remains license/environment blocked and was neither copied nor executed. Netflix/Gradient2 and Envoy build/conformance, JDK 21 and 24/25 VT paths, reactive/JDBC controls, and workload-interface compatibility remain unresolved. Therefore the selected-baseline completion gate remains **NOT COMPLETE**.


## Reduced adaptive-controller equation evidence (2026-10-04)

Pinned source inspection and a zero-download local validation now provide bounded evidence for the two remaining adaptive-controller families. The upstream pins and source blobs are recorded in `artifact/results/baseline-validation/adaptive-controllers/validation.json`; the original dependency-free comparator and independent Python oracle passed 17/17 deterministic checks with exit code 0.

| Comparator | Scoped result | What remains unverified |
|---|---|---|
| Netflix Gradient2-derived | **PASS: reduced state/equation trace only** — 12 stateful decisions match an independent oracle, including warm-up/EMA state, app-limited suppression, clamping, smoothing, and bounds. | Official Gradle build, resolved dependency checksums, library listener/metrics behavior, adapter integration, and performance. |
| Envoy gradient-derived | **PASS: reduced equation trace only** — five decisions match an independent oracle, including gradient clamp, headroom, truncation, and bounds. | Official Bazel build, proxy/filter/timer/histogram/CAS behavior, pinned binary/image provenance, deployment, and performance. |

The captured environment had Java 17 only and no `javac`, Gradle, Maven, Bazel/Bazelisk, Docker, or JDK 21/24/25 executables. Therefore official builds, JDK-version smoke, virtual-thread execution, reactive/JDBC compatibility, and shared-workload validation were **unattempted due to environment capability**, not failed upstream tests. These missing items remain blocking acceptance criteria.

**Aggregate gate remains NOT COMPLETE.** Reduced equation conformance cannot substitute for official build/smoke evidence or the required JDK 21 versus 24/25 and reactive/JDBC workload-interface checks.


## Local Docker runtime bundle preparation (2026-10-05 UTC)

A prepared bundle is now available at `artifact/runtime-validation/README.md`. From repository root run `bash artifact/scripts/validate-runtime.sh` on Linux/WSL with Python 3 and a local Docker daemon. It uses immutable linux/amd64 image manifests (registry-declared Temurin 21.0.12.1+1 and 25.0.4.1+1, PostgreSQL 16.15), a 29-JAR SHA-256 dependency lock, matched finite-pool JDBC/platform/virtual and genuine R2DBC cases, deterministic held-batch request assertions, preserved reduced-control adapters, and separate monitor/JNI JFR fixtures. JNI runs only if the pinned image has a native compiler; foreign-call coverage remains unattempted.

**PREPARED / RUNTIME UNATTEMPTED.** Java17 compilation and five constant-signal adapter checks passed; the actual missing-Docker command emitted an UNATTEMPTED manifest, logs and hashes under `artifact/results/runtime-validation/preparation`. Docker, JDK21/25, database/interface equivalence and JFR cases have not run here. Registry version metadata is not an observed runtime. The constant-capacity adapters do not validate dynamic controller behavior. Existing 17/17 reduced Gradient2/Envoy conformance is not an official upstream build or performance result. No existing baseline evidence was replaced.

The exact command, artifact layout, immutable pins, workload semantics and limitations are documented in the bundle README. Raw user-local results must be inspected before closing runtime/interface gates. **Aggregate scientific/selected-baseline gate remains NOT COMPLETE.**
