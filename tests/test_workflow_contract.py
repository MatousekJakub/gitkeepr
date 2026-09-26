#!/usr/bin/env python3
"""Focused static contract tests for GitKeepr workflow security and loop invariants."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = (ROOT / ".github/workflows/pr-loop.yml").read_text()
CALLER = (ROOT / "templates/gitkeepr.yml").read_text()
SELF_GATE = (ROOT / ".github/workflows/self-gate.yml").read_text()
VERSION = (ROOT / "VERSION").read_text().strip()


class WorkflowContractTests(unittest.TestCase):
    def test_core_has_minimal_reusable_contract(self):
        call_block = CORE.split("workflow_call:", 1)[1].split("workflow_dispatch:", 1)[0]
        for name in ("pr_number", "trigger_kind", "trigger_source_id"):
            self.assertIn(f"{name}:", call_block)
        for forbidden in ("build_model:", "review_model:", "max_cycles:"):
            self.assertNotIn(forbidden, call_block)

    def test_direct_dispatch_and_reusable_call_share_app_credentials_safely(self):
        call_block = CORE.split("workflow_call:", 1)[1].split("workflow_dispatch:", 1)[0]
        self.assertIn("app_private_key: { required: true }", call_block)

        fallback = "${{ secrets.app_private_key || secrets.GITKEEPR_APP_PRIVATE_KEY }}"
        self.assertEqual(CORE.count(fallback), 4)

        validation = CORE.split("- name: Validate repository configuration", 1)[1].split(
            "- name: Add OpenCode to PATH", 1
        )[0]
        token = CORE.split("- name: Create GitKeepr App token", 1)[1].split(
            "- name: Resolve GitKeepr bot identity", 1
        )[0]
        loop = CORE.split("- name: Run Build Review loop", 1)[1].split(
            "- name: Create final GitKeepr App token", 1
        )[0]
        final_token = CORE.split("- name: Create final GitKeepr App token", 1)[1].split(
            "- name: Publish result and finalize status", 1
        )[0]
        self.assertIn(f"APP_PRIVATE_KEY: {fallback}", validation)
        self.assertIn(f"private-key: {fallback}", token)
        self.assertIn(f"APP_PRIVATE_KEY_INPUT: {fallback}", loop)
        self.assertIn(f"private-key: {fallback}", final_token)
        self.assertIn("app_private_key: ${{ secrets.GITKEEPR_APP_PRIVATE_KEY }}", CALLER)

    def test_checkout_is_pinned_to_authorized_sha(self):
        checkout = CORE.split("- name: Check out exact PR head", 1)[1]
        self.assertIn("ref: ${{ steps.context.outputs.head_sha }}", checkout)
        self.assertIn("persist-credentials: false", checkout)
        self.assertNotIn("persist-credentials: true", checkout)
        self.assertIn('test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD"', checkout)
        self.assertIn('APP_TOKEN: ${{ steps.app-token.outputs.token }}', checkout)
        self.assertIn("GIT_CONFIG_KEY_0=http.extraHeader", checkout)
        self.assertIn('git fetch --no-tags origin "$BASE_REF"', checkout)

    def test_manual_trigger_uses_workflow_run_as_idempotence_key(self):
        authorize = CORE.split("- name: Resolve and authorize trigger", 1)[1].split(
            "- name: Duplicate trigger already handled", 1
        )[0]
        manual = authorize.split("if (kind === 'manual')", 1)[1].split(
            "const handledMarker", 1
        )[0]
        self.assertIn(
            "if (sourceId) return fail('Manual trigger must not supply trigger_source_id')",
            manual,
        )
        self.assertIn("triggerKey = `manual:${context.runId}`", manual)

    def test_standard_caller_is_pinned_to_current_release(self):
        self.assertIn(
            f"uses: MatousekJakub/gitkeepr/.github/workflows/pr-loop.yml@v{VERSION}",
            CALLER,
        )
        self.assertNotIn("pr-loop.yml@main", CALLER)

    def test_complete_loop_uses_configured_models_and_variants(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        self.assertIn('--model "$GITKEEPR_BUILD_MODEL"', loop)
        self.assertIn('--variant "$GITKEEPR_BUILD_VARIANT"', loop)
        self.assertIn('--model "$GITKEEPR_REVIEW_MODEL"', loop)
        self.assertIn('--variant "$GITKEEPR_REVIEW_VARIANT"', loop)
        self.assertIn('for cycle in $(seq 1 "$GITKEEPR_FINALIZATION_CYCLES")', loop)

    def test_build_does_not_own_git_operations(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        self.assertIn(
            "Do not commit, push, create branches, or modify GitHub metadata",
            loop,
        )
        self.assertIn('git -c core.hooksPath=/dev/null commit -m "gitkeepr: build cycle ${cycle}"', loop)
        self.assertIn('git -c core.hooksPath=/dev/null push "$remote_url"', loop)
        self.assertIn("push_head_with_app_token", loop)
        self.assertIn("including one retry with refreshed GitHub App credentials", loop)

    def test_build_review_run_block_is_valid_bash(self):
        step = CORE.split("      - name: Run Build Review loop", 1)[1].split(
            "      - name: Create final GitKeepr App token", 1
        )[0]
        script = step.split("        run: |\n", 1)[1]
        script = textwrap.dedent(script)

        result = subprocess.run(
            ["bash", "-n"],
            input=script,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_core_does_not_impose_a_generic_deterministic_test_command(self):
        self.assertNotIn("python3 -m unittest discover -s tests -v", CORE)
        self.assertIn("Run the relevant tests for the repository and task.", CORE)

    def test_third_party_actions_are_pinned_in_executing_workflows(self):
        expected = (
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7",
            "actions/github-script@3a2844b7e9c422d3c10d287c895573f7108da1b3 # v9",
            "actions/create-github-app-token@bcd2ba49218906704ab6c1aa796996da409d3eb1 # v3",
        )
        combined = CORE + SELF_GATE + (ROOT / ".github/workflows/ci.yml").read_text()
        for pin in expected:
            self.assertIn(pin, combined)
        for floating in ("actions/checkout@v7", "actions/github-script@v9", "actions/create-github-app-token@v3"):
            self.assertNotIn(floating, combined)

    def test_activation_is_explicit_only(self):
        self.assertIn("issue_comment:", CALLER)
        self.assertIn("workflow_dispatch:", CALLER)
        self.assertNotIn("pull_request:", CALLER)
        self.assertNotIn("pull_request_review:", CALLER)
        self.assertIn("github.event.comment.body == '/gitkeepr run'", CALLER)
        self.assertIn("github.event.comment.user.type != 'Bot'", CALLER)
        self.assertIn('[\"OWNER\",\"MEMBER\",\"COLLABORATOR\"]', CALLER)
        self.assertIn("issue_comment:", SELF_GATE)
        self.assertIn("workflow_dispatch:", SELF_GATE)
        self.assertNotIn("pull_request:", SELF_GATE)
        self.assertNotIn("pull_request_review:", SELF_GATE)
        self.assertIn("github.event.comment.body == '/gitkeepr run'", SELF_GATE)

    def test_core_requires_exact_command_and_same_repository(self):
        authorize = CORE.split("- name: Resolve and authorize trigger", 1)[1].split(
            "- name: Deprecated automatic trigger ignored", 1
        )[0]
        self.assertIn("pr.head.repo?.full_name !== expectedRepo", authorize)
        self.assertIn("isTrustedHuman", authorize)
        self.assertIn("String(comment.body || '').trim() !== '/gitkeepr run'", authorize)
        self.assertIn("Ignoring trusted non-command comment dispatched by the legacy v0.1 self-development gate", authorize)
        self.assertIn("core.setOutput('skip', 'true')", authorize)
        self.assertIn("triggerKey = `command:${comment.id}`", authorize)
        self.assertIn("<!-- gitkeepr-trigger:v2 key=${triggerKey} -->", authorize)
        self.assertIn("body === '/gitkeepr run'", authorize)

    def test_legacy_v01_trusted_non_command_comment_is_a_noop(self):
        authorize = CORE.split("- name: Resolve and authorize trigger", 1)[1].split(
            "- name: Deprecated automatic trigger ignored", 1
        )[0]
        self.assertIn("Trigger comment is not from a trusted human collaborator", authorize)
        self.assertIn("Ignoring trusted non-command comment dispatched by the legacy v0.1 self-development gate", authorize)
        self.assertIn("core.setOutput('skip', 'true')", authorize)
        self.assertIn("core.setOutput('duplicate', 'false')", authorize)

    def test_legacy_automatic_trigger_kinds_are_transition_noops(self):
        authorize = CORE.split("- name: Resolve and authorize trigger", 1)[1].split(
            "- name: Deprecated automatic trigger ignored", 1
        )[0]
        self.assertIn("const legacyKinds = new Set(['pr_opened', 'pr_sync', 'review'])", authorize)
        self.assertIn("core.setOutput('skip', 'true')", authorize)
        self.assertIn("Ignoring deprecated automatic GitKeepr trigger kind", authorize)

    def test_build_is_a_full_bounded_finalization_turn(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        self.assertIn("This is a bounded finalization run.", loop)
        self.assertIn("Resolve all safely actionable remaining work", loop)
        self.assertIn("Do not artificially limit yourself to one planned task.", loop)
        self.assertNotIn("implement only the first unfinished logical task", loop)
        self.assertIn("result=needs-supervisor", loop)
        self.assertIn("supervisor action is required", loop)
        self.assertNotIn("stopping to avoid an infinite loop", loop)
        self.assertNotIn("exhausted GITKEEPR_FINALIZATION_CYCLES", loop)

    def test_pr_head_ownership_supersedes_stale_runs(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1].split(
            "- name: Create final GitKeepr App token", 1
        )[0]
        self.assertIn("git_remote_head_once()", loop)
        self.assertIn('git -c core.hooksPath=/dev/null ls-remote "$remote_url" "refs/heads/${HEAD_REF}"', loop)
        self.assertIn("ensure_remote_head()", loop)
        self.assertIn('ensure_remote_head "$start_head"', loop)
        self.assertIn('push_head_with_app_token "$start_head"', loop)
        self.assertIn('ensure_remote_head "$current_head"', loop)
        self.assertIn("result=superseded", loop)
        final_token = CORE.split("- name: Create final GitKeepr App token", 1)[1].split(
            "- name: Publish result and finalize status", 1
        )[0]
        self.assertIn("steps.loop.outputs.result != 'superseded'", final_token)
        publish = CORE.split("- name: Publish result and finalize status", 1)[1]
        self.assertIn("if (pr.head.sha !== resultHead)", publish)
        self.assertIn("no PR state will be changed", publish)
        self.assertIn("const assertCurrentHead = async operation", publish)
        self.assertIn("abortIfSuperseded(`removing ${label}`)", publish)
        self.assertIn("abortIfSuperseded(`adding ${target}`)", publish)
        self.assertIn("abortIfSuperseded(`posting review ${reviewFiles[index]}`)", publish)
        self.assertIn("abortIfSuperseded('posting the completion comment')", publish)
        self.assertIn("const createdCommentIds = []", publish)
        self.assertIn("const restorePublication = async ()", publish)
        self.assertIn("github.rest.issues.deleteComment", publish)
        self.assertIn("originalStatusLabels", publish)

    def test_only_completed_logical_results_are_durable_labels(self):
        ensure = CORE.split("- name: Ensure GitKeepr status labels", 1)[1].split(
            "- name: Check out exact PR head", 1
        )[0]
        self.assertIn("gitkeepr:ready", ensure)
        self.assertIn("gitkeepr:needs-supervisor", ensure)
        for old in ("gitkeepr:building", "gitkeepr:reviewing", "gitkeepr:waiting-human", "gitkeepr:blocked"):
            self.assertNotIn(old, ensure)
        loop = CORE.split("- name: Run Build Review loop", 1)[1].split(
            "- name: Create final GitKeepr App token", 1
        )[0]
        self.assertNotIn("set_gitkeepr_status", loop)
        publish = CORE.split("- name: Publish result and finalize status", 1)[1]
        self.assertIn("ready: 'gitkeepr:ready'", publish)
        self.assertIn("'needs-supervisor': 'gitkeepr:needs-supervisor'", publish)

    def test_status_labels_are_not_provisioned_for_noop_or_duplicate_triggers(self):
        authorize = CORE.index("- name: Resolve and authorize trigger")
        ensure = CORE.index("- name: Ensure GitKeepr status labels")
        self.assertLess(authorize, ensure)
        ensure_step = CORE[ensure:].split("- name: Check out exact PR head", 1)[0]
        self.assertIn("steps.context.outputs.skip != 'true'", ensure_step)
        self.assertIn("steps.context.outputs.duplicate != 'true'", ensure_step)

    def test_technical_failures_do_not_publish_persistent_failure_state(self):
        final_token = CORE.split("- name: Create final GitKeepr App token", 1)[1].split(
            "- name: Publish result and finalize status", 1
        )[0]
        self.assertIn("steps.loop.outcome == 'success'", final_token)
        publish = CORE.split("- name: Publish result and finalize status", 1)[1]
        self.assertNotIn("gitkeepr-system-blocked", publish)
        self.assertNotIn("GitKeepr loop stopped", publish)

    def test_review_is_read_only_and_head_bound(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        self.assertIn("Do not edit repository files.", loop)
        self.assertIn("gitkeepr-system-review:v1 head=${current_head} verdict=continue", loop)
        self.assertIn("gitkeepr-system-review:v1 head=${current_head} verdict=pass", loop)
        self.assertIn('git diff --exit-code || fail "Review agent modified tracked repository files', loop)
        self.assertIn('review.count("<!-- gitkeepr-system-review:v1") != 1', loop)

    def test_credential_refresh_and_agent_secret_isolation_remain(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1].split(
            "- name: Create final GitKeepr App token", 1
        )[0]
        self.assertIn("GITKEEPR_SANITIZED", loop)
        self.assertIn("-u APP_PRIVATE_KEY_INPUT", loop)
        self.assertIn("-u APP_PRIVATE_KEY_MATERIAL", loop)
        self.assertIn("-u APP_TOKEN", loop)
        self.assertIn('3<<<"$APP_PRIVATE_KEY_INPUT"', loop)
        self.assertIn('APP_PRIVATE_KEY_MATERIAL="$(cat <&3)"', loop)
        self.assertIn('"$GITHUB_API_URL/app/installations/$APP_INSTALLATION_ID/access_tokens"', loop)
        self.assertIn('APP_TOKEN_EXPIRES_EPOCH" -le $((now + 300))', loop)
        self.assertIn("refreshing GitHub App credentials and retrying once", loop)
        invocation = 'env -u APP_PRIVATE_KEY_INPUT -u APP_PRIVATE_KEY_MATERIAL -u APP_TOKEN PATH="$AGENT_PATH" "$OPENCODE_BIN" run'
        self.assertEqual(loop.count(invocation), 2)

    def test_remote_head_probe_has_data_only_stdout(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1].split(
            "- name: Create final GitKeepr App token", 1
        )[0]
        self.assertIn('echo "::add-mask::$APP_TOKEN" >&2', loop)
        self.assertIn('echo "GitKeepr refreshed GitHub App credentials (expires $expires_at)." >&2', loop)
        self.assertIn('actual="$(remote_head_with_app_token)"', loop)

    def test_optional_mcp_tools_remain_available_to_both_agents(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        self.assertEqual(loop.count("Context7 and Chrome DevTools MCP tools are available on the runner."), 2)
        self.assertEqual(loop.count("optional tools, not required workflow steps"), 2)


if __name__ == "__main__":
    unittest.main()
