# Prior Art Evidence

Evidence review date: 2026-09-27.

OpenJDK JEP 444 establishes virtual threads in Java 21. Oracle Java 21 documentation says virtual threads should not be pooled to limit concurrency and recommends semaphores when access to a limited external resource must be bounded. It also notes that a database connection pool itself provides a concurrency boundary.

Sources:
- https://openjdk.org/jeps/444
- https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html

This means the project must not present virtual threads, semaphore-based limiting, connection-pool limiting, or the existence of downstream resource ceilings as new ideas.

A first exact-term and synonym search also found public benchmark artifacts showing database connection pools becoming the bottleneck after virtual threads remove a platform-thread ceiling. Those artifacts are useful leads but are not being treated as peer-reviewed novelty evidence.

The remaining candidate question is narrower: whether overload onset can be measured as a repeatable stability boundary across virtual-thread concurrency and finite downstream capacity, and whether adaptive admission control can maintain stable operation better than fixed limits. This remains unverified until deeper scholarly and citation-chain searches are complete.

Novelty status: UNVERIFIED.
