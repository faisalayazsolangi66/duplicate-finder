# Duplicate Finder

Find duplicate files by content hash and report them.

## Requirements

- Python 3.8+
- No third-party packages (standard library only)

## Usage

```bash
python3 main.py <folder> [--min-size BYTES] [--json] [--delete] [--no-recursive]
```

Files are first grouped by size, then hashed with SHA-256, so only files with identical content are reported as duplicates. `--delete` removes all but the first file in each group — use it carefully.

## Example

```bash
$ python3 main.py ./docs
Group 1 — 2048 bytes each, 2048 bytes wasted, hash a1b2c3d4e5f6...
  ./docs/report.pdf
  ./docs/report-copy.pdf

1 duplicate group(s), 2048 bytes recoverable.
```

## License

MIT — see [LICENSE](LICENSE).
