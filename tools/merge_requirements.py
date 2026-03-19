#!/usr/bin/env python3
import argparse
from pathlib import Path
import io


def collect_requirements(root: Path):
    req_files = []
    # collect files matching requirements*.txt and exact requirements.txt
    for p in root.rglob("requirements*.txt"):
        req_files.append(p)
    # Ensure root/requirements.txt is included as well (in case it's named exactly)
    root_req = root / "requirements.txt"
    if root_req.exists() and root_req not in req_files:
        req_files.append(root_req)
    # sort to have deterministic order
    req_files.sort()
    return req_files


def merge_requirements(files):
    seen = set()
    merged = []
    total_lines = 0
    for f in files:
        try:
            with f.open("r", encoding="utf-8") as fh:
                for raw in fh:
                    line = raw.rstrip("\n").rstrip("\r")
                    # normalize whitespace at ends
                    line_norm = line.strip()
                    if line_norm == "":
                        total_lines += 1
                        continue
                    total_lines += 1
                    if line_norm in seen:
                        continue
                    seen.add(line_norm)
                    merged.append(line)
        except Exception:
            # skip unreadable files
            continue
    return merged, total_lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", default=".", help="Root to search for requirement files"
    )
    parser.add_argument(
        "--output",
        default="requirements.txt",
        help="Output requirements file path (relative to root)",
    )
    parser.add_argument(
        "--dry-run",
        dest="dry",
        action="store_true",
        help="Dry run (do not write files)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = (
        Path(args.output).resolve()
        if not Path(args.output).is_absolute()
        else Path(args.output)
    )
    files = collect_requirements(root)

    merged, total = merge_requirements(files)

    print(f"Found {len(files)} requirement files to process.")
    print(f"Total lines scanned (including blanks): {total}")
    print(f"Unique entries collected: {len(merged)}")
    if args.dry:
        print(f"[Dry-run] Would write {output} with {len(merged)} unique lines.")
        return

    # Back up existing output if it exists
    if output.exists():
        try:
            backup = output.with_suffix(output.suffix + ".bak")
            output.rename(backup)
            print(f"Backed up old file to: {backup}")
        except Exception:
            pass

    # Write merged content
    with output.open("w", encoding="utf-8") as fw:
        for line in merged:
            fw.write(line)
            if not line.endswith("\n"):
                fw.write("\n")
    print(f"Wrote merged requirements to: {output}")


if __name__ == "__main__":
    main()
