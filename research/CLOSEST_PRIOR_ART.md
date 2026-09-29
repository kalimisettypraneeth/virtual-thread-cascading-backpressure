# Closest Prior Art — Virtual-Thread Cascading Backpressure

Review date: 2026-09-29  
Status: **EVIDENCE TABLE IN PROGRESS — NOVELTY UNVERIFIED**

Overlap taxonomy: `DIRECT`, `SUBSTANTIAL`, `PARTIAL`, `ADJACENT`, `FOUNDATIONAL`, `NONE IDENTIFIED`.

| Work | Year / venue | Research question or mechanism | Workload / setting | Metrics or decision signals | Artifact / primary source | Overlap | Exact differentiation still requiring proof |
|---|---|---|---|---|---|---|---|
| JEP 444: Virtual Threads | 2023 / OpenJDK specification | Make thread-per-request applications scale using lightweight threads; motivates throughput with Little's Law | Java server applications with blocking I/O | throughput, concurrency, latency framing | https://openjdk.org/jeps/444 | FOUNDATIONAL | Virtual threads and Little's-Law framing are not contributions. |
| JEP 491: Synchronize Virtual Threads without Pinning | 2025 / OpenJDK, delivered in JDK 24 | Let virtual threads blocked in `synchronized` code unmount from carrier threads, removing the dominant Java 21 monitor-pinning mode | Java virtual-thread applications using monitors | carrier availability, pinning/starvation/deadlock risk; JFR pinned events | https://openjdk.org/jeps/491; Oracle JDK 24 release notes https://www.oracle.com/java/technologies/javase/24-relnote-issues.html | DIRECT | Monitor pinning is version-dependent and largely removed in JDK 24. A mechanism observed only on JDK 21 synchronized blocking cannot be generalized as virtual-thread backpressure; test JDK 21 versus 24/25 and isolate remaining native/foreign-function pinning. |
| Considerations for Integrating Virtual Threads in a Java Framework: A Quarkus Example in a Resource-Constrained Environment | 2023 / ACM DEBS industry paper | Integrate virtual threads into Quarkus and compare them with traditional worker pools and reactive execution under scarce resources | Quarkus HTTP service in a resource-constrained container | throughput, latency, CPU, RSS across request rates | DOI 10.1145/3583678.3596895; proceedings https://2023.debs.org/proceedings/ | DIRECT | Resource-constrained Java framework comparisons and cases where virtual threads underperform reactive execution are established. The candidate must compare framework modes and attribute any instability to the finite downstream interaction rather than generic framework/runtime mismatch. |
| Oracle Java 21 Virtual Threads guidance | Java 21 / official platform guidance | Limit access to scarce services with virtual threads | semaphores and database connection pools | permit/pool concurrency boundary | https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html | SUBSTANTIAL | Fixed semaphores and pool limits are established. |
| Oracle Universal Connection Pool real-world performance guidance | Oracle Database 26 / official database guidance | Size total connection pools from database CPU capacity; avoid connection storms and excessive sessions | Java applications using Oracle UCP and finite database CPU | total connections, CPU cores, wait/response behavior, connection reuse | https://docs.oracle.com/en/database/oracle/oracle-database/26/jjucp/optimizing-real-world-performance.html | FOUNDATIONAL | Finite database capacity and CPU-based pool sizing are established operational constraints. Showing that unbounded virtual-thread demand queues behind a finite pool, by itself, is not novel. |
| A Study of Database Connection Pool in Microservice Architecture | 2022 / International Journal on Informatics Visualization | Empirically select a maximum database-connection count for horizontally scaled microservices | Proof-of-concept microservice/e-commerce setting with multiple service instances | request/response time across tested pool sizes | DOI 10.30630/joiv.6.2-2.1094; repository copy https://umpir.ump.edu.my/id/eprint/45609/ | PARTIAL | Connection-pool size affecting microservice response time and an empirical optimum are established, although the study is not virtual-thread-specific. The candidate must use broader workloads and prove a runtime-specific interaction rather than another pool-size benchmark. |
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
- runtime-specific contention signals in general;
- resource-constrained virtual-thread versus worker-pool/reactive performance comparisons;
- finite database capacity, CPU-based pool sizing, and empirical microservice connection-pool tuning;
- Java 21 `synchronized` pinning as a timeless virtual-thread property (JEP 491 removed this monitor-pinning mode in JDK 24).

A defensible virtual-thread contribution now requires all of these:

1. define a state or transition phenomenon tied specifically to virtual-thread execution plus a finite downstream pool, and show whether it persists across JDK 21 and JDK 24/25;
2. show that established queueing/admission models and controllers do not already predict or control it;
3. compare with fixed limits, pool-only limiting, USITS-style adaptive latency control, Breakwater credits, Gradient2/Envoy, Protego-style marginal-throughput signaling, Bouncer-style SLO admission, and TopFull where feasible;
4. demonstrate the effect across workload and downstream-capacity shifts, not one saturation point, while controlling framework mode, carrier parallelism, native/foreign pinning, and JFR pinning evidence;
5. state a falsifier under which the result is ordinary multi-tier queueing or connection-pool sizing rather than a new runtime interaction.

## Remaining searches before gate completion

- [x] Direct scholarly resource-constrained comparison of Quarkus virtual-thread, worker-pool, and reactive modes.
- [ ] Virtual-thread-specific scholarly work combining finite downstream saturation with admission/control.
- [ ] Forward/backward citation chains for Breakwater, Protego, Bouncer, and TopFull.
- [ ] Peer-reviewed evaluations of Netflix/Envoy-style adaptive concurrency.
- [x] Initial microservice connection-pool sizing evidence and official CPU-based pool guidance.
- [ ] Virtual-thread-specific connection-pool studies with comparable workloads and runtime controls.
- [ ] Artifact availability and reproducibility status for every mandatory baseline.

## Gate decision

**NOT COMPLETE.** Database/queueing overlap, finite-pool sizing, the JDK-version boundary, and one direct framework study are mapped. The exact virtual-thread-plus-finite-pool control intersection still lacks verified scholarly equivalence; virtual-thread-specific pool studies, citation chains, peer-reviewed adaptive-controller evaluations, and artifact verification remain open.
