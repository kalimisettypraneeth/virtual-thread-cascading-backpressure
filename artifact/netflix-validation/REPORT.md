# Official Netflix Gradient2 baseline validation — 2026-10-08

## Result

**PASS for the scoped official core build, frozen Gradient2 trace conformance, API/listener smoke, and bounded downstream adapter validation. Aggregate scientific readiness remains OPEN.** This is newly executed local correctness evidence, not a performance result or equivalence certification for the reduced comparator.

Base repository commit: `9de5ffcaf74c378134ff7132cc60186ce8f8803b`.
Official upstream: `https://github.com/Netflix/concurrency-limits.git`, detached revision `78a74b9878d38c4c048b0304ce12a162ab7b7222`.
Raw new evidence: `artifact/results/netflix-validation/20261008-official/`.
All work remains local and uncommitted. No GitHub writes, PRs, paid services, hosted runners or performance benchmarks were performed.

## Acceptance criteria and evidence

| Criterion | Result | Evidence / precise boundary |
|---|---|---|
| Preserve successful source/config evidence | PASS, newly verified | All 14 working-tree and committed source/config hashes equal the successful execution manifest. Existing committed/local audit ZIP matches companion SHA-256; checked again at completion. Neither package nor original source was rewritten. |
| Docker compatibility helper synthetic checks | PASS, 5 newly executed tests | Actual config byte hashing (not JSON reserialization); whitespace byte change changes digest; two-manifest and empty-manifest rejection; extracted actual Linux/AMD64 guard accepts Linux/AMD64 and rejects ARM64, Windows and missing fields. Results in helper-tests logs. |
| Official source identity/license | PASS, newly verified | Clone from official URL, detached requested commit; all 108 tracked upstream files match that commit. LICENSE is Apache-2.0 and retained. No upstream tracked files modified. |
| Tooling pin | PASS for captured local toolchain | Gradle 8.6 official ZIP checksum verified; all executed extracted distribution files equal that ZIP; wrapper JAR hash captured. Immutable local JDK/Git/JDK11 image ID and saved-image SHA-256 are locked. Installed package versions and downloaded .deb hashes retained. |
| Full resolved build/test closure for core gate | PASS | 275 downloaded dependency/metadata files hashed; per-configuration buildscript/project locks and Gradle strict SHA-256 verification metadata retained. Core gate replay succeeded offline with Docker network disabled. Extra resolved module artifacts are included as a superset; unexecuted modules/configurations are not certified complete. |
| Official core tests | PASS with upstream skips | Two successful official Gradle test executions, exit 0; offline replay reports 59 discovered: 56 passed, 3 upstream-ignored executor simulations, 0 failed/errors. Tests were not disabled or assertions weakened by us. Non-core gRPC/servlet/Jakarta/spectator suites UNATTEMPTED. |
| Independent pre-execution expectations | PASS | 108 rational-arithmetic samples frozen and hashed before Java probe execution, plus listener/workload expectations and Java test hashes. The oracle does not call/read outputs of the Java implementation. It is independently implemented by the same auditor, not externally second-reviewed. |
| Gradient2 conformance | PASS, 108/108 | Warm-up, sustained rises/falls, long-window recovery, app-limited suppression, lower/upper bounds, paired drop/no-drop traces, change-notification accounting. Exact integer limits/counts; frozen ±1 ns tolerance only for exposed truncated long RTT. |
| Minimal official API/listener smoke | PASS | Acquire two/reject third; success/drop/ignore; duplicate and racing terminal events; zero inflight and exactly restored capacity. CAS protection belongs to our adapter, not raw upstream listener API. |
| Matched downstream integration | PASS, 6/6 | JDK21 and JDK25 × JDBC platform/JDBC virtual/R2DBC. Same 12-row fixture, 7×id+3 values, autocommit READ COMMITTED, pool 2, batch 3, 8 accepted/4 rejected. All outcome files independently rechecked. |
| Error/cancellation/resource ownership | PASS within stated injection points | Real SQL division-by-zero error; cancellation after a real borrow before SQL; cancellation pending at an exhausted pool. Each case reports 10 instrumented borrows/10 releases, peak 2, active 0, restored admission. Pool-exhaustion setup connections are separately returned and final pool accounting checked. |
| Cleanup | PASS | Database/network cleanup exit 0; final read-only Docker queries found no run resources. Tooling image/cache retained intentionally. |
| Blocked criteria within this scoped gate | BLOCKED: none | Two prerequisite failures were resolved and preserved below. |
| Broader selected-baseline/research gate | OPEN | No performance, active-query cancellation, overload/saturation dynamics, full official-module suite, or aggregate readiness claim. |

Historical evidence is explicitly separate: the original 30-case matrix, its 94 assertions, and its JFR observations were **not rerun**. The prior audit remains the account of that execution. New source/ZIP integrity verification and synthetic tests do not relabel old executions as new ones.

## Failures, resolutions, and warnings

1. `official-core-tests`, exit **1**: the base Temurin image lacked Git. Nebula could not identify the checkout and failed configuration with missing `postRelease`. Built a local tooling image with Git; no upstream build/Java source edits.
2. `official-core-tests-with-git`, exit **1**: Jakarta project configuration required JDK11. Added the exact recorded Ubuntu JDK11 packages to the local tooling image. The final image is frozen and saved. Gradle filesystem watching was disabled after its container/emulation watcher error; test behavior was not altered.
3. `official-core-tests-jdk11`, exit **0**, and `official-core-offline-locked`, exit **0**, both completed. XML results after the offline replay are retained; the first successful run's console logs/exit remain, but its XML was replaced by the official replay task.
4. Initial database readiness query failed while PostgreSQL initialized, then recovered. Failed command/log evidence is retained.
5. The standalone probe uses SLF4J API without a logging binding and emits the documented no-op logger warning. Controller checks and listener accounting do not depend on log output. Official tests use their resolved reload4j dependencies.

The successful original Docker compatibility fix required no change. All original runtime-validation source/config files remain byte-identical. The full old matrix was unnecessary to rerun.

## Dependency/tooling reproducibility

See `locks/tooling.lock.json`, `locks/resolved-dependencies.json`, `locks/upstream/`, `locks/verification-metadata.xml`, and `locks/integration-dependencies.json`.

The executed core closure resolves JUnit 4.+ to 4.13.2, JUnit engines 5.+ to 5.10.2, and SLF4J 1.7.+ to 1.7.36, with all transitives locked. Additional resolved configurations record Mockito 4.11.0, Spectator 1.7.9, Spring test 5.3.33 and other versions; consult per-configuration locks rather than assuming the whole repository was built. The Jakarta module lock contains only configurations that actually resolved; its suite and unresolvable/unrequested closure are not claimed verified.

Tooling observed: Temurin 21.0.12.1+1-LTS; Ubuntu OpenJDK 11.0.32.1+1-post-1ubuntu1-22.04-Ubuntu; Git 2.34.1 in the tooling image; Gradle 8.6. Adapter execution observed Temurin 21.0.12.1+1-LTS and 25.0.4.1+1-LTS. Docker engine 28.1.1/Desktop 4.41.1; host ARM64 Mac, Linux ARM64 VM, AMD64 containers through emulation. Scheduler parallelism/max pool size are both two for adapter runs. Limits/argv and exact versions are in full logs.

The Dockerfile records discovery against apt repositories; **the saved tooling-image.tar plus its checksum is the exact toolchain snapshot**, not a claim that mutable apt repositories will rebuild identical bytes later. The review ZIP omits this binary image and caches to stay compact. Offline replay requires those preserved local binaries. Dependency hashes were captured from first resolution and subsequently enforced offline; they establish reproducibility, not independent publisher-signature validation. No cloud build scan was used.

## Method and deviation boundary

Detailed source-to-oracle and adapter deviations are in README.md. Of particular importance:

- Official long-RTT warm-up is ten samples; the reduced comparator permits other warm-ups and the old adapter used one.
- Official recovery updates stored RTT after capturing the snapshot used in the current gradient. Reduced code uses its updated field immediately. Under legal tolerance ≥1 and the recovery guard, both current gradients clamp to one; this does not grant general upstream equivalence.
- Official drops are sampled but Gradient2's equation ignores didDrop; paired traces check that behavior. Cancelled work maps to onIgnore in our adapter. This is a documented policy.
- Raw SimpleLimiter callbacks are not idempotent. Atomic terminal ownership in OfficialAdmission supplies exactly-once callbacks; tests cover duplicate/racing completion.
- Database cases deliberately fix admission at two and use a scripted clock. Dynamic equations are separately checked against frozen traces; adaptive feedback from actual database latency under offered load remains UNATTEMPTED.
- Cancellation after borrowing is before query execution (JDBC latch/reactive never publisher). Active server-query cancellation, connection-creation/network failures, close/callback exceptions, timeouts and repeated stress schedules remain UNATTEMPTED.
- Queue-size functions, all defaults/invalid configurations, metrics-export behavior, upstream release tasks and non-core modules remain outside this gate. No assertions were weakened to get PASS.

## Next smallest valid milestone

The official **core** build/smoke/frozen-trace and bounded adapter criteria now have direct evidence. Next extend the already isolated adapter tests to **active database-query cancellation and timeout/error ownership**, freezing expected terminal policy and resource-accounting invariants first. This closes a specific cancellation boundary without introducing performance claims. If the research matrix requires Jakarta/gRPC/servlet/spectator, provide its required JDK17 toolchain and separately lock/build/test those module configurations; do not promote the present core PASS to a whole-repository PASS.

Official Envoy, any selected native/foreign-call coverage, dynamic adaptation under controlled load, and preregistered performance experiments remain separate milestones. No aggregate scientific conclusion follows.

## Review package and preservation

The new `NETFLIX_GRADIENT2_BASELINE_REVIEW_20261008.zip` contains original integration/oracle/tests, locks, this report/README, new JSON evidence, all new stdout/stderr and command logs, pinned upstream source/license/build files, and official XML test results. Package inventory records original and share-copy hashes. Personal paths and the fixture password in command logs are redacted only in the share copy; integration source retains its explicitly local disposable fixture values for executable review. No account credentials are included.

The package excludes .git databases, Gradle caches/daemon state, generated classes, downloaded dependency JARs, toolchain image/distribution binaries, and unrelated original runs. These remain local and are covered by dependency/tooling locks or the raw-evidence index where applicable. PACKAGE_SHA256SUMS validates packaged files, while RAW_SHA256SUMS describes selected original evidence before redaction; they are intentionally different indexes. The ZIP companion SHA-256 verifies the ZIP itself. The existing runtime audit ZIP is untouched.
