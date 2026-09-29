# Prior-Art Search Log

| Date | Database/Search Engine | Query | Filters | Number/Type of Results | Relevant Results |
|---|---|---|---|---|---|
| 2026-09-26 | OpenJDK | virtual threads concurrency limiting scarce resources | official Java/OpenJDK | JEP/documentation | JEP 444 establishes virtual threads and warns against pooling virtual threads to limit concurrency; use semaphores for scarce resources. |
| 2026-09-27 | Oracle | virtual threads adoption semaphore database connection pool | official guidance | platform documentation | Semaphores and connection pools are established concurrency boundaries. |
| 2026-09-27 | Artifact discovery | Java virtual threads database connection pool bottleneck benchmark | public engineering artifacts | repositories/reports | Public artifacts demonstrate pool saturation after removing platform-thread ceilings; they are leads, not peer-reviewed novelty proof. |
| 2026-09-27 | Mechanism search | virtual threads overload backpressure downstream saturation | exact concept + synonyms | engineering/research leads | Fixed limiting and downstream bottlenecks are established. |
| 2026-09-28 | OpenJDK | JEP 444 throughput Little's Law concurrency latency | official source | JEP | Basic throughput/concurrency framing is not novel. |
| 2026-09-28 | ACM SoCC / author paper | DAGOR overload control scaling microservices | peer-reviewed source | SoCC 2018 | Distributed microservice admission/load shedding and fairness are established. |
| 2026-09-28 | USENIX OSDI | Breakwater overload queueing delay credits | peer-reviewed source | OSDI 2020 | Queue-delay credit admission and fast overload recovery are direct prior art. |
| 2026-09-28 | Netflix first-party repository | concurrency-limits Vegas Gradient2 | implementation/docs | Java library | RTT/queue-trend adaptive concurrency is a mandatory engineering baseline. |
| 2026-09-28 | Envoy documentation | adaptive concurrency gradient controller | first-party docs | production component | Proxy-level gradient control is established. |
| 2026-09-28 | ACM SIGCOMM / author paper | TopFull adaptive overload SLO microservices | peer-reviewed source | SIGCOMM 2024 | Global entry-point control for SLO-compliant goodput is direct overlap. |
| 2026-09-28 | USENIX USITS | adaptive overload control busy Internet servers percentile response | peer-reviewed source | USITS 2003 | Adaptive admission targeting 90th-percentile response time predates the proposed controller. |
| 2026-09-28 | WWW / IBM Research | transparent admission request scheduling multi-tier e-commerce stable overload | peer-reviewed primary record | WWW 2004 | Admission and scheduling already achieve stable multi-tier behavior under overload. |
| 2026-09-28 | Journal of Applied Probability | overloaded queueing network measurement admission stability region | peer-reviewed theory | 2006 journal article | Measurement-based admission already characterizes stability regions and sensitivity to feedback parameters. |
| 2026-09-28 | USENIX NSDI | Protego unpredictable lock contention marginal throughput admission | peer-reviewed source | NSDI 2023 | Runtime-specific contention, failure of conventional signals, and marginal-throughput credit control are established. |
| 2026-09-28 | ACM SIGMOD / preprint | Bouncer response time objectives online data systems admission | peer-reviewed industrial-track record + preprint | SIGMOD 2024 | Per-query percentile-response estimates, early rejection, class SLOs, utilization, and starvation handling constrain database-admission claims. |
| 2026-09-28 | Synthesis | finite downstream pool stability transition virtual threads versus queueing | exact differentiation review | evidence synthesis | A generic stability surface is unsafe; the candidate must demonstrate a virtual-thread/finite-pool interaction not explained by established queueing and admission work. |

| 2026-09-29 | OpenJDK / Oracle | JEP 491 synchronized virtual threads without pinning JDK 24 | authoritative platform and release documentation | JEP + JDK 24 release notes | JDK 24 lets virtual threads blocked in `synchronized` code release carriers. Java 21 monitor-pinning results are version-specific; native/foreign-function pinning remains in Oracle's JDK 24 guidance. |
| 2026-09-29 | ACM DEBS | Quarkus virtual threads resource constrained reactive worker pool | peer-reviewed industry paper + official proceedings | DEBS 2023 paper | Navarro et al. compare virtual threads, traditional worker pools, and reactive Quarkus under scarce resources and report that the virtual-thread integration did not outperform Quarkus reactive execution. Generic resource-constrained VT comparisons are established. |
| 2026-09-29 | Mechanism synthesis | virtual thread finite pool stability JDK 21 JDK 24 pinning framework mismatch | operational discriminator | evidence synthesis | Any proposed transition must persist beyond removed monitor pinning, or be explicitly scoped to JDK 21. Experiments must separate finite-pool coupling from framework integration, carrier scheduling, and remaining native/foreign pinning. |
## Evidence discipline

- Official Java/OpenJDK guidance defines platform and resource-boundary semantics, including the JDK 24 removal of monitor-related carrier pinning.
- Peer-reviewed systems, database, and queueing papers define scholarly overlap.
- First-party Netflix and Envoy artifacts define deployed engineering overlap.
- Broad adaptive-admission, percentile-control, multi-tier stability, measured stability-region novelty, and generic resource-constrained virtual-thread comparisons are rejected.
- JDK-version effects must be explicit: synchronized blocking pins carriers on Java 21 but not as a general rule on JDK 24/25; native/foreign calls remain a pinning control.
- The virtual-thread-specific transition remains **UNVERIFIED** pending the exact virtual-thread-plus-finite-pool admission intersection, citation chains, connection-pool studies, and artifact verification.
