#!/usr/bin/env python3
"""Release-version consistency and release-preparation contract tests."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text().strip()
CLI = (ROOT / "bin/gitkeepr").read_text()
INSTALLER = (ROOT / "install.sh").read_text()
CALLER = (ROOT / "templates/gitkeepr.yml").read_text()
PREPARE_PATH = ROOT / "scripts" / "prepare-release.py"

SPEC = importlib.util.spec_from_file_location("prepare_release", PREPARE_PATH)
assert SPEC is not None and SPEC.loader is not None
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


def make_fixture(root: Path) -> None:
    (root / "bin").mkdir(parents=True)
    (root / "templates").mkdir(parents=True)
    (root / "docs" / "releases").mkdir(parents=True)
    (root / "VERSION").write_text("0.1.0\n")
    (root / "bin" / "gitkeepr").write_text(
        '#!/usr/bin/env bash\nVERSION="0.1.0"\n'
    )
    (root / "install.sh").write_text(
        '#!/usr/bin/env bash\nVERSION="${GITKEEPR_VERSION:-0.1.0}"\n'
    )
    (root / "templates" / "gitkeepr.yml").write_text(
        "jobs:\n"
        "  gitkeepr:\n"
        "    uses: MatousekJakub/gitkeepr/.github/workflows/pr-loop.yml@v0.1.0\n"
    )


class ReleaseToolingTests(unittest.TestCase):
    def test_versioned_distribution_files_are_consistent(self):
        self.assertRegex(
            VERSION,
            r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$",
        )
        self.assertIn(f'VERSION="{VERSION}"', CLI)
        self.assertIn(f'VERSION="${{GITKEEPR_VERSION:-{VERSION}}}"', INSTALLER)
        self.assertIn(
            f"uses: MatousekJakub/gitkeepr/.github/workflows/pr-loop.yml@v{VERSION}",
            CALLER,
        )
        self.assertNotIn("pr-loop.yml@main", CALLER)

    def test_prepare_release_dry_run_for_next_patch(self):
        major, minor, patch = (int(part) for part in VERSION.split("."))
        target = f"{major}.{minor}.{patch + 1}"
        result = subprocess.run(
            [sys.executable, str(PREPARE_PATH), "--dry-run", target],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in (
            "VERSION",
            "bin/gitkeepr",
            "install.sh",
            "templates/gitkeepr.yml",
            f"docs/releases/v{target}.md",
        ):
            self.assertIn(expected, result.stdout)

    def test_prepare_release_primary_write_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root)

            old_version, updates = PREPARE.build_updates("0.1.1", root)
            self.assertEqual(old_version, "0.1.0")
            PREPARE.write_updates(updates)

            self.assertEqual((root / "VERSION").read_text(), "0.1.1\n")
            self.assertIn(
                'VERSION="0.1.1"',
                (root / "bin" / "gitkeepr").read_text(),
            )
            self.assertIn(
                'VERSION="${GITKEEPR_VERSION:-0.1.1}"',
                (root / "install.sh").read_text(),
            )
            self.assertIn(
                "pr-loop.yml@v0.1.1",
                (root / "templates" / "gitkeepr.yml").read_text(),
            )
            notes = root / "docs" / "releases" / "v0.1.1.md"
            self.assertTrue(notes.exists())
            self.assertIn("# GitKeepr v0.1.1", notes.read_text())
            self.assertIn("supersedes `v0.1.0`", notes.read_text())

    def test_prepare_release_rolls_back_partial_write_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_fixture(root)
            tracked = [
                root / "VERSION",
                root / "bin" / "gitkeepr",
                root / "install.sh",
                root / "templates" / "gitkeepr.yml",
            ]
            originals = {path: path.read_text() for path in tracked}
            notes = root / "docs" / "releases" / "v0.1.1.md"

            _, updates = PREPARE.build_updates("0.1.1", root)
            calls = 0

            def failing_writer(path: Path, content: str) -> None:
                nonlocal calls
                calls += 1
                path.write_text(content)
                if calls == 3:
                    raise OSError("simulated write failure")

            with self.assertRaisesRegex(RuntimeError, "changes rolled back"):
                PREPARE.write_updates(updates, writer=failing_writer)

            for path, original in originals.items():
                self.assertEqual(path.read_text(), original)
            self.assertFalse(notes.exists())

    def test_prepare_release_rejects_invalid_version(self):
        result = subprocess.run(
            [sys.executable, str(PREPARE_PATH), "--dry-run", "not-a-version"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("version must be X.Y.Z", result.stderr)


if __name__ == "__main__":
    unittest.main()
