#!/usr/bin/env python3
"""Find duplicate files by content hash and report them.

Usage:
    python3 main.py <folder> [--min-size 1024] [--delete] [--json]
"""
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

CHUNK_SIZE = 1024 * 1024


def hash_file(path: Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(folder: Path, min_size: int, recursive: bool):
    files = folder.rglob("*") if recursive else folder.iterdir()
    by_size = defaultdict(list)
    for p in files:
        if p.is_file():
            try:
                size = p.stat().st_size
            except OSError:
                continue
            if size >= min_size:
                by_size[size].append(p)
    groups = []
    for size, candidates in by_size.items():
        if len(candidates) < 2:
            continue
        by_hash = defaultdict(list)
        for p in candidates:
            try:
                by_hash[hash_file(p)].append(p)
            except OSError as exc:
                print(f"Warning: cannot read {p}: {exc}", file=sys.stderr)
        for digest, paths in by_hash.items():
            if len(paths) > 1:
                groups.append({"hash": digest, "size": size,
                               "files": [str(p) for p in sorted(paths)]})
    return sorted(groups, key=lambda g: (-g["size"], g["files"][0]))


def main():
    parser = argparse.ArgumentParser(
        description="Find duplicate files by content hash and report them.")
    parser.add_argument("folder", type=Path, help="Folder to scan")
    parser.add_argument("--min-size", type=int, default=1,
                        help="Ignore files smaller than this many bytes (default: 1)")
    parser.add_argument("--recursive", action="store_true", default=True,
                        help="Scan subfolders too (default)")
    parser.add_argument("--no-recursive", dest="recursive", action="store_false",
                        help="Only scan the top-level folder")
    parser.add_argument("--json", action="store_true",
                        help="Print the report as JSON")
    parser.add_argument("--delete", action="store_true",
                        help="Delete duplicates, keeping the first file in each group")
    args = parser.parse_args()
    if not args.folder.is_dir():
        parser.error(f"not a directory: {args.folder}")
    groups = find_duplicates(args.folder, args.min_size, args.recursive)
    if args.json:
        print(json.dumps(groups, indent=2))
    else:
        if not groups:
            print("No duplicates found.")
        for i, group in enumerate(groups, 1):
            wasted = group["size"] * (len(group["files"]) - 1)
            print(f"\nGroup {i} — {group['size']} bytes each, "
                  f"{wasted} bytes wasted, hash {group['hash'][:12]}...")
            for path in group["files"]:
                print(f"  {path}")
    if args.delete and groups:
        removed = 0
        for group in groups:
            for path in group["files"][1:]:
                Path(path).unlink()
                removed += 1
                print(f"Deleted duplicate: {path}")
        print(f"Deleted {removed} duplicate file(s).")
    total_wasted = sum(g["size"] * (len(g["files"]) - 1) for g in groups)
    print(f"\n{len(groups)} duplicate group(s), {total_wasted} bytes recoverable.")


if __name__ == "__main__":
    main()
