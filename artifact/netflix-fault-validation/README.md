# Prepared server-query interruption correctness harness

**Runtime UNATTEMPTED. Java compilation UNATTEMPTED. Aggregate gate OPEN.**

This harness extends the preserved official Gradient2 adapter with real PostgreSQL `pg_cancel_backend` and `statement_timeout` cases. It is preparation, not an executed runtime result or performance benchmark. The existing frozen contract and its original freeze record are preserved unchanged.

## Scope and invariants

The 18 intended cases combine JDK 21/25, platform JDBC / virtual-thread JDBC / genuine R2DBC, and cancellation before query / server-confirmed active query cancellation / server statement timeout. A control connection polls `pg_stat_activity` for the target backend PID and unique query marker before server cancellation. Timeout cases require active observation and SQLSTATE 57014. Connection close and server inactivity precede exactly one adapter terminal callback; duplicate terminal attempts must not invoke upstream twice. A linked subsequent request must succeed and restore capacity. Failure emits linked request/connection/backend IDs and separate late-cleanup events; such a case cannot pass.

Admission is constant at two with the preserved scripted clock. Requests run sequentially. Physical connections are newly created and closed, not reused pooled connections. These cases cannot certify pooled reuse, dynamic Gradient2 adaptation, concurrent callback races, client subscription cancellation, network faults, native/foreign pinning, or native performance. R2DBC setup uses blocking orchestration while the actual query is a subscribed publisher.

## Offline invocation

Run from the repository root using existing user-owned Docker and the preserved full official evidence directory:

```sh
python3 artifact/netflix-fault-validation/run.py --official-evidence /absolute/path/to/20261008-official --preflight
python3 artifact/netflix-fault-validation/run.py --official-evidence /absolute/path/to/20261008-official
```

The official directory must include `upstream/concurrency-limits-core/build/classes/java/main/` and `runtime-dependencies/`. Required class and JAR bytes are checked against inherited locks. Source pinning or archived hash listings alone cannot recover missing binaries. This runner never downloads dependencies or pulls images, and fails when any required input is missing. Images reuse the existing digest pins; Docker execution explicitly uses linux/amd64. ARM64 execution therefore remains emulated correctness and never native performance. Retain the entire new `artifact/results/netflix-fault-validation/run-*` directory, including command arrays, exit codes, stdout/stderr, versions and results. A PASS requires all 18 runtime executions plus the frozen checker. Compile failure or incomplete runs are FAIL/Partial, not PASS. Every outcome, including preflight, compilation failure and partial runtime failure, receives an outcome manifest and SHA256SUMS covering all emitted raw files.

## Available local checks

`python3 artifact/netflix-fault-validation/test_invariants.py` runs synthetic checker tests. Nine tests passed, covering a valid synthetic matrix and rejection of missing active observation, duplicate close, duplicate callback, unresolved work, wrong backend PID, missing linked followup, early terminal and failed cancellation. These are checker tests only. Python syntax checks do not certify Java compilation or runtime behavior.

Preflight in the available environment records missing Docker and required omitted official class/JAR binaries. No actual query was issued and no runtime result is available.
