#!/usr/bin/env python3
"""Validate and install a private cross-device project bundle, without overwriting work."""
import argparse
import hashlib
import json
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--destination', required=True, type=Path)
    args = parser.parse_args()
    destination = args.destination.expanduser().absolute()
    if destination.is_symlink():
        raise RuntimeError('Refusing symlink project destination')
    with zipfile.ZipFile(args.bundle) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise RuntimeError('Duplicate paths in bundle')
        if len(names) != len({name.casefold() for name in names}):
            raise RuntimeError('Case-insensitive path collision in bundle')
        if sum(info.file_size for info in infos) > 20_000_000:
            raise RuntimeError('Bundle exceeds the 20 MB project-text limit')
        for info in infos:
            path = PurePosixPath(info.filename)
            if (path.is_absolute() or '..' in path.parts or '\\' in info.filename
                    or ':' in info.filename or path.as_posix() != info.filename
                    or stat.S_ISLNK(info.external_attr >> 16)):
                raise RuntimeError('Unsafe path in bundle')
            if info.is_dir():
                raise RuntimeError('Bundle must contain files, not directory entries')
        manifest = json.loads(archive.read('bundle-manifest.json'))
        files = manifest['files']
        if set(names) != set(files) | {'bundle-manifest.json'}:
            raise RuntimeError('Manifest does not match bundle contents')
        payloads = {}
        for name, expected in files.items():
            data = archive.read(name)
            if hashlib.sha256(data).hexdigest() != expected:
                raise RuntimeError('Checksum mismatch: ' + name)
            payloads[name] = data
            target = destination / name
            # Validate every target and parent before writing anything.
            for parent in [target, *target.parents]:
                if parent.is_symlink():
                    raise RuntimeError('Refusing symlink project path')
                if parent == destination.parent:
                    break
            if target.exists() and (not target.is_file() or target.read_bytes() != data):
                raise RuntimeError('Existing work differs; will not overwrite: ' + name)
        for name, data in payloads.items():
            target = destination / name
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(data)
            temporary.replace(target)
        for name, expected in files.items():
            if hashlib.sha256((destination / name).read_bytes()).hexdigest() != expected:
                raise RuntimeError('Installed file differs: ' + name)
    print('PASS: installed and verified ' + str(len(files)) + ' private project files')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
