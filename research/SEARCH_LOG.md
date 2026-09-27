# Prior-Art Search Log

| Date | Database/Search Engine | Query | Filters | Number/Type of Results | Relevant Results |
|---|---|---|---|---|---|
| 2026-09-26 | OpenJDK | virtual threads concurrency limiting scarce resources | official Java/OpenJDK | JEP/documentation | JEP 444 establishes virtual threads and explicitly warns against pooling virtual threads to limit concurrency; use semaphores for scarce resources. |
| 2026-09-27 | Inside Java / Oracle | virtual threads adoption guide semaphore database connection pool | official Java guidance | adoption guide | The official guide shows semaphore-based throttling and states that a database connection pool itself serves as a semaphore/concurrency boundary. This directly constrains novelty around fixed admission limiting. |
| 2026-09-27 | Web / GitHub artifact discovery | Java virtual threads database connection pool bottleneck benchmark | reproducible/public engineering artifacts; non-peer-reviewed | benchmark repositories and reports | Multiple public artifacts explicitly demonstrate connection-pool saturation after virtual threads remove the platform-thread ceiling. These are leads and engineering prior art, not peer-reviewed novelty proof. |
| 2026-09-27 | Web search | virtual threads backpressure admission control downstream resource saturation Java | exact concept + synonyms | technical articles / engineering discussions | Downstream-resource exhaustion, connection-pool queues, bounded admission, and semaphore guards are already discussed publicly; broad “bottleneck moves downstream” claims are unsafe. |
| 2026-09-27 | Mechanism search | virtual threads overload control concurrency limiting semaphore JEP 444 | mechanism-focused | OpenJDK/Java guidance + technical material | Fixed resource limiting is established. Candidate differentiation must concern measured stability transitions and an adaptive controller, not the existence of backpressure or semaphores. |
| 2026-09-27 | Citation/lead chaining | virtual thread benchmark JDBC HikariCP connection pool saturation | artifact/reference chaining | public benchmark repositories | TNG/java-virtual-thread-benchmark and newer reproducible benchmark artifacts provide implementation/measurement leads for JDBC/HikariCP saturation. Treat as engineering artifacts unless a peer-reviewed publication is verified. |

## Evidence discipline

- Official Java/OpenJDK guidance is used for platform semantics and recommended resource-limiting patterns.
- Public benchmark repositories/articles are recorded as engineering prior art and experimental leads, not substituted for peer-reviewed evidence.
- The candidate claim that a repeatable stability boundary plus adaptive admission control is novel remains **UNVERIFIED** pending deeper scholarly/citation-chain review.
