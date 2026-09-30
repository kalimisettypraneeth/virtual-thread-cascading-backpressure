# Isolated native controls

`NativeControls.java` is an original, self-contained conformance fixture for fixed admission and a semaphore-backed pool boundary. It is not a JDBC implementation, external author artifact, adaptive controller, candidate experiment, or performance benchmark.

Fixed admission uses nonblocking `tryAcquire` and rejects above capacity. Pool-only borrowing waits interruptibly until a permit is available. Leases return one permit at most once. The deliberately minimal common interface is acquisition plus an `AutoCloseable` lease; no workload adapter compatibility is implied.

Run the capture script documented in `artifact/REPRODUCIBILITY.md`. The fixture exercises capacity rejection, double-close safety, complete release, pool exhaustion, platform-thread handoff, interrupted acquisition, CompletionStage plumbing, and invalid capacities. Five-second waits are deadlock safety bounds, not latency metrics. No Breakwater, TopFull, Netflix or Envoy source is included.

Limitations: no cancellation/timeout API, JDBC pool semantics, reactive-framework backpressure, fairness guarantee, virtual threads, JFR observation, adaptive control, workload interface, or multi-JDK compatibility is validated. External baseline work remains explicitly blocked in `research/BASELINE_ARTIFACTS.md`.

