#!/usr/bin/env python3
"""Validate reduced Netflix Gradient2- and Envoy-style equation comparators.

The expected traces below are calculated independently in Python. The Java implementation output
is never reused as its own oracle. This validator performs no downloads and uses only the Python
standard library plus the installed Java source launcher.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "artifact/baselines/AdaptiveControllerComparators.java"
VALIDATOR = Path(__file__).resolve()

UPSTREAM = {
    "netflix": {
        "repository": "Netflix/concurrency-limits",
        "commit": "78a74b9878d38c4c048b0304ce12a162ab7b7222",
        "gradient2_path": "concurrency-limits-core/src/main/java/com/netflix/concurrency/limits/limit/Gradient2Limit.java",
        "gradient2_blob": "08ea57f7e2413ca175e65b823643171d899c03a8",
        "expavg_path": "concurrency-limits-core/src/main/java/com/netflix/concurrency/limits/limit/measurement/ExpAvgMeasurement.java",
        "expavg_blob": "ee70320a4110aba33f751754212ff9bf71ea5515",
        "license": "Apache-2.0",
    },
    "envoy": {
        "repository": "envoyproxy/envoy",
        "commit": "0ac73c8f38e5c1c875103980b0979ef536cd7573",
        "controller_path": "source/extensions/filters/http/adaptive_concurrency/controller/gradient_controller.cc",
        "controller_blob": "610b2dec7757364553859c26d8eafff322d73127",
        "documentation_path": "docs/root/configuration/http/http_filters/adaptive_concurrency_filter.rst",
        "documentation_blob": "3a3cd16866a3fbde8fc304f85678aa3bcfaadb01",
        "license": "Apache-2.0",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd: list[str], *, stdin: str | None = None) -> dict:
    completed = subprocess.run(cmd, input=stdin, text=True, capture_output=True, cwd=ROOT)
    return {
        "command": cmd,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


class NetflixOracle:
    def __init__(self) -> None:
        self.estimated = 20.0
        self.minimum = 1
        self.maximum = 200
        self.smoothing = 0.2
        self.queue = 4
        self.tolerance = 1.5
        self.long_window = 600
        self.warmup = 10
        self.long_rtt = 0.0
        self.total = 0.0
        self.count = 0

    def sample(self, rtt: float, inflight: int) -> tuple[int, float, float]:
        if self.count < self.warmup:
            self.count += 1
            self.total += rtt
            self.long_rtt = self.total / self.count
        else:
            factor = 2.0 / (self.long_window + 1.0)
            self.long_rtt = self.long_rtt * (1.0 - factor) + rtt * factor
        if self.long_rtt / rtt > 2.0:
            self.long_rtt *= 0.95
        if inflight < self.estimated / 2.0:
            return int(self.estimated), self.estimated, self.long_rtt
        gradient = max(0.5, min(1.0, self.tolerance * self.long_rtt / rtt))
        proposed = self.estimated * gradient + self.queue
        proposed = self.estimated * (1.0 - self.smoothing) + proposed * self.smoothing
        self.estimated = max(self.minimum, min(self.maximum, proposed))
        return int(self.estimated), self.estimated, self.long_rtt


def envoy_oracle(old: int, minimum: int, maximum: int, min_rtt: float,
                 buffer_fraction: float, sample_rtt: float) -> int:
    gradient = max(0.5, min(2.0, min_rtt * (1.0 + buffer_fraction) / sample_rtt))
    scaled = old * gradient
    return max(minimum, min(maximum, int(scaled + math.sqrt(scaled))))


def main() -> int:
    output = Path(sys.argv[1] if len(sys.argv) > 1 else
                  ROOT / "artifact/results/baseline-validation/adaptive-controllers/validation.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    netflix_samples = [
        (10.0, 20), (10.0, 20), (10.0, 20),
        (30.0, 22), (40.0, 20), (8.0, 0),
        (8.0, 20), (100.0, 20), (10.0, 20), (10.0, 20),
        (10.0, 20), (60.0, 20),
    ]
    envoy_samples = [
        (20, 3, 1000, 10.0, 0.25, 10.0),
        (20, 3, 1000, 10.0, 0.25, 25.0),
        (20, 3, 1000, 10.0, 0.25, 100.0),
        (900, 3, 1000, 10.0, 0.25, 5.0),
        (3, 3, 1000, 10.0, 0.0, 100.0),
    ]

    stdin_lines = ["NC,20,1,200,0.2,4,1.5,600,10"]
    netflix_expected = []
    oracle = NetflixOracle()
    for rtt, inflight in netflix_samples:
        stdin_lines.append(f"NS,{rtt},{inflight}")
        netflix_expected.append(oracle.sample(rtt, inflight))
    envoy_expected = []
    for sample in envoy_samples:
        stdin_lines.append("E," + ",".join(map(str, sample)))
        envoy_expected.append(envoy_oracle(*sample))
    input_text = "\n".join(stdin_lines) + "\n"

    execution = run(["java", "--source", "17", str(SOURCE)], stdin=input_text)
    lines = [line for line in execution["stdout"].splitlines() if line]
    checks: list[dict] = []
    if execution["exit_code"] == 0 and lines and lines[0] == "NC,OK":
        cursor = 1
        for index, expected in enumerate(netflix_expected):
            parts = lines[cursor].split(",")
            actual = (int(parts[1]), float(parts[2]), float(parts[3]))
            passed = (actual[0] == expected[0] and
                      math.isclose(actual[1], expected[1], abs_tol=1e-9) and
                      math.isclose(actual[2], expected[2], abs_tol=1e-9))
            checks.append({"controller": "netflix-gradient2-derived", "case": index,
                           "input": netflix_samples[index], "expected": expected,
                           "actual": actual, "pass": passed})
            cursor += 1
        for index, expected in enumerate(envoy_expected):
            parts = lines[cursor].split(",")
            actual = int(parts[1])
            checks.append({"controller": "envoy-gradient-derived", "case": index,
                           "input": envoy_samples[index], "expected": expected,
                           "actual": actual, "pass": actual == expected})
            cursor += 1
    else:
        checks.append({"controller": "process", "case": "source-launcher",
                       "expected": "exit 0 and NC,OK", "actual": execution,
                       "pass": False})

    java_version = run(["java", "-version"])
    result = {
        "schema": 1,
        "scope": "Reduced equation/state conformance only; not official artifact builds or performance evidence.",
        "upstream_pins": UPSTREAM,
        "source_sha256": sha256(SOURCE),
        "validator_sha256": sha256(VALIDATOR),
        "fixture_provenance": "Independent Python oracle implementing the pinned source equations and state order.",
        "input_trace": input_text,
        "execution": execution,
        "environment": {
            "platform": platform.platform(),
            "python": sys.version,
            "java": java_version,
            "executables": {name: shutil.which(name) for name in
                            ["java", "javac", "docker", "gradle", "mvn", "bazel", "bazelisk"]},
            "cwd": str(ROOT),
        },
        "checks": checks,
        "summary": {
            "passed": sum(1 for check in checks if check["pass"]),
            "total": len(checks),
            "all_passed": all(check["pass"] for check in checks),
        },
        "deviations": [
            "Netflix: no official dependency graph, metrics, listener plumbing, or Gradle build; only Gradient2 update and ExpAvg state order are represented.",
            "Envoy: no proxy, histogram, timer, forwarding CAS, minRTT sampling window, Bazel build, or runtime config; only calculateNewLimit arithmetic is represented.",
            "No timing, throughput, latency, workload integration, JDK 21/24/25, JDBC, or reactive-framework claim is made.",
        ],
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))
    return 0 if result["summary"]["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
