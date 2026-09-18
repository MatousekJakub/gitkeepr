#!/usr/bin/env python3
"""Focused static tests for GitKeepr CLI safety and project-init contracts."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = (ROOT / "bin/gitkeepr").read_text()


class CliContractTests(unittest.TestCase):
    def function_body(self, name: str, next_name: str) -> str:
        return CLI.split(f"{name}() {{", 1)[1].split(f"{next_name}() {{", 1)[0]

    def test_project_init_never_owns_git_history(self):
        init = self.function_body("project_init", "project_doctor")
        for forbidden in (
            "git add",
            "git commit",
            "git push",
            "git reset",
            "git stash",
        ):
            self.assertNotIn(forbidden, init)
        self.assertIn("git status --short", init)

    def test_project_init_rejects_public_standard_targets(self):
        init = self.function_body("project_init", "project_doctor")
        self.assertIn('[[ "${visibility,,}" == "public" ]]', init)
        self.assertIn("does not support public target repositories", init)

    def test_project_init_requires_app_confirmation(self):
        init = self.function_body("project_init", "project_doctor")
        self.assertIn("Is the GitKeepr App installed for this repository?", init)
        self.assertIn("Add $repo to the GitKeepr GitHub App installation", init)

    def test_project_init_only_writes_the_caller_file_locally(self):
        init = self.function_body("project_init", "project_doctor")
        self.assertIn('WORKFLOW_PATH=".github/workflows/gitkeepr.yml"', CLI)
        self.assertIn('cp "$tmp" "$WORKFLOW_PATH"', init)
        for forbidden in (".ai/plan.md", "AGENTS.md", ".gitkeepr/"):
            self.assertNotIn(forbidden, init)

    def test_project_doctor_detects_stale_caller_without_replacing_it(self):
        doctor = self.function_body("project_doctor", "server_doctor")
        self.assertIn('curl -fsSL "$RAW_BASE/templates/gitkeepr.yml" -o "$tmp"', doctor)
        self.assertIn('cmp -s "$tmp" "$WORKFLOW_PATH"', doctor)
        self.assertIn("differs from the current GitKeepr template", doctor)
        self.assertIn("run 'gitkeepr init' to review replacement", doctor)
        self.assertNotIn('cp "$tmp" "$WORKFLOW_PATH"', doctor)
        self.assertNotIn('rm "$WORKFLOW_PATH"', doctor)
        self.assertIn("diagnostics made no persistent changes", doctor)

    def test_server_doctor_is_read_only(self):
        doctor = self.function_body("server_doctor", "server_unimplemented")
        # Diagnostics may print commands the operator should run. Protect against
        # executable mutation statements instead of rejecting guidance text.
        for forbidden_line in (
            "apt-get ",
            "apt ",
            "useradd ",
            "adduser ",
            "systemctl enable ",
            "systemctl start ",
            "gh auth login",
            "opencode auth login",
            "chmod ",
            "chown ",
        ):
            self.assertFalse(
                any(line.lstrip().startswith(forbidden_line) for line in doctor.splitlines()),
                f"server doctor executes mutating command: {forbidden_line}",
            )
        self.assertNotIn("> $SERVER_CONFIG", doctor)
        self.assertNotIn('> "$SERVER_CONFIG"', doctor)
        self.assertIn("run 'gh auth login'", doctor)
        self.assertIn("diagnostics made no changes", doctor)

    def test_server_doctor_checks_supported_platform_and_config(self):
        doctor = self.function_body("server_doctor", "server_unimplemented")
        self.assertIn("Ubuntu/Debian", doctor)
        self.assertIn("systemd", doctor)
        self.assertIn("x86_64|amd64|aarch64|arm64", doctor)
        self.assertIn("GITKEEPR_APP_CLIENT_ID", doctor)
        self.assertIn("GITKEEPR_APP_PRIVATE_KEY_PATH", doctor)
        self.assertIn("github-runner", doctor)
        self.assertIn("opencode", doctor)

    def test_server_doctor_reads_protected_config_without_weakening_permissions(self):
        doctor = self.function_body("server_doctor", "server_unimplemented")
        self.assertIn('config_contents="$(sudo cat "$SERVER_CONFIG"', doctor)
        self.assertIn('mode="$(sudo stat -c \'%a\' "$SERVER_CONFIG"', doctor)
        self.assertIn('sudo test -r "$config_key"', doctor)
        self.assertIn('[[ "$(id -u)" -eq 0 ]]', doctor)
        self.assertNotIn('sudo chmod', doctor)
        self.assertNotIn('sudo chown', doctor)

    def test_server_doctor_enforces_protected_config_metadata(self):
        doctor = self.function_body("server_doctor", "server_unimplemented")
        self.assertIn("stat -c '%U:%G'", doctor)
        self.assertIn('[[ "$owner" == "root:root" ]]', doctor)
        self.assertIn('[[ "$mode" == "600" || "$mode" == "400" ]]', doctor)
        self.assertIn("expected root:root", doctor)
        self.assertIn("expected 600 or 400", doctor)

    def test_server_doctor_checks_every_runtime_used_by_core_workflow(self):
        doctor = self.function_body("server_doctor", "server_unimplemented")
        for command in ("curl", "git", "jq", "tar", "gh", "python3"):
            self.assertIn(command, doctor)


if __name__ == "__main__":
    unittest.main()
