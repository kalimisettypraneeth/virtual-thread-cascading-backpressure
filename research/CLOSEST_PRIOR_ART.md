# Closest Prior Art — Virtual-Thread Cascading Backpressure

Review date: 2026-09-28  
Status: **EVIDENCE TABLE IN PROGRESS — NOVELTY UNVERIFIED**

Overlap taxonomy: `DIRECT`, `SUBSTANTIAL`, `PARTIAL`, `ADJACENT`, `FOUNDATIONAL`, `NONE IDENTIFIED`.

| Work | Year / venue | Research question or mechanism | Workload / setting | Metrics or decision signals | Artifact / primary source | Overlap | Exact differentiation still requiring proof |
|---|---|---|---|---|---|---|---|
| JEP 444: Virtual Threads | 2023 / OpenJDK specification | Make thread-per-request applications scale using lightweight threads; motivates throughput with Little's Law | Java server applications with blocking I/O | throughput, concurrency, latency framing | https://openjdk.org/jeps/444 | FOUNDATIONAL | Virtual threads and Little's-Law framing are not contributions. |
| Oracle Java 21 Virtual Threads guidance | Java 21 / official platform guidance | Limit access to scarce services with virtual threads | semaphores and database connection pools | permit/pool concurrency boundary | https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html | SUBSTANTIAL | Fixed semaphores and pool limits are established. |
| Adaptive Overload Control for Busy Internet Servers | 2003 / USENIX USITS | Adapt admission to bound percentile response time during overload | dynamic Internet services with explicit request queues | 90th-percentile response time and admitted load | https://www.usenix.org/conference/usits-03/adaptive-overload-control-busy-internet-servers | DIRECT | Adaptive percentile-latency admission predates virtual threads; latency-target control is not novel. |
| A Method for Transparent Admission Control and Request Scheduling in E-Commerce Web Sites | 2004 / WWW | Achieve stable behavior and improved response time in overloaded multi-tier Web sites | multi-tier e-commerce applications | stability, throughput, response time | IBM record: https://research.ibm.com/publications/a-method-for-transparent-admission-control-and-request-scheduling-in-e-commerce-web-sites | DIRECT | Stable multi-tier overload behavior through admission and scheduling is established. |
| Stabilization of an Overloaded Queueing Network Using Measurement-Based Admission Control | 2006 / Journal of Applied Probability | Characterize stability when distributed admission uses imperfect measurements | overloaded queueing network model | stability region and sensitivity to feedback parameters | DOI 10.1239/jap/1143936256 | DIRECT | A measured stability region and feedback sensitivity are established theory; a “transition surface” alone is unsafe. |
| Overload Control for Scaling WeChat Microservices (DAGOR) | 2018 / ACM SoCC | Decentralized overload control and collaborative shedding | account-oriented WeChat microservices | success rate and fairness | DOI 10.1145/3267809.3267823; https://www.cs.columbia.edu/~junfeng/papers/dagor-socc18.pdf | SUBSTANTIAL | Generic microservice overload control is established. |
| Overload Control for microsecond-scale RPCs with Breakwater | 2020 / USENIX OSDI | Server-driven credit admission using queueing delay | microsecond RPC services and load spikes | queueing delay, goodput, recovery time, tail latency | https://www.usenix.org/conference/osdi20/presentation/cho | DIRECT | Queue-delay credit control and rapid recovery are mandatory baselines. |
| Protego: Overload Control for Applications with Unpredictable Lock Contention | 2023 / USENIX NSDI | Prevent collapse when traditional CPU/latency signals fail under unknown lock contention | Lucene and Memcached | goodput, p99 latency, marginal throughput, congestion collapse | https://www.usenix.org/conference/nsdi23/presentation/cho-inho | DIRECT | Runtime-specific hidden contention and alternative signals are established. A virtual-thread-specific signal must be proven, not assumed. |
| Bouncer: Admission Control with Response Time Objectives for Low-latency Online Data Systems | 2024 / ACM SIGMOD industrial track | Admit queries using per-request percentile response-time estimates and class-specific SLOs | simulation and a production-grade in-memory distributed graph database | percentile response-time objectives, rejection, utilization, starvation | https://arxiv.org/abs/2312.15123 | DIRECT | Database/data-system SLO admission and early rejection are established. |
| Netflix Concurrency Limits (Vegas / Gradient2) | first-party engineering artifact | Estimate service concurrency from latency and queue trends | Java service integrations | inflight concurrency, RTT, divergence, drops/timeouts | https://github.com/Netflix/concurrency-limits | DIRECT | Gradient-based adaptive concurrency is a mandatory baseline. |
| Envoy Adaptive Concurrency filter | official Envoy component | Restrict requests using a gradient concurrency controller | HTTP proxy/service traffic | sample latency, minimum RTT, calculated concurrency limit | https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/adaptive_concurrency_filter.html | DIRECT | Applying gradient control to Java is not differentiation. |
| TopFull: Adaptive Top-Down Overload Control for SLO-Oriented Microservices | 2024 / ACM SIGCOMM | Entry-point control using global observations to maximize SLO-compliant goodput | Online Boutique and other open-source microservice benchmarks | goodput under overload | https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final654-acmpaginated.pdf | DIRECT | Global SLO-goodput control is established. |

## Revised novelty boundary

The following are established and must not be claimed:

- adaptive admission or load shedding;
- percentile-latency/SLO control;
- stable multi-tier behavior under overload;
- queueing stability regions or feedback sensitivity;
- credit-, queue-delay-, gradient-, marginal-throughput-, or global-observation control;
- early rejection for low-latency data systems;
- runtime-specific contention signals in general.

A defensible virtual-thread contribution now requires all of these:

1. define a state or transition phenomenon tied specifically to virtual-thread execution plus a finite downstream pool;
2. show that established queueing/admission models and controllers do not already predict or control it;
3. compare with fixed limits, pool-only limiting, USITS-style adaptive latency control, Breakwater credits, Gradient2/Envoy, Protego-style marginal-throughput signaling, Bouncer-style SLO admission, and TopFull where feasible;
4. demonstrate the effect across workload and downstream-capacity shifts, not one saturation point;
5. state a falsifier under which the result is ordinary multi-tier queueing rather than a new runtime interaction.

## Remaining searches before gate completion

- [ ] Virtual-thread-specific scholarly work combining downstream saturation with admission.
- [ ] Forward/backward citation chains for Breakwater, Protego, Bouncer, and TopFull.
- [ ] Peer-reviewed evaluations of Netflix/Envoy-style adaptive concurrency.
- [ ] Connection-pool/database-pool empirical studies with comparable workloads.
- [ ] Artifact availability and reproducibility status for every mandatory baseline.

## Gate decision

**NOT COMPLETE.** Database/queueing overlap is now substantially mapped and rules out a generic stability-surface claim. Virtual-thread-specific evidence and citation-chain/artifact verification remain open.
