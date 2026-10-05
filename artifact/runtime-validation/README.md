# Local runtime validation bundle

**Prepared and compile-checked; Docker/JDK 21/25/database runtime execution is UNATTEMPTED in the preparation environment.** This is a correctness smoke harness, not benchmark data, an official Netflix/Envoy build, or validation of a research claim.

## One command

From the repository root on Linux or WSL with Python 3, Bash, Git and a working local Docker daemon:

```bash
bash artifact/scripts/validate-runtime.sh
```

No host JDK, Maven, Compose, service account, paid runner, or hosted database is required. Docker Desktop through WSL is supported in design but untested. The pinned images are **linux/amd64**; other host architectures require Docker emulation and must not be used for performance inference. Bind mounts require Docker to access the checkout/output paths. The runner uses Linux uid/gid and is not a native Windows script.

The command downloads checksum-pinned dependencies from Maven Central and three digest-pinned Docker images, compiles in JDK 21, then uses only a private internal Docker network. PostgreSQL has no published host port and uses disposable tmpfs storage. The fixed `smoke` credentials are local fixture credentials, not secrets. The command always attempts container/network cleanup; an interrupted Docker daemon may require manual cleanup of resources with the emitted `vt-…` name prefix.

Optional output selection (the matrix is intentionally a fixed smoke contract):

```bash
bash artifact/scripts/validate-runtime.sh --matrix artifact/runtime-validation/matrix.json --output artifact/results/runtime-validation
```

Runs produce a unique UTC directory. Missing Docker yields exit **2**, `UNATTEMPTED`, and provenance rather than pretend JFR/runtime output. Other preparation failures on a Docker host yield `FAIL`; inspect logs to distinguish download/compile/startup from actual case execution. Successful bundled smoke yields exit **0**, but does not imply native/foreign coverage or baseline/scientific completion.

## Pins and provenance

`images.lock.json` was resolved from Docker Hub manifests on 2026-10-05 UTC. Manifest and config response bytes were SHA-256 verified. Source tags are discovery metadata; execution uses the locked amd64 manifest digest only. Config digests are checked again after pull. Registry configuration declares Temurin **21.0.12.1+1**, Temurin **25.0.4.1+1**, and PostgreSQL **16.15**; these are registry metadata, not locally observed running versions. The runner captures actual `java -version`, JVM flags/settings, JFR metadata, PostgreSQL version, Docker version/info and image inspect output.

`dependencies.lock.json` freezes all 29 resolved runtime JARs, URLs and SHA-256 values. Primary versions: PostgreSQL JDBC 42.7.5; PostgreSQL R2DBC 1.0.7.RELEASE; R2DBC Pool 1.0.2.RELEASE; Reactor Core 3.6.11. `pom.xml` records the resolution roots. Apache Maven 3.9.9 with dependency-plugin 3.8.1 resolved the closure during preparation; Maven is not invoked by the runner, so later dependency-resolution changes cannot silently replace the lock.

Every run contains:

- `manifest.json`: source commit, pre-output git dirty status, source/config hashes, matrix, image pins, host/runtime facts and resource limits.
- `commands.jsonl` and `logs/`: ordered argv, cwd, UTC start/end, exit codes, full stdout/stderr, including failed commands and cleanup. `downloads.jsonl` records dependency URLs/times/hashes.
- `dependencies/`, `classes/`, `cases/<case>/`: exact JARs, compiled classes, request outcomes, assertion results, Java properties/flags, and JFR recordings. Separate JFR print logs retain event fields, stacks and reasons supported by that runtime.
- `assertions.json`, `summary.json`, `SHA256SUMS`: explicit outcomes and hashes of emitted files. SHA256SUMS excludes itself. Run `sha256sum -c SHA256SUMS` inside a completed run directory.

Generated output is created only after the git source snapshot. Existing unrelated dirty files still appear. Source hashing includes the selected matrix independently and all bundled source/lock files. Do not commit user-local run directories without reviewing their size and provenance.

## Matched workload and assertions

The fixed database contains request IDs 0–11 and expected value `7*id+3`. Every interface performs the same SELECT against the same local PostgreSQL container, with autocommit and READ COMMITTED. Blocking JDBC uses exactly two preopened connections and a bounded ArrayBlockingQueue; genuine R2DBC uses a max-size-two reactive pool. Each round dispatches three requests. JDBC checks the actual virtual/platform thread identity; reactive work uses driver publishers, with blocking only at the outer batch completion boundary.

For fixed and reduced controls, the batch acquires all admission leases before dispatch. Exactly the first two requests are accepted and the third rejected. Pool-only accepts all three and queues at the finite connection pool. This artificial held-batch contract makes rejection deterministic and comparable without equating concurrent scheduling with controller conformance. The fixed and pool-only limiting sources are preserved; the integrated credit/Gradient2/Envoy adapters call the existing reduced comparator sources. Constant scripted inputs keep their capacity at two. This validates a narrow adapter path, not adaptation, fairness, timeouts under stress, overload dynamics, or official upstream behavior.

Across JDK 21 and 25, each of five controls runs platform JDBC, virtual JDBC, and R2DBC (30 cases). Assertions independently calculate the exact expected request outcomes, reject duplicates/missing IDs/wrong values, check zero active operations/returned connection and admission capacity, enforce peak operations at or below pool capacity, and compare outcome files across all interfaces and JDKs. These are no-timing correctness assertions. No throughput or latency ranking is calculated. Cancellation/error injection and steady-state saturation remain future validation work.

## JFR and the JEP 491 boundary

Each JDK runs platform/virtual monitor-held sleep cases. Four custom JFR markers establish that the fixture ran; `jdk.VirtualThreadPinned` must be available and is enabled with zero threshold and stacks. The narrow expected observation is at least one virtual-thread monitor pin on JDK 21, zero on JDK 25 after JEP 491, and zero for platform threads. Unexpected events fail with recordings retained for investigation; absent events are not evidence about other workloads. Scheduler parallelism and max pool size are both explicitly two and recorded. Workload cases also record profile JFR.

`native_pinning.c` is a separate JNI callback that sleeps in Java while a native frame remains on the stack. If `cc` exists in the pinned JDK21 image, the runner builds and executes this separate platform/virtual fixture on both JDKs and checks the expected native-frame pin. If no compiler exists, it records **UNATTEMPTED: cc unavailable** and installs nothing. The JNI fixture is not foreign-function coverage; foreign-call isolation is explicitly unattempted. Preparation here executed neither monitor nor native fixture.

Primary API/behavior references: [JEP 491](https://openjdk.org/jeps/491), [R2DBC pool](https://github.com/r2dbc/r2dbc-pool), [PostgreSQL R2DBC](https://github.com/pgjdbc/r2dbc-postgresql). Existing reduced-control provenance remains in `artifact/baselines/README.md` and the prior validation JSON.

## Preparation evidence and remaining gate

`artifact/results/runtime-validation/preparation/validation.json` records the actual Java17 compilation and five scripted adapter checks. `preflight/` records an actual missing-Docker invocation of the single command. Neither establishes JDK21/25 execution, JDBC/R2DBC runtime equivalence, observed JFR behavior, official baseline buildability, or performance. Existing 10/10 native, 11/11 Breakwater-inspired and 17/17 reduced adaptive-controller evidence is preserved without upgrading its scope. The aggregate runtime/scientific gate remains open until user-local runtime artifacts are reviewed.
