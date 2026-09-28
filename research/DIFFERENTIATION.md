# Differentiation — Virtual-Thread Cascading Backpressure

Review date: 2026-09-28  
Source audit head: `143bf4b26e160d6c7f2d1b6ac7055e339d936767`  
Status: **PROVISIONAL — NOVELTY UNVERIFIED**

## Research question

Under workload shifts, can a measurable stability-transition surface across offered load, virtual-thread concurrency, and finite downstream capacity predict collapse early enough for adaptive admission control to preserve throughput and tail latency better than fixed limits?

## Closest established work and exact boundary

| Established result or mechanism | Overlap | Not our contribution | Candidate differentiation |
|---|---|---|---|
| JEP 444 / virtual threads | FOUNDATIONAL | Virtual threads, high-concurrency throughput, Little's-Law framing | Stability-transition characterization for virtual-thread services with finite downstream capacity |
| Oracle Java 21 guidance | SUBSTANTIAL | Semaphores for scarce resources; connection pools as concurrency boundaries | Online estimation and adaptation of the safe operating region |
| Fixed concurrency limits and pool sizing | SUBSTANTIAL | Limiting callers to downstream capacity | Controller response to workload/capacity shifts rather than a manually selected fixed limit |
| General backpressure and overload control | SUBSTANTIAL | Queues, rejection, load shedding, or downstream saturation | A virtual-thread-specific empirical map only if results show behavior not explained by generic queueing alone |

## Candidate contributions

1. A reproducible **stability-transition surface** parameterized by arrival process, service-time distribution, virtual-thread concurrency, pool capacity, and queue/admission policy.
2. Observable early-warning signals—such as queue growth, wait/service-time separation, rejection rate, and tail-latency slope—that predict transition before sustained collapse.
3. An adaptive admission controller compared against:
   - no explicit admission limit;
   - connection-pool-only limiting;
   - fixed semaphore limits;
   - a standard adaptive-concurrency baseline.
4. Evidence separating virtual-thread effects from ordinary finite-capacity queueing.

## Claims this paper must not make

- Virtual threads, Little's Law, semaphores, connection pools, backpressure, or downstream bottlenecks are new.
- Fixed admission limiting is a novel controller.
- A throughput plateau or rising latency alone proves a new stability phenomenon.
- Better results in one configuration establish generality.

## Falsifiers

The candidate contribution is weakened or rejected if:

- the transition is fully predicted by a standard queueing model with no material virtual-thread-specific effect;
- a fixed limit selected without hindsight performs equivalently across tested workload shifts;
- controller gains disappear outside one database, pool, or service-time distribution;
- the proposed warning signal detects collapse only after tail latency is already unacceptable;
- scholarly search finds a prior system that maps the same transition surface and applies equivalent adaptive control.

## Evidence required to pass this gate

- [ ] Closest adaptive-concurrency, overload-control, database-admission, and queueing papers are tabulated with workload, metrics, and artifacts.
- [ ] Each candidate contribution is classified against those papers using the repository overlap taxonomy.
- [ ] The standard adaptive-concurrency baseline is named and justified.
- [ ] Generic queueing predictions are separated from virtual-thread-specific hypotheses.
- [ ] Search log includes exact-term, synonym, mechanism, and backward/forward citation chaining.
- [ ] Candidate claims remain labeled unverified until the evidence table is complete.

## Gate decision

**NOT COMPLETE.** This file fixes the differentiation target and falsifiers, but the gate remains open until the closest-work table and citation-chain evidence satisfy every checklist item.
