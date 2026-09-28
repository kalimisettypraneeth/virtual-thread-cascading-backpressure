# Closest Prior Art — Virtual-Thread Cascading Backpressure

Review date: 2026-09-28  
Status: **EVIDENCE TABLE IN PROGRESS — NOVELTY UNVERIFIED**

Overlap taxonomy: `DIRECT`, `SUBSTANTIAL`, `PARTIAL`, `ADJACENT`, `FOUNDATIONAL`, `NONE IDENTIFIED`.

| Work | Year / venue | Research question or mechanism | Workload / setting | Metrics or decision signals | Artifact / primary source | Overlap | Exact differentiation still requiring proof |
|---|---|---|---|---|---|---|---|
| JEP 444: Virtual Threads | 2023 / OpenJDK specification | Make thread-per-request applications scale by making threads lightweight; motivates concurrency and throughput with Little's Law | Java server applications with blocking I/O | Throughput, concurrency, latency framing; no project-specific stability experiment | https://openjdk.org/jeps/444 | FOUNDATIONAL | Our work must study a measured transition surface under finite downstream capacity; virtual threads and Little's-Law framing are not contributions. |
| Oracle Java 21 Virtual Threads guidance | Java 21 / official platform guidance | How to limit access to scarce services when using virtual threads | Semaphores and database connection pools | Permit/pool concurrency boundary | https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html | SUBSTANTIAL | Fixed semaphores and pool limits are established. Any contribution must concern online stability estimation and adaptation under shifts. |
| Overload Control for Scaling WeChat Microservices (DAGOR) | 2018 / ACM SoCC | Decentralized overload control and collaborative load shedding for large microservice deployments | Account-oriented WeChat microservices | Success rate and fairness under overload | DOI 10.1145/3267809.3267823; author paper https://www.cs.columbia.edu/~junfeng/papers/dagor-socc18.pdf | SUBSTANTIAL | A virtual-thread paper must exceed generic microservice overload control by isolating finite downstream capacity and virtual-thread/runtime effects. |
| Overload Control for microsecond-scale RPCs with Breakwater | 2020 / USENIX OSDI | Server-driven credit admission using server-side queueing delay | Microsecond RPC services; demand spike reported at 1.4x capacity | Queueing delay, goodput/stability, recovery time, tail latency | Paper and metadata: https://www.usenix.org/conference/osdi20/presentation/cho | DIRECT | Queue-delay-driven adaptive admission and fast recovery are established. The proposed controller must compare directly and justify why virtual-thread/downstream-pool dynamics require a different model. |
| Netflix Concurrency Limits (Vegas / Gradient2) | public engineering artifact | Automatically estimate service concurrency limits from latency and queueing trends | Java service integrations | Inflight concurrency, minimum/sample RTT, short/long RTT divergence, drops/timeouts | https://github.com/Netflix/concurrency-limits | DIRECT | Latency-gradient adaptive concurrency is established engineering prior art and a mandatory baseline; a renamed gradient controller is not novel. |
| Envoy Adaptive Concurrency filter | official Envoy component | Dynamically restrict requests using a gradient concurrency controller | HTTP proxy/service traffic | Sample latency, minimum RTT, calculated concurrency limit | https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/adaptive_concurrency_filter.html | DIRECT | Proxy-level gradient control is established. Differentiation requires a stronger operational discriminator than using adaptive limits in Java. |
| TopFull: An Adaptive Top-Down Overload Control for SLO-Oriented Microservices | 2024 / ACM SIGCOMM | Entry-point overload control using global observations to maximize SLO-compliant goodput | Online Boutique and other open-source microservice benchmarks | Goodput under overload and comparison with DAGOR/Breakwater | Author-hosted paper: https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final654-acmpaginated.pdf; artifact not verified in this pass | DIRECT | Global adaptive overload control and SLO-goodput optimization already exist. A remaining claim must isolate the virtual-thread/downstream-capacity transition and demonstrate non-equivalence. |

## Current synthesis

The broad phrase **adaptive admission control for overloaded services** is not novel. Breakwater, DAGOR, TopFull, Netflix Concurrency Limits, and Envoy already cover queueing-delay, service-level, distributed, global, and latency-gradient control variants.

A potentially defensible contribution is narrower:

1. operationally define a stability-transition surface for a Java virtual-thread service coupled to a finite downstream pool;
2. demonstrate behavior not adequately predicted by generic queueing or reproduced by existing adaptive-concurrency controllers;
3. identify an early-warning signal that precedes SLO failure under workload or downstream-capacity shifts; and
4. evaluate a controller against Breakwater-inspired credit control, Netflix Gradient2, Envoy-style gradient control, fixed limits, and pool-only limiting.

## Remaining searches before gate completion

- [ ] Database admission-control and connection-pool sizing literature.
- [ ] Queueing-theoretic stability and heavy-traffic transition literature tied to finite server pools.
- [ ] Forward/backward citation chains for Breakwater, DAGOR, and TopFull.
- [ ] Peer-reviewed evaluations of Netflix/Envoy-style adaptive concurrency.
- [ ] Virtual-thread-specific scholarly work combining downstream saturation with adaptive admission.
- [ ] Artifact availability and reproducibility status for every baseline.

## Gate decision

**NOT COMPLETE.** This table materially narrows the claim and identifies mandatory baselines, but the database/queueing and citation-chain searches remain open.
