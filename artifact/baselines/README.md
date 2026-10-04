# Isolated native controls

`NativeControls.java` is an original, self-contained conformance fixture for fixed admission and a semaphore-backed pool boundary. It is not a JDBC implementation, external author artifact, adaptive controller, candidate experiment, or performance benchmark.

Fixed admission uses nonblocking `tryAcquire` and rejects above capacity. Pool-only borrowing waits interruptibly until a permit is available. Leases return one permit at most once. The deliberately minimal common interface is acquisition plus an `AutoCloseable` lease; no workload adapter compatibility is implied.

Run the capture script documented in `artifact/REPRODUCIBILITY.md`. The fixture exercises capacity rejection, double-close safety, complete release, pool exhaustion, platform-thread handoff, interrupted acquisition, CompletionStage plumbing, and invalid capacities. Five-second waits are deadlock safety bounds, not latency metrics. No Breakwater, TopFull, Netflix or Envoy source is included.

Limitations: no cancellation/timeout API, JDBC pool semantics, reactive-framework backpressure, fairness guarantee, virtual threads, JFR observation, adaptive control, workload interface, or multi-JDK compatibility is validated. External baseline work remains explicitly blocked in `research/BASELINE_ARTIFACTS.md`.



## Breakwater-inspired paper-derived comparator

`BreakwaterInspired.java` is an original reduced comparator derived only from Cho et al., *Overload Control for μs-scale RPCs with Breakwater* (OSDI 2020), https://www.usenix.org/system/files/osdi20-cho.pdf. It is not the authors' artifact and is not an exact reproduction.

### Paper-to-code mapping

| Comparator behavior | Primary-paper anchor | Code |
|---|---|---|
| Queue-delay target and global credit pool | §3.1 and §3.2.1 | `updatePool` inputs `measuredDelay` and `targetDelay` |
| Additive pool growth | §3.2.1, Eq. (1) | below-target branch in `updatePool` |
| Proportional multiplicative decrease with a 0.5 floor | §3.2.1, Eq. (2) | overloaded branch in `updatePool` |
| Client-count-dependent additive step | §3.2.2, Eq. (3) | `additive = max(alpha * clients, 1)` |
| Speculative per-client overcommitment | §3.2.2, Eq. (4) | `overcommit` in `updateClient` |
| Lazy issue/revoke decision | §3.2.2, Eqs. (5) and (6) | the two `updateClient` branches |

### Deliberate deviations

The comparator executes synchronous scalar transitions instead of a distributed RPC system. It uses integer credit counts and integer division for Eq. (4), clamps Eq. (6) at zero to prevent a negative unused-credit state, and rejects invalid numeric inputs. It does not implement Shenango queue measurement, RTT scheduling, piggyback messages, max-min fairness, random explicit-credit selection, AQM, client request expiration, RPC transport, or the author artifact's topology.

The validator's eleven literal fixtures are independent expected traces transcribed from the cited equations. They cover additive growth, equal-target behavior, proportional reduction, the multiplicative floor, demand and availability bounds, single-credit revocation, the explicit non-negative deviation, and invalid inputs. The Java program does not generate its own expected oracle. This is correctness-only evidence; no performance, equivalence, workload compatibility, or novelty claim follows.


## Reduced Gradient2- and Envoy-derived comparators

`AdaptiveControllerComparators.java` is an original dependency-free comparator, not copied upstream code and not an official Netflix or Envoy build. It is derived from the following pinned Apache-2.0 sources:

- Netflix `concurrency-limits@78a74b9878d38c4c048b0304ce12a162ab7b7222`: `Gradient2Limit.java` blob `08ea57f7e2413ca175e65b823643171d899c03a8` and `ExpAvgMeasurement.java` blob `ee70320a4110aba33f751754212ff9bf71ea5515`.
- Envoy `envoy@0ac73c8f38e5c1c875103980b0979ef536cd7573`: `gradient_controller.cc` blob `610b2dec7757364553859c26d8eafff322d73127` and adaptive-concurrency documentation blob `3a3cd16866a3fbde8fc304f85678aa3bcfaadb01`.

The Netflix-derived path retains warm-up averaging, long-window exponential averaging, the recovery adjustment, app-limited suppression, the [0.5, 1.0] gradient clamp, queue allowance, smoothing, and configured bounds. The Envoy-derived path retains buffered-minRTT/sampleRTT, the [0.5, 2.0] gradient clamp, square-root headroom, integer truncation, and configured bounds.

The validator computes expected decisions independently in Python and compares them with Java output over 12 stateful Netflix samples and five Envoy equation fixtures. It does not use the implementation output as its oracle. All 17 checks passed on the captured Java 17 environment.

Evidence boundary: this validates reduced equation/state behavior only. It is not an upstream Gradle or Bazel build, proxy deployment, exact artifact reproduction, latency histogram/timer validation, workload adapter, or performance result. The environment had no Gradle, Maven, Bazel/Bazelisk, Docker, or JDK 21/24/25, so official builds and runtime/workload compatibility were unattempted rather than failed.
