#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    yaml = None


def ensure_yaml():
    global yaml
    if yaml is None:
        raise RuntimeError(
            "PyYAML is not installed. Install it in your environment to use this script."
        )


def collect_compose_files(root: Path):
    files = []
    if (root / "docker-compose.yml").exists():
        files.append(root / "docker-compose.yml")
    if (root / "docker-compose.yaml").exists():
        files.append(root / "docker-compose.yaml")
    files.extend(list(root.rglob("docker-compose*.yml")))
    files.extend(list(root.rglob("docker-compose*.yaml")))
    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for f in files:
        if f in seen:
            continue
        seen.add(f)
        uniq.append(f)
    return uniq


def load_yaml(p: Path):
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def merge_dict(a: dict, b: dict) -> dict:
    # Recursive merge: dicts merge deeply, lists concatenate and dedupe, scalar values prefer a's value
    out = dict(a) if a else {}
    for k, v in (b or {}).items():
        if k not in out:
            out[k] = v
        else:
            av = out[k]
            if isinstance(av, dict) and isinstance(v, dict):
                out[k] = merge_dict(av, v)
            elif isinstance(av, list) and isinstance(v, list):
                merged = av[:]
                for item in v:
                    if item not in merged:
                        merged.append(item)
                out[k] = merged
            else:
                # prefer existing (from earlier file)
                pass
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", default=".", help="Root to search for docker-compose files"
    )
    parser.add_argument(
        "--output",
        default="docker-compose.all.yml",
        help="Output merged docker-compose file path (relative to root)",
    )
    parser.add_argument(
        "--dry-run", dest="dry", action="store_true", help="Dry run (do not write)"
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = (
        Path(args.output).resolve()
        if not Path(args.output).is_absolute()
        else Path(args.output)
    )

    if yaml is None:
        print(
            "PyYAML is not installed. Install it with: pip install PyYAML",
            file=sys.stderr,
        )
        sys.exit(1)
    ensure_yaml()

    files = collect_compose_files(root)
    if not files:
        print("No docker-compose files found.")
        return

    merged: dict = {}
    for f in files:
        doc = load_yaml(f)
        if not isinstance(doc, dict):
            continue
        merged = merge_dict(merged, doc)

    # Ensure 'services' key exists for readability in the merged output
    if "services" not in merged:
        merged["services"] = {}

    # Dump YAML content
    dumped = yaml.safe_dump(merged, sort_keys=False)

    if args.dry:
        print("Merged docker-compose (dry-run):")
        print(dumped)
        print(f"[Dry-run] Would write to: {str(output)}")
        return

    # Write output
    if output.exists():
        backup = output.with_suffix(output.suffix + ".bak")
        output.rename(backup)
        print(f"Backed up old file to: {backup}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as wf:
        wf.write(dumped)
    print(f"Wrote merged docker-compose to: {output}")


if __name__ == "__main__":
    main()
