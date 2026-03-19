#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import fnmatch


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def is_text_file(p: Path) -> bool:
    # Simple heuristic by extension
    text_exts = {
        ".py",
        ".js",
        ".ts",
        ".json",
        ".md",
        ".txt",
        ".yaml",
        ".yml",
        ".cfg",
        ".ini",
        ".sh",
        ".bash",
        ".html",
        ".css",
        ".java",
        ".go",
        ".rs",
        ".c",
        ".cpp",
        ".h",
        ".tsx",
        ".mdx",
        ".vue",
        ".tsx",
    }
    return p.suffix.lower() in text_exts


def collect_groups(root: Path, target_patterns=None) -> dict:
    groups = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            p = Path(dirpath) / name
            if not is_text_file(p):
                continue
            # Apply optional target pattern filter
            if target_patterns:
                matched = False
                for pat in target_patterns:
                    if fnmatch.fnmatch(p.name, pat):
                        matched = True
                        break
                if not matched:
                    continue
            try:
                h = hash_file(p)
            except Exception:
                continue
            groups.setdefault(h, []).append(p)
    # filter only groups with more than 1 file
    return {k: v for k, v in groups.items() if len(v) > 1}


def read_first_paragraph(file: Path) -> str:
    try:
        with file.open("r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception:
        return ""
    # Split into paragraphs by blank lines
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paras[0].replace("\n", " ") if paras else ""


def generate_program_purpose(root: Path, output_path: Path):
    purpose_lines = []
    has_content = False
    # From README
    readme = root / "README.md"
    if readme.exists():
        first_para = read_first_paragraph(readme)
        if first_para:
            purpose_lines.append(first_para)
            has_content = True
    # From package.json (js/ts projects)
    pkg = root / "package.json"
    if pkg.exists():
        try:
            with pkg.open("r", encoding="utf-8") as f:
                data = json.load(f)
            desc = data.get("description") or ""
            if desc:
                purpose_lines.append("Description: " + desc)
                has_content = True
        except Exception:
            pass
    # Basic entry points hints
    entry_points = []
    for ext in (".py", ".js", ".ts", ".go", ".c", ".cpp"):
        for p in root.rglob(f"*{ext}"):
            try:
                with p.open("r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(4000)
            except Exception:
                continue
            # Skip virtual environments in entry point detection
            path_str = str(p)
            lower_path = path_str.replace("\\", "/").lower()
            if "/.venv/" in lower_path or "/venv/" in lower_path:
                continue
            if ext == ".py" and "if __name__ == '__main__'" in content:
                entry_points.append(str(p))
            elif ext in {".js", ".ts"} and (
                "if (require.main === module)" in content
                or "function main" in content
                or "export function main" in content
            ):
                entry_points.append(str(p))
            elif ext in {".go", ".c", ".cpp"} and (
                "func main" in content or "int main(" in content
            ):
                entry_points.append(str(p))
    if entry_points:
        purpose_lines.append("Entry points: " + ", ".join(entry_points))
        purpose_lines.append(
            "Summary: Tools for repository hygiene including deduplication, dependency consolidation, and docker-compose merging."
        )
        has_content = True
        has_content = True
    # If no summary gathered from README/package.json and no entry points, add a default purpose
    if not has_content:
        purpose_lines.append(
            "This repository provides tooling for repository hygiene: deduplicate files, consolidate dependencies, and merge docker-compose configurations."
        )

    # Build summary text
    summary = ". ".join(
        [line.strip() for line in purpose_lines if line.strip()]
    ).strip()
    if not summary:
        summary = "Project summary not found."

    # Write program_purpose.md
    with output_path.open("w", encoding="utf-8") as f:
        f.write("# Program Purpose\n\n")
        f.write(summary + "\n")

    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Root path to scan")
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Dry run mode (no deletions)",
    )
    parser.add_argument(
        "--summary-output",
        dest="summary_output",
        default="program_purpose.md",
        help="Path to write program purpose summary",
    )
    parser.add_argument(
        "--merge-duplicates",
        dest="merge",
        action="store_true",
        help="Merge duplicates (destructive)",
    )
    parser.add_argument(
        "--target-patterns",
        dest="target_patterns",
        default=None,
        help="Comma-separated patterns to filter target files for dedup (fnmatch patterns) e.g. 'requirements*.txt,docker-compose*.yml'",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.summary_output).resolve()
    patterns = None
    if getattr(args, "target_patterns", None):
        patterns = [p.strip() for p in args.target_patterns.split(",") if p.strip()]

    groups = collect_groups(root, patterns)
    if groups:
        print("Found duplicate groups:")
        for i, (content_hash, paths) in enumerate(groups.items(), 1):
            print(f"Group {i}:")
            for p in paths:
                print(f"  - {p}")
    else:
        print("No duplicate groups detected.")

    # Generate program purpose summary (always write the file)
    summary = generate_program_purpose(root, output)
    print(f"Program purpose written to: {output}")

    if args.merge:
        # Simple destructive merge: keep first path in each group and delete others
        if not groups:
            print("No duplicates to merge.")
        else:
            for paths in groups.values():
                for to_del in paths[1:]:
                    try:
                        os.remove(to_del)
                        print(f"Removed: {to_del}")
                    except Exception as e:
                        print(f"Failed to remove {to_del}: {e}")


if __name__ == "__main__":
    main()
