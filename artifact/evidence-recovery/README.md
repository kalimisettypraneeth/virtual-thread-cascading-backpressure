# Original baseline evidence recovery (preparation only)

Inspected source commit: `c26f24cfcf9d5753665b3c931b8c3442e40c8b67`.
No real full-original recovery, Docker run, native execution, benchmark, or scientific replay was performed. The full scientific gate remains **OPEN**.

## Observed layouts and source binding

`expected.json` binds the two review ZIPs by SHA-256 and records 836 distinct expected original paths/hashes. Its allowlist is the union of:

* Runtime `artifact/results/runtime-validation/20261008T064525Z-e67bd535/SHA256SUMS` (408 entries), `artifact/review/PACKAGE_INVENTORY.json` original hashes, and `artifact/review/EXCLUDED_EVIDENCE.json` hashes in `VT_BASELINE_VALIDATION_AUDIT_20261008.zip`.
* Netflix `artifact/results/netflix-validation/20261008-official/RAW_SHA256SUMS` and root `PACKAGE_INVENTORY.json` original hashes in `NETFLIX_GRADIENT2_BASELINE_REVIEW_20261008.zip`.

The runtime packager excludes Docker image TARs, dependency JARs, JFR recordings and compiled/generated binaries. Netflix's raw index includes retained tooling/dependency files; its compact packager omits many of those bytes, and the original index intentionally excludes `.git`, `.gradle` and `gradle-cache`. This recovery does not claim to recover unindexed caches. Both review ZIPs **include small raw records**. Some packaged text is redacted and its package hash differs from the original hash. Package-byte verification alone does not establish original full-local hashes or omitted binary integrity.

The pinned allowlist includes original source inventory files as well as both run directories; supply the historical original repository root with those exact bytes. A current checkout or extracted redacted ZIP is insufficient. Never regenerate original indexes or overwrite source files to make checks pass. Source hashes and historical `source_head`/`source_status` remain in original manifests: an uncommitted runner patch there describes the historical execution snapshot, not today's status.

## Exact local invocation

Requires Python 3.9+ on a POSIX host with `O_NOFOLLOW` and directory descriptors. Use a stable, user-owned evidence tree with no concurrent writers. No dependencies, network calls, recursive collection, credential lookup, or workloads are used.

```sh
python3 artifact/evidence-recovery/recover.py --root /absolute/path/to/original-repository
python3 artifact/evidence-recovery/recover.py --root /absolute/path/to/original-repository --output /absolute/path/to/private-output/baseline-originals.tar
```

First command is the dry-run: it checks every required original and reports payload bytes and a conservative uncompressed archive disk bound. Second repeats verification and prints sizes **before** archive creation; it requires sufficient free space and a new output name. Missing originals or any mismatch exits 1 and creates no final archive. Parent output directory must already exist. Output permissions are 0600. Raw evidence can retain private paths and fixture values: keep this archive local/private; review separately before sharing. The collector does not redact or claim to detect every secret.

Archive layout: `originals/<original repository-relative path>`, byte-identical `RECOVERY_PLAN.json`, and `RECOVERY_MANIFEST.json` with each original SHA-256, byte count and observed filesystem mtime in integer nanoseconds. Recorded timestamps embedded in original evidence remain byte-identical. Observed mtimes are collection-time filesystem metadata, not independently verified historical timestamps; TAR timestamps are convenience fields and the integer manifest is authoritative. No absolute host root is added. The archive is re-read and every payload rehashed before atomic no-clobber publication. Source inputs are never modified. Symlinks (including intermediate parents), traversal, absolute names, control characters, nonregular files and ambiguous paths fail. No archive extraction is performed. Integrity PASS is not replay PASS.

## Verification and blockers

```sh
python3 -m unittest discover -s artifact/evidence-recovery -v
```

Nine synthetic tests pass: complete byte/metadata preservation, dry-run, missing original, mismatched original, unsafe paths, leaf link, parent link, no-clobber and nonblocking FIFO rejection. Real-original acceptance remains blocked because full historical runtime/Netflix originals (including omitted binaries) are not supplied here. Existing review ZIP small records remain available and are not described as missing. Preparation is reviewable; full recovery requires a later user-side original-byte verification. No performance or novelty conclusion follows from these tests.
