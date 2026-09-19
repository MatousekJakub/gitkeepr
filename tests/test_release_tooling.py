#!/usr/bin/env python3
"""Release-version consistency and release-preparation contract tests."""

from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text().strip()
CLI = (ROOT / "bin/gitkeepr").read_text()
INSTALLER = (ROOT / "install.sh").read_text()
CALLER = (ROOT / "templates/gitkeepr.yml").read_text()
PREPARE = ROOT / "scripts" / "prepare-release.py"


class ReleaseToolingTests(unittest.TestCase):
    def test_versioned_distribution_files_are_consistent(self):
        self.assertRegex(VERSION, r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
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
            [sys.executable, str(PREPARE), "--dry-run", target],
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

    def test_prepare_release_rejects_invalid_version(self):
        result = subprocess.run(
            [sys.executable, str(PREPARE), "--dry-run", "not-a-version"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("version must be X.Y.Z", result.stderr)


if __name__ == "__main__":
    unittest.main()
