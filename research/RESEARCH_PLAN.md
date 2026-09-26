# Research Plan

## Hypothesis
Increasing virtual-thread concurrency against a finite downstream resource may produce a nonlinear transition from stable queuing to resource amplification and tail-latency collapse.

## Independent variables
- virtual-thread concurrency
- request arrival rate
- downstream connection/concurrency limit
- downstream service time
- heap size
- CPU allocation
- timeout settings

## Dependent variables
- throughput
- p50/p95/p99/p99.9 latency
- queue depth
- active/suspended virtual threads
- heap occupancy and allocation rate
- GC pause/time
- downstream utilization
- timeout and error rate

## Baselines
1. virtual threads without explicit admission control
2. fixed semaphore/concurrency limit
3. bounded platform-thread worker pool
4. adaptive controller

## Evidence gates
1. Prior-art audit
2. Baseline implementation
3. Reproducibility check
4. Parameter sweep
5. Controller implementation
6. Statistical analysis
7. Manuscript and artifact review
