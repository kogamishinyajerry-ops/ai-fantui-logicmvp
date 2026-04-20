#!/usr/bin/env python3
"""
P40 · Verify uploads/ provenance SHA integrity.

Reads docs/provenance/sha_registry.yaml (single source of truth) and compares
against actual SHA256 / size of every file in uploads/.

Exits:
  0 — every uploads/ file is registered and its SHA + size match the registry
  1 — any drift (unregistered file, missing file, SHA mismatch, size mismatch,
       or registry parse error)

Usage:
  python3 scripts/verify_provenance_hashes.py              # standard
  python3 scripts/verify_provenance_hashes.py --strict     # also verify
                                                            # each registry
                                                            # reference file
                                                            # exists

Integrated into pytest default lane via
  tests/test_provenance_sha_integrity.py
so any drift fails CI immediately.

Authority: Kogami 2026-04-20 GATE-P40-PLAN Approved (Q1=A pytest lane ·
Q2=A YAML registry · Q3=A hard fail exit 1).
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print(
        "[verify_provenance_hashes] ERROR: pyyaml not installed. "
        "Install via `pip install pyyaml` (already in project pyproject.toml).",
        file=sys.stderr,
    )
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "docs" / "provenance" / "sha_registry.yaml"
UPLOADS_DIR = REPO_ROOT / "uploads"


def compute_sha256(path: Path, chunk_size: int = 65536) -> str:
    """Stream-hash a file to avoid loading large PDFs fully into memory."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"SHA registry not found at {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Registry {path} did not parse as a mapping")
    if data.get("version") != 1:
        raise ValueError(
            f"Registry {path} has unsupported version {data.get('version')!r}"
        )
    if "files" not in data or not isinstance(data["files"], list):
        raise ValueError(f"Registry {path} missing `files:` list")
    return data


def verify_registered_file(
    entry: dict[str, Any], repo_root: Path
) -> list[str]:
    """Return a list of errors for this registry entry (empty = OK)."""
    errors: list[str] = []
    path_str = entry.get("path")
    if not path_str:
        return ["registry entry missing `path`"]
    actual = repo_root / path_str
    if not actual.exists():
        errors.append(f"registered file missing on disk: {path_str}")
        return errors
    expected_sha = entry.get("sha256")
    if not expected_sha or not isinstance(expected_sha, str):
        errors.append(f"{path_str}: registry entry missing `sha256`")
    else:
        actual_sha = compute_sha256(actual)
        if actual_sha != expected_sha:
            errors.append(
                f"{path_str}: SHA mismatch · expected {expected_sha} · "
                f"actual {actual_sha}"
            )
    expected_size = entry.get("size")
    if expected_size is not None:
        actual_size = actual.stat().st_size
        if actual_size != expected_size:
            errors.append(
                f"{path_str}: size mismatch · expected {expected_size} · "
                f"actual {actual_size}"
            )
    return errors


def verify_coverage(
    registered: set[str], uploads_dir: Path, repo_root: Path
) -> list[str]:
    """Every file in uploads/ must appear in registry."""
    errors: list[str] = []
    if not uploads_dir.exists():
        return []  # empty uploads/ is fine; registry may list aspirational paths
    for item in uploads_dir.iterdir():
        if not item.is_file():
            continue
        rel = str(item.relative_to(repo_root)).replace("\\", "/")
        if rel not in registered:
            errors.append(
                f"uploads/ file not registered: {rel} · add entry to "
                f"docs/provenance/sha_registry.yaml or remove the file"
            )
    return errors


def verify_references(
    entries: list[dict[str, Any]], repo_root: Path
) -> list[str]:
    """--strict: registry `references:` files must exist."""
    errors: list[str] = []
    for entry in entries:
        refs = entry.get("references", []) or []
        path_str = entry.get("path", "<unknown>")
        for ref in refs:
            if not isinstance(ref, str):
                errors.append(
                    f"{path_str}: reference entry is not a string: {ref!r}"
                )
                continue
            ref_path = repo_root / ref
            if not ref_path.exists():
                errors.append(
                    f"{path_str}: reference file missing: {ref}"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify uploads/ provenance SHA integrity vs sha_registry.yaml."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also verify that all registry `references:` files exist.",
    )
    args = parser.parse_args()

    try:
        registry = load_registry(REGISTRY_PATH)
    except (FileNotFoundError, ValueError, yaml.YAMLError) as exc:
        print(f"[verify_provenance_hashes] REGISTRY ERROR: {exc}", file=sys.stderr)
        return 1

    entries: list[dict[str, Any]] = registry["files"]
    registered_paths = {e.get("path") for e in entries if e.get("path")}

    all_errors: list[str] = []
    for entry in entries:
        all_errors.extend(verify_registered_file(entry, REPO_ROOT))
    all_errors.extend(verify_coverage(registered_paths, UPLOADS_DIR, REPO_ROOT))
    if args.strict:
        all_errors.extend(verify_references(entries, REPO_ROOT))

    if all_errors:
        print("[verify_provenance_hashes] FAIL", file=sys.stderr)
        for err in all_errors:
            print(f"  · {err}", file=sys.stderr)
        print(
            f"[verify_provenance_hashes] {len(all_errors)} error(s) · see "
            f"docs/provenance/sha_registry.yaml and adjust.",
            file=sys.stderr,
        )
        return 1

    print(
        f"[verify_provenance_hashes] OK · verified {len(entries)} file(s) · "
        f"strict={args.strict}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
