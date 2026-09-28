# Prior-Art Search Log

| Date | Database/Search Engine | Query | Filters | Number/Type of Results | Relevant Results |
|---|---|---|---|---|---|
| 2026-09-26 | OpenJDK | virtual threads concurrency limiting scarce resources | official Java/OpenJDK | JEP/documentation | JEP 444 establishes virtual threads and warns against pooling virtual threads to limit concurrency; use semaphores for scarce resources. |
| 2026-09-27 | Inside Java / Oracle | virtual threads adoption guide semaphore database connection pool | official Java guidance | adoption guide | Official guidance shows semaphore-based throttling and states that a database connection pool itself serves as a concurrency boundary. |
| 2026-09-27 | Web / GitHub artifact discovery | Java virtual threads database connection pool bottleneck benchmark | reproducible/public engineering artifacts; non-peer-reviewed | benchmark repositories and reports | Public artifacts demonstrate connection-pool saturation after virtual threads remove the platform-thread ceiling. These are engineering leads, not peer-reviewed novelty proof. |
| 2026-09-27 | Web search | virtual threads backpressure admission control downstream resource saturation Java | exact concept + synonyms | technical articles / engineering discussions | Downstream-resource exhaustion, connection-pool queues, bounded admission, and semaphore guards are already discussed publicly. |
| 2026-09-27 | Mechanism search | virtual threads overload control concurrency limiting semaphore JEP 444 | mechanism-focused | OpenJDK/Java guidance + technical material | Fixed resource limiting is established; candidate differentiation must concern a measured transition surface and adaptive behavior. |
| 2026-09-27 | Citation/lead chaining | virtual thread benchmark JDBC HikariCP connection pool saturation | artifact/reference chaining | public benchmark repositories | TNG/java-virtual-thread-benchmark and newer public artifacts provide JDBC/HikariCP implementation leads. |
| 2026-09-28 | OpenJDK citation-chain review | JEP 444 throughput Little's Law concurrency latency | official primary source | JEP | JEP 444 already frames virtual-thread throughput using Little's Law; basic throughput/concurrency framing is not novel. |
| 2026-09-28 | Oracle primary-source review | Java 21 virtual threads semaphore limited resource connection pool | official documentation | platform guidance | Oracle explicitly prescribes semaphores for limited services and treats connection pools as an existing concurrency boundary. |
| 2026-09-28 | ACM SoCC / author paper | DAGOR overload control scaling microservices adaptive admission | peer-reviewed + author-hosted primary paper | SoCC 2018 paper | DAGOR establishes decentralized overload detection, admission/load shedding, and fairness for large microservice deployments. |
| 2026-09-28 | USENIX OSDI | Breakwater overload control queueing delay credits | peer-reviewed primary source | OSDI 2020 paper | Breakwater uses server-issued credits based on queueing delay and reports rapid recovery from overload; queue-delay adaptive admission is direct prior art. |
| 2026-09-28 | Official GitHub engineering artifact | Netflix concurrency-limits Vegas Gradient2 | first-party implementation | Java library and algorithm documentation | Vegas and Gradient2 estimate concurrency from RTT/queue signals; this is a mandatory engineering baseline, not peer-reviewed novelty evidence. |
| 2026-09-28 | Envoy official documentation | adaptive concurrency gradient controller min RTT | first-party component docs | production proxy feature | Envoy provides gradient-based adaptive concurrency control; merely applying adaptive limits to Java is insufficient differentiation. |
| 2026-09-28 | ACM SIGCOMM / author paper | TopFull adaptive top-down overload control SLO microservices | peer-reviewed author-hosted paper | SIGCOMM 2024 paper | TopFull maximizes SLO-compliant goodput using entry-point global observations and compares against DAGOR and Breakwater. |

## Evidence discipline

- Official Java/OpenJDK guidance is used for platform semantics and resource-limiting patterns.
- Peer-reviewed systems papers define scholarly overlap; first-party Netflix and Envoy artifacts define deployed engineering overlap.
- Public benchmark repositories are experiment leads, not substitutes for peer-reviewed evidence.
- Broad adaptive-admission novelty is rejected. The stability-transition surface remains **UNVERIFIED** pending database admission-control, queueing, forward/backward citation-chain, and virtual-thread-specific searches.
