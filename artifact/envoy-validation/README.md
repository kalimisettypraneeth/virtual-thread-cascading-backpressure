# Envoy-derived aggregate-boundary comparator

**Partial milestone.** This is a reduced, deterministic Python reimplementation of selected Envoy controller and filter lifecycle transitions. It passes a hand-derived oracle over 45 state snapshots and 112 asserted fields. It is not an official Envoy build, a proxy test, an upstream differential test, or certification of universal trace equivalence. No performance or virtual-thread claim follows.

## Reproduce

From the repository root, using Python 3 (captured run: 3.12.14):

```sh
python3 artifact/envoy-validation/run.py
python3 artifact/envoy-validation/test_validation.py
```

The first command checks the existing frozen oracle and upstream byte pins before executing the comparator. It overwrites `artifact/results/envoy-validation/validation.json` with the new run and environment. The second runs isolated temporary copies and verifies clean execution, rejection of changed oracle bytes, rejection of changed upstream source bytes, and detection of an incorrect upper gradient clamp. No package installation, paid service, Docker, or CI is used. Regenerate the result-directory `SHA256SUMS` if intentionally recapturing results.

`freeze_oracle.py` creates the initial freeze exclusively and refuses to overwrite it. It was executed after authoring literal expected states and before implementing/executing `comparator.py`. The oracle has no dependency on actual outputs. Do not remove/recreate a freeze to hide a disagreement; retain a failed run and document any correction with a separately versioned oracle.

## Provenance

`provenance.json` pins actual retrieved source at Envoy revision `0ac73c8f38e5c1c875103980b0979ef536cd7573`. Unmodified copies of the controller implementation, controller header, HTTP filter implementation, Apache-2.0 LICENSE, and NOTICE are in `upstream/`. Both Git blob SHA-1 and SHA-256 are verified against local bytes before each run. Upstream URLs and file hashes are recorded individually. The Python comparator is explicitly modified/reimplemented logic; upstream files are reference material and are not compiled. Existing reduced-controller and runtime baseline evidence elsewhere in the repository is preserved.

## Observed checks and interpretation

| Area | Frozen checks | Interpretation |
|---|---|---|
| minRTT collection | Startup, request threshold, deferred-limit restoration | Selected controller transitions with injected aggregate output |
| Window lifecycle | Active-window no-op, empty-window no-op, repeated entry, old-epoch sample exclusion | Deterministic event order, not concurrent timer behavior |
| Adaptation | Buffer 25%, gradient 1.25, clamps 0.5/2.0, square-root headroom, truncation, min/max limits | Arithmetic at the aggregate boundary |
| Recovery | Four minimum updates do not trigger; fifth does; explicit timer delivery; new minRTT and growth | Scheduling request modeled; wall-clock scheduling not tested |
| Fixed RTT | Initial value, no recovery scheduling after five minimum updates | Selected fixed-mode state behavior |
| Admission/lifecycle | Full-capacity reject, complete releases/sample, destroy releases/no sample, bypass | Sequential synthetic request handles |
| Adapter guard | Double complete/destroy do not release twice | Additional Python handle guard, not an upstream controller guarantee |
| Negative controls | Oracle/source mutation rejected; incorrect gradient clamp fails | The gate can detect these particular corruptions |

The default traces use minimum concurrency 3; a separate trace deliberately sets controller minimum 4 and sampling concurrency 3 to exercise their distinction. `repeat_window` expands to sequential admit/complete/window calls; it does not inject a desired limit. All complete output snapshots are retained even when only selected fields are asserted. The count of 112 is field assertions, not 112 independent scenarios.

## Deliberate abstraction and remaining gaps

`aggregate` is supplied at the histogram-output boundary. It is not computed by Envoy's `circllhist` approximation and is not a claim that raw latency samples yield exactly that value upstream. The comparator stores/counts synthetic samples but tests no histogram quantile implementation. Timers are explicit events; zero-jitter scheduling and periodic re-entry ordering are modeled only through those events. There is no automatic timer wheel, jitter RNG, dispatcher, mutex, atomics/CAS race test, stats system, runtime override validation, protobuf configuration, upstream forwarding, HTTP/2 reset behavior, error-status handling, or bounded worker-pool integration. Request times are synthetic integers, not observed latency. The handle guard covers one terminal outcome per request; upstream controller methods alone assert outstanding work and do not implement this guard.

The captured environment has no `envoy`, `bazel`, `bazelisk`, or `docker` executable on PATH. Official build execution was **unattempted**, not failed, and this does not prove a build is impossible on another free environment. No dependency-resolution or official binary conformance evidence is claimed. Completing the stronger gate requires the pinned official controller/proxy, its real histogram and event loop, differential traces including races and error/reset lifecycle, and recorded build/runtime provenance.

## Research boundary and falsifiers

This comparator represents an established adaptive-admission mechanism. Its passing trace does not establish a novel controller, stability surface, overload behavior, throughput, or a virtual-thread mechanism. A differential mismatch under matched pinned upstream configuration falsifies any claimed equivalence for that trace. A histogram, timer, or lifecycle mismatch requires narrowing the comparison or replacing the model with the official implementation. Scientific differentiation still requires controls that distinguish ordinary queueing/controller effects; effects explained by those controls or disappearing after JEP 491 cannot support the stronger virtual-thread claim. Native/foreign pinning and JDK 21 versus 24/25 carrier/JFR controls remain separate work.

## Evidence inventory

`artifact/results/envoy-validation/oracle-freeze.json` records the pre-execution oracle hash and time; `validation.json` records complete trace inputs/expected fields/actual snapshots, input hashes, environment, and PASS/FAIL; `negative-controls.log` records four tests. `SHA256SUMS` binds all files in these two directories except itself. These checks verify these locally included files only; they do not newly verify omitted binaries or inherited raw evidence. Source revision, interpreter and tool availability are observations of this run, not registry-derived runtime facts.
