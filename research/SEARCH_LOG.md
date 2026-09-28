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

## Evidence discipline

- Official Java/OpenJDK guidance is used for platform semantics and recommended resource-limiting patterns.
- Public benchmark repositories/articles are engineering prior art and experiment leads, not substitutes for peer-reviewed evidence.
- The proposed stability-transition surface and adaptive admission controller remain **UNVERIFIED** pending explicit scholarly searches for adaptive concurrency, admission control, overload control, and database queueing.
