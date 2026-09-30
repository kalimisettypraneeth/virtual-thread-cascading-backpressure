#!/usr/bin/env python3
"""Capture an isolated native-control validation without external services."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "artifact/results/baseline-validation/local"
out.mkdir(parents=True, exist_ok=True)
source = ROOT / "artifact/baselines/NativeControls.java"
commands = [
    ["uname", "-a"], ["java", "-version"], ["java", "--list-modules"],
    ["java", "--source", "17", str(source)],
]
records = []
for index, command in enumerate(commands):
    p = subprocess.run(command, capture_output=True, text=True, timeout=60)
    record = {"argv": command, "exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    records.append(record)
manifest = {
    "captured_at_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "isolated native controls only; not a performance experiment",
    "platform": platform.platform(), "architecture": platform.machine(),
    "os_release": Path("/etc/os-release").read_text(),
    "cpuinfo_first_processor": Path("/proc/cpuinfo").read_text().split("\n\n")[0],
    "logical_cpu_count": os.cpu_count(),
    "meminfo": Path("/proc/meminfo").read_text(),
    "python": sys.version,
    "tools": {name: shutil.which(name) for name in ["java", "javac", "gradle", "mvn", "docker", "podman"]},
    "jdk_directories": sorted(os.listdir("/usr/lib/jvm")),
    "external_services": [], "container_image_digest": None,
    "container_image_note": "No image pulled or launched; host image digest unavailable",
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "validator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "commands": records,
}
(out / "validation.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"evidence": str(out / "validation.json"), "native_exit": records[-1]["exit_code"], "native_stdout": records[-1]["stdout"]}))
sys.exit(records[-1]["exit_code"])
