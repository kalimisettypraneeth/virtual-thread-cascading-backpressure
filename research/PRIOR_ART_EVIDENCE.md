# Prior Art Evidence

Evidence review date: 2026-09-28.

## Established work that constrains novelty

OpenJDK JEP 444 establishes virtual threads in Java 21 and explains their throughput purpose using Little's Law: for a fixed latency, higher throughput requires more concurrent work. Oracle Java 21 guidance says virtual threads should not be pooled to limit concurrency; scarce external resources should instead be bounded with mechanisms such as semaphores, and a database connection pool already acts as such a boundary.

Verified sources:
- https://openjdk.org/jeps/444
- https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html

Public benchmark artifacts also show database connection pools becoming the bottleneck after virtual threads remove a platform-thread ceiling. They are useful implementation leads, but are not treated as peer-reviewed novelty evidence.

## Claims this project must not make

- Virtual threads, Little's-Law concurrency reasoning, or downstream resource ceilings are new.
- Semaphore-based admission limiting or connection-pool concurrency boundaries are new.
- Removing a platform-thread bottleneck can expose a downstream bottleneck is new.
- Fixed concurrency limiting alone is a novel controller.

## Candidate defensible gap — UNVERIFIED

The remaining candidate is narrower: measure a repeatable stability-transition surface across offered load, virtual-thread concurrency, and finite downstream capacity; identify observable precursors to overload; and evaluate whether an adaptive admission controller maintains stable operation better than fixed concurrency limits under workload shifts.

This is a research hypothesis, not a novelty claim. It must still be checked against overload-control, queueing, adaptive-concurrency, database admission-control, and citation-chain literature before differentiation can be frozen.

Novelty status: **UNVERIFIED**.
