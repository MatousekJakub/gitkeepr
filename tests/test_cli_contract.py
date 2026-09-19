#!/usr/bin/env python3
"""Focused static tests for GitKeepr CLI safety and V1 lifecycle contracts."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = (ROOT / "bin/gitkeepr").read_text()
INSTALLER = (ROOT / "install.sh").read_text()
VERSION = (ROOT / "VERSION").read_text().strip()


class CliContractTests(unittest.TestCase):
    def function_body(self, name: str, next_name: str) -> str:
        return CLI.split(f"{name}() {{", 1)[1].split(f"{next_name}() {{", 1)[0]

    def test_distribution_is_release_pinned(self):
        self.assertIn(f'VERSION="{VERSION}"', CLI)
        self.assertIn('RELEASE_TAG="v${VERSION}"', CLI)
        self.assertIn('raw.githubusercontent.com/MatousekJakub/gitkeepr/${RELEASE_TAG}', CLI)
        self.assertIn(f'VERSION="${{GITKEEPR_VERSION:-{VERSION}}}"', INSTALLER)
        self.assertIn('releases/download/${TAG}', INSTALLER)
        self.assertIn('"$tmp" version', INSTALLER)

    def test_project_init_never_owns_git_history(self):
        init = self.function_body("project_init", "project_doctor")
        for forbidden in ("git add", "git commit", "git push", "git reset", "git stash"):
            self.assertNotIn(forbidden, init)
        self.assertIn("git status --short", init)

    def test_project_init_rejects_public_standard_targets_but_allows_self_development(self):
        init = self.function_body("project_init", "project_doctor")
        self.assertIn('[[ "${visibility,,}" == "public" ]]', init)
        self.assertIn('is_public_self_repo "$repo"', init)
        self.assertIn("does not support public target repositories", init)
        self.assertIn("no standard caller file is created", init)

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
        self.assertIn("diagnostics made no persistent changes", doctor)

    def test_project_doctor_checks_server_synced_credentials_and_runner_health(self):
        doctor = self.function_body("project_doctor", "server_doctor")
        self.assertIn("GITKEEPR_APP_CLIENT_ID", doctor)
        self.assertIn("gh secret list", doctor)
        self.assertIn("GITKEEPR_APP_PRIVATE_KEY", doctor)
        self.assertIn("actions/runners?per_page=100", doctor)
        self.assertIn('== "gitkeepr"', doctor)
        self.assertIn("registered and online", doctor)
        self.assertIn("project doctor does not have the private key", doctor)

    def test_project_doctor_supports_public_self_development_workflows(self):
        doctor = self.function_body("project_doctor", "server_doctor")
        self.assertIn('is_public_self_repo "$repo"', doctor)
        self.assertIn("Public upstream repository uses the GitKeepr self-development gate", doctor)
        self.assertIn("self-gate.yml pr-loop.yml", doctor)

    def test_server_doctor_is_read_only(self):
        doctor = self.function_body("server_doctor", "server_init")
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
            "rm -rf ",
        ):
            self.assertFalse(
                any(line.lstrip().startswith(forbidden_line) for line in doctor.splitlines()),
                f"server doctor executes mutating command: {forbidden_line}",
            )
        self.assertNotIn("> $SERVER_CONFIG", doctor)
        self.assertNotIn('> "$SERVER_CONFIG"', doctor)
        self.assertIn("run 'gh auth login'", doctor)
        self.assertIn("diagnostics made no changes", doctor)

    def test_server_doctor_checks_runtime_config_cache_and_models(self):
        doctor = self.function_body("server_doctor", "server_init")
        self.assertIn("Ubuntu/Debian", doctor)
        self.assertIn("systemd", doctor)
        self.assertIn("x86_64|amd64|aarch64|arm64", doctor)
        for command in ("curl", "git", "jq", "tar", "gh", "python3", "openssl", "xz", "node", "npm", "npx"):
            self.assertIn(command, doctor)
        self.assertIn("GITKEEPR_APP_CLIENT_ID", doctor)
        self.assertIn("GITKEEPR_APP_PRIVATE_KEY_PATH", doctor)
        self.assertIn("root:root", doctor)
        self.assertIn("600", doctor)
        self.assertIn("runner_cache_path", doctor)
        self.assertIn('"$opencode_path" models', doctor)
        self.assertIn("node_runtime_ok", doctor)
        self.assertIn("runner_chromium_path", doctor)
        self.assertIn("chrome-devtools-mcp", doctor)
        self.assertIn("context7-mcp", doctor)
        self.assertIn("mcp list", doctor)
        self.assertIn("Runner filesystem free space", doctor)
        self.assertIn("actions.runner.*", doctor)

    def test_admin_check_prefers_passwordless_sudo_before_interactive_validation(self):
        admin = self.function_body("require_admin", "as_root")
        self.assertIn("sudo -n true", admin)
        self.assertIn("sudo -v", admin)
        self.assertLess(admin.index("sudo -n true"), admin.index("sudo -v"))

    def test_protected_server_config_existence_checks_run_as_root(self):
        load = self.function_body("load_server_config", "base64url")
        self.assertIn('as_root test -e "$SERVER_CONFIG"', load)
        self.assertNotIn('[[ -e "$SERVER_CONFIG" ]]', load)

        init = self.function_body("server_init", "runner_add")
        self.assertIn('if as_root test -e "$SERVER_CONFIG"; then', init)
        self.assertNotIn('if [[ -e "$SERVER_CONFIG" ]]; then', init)

    def test_server_init_bootstraps_host_without_touching_existing_runners(self):
        init = self.function_body("server_init", "runner_add")
        self.assertIn("apt-get install -y", init)
        for package in ("curl", "git", "jq", "tar", "xz-utils", "ca-certificates", "gh", "python3", "openssl"):
            self.assertIn(package, init)
        self.assertIn('useradd --create-home --shell /bin/bash "$RUNNER_USER"', init)
        self.assertIn("gh auth login", init)
        self.assertIn("https://opencode.ai/install", init)
        self.assertIn('"$opencode_path" auth login', init)
        self.assertIn('"$opencode_path" models', init)
        self.assertIn("install_node_runtime", init)
        self.assertIn("configure_runner_mcp_tools", init)
        self.assertIn("repos/actions/runner/releases/latest", init)
        self.assertIn('install -o root -g root -m 0600 "$tmp" "$SERVER_CONFIG"', init)
        self.assertIn("Existing repository runners were not modified.", init)
        self.assertNotIn("remove_runner_installation", init)
        self.assertNotIn('rm -rf "$home/runners"', init)

    def test_runner_mcp_tooling_is_installed_and_merged_into_opencode_config(self):
        helper = self.function_body("configure_runner_mcp_tools", "server_doctor")
        self.assertIn("chrome-devtools-mcp@latest", helper)
        self.assertIn("@upstash/context7-mcp@latest", helper)
        self.assertIn("playwright@latest install --with-deps --no-shell chromium", helper)
        self.assertIn("PLAYWRIGHT_BROWSERS_PATH", helper)
        self.assertIn('.mcp["chrome-devtools"]', helper)
        self.assertIn(".mcp.context7", helper)
        self.assertIn("--headless", helper)
        self.assertIn("--isolated", helper)
        self.assertIn("--experimental-vision", helper)
        self.assertIn("--chrome-arg=--lang=cs-CZ", helper)
        self.assertIn('"$opencode_path" mcp list', helper)

    def test_app_verification_uses_server_client_id_and_private_key(self):
        jwt = self.function_body("github_app_jwt", "verify_app_access")
        self.assertIn('"iss":"%s"', jwt)
        self.assertIn('"$APP_CLIENT_ID"', jwt)
        self.assertIn('openssl dgst -sha256 -sign "$APP_KEY_PATH"', jwt)

        verify = self.function_body("verify_app_access", "verify_project_vars")
        self.assertIn("https://api.github.com/repos/$repo/installation", verify)
        self.assertIn("Authorization: Bearer $jwt", verify)
        self.assertIn(".permissions", verify)
        self.assertIn("write\\twrite\\twrite\\twrite", verify)

    def test_runner_name_does_not_turn_hostname_newline_into_separator(self):
        helper = self.function_body("runner_name_for", "runner_record")
        self.assertIn('printf \'%s\' "$(hostname -s)"', helper)
        self.assertNotIn("hostname -s | tr -c", helper)

    def test_runner_add_validates_before_registration_and_syncs_credentials(self):
        add = self.function_body("runner_add", "runner_remove")
        validation_end = add.index('cache_path="$(runner_cache_path)"')
        validation = add[:validation_end]
        self.assertIn('validate_target_repo "$repo"', validation)
        self.assertIn('verify_project_vars "$repo"', validation)
        self.assertIn('verify_app_access "$repo"', validation)
        self.assertIn('sync_app_credentials "$repo"', validation)
        self.assertIn("registration-token", add)
        self.assertIn("--labels gitkeepr", add)
        self.assertIn("./svc.sh install", add)
        self.assertIn("./svc.sh start", add)
        self.assertIn('"$status" == "online"', add)

    def test_runner_add_healthy_rerun_resyncs_without_reconfigure(self):
        add = self.function_body("runner_add", "runner_remove")
        healthy = add.split('if [[ -d "$dir" && -f "$dir/.runner"', 1)[1].split(
            'if [[ -d "$dir" || -n "$record" ]]', 1
        )[0]
        self.assertIn('runner_service_healthy "$dir"', healthy)
        self.assertIn("already configured and online", healthy)
        self.assertIn("App credentials were resynchronized", healthy)
        self.assertIn("return 0", healthy)

    def test_runner_reconfigure_uses_fresh_remove_and_registration_tokens(self):
        helper = self.function_body("remove_runner_installation", "project_init")
        self.assertIn("actions/runners/remove-token", helper)
        self.assertIn("./config.sh remove --token", helper)
        add = self.function_body("runner_add", "runner_remove")
        self.assertIn("Reconfigure it? [y/N]", add)
        self.assertIn('remove_runner_installation "$repo" "$dir" "$runner_id"', add)
        self.assertIn("actions/runners/registration-token", add)

    def test_runner_remove_leaves_repository_configuration_intact(self):
        remove = CLI.split("runner_remove() {", 1)[1].split('case "${1:-}" in', 1)[0]
        self.assertIn('remove_runner_installation "$repo" "$dir" "$runner_id"', remove)
        self.assertIn("Repository variables, secrets, and workflow files were left unchanged.", remove)
        self.assertNotIn("gh variable delete", remove)
        self.assertNotIn("gh secret delete", remove)
        self.assertNotIn("delete_file", remove)

    def test_public_runner_exception_is_only_upstream_self_dogfood(self):
        helper = self.function_body("is_public_self_repo", "validate_target_repo")
        self.assertIn('upstream="$(upstream_repo_from_raw_base || true)"', helper)
        self.assertIn('"$repo" == "$upstream"', helper)
        self.assertIn(".github/workflows/self-gate.yml", helper)
        self.assertIn(".github/workflows/pr-loop.yml", helper)

        validate = self.function_body("validate_target_repo", "runner_dir_for")
        self.assertIn('is_public_self_repo "$repo"', validate)
        self.assertIn("does not support public target repositories", validate)

    def test_public_self_runner_check_does_not_require_standard_caller(self):
        check = self.function_body("warn_if_caller_missing", "remove_runner_installation")
        self.assertIn('is_public_self_repo "$repo"', check)
        self.assertIn("Public self-development workflows are visible", check)


if __name__ == "__main__":
    unittest.main()
