# Official Netflix Gradient2 validation

This is a separate official-core baseline at upstream revision
`78a74b9878d38c4c048b0304ce12a162ab7b7222`, Apache-2.0.
It does not replace the preserved reduced comparator or the earlier 30-case bundle.
The new evidence is under `artifact/results/netflix-validation/20261008-official`.

## Recorded execution and replay

Use a separate local checkout/copy for replay to avoid overwriting frozen evidence.
The scripts intentionally use a fixed evidence root for this bounded validation.
No script publishes, pushes, opens a PR, or enables a hosted runner.

1. Run `python3 artifact/netflix-validation/test_docker_compatibility.py` for the five
   synthetic regression tests. The platform test extracts and executes the actual
   platform guard AST in the preserved runner, not a duplicate of that predicate.
2. Obtain the pinned upstream checkout at the evidence root's `upstream` directory;
   verify commit and LICENSE using `source-identity.json`. Copy the preserved
   per-project locks from `locks/upstream/` to that checkout and copy
   `locks/verification-metadata.xml` to its `gradle/verification-metadata.xml`.
3. For exact toolchain replay, verify the retained `tooling-image.tar` against
   `locks/tooling.lock.json`, then `docker load` it locally. The image is selected
   by immutable local ID by run_core.py. The Dockerfile is the *discovery recipe*,
   using distribution package repositories; it is not an exact cold-rebuild lock.
   Recorded .deb checksums and installed package versions are in the environment
   log. The saved image is the exact reproducible toolchain snapshot.
4. Verify the 275 cached dependency/metadata files using `locks/resolved-dependencies.json`.
   Preserve the populated Gradle cache to replay offline. Gradle 8.6's official ZIP
   checksum, all executed distribution-file matches, and wrapper JAR checksum are
   captured. Cold dependency downloads must be checked against verification XML,
   never regenerate trusted hashes just to accept changed artifacts.
5. `python3 artifact/netflix-validation/run_core.py replay-core offline` executes
   the official core test task with strict verification, dependency locks,
   `--rerun-tasks`, `--offline`, and Docker `--network none`.
6. Copy the frozen oracle input, expectations and freeze records into the fresh
   evidence root. Preserve these before executing OfficialProbe. Do not regenerate
   expected values from probe output. `run_integration.py` compiles our three Java
   files against official built classes, runs the API/conformance probe and compares
   frozen expectations, then runs six local PostgreSQL adapter cases.
   It reuses the separately verified 29 runtime JARs plus pinned SLF4J API. It needs
   the original runtime dependency directory and the fixed SQL fixture; all their
   checksums are in the locks and preserved runtime manifest.
7. `record.py` records each command, UTC interval, exit code, full stdout/stderr.
   Use new labels/evidence copy for a replay. The initial discovery commands and
   actual immutable image IDs are in commands.jsonl.

The supplied review ZIP excludes binary caches/images; exact offline replay requires
those retained local files. The report describes the narrower scope of tests and
remaining acceptance criteria. No benchmark workloads were run.

## Independent oracle

`freeze_oracle.py` derives rational arithmetic expectations from the pinned source
in a separate language; it does not import/invoke the implementation or read actual
outputs. Original freeze timestamp/hashes precede conformance execution. Trace input
covers ten warm-up samples, sustained increase/decrease, recovery, app-limited samples,
minimum/maximum bounds, and paired drop/no-drop sequences. Exact integer limits and
notification counts are required; the exposed integer nanosecond RTT permits an
absolute difference of one ns due to binary floating-point/truncation.

`listener-workload-freeze.json` freezes terminal-accounting and database expectations
before execution. This oracle is independently implemented, not independently authored;
no external second-reviewer claim is made.

## Adapter policy and reduced-comparator deviations

- Official `Gradient2Limit`, `AbstractLimit`, `SimpleLimiter` and listener code are
  built from unchanged upstream sources. The reduced Java comparator remains an
  original equation-only implementation and is never called by these new tests.
- Upstream fixes warm-up to ten samples. The reduced implementation exposes a
  configurable warm-up; the earlier runtime adapter used one. This is a deliberate
  difference from the historical constant-capacity smoke, not upstream equivalence.
- Upstream accepts integer nanosecond RTT; reduced input is double. Tests use positive
  integral nanoseconds. Zero/negative/overflow inputs are outside this validation.
- Upstream uses a pre-recovery local RTT snapshot for the current gradient while
  storing the 0.95 recovery adjustment. Reduced code immediately uses the adjusted
  field. With legal tolerance >=1 and the recovery condition ratio>2, both gradients
  clamp to 1 for that sample; this algebraic observation is scoped, not universal
  trace-equivalence certification for every configurable reduced input.
- Both equations ignore didDrop. Official API receives the drop flag; the reduced
  signature has none. Paired official traces verify drop/no-drop decision equality.
- Upstream supports a queue-size function, metrics, logging, change listeners,
  synchronized publication, defaults and builder validation. Reduced code has a
  scalar queue, custom config and no equivalent API/lifecycle instrumentation.
  This suite covers constant queues only; every possible function/default or invalid
  builder configuration is not certified.
- Official SimpleLimiter uses permits and inflight/listener accounting. Its terminal
  callbacks must be called once. Our CAS adapter makes terminal calls idempotent and
  race-safe: success -> onSuccess, SQL error -> onDropped, cancellation -> onIgnore.
  Cancellation thus excludes unfinished work from the latency estimator. This is an
  explicit adapter policy, not a claim that raw upstream listeners are idempotent.
- Workload checks pin Gradient2 min/initial/max to two with queue zero and a scripted
  clock, matching the held-batch fixture. Dynamic controller decisions are validated
  separately by the frozen trace; database-driven dynamic adaptation is unattempted.
- The JDBC cancellation test interrupts a task paused after borrowing, before issuing
  SQL. Reactive cancellation terminates a never-completing publisher after a real
  borrow. Both also cancel while waiting for an exhausted pool. Active server-query
  cancellation, connection-establishment failure, cleanup-callback exceptions,
  network faults, repeated stress schedules and timeout policy remain unattempted.
- Reactive cleanup uses usingWhen; the terminal hook handles cancel explicitly.
  The old reduced harness's doOnTerminate plus end-of-batch lease sweep was a
  correctness-smoke mechanism without cancellation validation. It remains untouched.
