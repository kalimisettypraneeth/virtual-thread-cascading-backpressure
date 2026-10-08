# Baseline evidence reconciliation — 2026-10-08

**Scoped packaged-evidence audit: PASS. Aggregate scientific/selected-baseline gate: OPEN.** Source readback: `b059710efe659e5b56f092a48a654b685326053b`. This audit independently parses retained records and reruns five synthetic compatibility tests. It does not rerun Docker, Gradle, JDBC/R2DBC workloads or benchmarks.

## Integrity and direct checks

| Check | Result and exact evidence |
|---|---|
| Official ZIP integrity | `artifact/review/NETFLIX_GRADIENT2_BASELINE_REVIEW_20261008.zip`: SHA256 `160a1ea4bff22abf9abac2627d24bc5055cc188a9b6e28c8cd142188867880bb`; companion matches; all 262 indexed package entries rehashed |
| Historical Docker ZIP integrity | `artifact/review/VT_BASELINE_VALIDATION_AUDIT_20261008.zip`: SHA256 `175955ad5cb05dbb8e062921155f3b9424889d4f31d73c709bc9d2d737825d96`; companion matches; all 378 indexed package entries rehashed |
| Official test records | 13 `upstream/concurrency-limits-core/build/test-results/test/TEST-*.xml` files total 59 tests, 3 skipped, 0 failures/errors, hence 56 passed |
| Build chronology | `commands.jsonl` preserves initial missing-Git and missing-JDK11 failures (exit 1), then successful core run and offline locked replay (exit 0). First successful XML was replaced by replay XML; two independent XML sets are not claimed |
| Frozen trace integrity/order | Rehashed `oracle-freeze.json`'s three files. Freeze 07:09:46 UTC precedes `conformance` start 07:15:14 UTC. Listener/workload freeze 07:11:48 UTC also precedes execution |
| Independent trace comparison | Recompared all 108 `logs/conformance.stdout` rows against `expected-traces.json`: exact scenario/index/limit/notifications; RTT absolute tolerance 1 ns. All pass. This checks recorded output, not a fresh Java execution |
| Official adapter outcomes | Independently recalculated 12 outcomes for each of 6 `cases/*/outcomes.csv`: IDs 0–11, accepted values 7×id+3; each third request rejected. Assertions report PASS and active_at_end 0 |
| Historical runtime | Parsed all 94 top-level assertions and recalculated outcomes for all 30 cases. Pool-only accepts all 12; fixed/reduced adapters reject every third held-batch request. All pass with final active 0 |
| Monitor event extracts | Independently counted four retained `logs/*jfr-events*.stdout` JSONs: four `validation.Scenario` markers each; four `jdk.VirtualThreadPinned` events only in JDK21 virtual fixture, zero in JDK25 virtual and both platform fixtures |
| Compatibility patch | Packaged `artifact/review/run.py.compatibility.patch` equals Git diff from `5aabf1d18a4bbdc1dd66b101e4d603972a0bd9a4` to audited source for `artifact/runtime-validation/run.py`. Current synthetic helper suite passes 5/5 |

Netflix raw-path references above are under the official ZIP's `artifact/results/netflix-validation/20261008-official/`. Historical runtime references are under the older ZIP's `artifact/results/runtime-validation/20261008T064525Z-e67bd535/`. Both archives include command logs, stdout/stderr and small raw records. The Docker report is present as `artifact/review/VALIDATION_AUDIT_REPORT.md`; the official report is `artifact/netflix-validation/REPORT.md`. Their execution-time “uncommitted/no push” wording is historical: they are published in the audited source commit.

## Interpretation and provenance limits

The pinned upstream is Netflix `78a74b9878d38c4c048b0304ce12a162ab7b7222`, with retained Apache-2.0 source and identity hashes. Official code, reduced equation comparators, and the original adapter are different artifacts. The rational-arithmetic oracle is a separate implementation derived from source, not an independently authored external oracle. Its expected values were frozen before actual output. API exactly-once terminal ownership belongs to `OfficialAdmission`'s CAS wrapper, not raw upstream listeners. The official downstream adapter fixes capacity at two and uses a scripted clock; its success does not validate adaptive feedback under load. Cancellation is before active SQL or pending at a pool, not active server-query cancellation.

Version logs directly record Temurin 21.0.12.1+1-LTS and 25.0.4.1+1-LTS, PostgreSQL 16.15 and AMD64 JVM architecture. The recorded host/VM architecture is ARM64; Docker commands request Linux/AMD64. This supports emulated correctness only. Registry-declared versions in older preparation documents are distinct from these observed execution records. No present-host Docker availability or rerun is implied.

The compatibility patch hashes actual config bytes from the single saved-image manifest when Docker's inspected ID differs from the locked config digest, enforces Linux/AMD64 in that fallback, then compares the unchanged expected digest. It does not weaken digest acceptance. The five newly executed tests cover raw-byte hashing, changed whitespace, empty/ambiguous manifests, and the actual platform-guard AST.

## Exact remaining evidence boundaries

- The historical package's `EXCLUDED_EVIDENCE.json` names omitted image TARs, 29 dependency JARs, 34 binary JFR recordings and compiled classes. Its original 408-file index is not a new 408/408 verification: this audit rehashes packaged copies only. Raw full-local evidence is not located in this audit workspace; no claim is made that it does not exist elsewhere. Image config extracts and event extracts are available, while regeneration from original binaries remains blocked by the excluded files.
- The official package omits `tooling-image.tar`, `gradle-cache/`, generated classes and runtime dependency JARs. Exact offline replay requires those locked binaries; preserved hashes do not establish their present availability. Gradle/tooling locks describe captured execution, not an identical rebuild from mutable apt repositories.
- Outer-shell Docker exit zero remains inherited reporting: no raw outer-shell exit-code file was found in the retained package. Command-level exits, cleanup commands and result assertions are directly available. No live cleanup state is inferred.
- Non-core Netflix suites, active-query cancellation/timeouts and connection/network/cleanup faults, dynamic adaptation under controlled load, official Envoy execution, and selected JNI/foreign-call coverage are open. The native fixture reports no compiler; foreign calls were unattempted.

JEP 491's JDK24 monitor boundary must remain explicit. A zero-pin JDK25 monitor fixture does not cover native/foreign pinning, establish a VT-specific mechanism, or remove the need for matched carrier/JFR, bounded platform and reactive controls. Reject or narrow a candidate if ordinary queueing or established controllers explain it, or its effect disappears after JEP 491. No latency, throughput, overload, fairness or novelty conclusion follows from these records.

**Acceptance disposition:** official core/trace/bounded adapter and historical runtime evidence are supported within scope; exact binary replay and remaining selected-baseline/scientific criteria are not complete. Keep the gate open and preserve all historical reduced evidence.
