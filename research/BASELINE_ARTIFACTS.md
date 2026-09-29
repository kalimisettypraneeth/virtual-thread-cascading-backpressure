# Mandatory baseline artifact inventory

Review date: 2026-09-29

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
