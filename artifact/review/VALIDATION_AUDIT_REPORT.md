# Virtual Thread baseline validation audit

## Decision and provenance

**Local deterministic correctness smoke gate: PASS. Aggregate scientific/selected-baseline readiness gate: OPEN.** Audited the existing run `artifact/results/runtime-validation/20261008T064525Z-e67bd535`; no matrix, container, benchmark, dependency resolution, or download was executed for this audit. Original raw evidence remains untouched.

Commit `5aabf1d18a4bbdc1dd66b101e4d603972a0bd9a4` plus the exact uncommitted runner compatibility patch. All source/config hashes recorded in manifest.json still match local files. Current Git diff is byte-identical to the patch preserved after execution and is included at `artifact/review/run.py.compatibility.patch`. The patch is unredacted and exact. No commit/push was performed.

## Independently verified in this audit

| Item | Status | Direct evidence |
|---|---|---|
| Top-level assertions | PASS: 94/94 | Parsed assertions.json; every entry PASS |
| Workload cases | PASS: 30/30 | Enumerated 2 JDKs × 5 controls × 3 modes; inspected per-case assertions and independently calculated all 12 expected requests per case |
| File integrity | PASS: 408/408 | Rehashed every original SHA256SUMS entry, including excluded binaries |
| Image integrity | PASS: 3/3 | Rehashed actual config bytes in local saved image archives against unchanged config locks; verified Linux/AMD64 |
| JDK observations | PASS | Version stderr and JVM properties: Temurin 21.0.12.1+1-LTS and 25.0.4.1+1-LTS |
| PostgreSQL observation | PASS | database-version stdout records PostgreSQL 16.15 |
| Monitor fixtures | PASS: 4/4 | Parsed pinning.json and independently counted retained JFR JSON events: four scenario markers each; JDK21 virtual 4 pins, other three fixtures 0 |
| Architecture | PASS, with scope limitation | Manifest macOS 26.6.2/arm64; Docker info aarch64; Docker command argv requests linux/amd64 and JVM os.arch is amd64. AMD64 emulation on ARM64 is established by these recorded architectures; specific emulation engine not recorded |
| Compatibility patch/source | PASS | Current SHA-256 matches execution manifest; diff matches previously preserved patch |
| Command failures | No unresolved failure | Only nonzero recorded command is initial pg_isready exit 2; later readiness succeeds. Build/case/cleanup commands exit zero |
| JNI compiler/native fixture | UNATTEMPTED | native-build stdout: NATIVE_UNAVAILABLE_NO_CC; no packages installed |
| Foreign calls and performance | UNATTEMPTED | No FFM fixture or performance experiment in this bundle |
| Mandatory checks blocked in this run | BLOCKED: none | All mandatory smoke checks completed |

Every workload outcome CSV was compared against an independently calculated oracle: IDs 0–11, value 7×ID+3, fixed/reduced controls reject each third held-batch request, pool-only accepts all. Per-case peak active operations are at most two and active_at_end is zero. Returned pool/admission capacity and interface identity are enforced by the executed harness; independent reinspection of their runtime internals was not performed. Passing recorded assertions is evidence of this contract, not a new execution.

Docker logs record client/engine 28.1.1, Desktop 4.41.1 (191279), Linux VM kernel 6.10.14-linuxkit. The run's resource limits, scheduler flags, start/end timestamps, dependency downloads and image references are preserved. Scope is constant-input, held-batch smoke validation; reduced Gradient2/Envoy/Breakwater comparators are not official upstream baselines.

## Facts inherited from prior reporting, not independently reobserved

The prior Codex report and session recorded outer command exit **0**. The bundle records PASS and contains runner source identity, but no raw outer-shell exit-code file; this audit did not reexecute the command to observe that code. Source logic maps PASS to zero. The prior report also recorded absence of live Docker resources after cleanup and 83 GiB free host space. This audit verifies successful historical cleanup commands only; it did not query live Docker or disk availability. Prior synthetic patch-unit-test results are historical, not rerun here. These claims are not needed to establish artifact integrity.

## Package contents, transformations, and exclusions

Repository-relative paths are preserved. All small successful-run logs are included, including both JDK version/flags/JFR metadata logs, JFR event JSON text, PostgreSQL readiness/version/database logs, image pull/inspect/save logs, and the transient failed-command logs. All 30 original assertion JSONs, outcome CSVs and JVM property texts are included. Original runner output has no outcome JSONs: 30 derived outcomes.json files are lossless CSV conversions with explicit provenance labels. Four pinning.json files are included.

Personal checkout paths become `<REPO_ROOT>`; user-home paths become `<USER_HOME>`; the disposable PostgreSQL fixture password is replaced by `<REDACTED_FIXTURE_PASSWORD>`. Redactions affect share copies only. No production credentials are needed. The exact compatibility patch contains neither credentials nor personal paths. Local uid/gid and technical host architecture remain as reproducibility metadata.

Original SHA256SUMS is included unchanged as the 408-file raw-evidence index. **It cannot validate this compact ZIP end-to-end**: some files are omitted and selected text copies are redacted. PACKAGE_INVENTORY.json maps original to packaged hashes and flags redactions. PACKAGE_SHA256SUMS verifies all packaged entries except itself. AUDIT_VERIFICATION.json captures independent verification. ZIP has a separate external .sha256 file.

EXCLUDED_EVIDENCE.json lists every omitted run file, size, reason, and raw hash: three Docker image TARs, 29 dependency JARs, 34 JFR binaries, and compiled classes. JFR binaries remain in the original run; no fixture failure required their inclusion. Excluding binaries limits remote review to preserved event extracts and audited hash assertions; ChatGPT cannot independently regenerate events or inspect the full excluded images from this ZIP. Three small config blobs extracted byte-for-byte from the saved images are included under artifact/review/image-configs; their SHA-256 values can be compared directly against the image lock, independently of Docker .Id. Unrelated files, prior runs, Git internals and the previous Codex narrative report are excluded. Raw evidence must remain available locally for deeper review.

Context README/research inventory documents are included as historical records. Their PREPARED/UNATTEMPTED and missing-local-Docker wording predates this successful run; the scoped runtime result above supersedes those specific historical environment statements, without upgrading official-baseline readiness.

## Next scientifically valid milestone (proposed, not executed)

**Pinned official Netflix Gradient2 build, smoke, and independent dynamic-trace conformance**, as already required by research/BASELINE_ARTIFACTS.md. This closes a concrete external-baseline gap without pretending the constant-capacity reduced adapter establishes adaptation or upstream equivalence.

Acceptance criteria:

1. Use recorded upstream revision `78a74b9878d38c4c048b0304ce12a162ab7b7222`; verify source identity and license from the pinned checkout before building. Existing inventory is historical evidence, not a fresh upstream verification.
2. Freeze build tooling and the full resolved dependency closure with versions/checksums; resolve documented dynamic ranges explicitly. Preserve upstream changes separately and justify them. Record commands, exit codes and full logs.
3. Run official tests and a minimal Gradient2 API/listener smoke test in a pinned local environment. Capture actual JDK and platform versions; do not call upstream failures comparator failures or hide build blockers.
4. Define fixed independent expected traces before testing: warm-up, sustained increase/decrease, EMA/recovery, app-limited suppression, clamps/bounds, drops, and completion/listener accounting. Obtain the expected decisions from the pinned specification/source through a separate oracle; do not use implementation outputs as expected values. Document tolerances and every adapter/reduced-comparator deviation.
5. Verify the official adapter against the same downstream resource/workload semantics, including error/cancellation lease release. Retain the current reduced comparator as separately labeled evidence. Publish PASS/FAIL/BLOCKED/UNATTEMPTED outcomes and hashes. No numeric performance conclusions at this gate.

This milestone does not by itself finish all selected baselines: official Envoy provenance/smoke/conformance, JNI/foreign coverage where selected, bounded platform worker-pool coverage, and stress/error/cancellation/saturation remain open. Before a performance milestone, preregister workload, warm-up/repetitions, offered-load measurement, coordinated-omission treatment, metrics/statistical analysis and hardware/resource controls; run on appropriate native hardware with complete provenance. AMD64-on-ARM64 smoke results do not support JDK latency rankings, throughput claims, overload collapse, fairness, or the paper's research conclusions.
