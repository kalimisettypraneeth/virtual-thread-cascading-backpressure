# Zero-cost native validation and resource plan — DRAFT

The current coordinator host is reported x86_64 with Docker absent; no native performance measurements are available. No available native performance runner is claimed. No hosted/paid compute, quota bypass or cloud account is needed or authorized by this plan. Existing ARM64-host/AMD64-emulated correctness evidence is not native performance evidence.

## Smallest executable next step: local correctness only

Use an already-owned Linux x86_64 machine (or WSL2 x86_64; record VM limits). Suggested preparation allowance: at least 4 logical CPUs, 8 GiB free RAM and 15 GiB free disk for images/dependencies/results. These are planning allowances, not measured minima. The existing runner uses app 2 CPUs/1 GiB and DB 1 CPU/512 MiB; reserve the remaining host capacity for Docker and orchestration. Internet access is needed initially for locked images and dependencies. Python3, Bash, Git and a working local Docker daemon are required; no host JDK/Maven is required. Docker licensing eligibility must already fit the user's local setup; use an existing no-cost Docker Engine installation where applicable.

From an already cloned, reviewed checkout at the eventual approved source commit:

```bash
uname -m
lscpu
docker info --format '{{.OSType}} {{.Architecture}}'
git rev-parse HEAD
git status --short
bash artifact/scripts/validate-runtime.sh --output artifact/results/runtime-validation
```

The command exists today and runs correctness smoke, not a benchmark. Check host x86_64 and Docker Linux AMD64 together; additionally confirm no QEMU/binfmt translation or nested architecture emulation. A Linux/AMD64 container alone is insufficient. Preserve complete generated logs/manifest/JFR/hashes and independently read back all assertions. Missing Docker yields documented UNATTEMPTED rather than a result. This invocation does not extend active-query cancellation, official Envoy, foreign-call or dynamic-load coverage; those remain separate baseline work. No command in this document executes a candidate controller or a performance experiment.

For an ARM64-only local machine, run the pinned AMD64 bundle only for correctness if desired. Native ARM64 performance requires a separately pinned ARM64 JDK/DB/dependency configuration and independent correctness review; do not substitute image tags or infer equivalent performance. If no suitable owned native machine is available, keep performance BLOCKED and proceed only with draft review and existing evidence audit.

## Proposed future performance allocation, after all gates

A minimal single-host exploratory allocation is one owned native x86_64 machine with 8 logical CPUs and 16 GiB free RAM: app 2 CPUs/2 GiB, PostgreSQL 2 CPUs/2 GiB, load generator 2 CPUs/1 GiB, at least 2 CPUs and remaining RAM for the OS/telemetry. Use disjoint affinity sets where topology permits, record sibling/NUMA placement, effective quotas and throttling; keep all arms identical. This is a proposed budget, not verified sufficient capacity. If fewer resources are available, amend and approve the design before data; do not oversubscribe silently. Single-host shared cache/thermal/network effects limit generality. A second owned native host can isolate generation, but its availability is not assumed.

There is no existing performance-runner invocation supplied: it must be implemented only after independent baseline/design approval and validated against the measurement contract. Implementation must emit a dry-run manifest showing exact cells, seeds, durations, resources, bounds and estimated wall time before approval to run. A provisional RQ1 core of 2 JDKs × 3 modes × 3 pools × 5 loads × 2 demand distributions × 10 blocks is 1,800 trials. At 60 s warmup +180 s measurement +30 s drain this is 135 hours serial, excluding startup/calibration; it is not a promise of completion by a calendar checkpoint. Stage an approved reduced primary set if needed: 2 JDKs ×3 modes ×2 pools ×1 primary load ×2 demands ×10 blocks =240 trials, 18 hours plus overhead. The reduced set tests the primary contrast but cannot claim the full stability surface.

Controller and ablation phases add separate preregistered costs and must not steal replicates from the primary analysis after outcomes are seen. No concurrent performance arms on the same hardware. Capture disk budget estimates from pilot raw-record sizes and retain every request; if storage is insufficient, prospectively reduce scope instead of dropping tails/failures. Duration remains fixed per run, and no work-hour constraint is imposed.
