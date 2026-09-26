#!/usr/bin/env python3
"""Prepare GitKeepr repository files for a new release without publishing it."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def normalize_version(value: str) -> str:
    value = value.strip()
    if value.startswith("v"):
        value = value[1:]
    if not SEMVER_RE.fullmatch(value):
        raise ValueError("version must be X.Y.Z, optionally prefixed with v")
    return value


def version_tuple(value: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in value.split("."))


def current_version(root: Path = ROOT) -> str:
    return normalize_version((root / "VERSION").read_text().strip())


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one occurrence of {old!r}, found {count}"
        )
    return text.replace(old, new, 1)


def release_notes_template(version: str, previous: str) -> str:
    return f"""# GitKeepr v{version}

## Summary

<!-- Replace this comment with a concise release summary. -->

## Changes

- TODO

## Validation

- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `bash -n bin/gitkeepr`
- [ ] `bash -n install.sh`
- [ ] Self-development PR reached `gitkeepr:ready` with Review `PASS`

## Upgrade

This release supersedes `v{previous}`. Installing the newer release updates the CLI.
Run `gitkeepr init` in each managed private repository to review and explicitly
update its release-pinned caller. Existing healthy repository runners do not need
to be re-registered solely because the GitKeepr release changed.
"""


def build_updates(
    new_version: str, root: Path = ROOT
) -> tuple[str, dict[Path, str]]:
    old_version = current_version(root)
    if version_tuple(new_version) <= version_tuple(old_version):
        raise ValueError(
            f"new version {new_version} must be greater than current version {old_version}"
        )

    version_path = root / "VERSION"
    release_notes = root / "docs" / "releases" / f"v{new_version}.md"
    if release_notes.exists():
        raise RuntimeError(
            f"release notes already exist: {release_notes.relative_to(root)}"
        )

    cli_path = root / "bin" / "gitkeepr"
    installer_path = root / "install.sh"
    caller_path = root / "templates" / "gitkeepr.yml"

    cli = replace_once(
        cli_path.read_text(),
        f'VERSION="{old_version}"',
        f'VERSION="{new_version}"',
        "bin/gitkeepr",
    )
    installer = replace_once(
        installer_path.read_text(),
        f'VERSION="${{GITKEEPR_VERSION:-{old_version}}}"',
        f'VERSION="${{GITKEEPR_VERSION:-{new_version}}}"',
        "install.sh",
    )
    caller = replace_once(
        caller_path.read_text(),
        f"MatousekJakub/gitkeepr/.github/workflows/pr-loop.yml@v{old_version}",
        f"MatousekJakub/gitkeepr/.github/workflows/pr-loop.yml@v{new_version}",
        "templates/gitkeepr.yml",
    )

    updates = {
        version_path: f"{new_version}\n",
        cli_path: cli,
        installer_path: installer,
        caller_path: caller,
        release_notes: release_notes_template(new_version, old_version),
    }
    return old_version, updates


def write_updates(
    updates: dict[Path, str],
    writer: Callable[[Path, str], None] | None = None,
) -> None:
    """Write all updates and restore the original state if any write fails."""
    backups: dict[Path, str | None] = {
        path: path.read_text() if path.exists() else None for path in updates
    }
    written: list[Path] = []

    if writer is None:
        def writer(path: Path, content: str) -> None:
            path.write_text(content)

    try:
        for path, content in updates.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            written.append(path)
            writer(path, content)
    except Exception as exc:
        rollback_errors: list[str] = []
        for path in reversed(written):
            try:
                original = backups[path]
                if original is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_text(original)
            except Exception as rollback_exc:
                rollback_errors.append(f"{path}: {rollback_exc}")

        if rollback_errors:
            details = "; ".join(rollback_errors)
            raise RuntimeError(
                f"release preparation write failed ({exc}); rollback also failed: {details}"
            ) from exc
        raise RuntimeError(
            f"release preparation write failed ({exc}); repository changes rolled back"
        ) from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare version-coupled GitKeepr files for a new release."
    )
    parser.add_argument("version", help="new release version, e.g. 0.1.1 or v0.1.1")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and print planned files without writing them",
    )
    args = parser.parse_args()

    try:
        new_version = normalize_version(args.version)
        old_version, updates = build_updates(new_version)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    verb = "Would prepare" if args.dry_run else "Preparing"
    print(f"{verb} GitKeepr v{new_version} from v{old_version}:")
    for path in updates:
        print(f"  {path.relative_to(ROOT)}")

    if args.dry_run:
        return 0

    try:
        write_updates(updates)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("")
    print("Release preparation written. Next:")
    print("  1. Complete the generated release notes.")
    print("  2. Run: python3 -m unittest discover -s tests -v")
    print("  3. Run: bash -n bin/gitkeepr && bash -n install.sh")
    print("  4. Inspect git diff and open a normal self-development PR.")
    print("  5. After merge, create the GitHub Release from the exact main commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
