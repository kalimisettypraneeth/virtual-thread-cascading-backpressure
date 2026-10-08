#!/usr/bin/env python3
"""Local, allowlisted original-byte collector. Never extracts or executes evidence."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tarfile
import tempfile
import io


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    if (not isinstance(name, str) or not name or '\\' in name or
            any(ord(c) < 32 for c in name) or ':' in name or
            PurePosixPath(name).is_absolute() or
            any(p in ('', '.', '..') for p in name.split('/'))):
        raise ValueError('unsafe path: ' + repr(name))
    return name


def read_original(root, name):
    """Walk directory descriptors with O_NOFOLLOW; reject links including parents."""
    parts = safe_name(name).split('/')
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        f = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        with os.fdopen(f, 'rb') as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise ValueError('not regular: ' + name)
            h = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
            after = os.fstat(stream.fileno())
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise ValueError('changed while reading: ' + name)
            return h.hexdigest(), before
    finally:
        os.close(fd)


def validate(root, plan):
    if plan.get('schema') != 1 or not plan.get('files'):
        raise ValueError('invalid/empty plan')
    records = []
    for name, expected in sorted(plan['files'].items()):
        safe_name(name)
        if not re.fullmatch('[0-9a-f]{64}', expected):
            raise ValueError('invalid hash: ' + name)
        try:
            actual, info = read_original(root, name)
        except OSError as exc:
            raise OSError(f"missing or unsafe original {name}: {exc.strerror}") from exc
        if actual != expected:
            raise ValueError('hash mismatch: ' + name)
        records.append({'path': name, 'sha256': actual, 'bytes': info.st_size,
                        'observed_mtime_ns': info.st_mtime_ns})
    return records


def collect(root, plan_path, output=None):
    plan_bytes = Path(plan_path).read_bytes()
    plan = json.loads(plan_bytes)
    records = validate(root, plan)
    payload = sum(r['bytes'] for r in records)
    # Uncompressed tar: rounded payloads, conservative per-entry PAX/header allowance.
    bound = sum(((r['bytes'] + 511)//512)*512 + 4096 for r in records) + len(plan_bytes)*2 + len(records)*1024 + 102400
    print(json.dumps({'status': 'VERIFIED_ORIGINAL_BYTES', 'files': len(records),
                      'payload_bytes': payload, 'archive_disk_bound_bytes': bound,
                      'scope': 'integrity only; no scientific replay'}, sort_keys=True), flush=True)
    if output is None:
        return records
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError('output already exists')
    if shutil.disk_usage(output.parent).free < bound:
        raise ValueError('insufficient free disk space')
    # Snapshot to private temporary archive; rehash archived bytes before publication.
    fd, tmp = tempfile.mkstemp(prefix='.evidence-', suffix='.tar', dir=output.parent)
    os.close(fd)
    try:
        with tarfile.open(tmp, 'w', format=tarfile.PAX_FORMAT) as tar:
            for r in records:
                name = r['path']
                # Safely acquire each descriptor anew, with no link-following ancestors.
                d = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                try:
                    parts = name.split('/')
                    for part in parts[:-1]:
                        n = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=d)
                        os.close(d); d = n
                    f = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=d)
                    with os.fdopen(f, 'rb') as stream:
                        info = os.fstat(stream.fileno())
                        if not stat.S_ISREG(info.st_mode) or info.st_size != r['bytes'] or info.st_mtime_ns != r['observed_mtime_ns']:
                            raise ValueError('source changed: ' + name)
                        entry = tarfile.TarInfo('originals/' + name)
                        entry.size = info.st_size; entry.mode = 0o600
                        entry.pax_headers = {'mtime': str(info.st_mtime_ns / 1e9)}
                        tar.addfile(entry, stream)
                finally:
                    os.close(d)
            metadata = {'scope': 'integrity only; no replay', 'plan_sha256': digest(plan_bytes), 'files': records}
            for name, data in [('RECOVERY_PLAN.json', plan_bytes), ('RECOVERY_MANIFEST.json', (json.dumps(metadata, indent=2)+'\n').encode())]:
                entry = tarfile.TarInfo(name); entry.size = len(data); entry.mode = 0o600
                tar.addfile(entry, io.BytesIO(data))
        with tarfile.open(tmp, 'r') as tar:
            for r in records:
                h = hashlib.sha256()
                with tar.extractfile('originals/' + r['path']) as stream:
                    for chunk in iter(lambda: stream.read(1024*1024), b''): h.update(chunk)
                if h.hexdigest() != r['sha256']:
                    raise ValueError('archive mismatch: ' + r['path'])
        os.link(tmp, output)  # Atomic no-clobber publication, same filesystem.
        print(json.dumps({'archive': str(output), 'status': 'PASS', 'bytes': output.stat().st_size}))
    finally:
        os.unlink(tmp)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, help='original repository root, never review ZIP extraction')
    parser.add_argument('--plan', default=str(Path(__file__).with_name('expected.json')))
    parser.add_argument('--output', help='new local private .tar; omitted means dry-run')
    args = parser.parse_args()
    try:
        collect(args.root, args.plan, args.output)
    except (OSError, ValueError, KeyError, tarfile.TarError) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
