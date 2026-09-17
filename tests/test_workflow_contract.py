#!/usr/bin/env python3
"""Focused static contract tests for GitKeepr workflow security invariants."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = (ROOT / ".github/workflows/pr-loop.yml").read_text()
CALLER = (ROOT / "templates/gitkeepr.yml").read_text()
SELF_GATE = (ROOT / ".github/workflows/self-gate.yml").read_text()


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
        self.assertEqual(CORE.count(fallback), 2)

        validation = CORE.split("- name: Validate repository configuration", 1)[1].split(
            "- name: Add OpenCode to PATH", 1
        )[0]
        token = CORE.split("- name: Create GitKeepr App token", 1)[1].split(
            "- name: Resolve GitKeepr bot identity", 1
        )[0]
        self.assertIn(f"APP_PRIVATE_KEY: {fallback}", validation)
        self.assertIn(f"private-key: {fallback}", token)

        # The normal target caller should continue to pass the repository secret
        # through the reusable workflow's deliberately small secret alias.
        self.assertIn("app_private_key: ${{ secrets.GITKEEPR_APP_PRIVATE_KEY }}", CALLER)

    def test_authorization_happens_before_checkout(self):
        authorize = CORE.index("- name: Resolve and authorize trigger")
        checkout = CORE.index("- name: Check out exact PR head")
        self.assertLess(authorize, checkout)
        security_block = CORE[authorize:checkout]
        self.assertIn("pr.head.repo?.full_name !== expectedRepo", security_block)
        self.assertIn("isTrustedHuman", security_block)
        self.assertIn("gitkeepr:no-build", security_block)

    def test_checkout_is_pinned_to_authorized_sha(self):
        checkout = CORE.split("- name: Check out exact PR head", 1)[1]
        self.assertIn("ref: ${{ steps.context.outputs.head_sha }}", checkout)
        self.assertIn('test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD"', checkout)

    def test_success_marker_is_not_yet_written_by_bootstrap_stub(self):
        # Until the real loop exists, an incomplete/failed run must never consume a trigger.
        after_context = CORE.split("- name: Duplicate trigger already handled", 1)[1]
        self.assertNotIn("gitkeepr-trigger:v1 key=", after_context)

    def test_caller_rejects_forks_and_bot_sync_without_hardcoded_identity(self):
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", CALLER)
        self.assertIn("github.event.sender.type != 'Bot'", CALLER)
        self.assertNotIn("gitkeepr-githubapp[bot]", CALLER)

    def test_caller_comment_trust_is_conservative(self):
        self.assertIn("github.event.comment.user.type != 'Bot'", CALLER)
        self.assertIn('[\"OWNER\",\"MEMBER\",\"COLLABORATOR\"]', CALLER)
        self.assertIn("<!-- gitkeepr:no-build -->", CALLER)

    def test_public_self_gate_checks_same_repo_before_candidate_dispatch(self):
        gate_step = SELF_GATE.split("- name: Verify same-repository PR and dispatch candidate core", 1)[1]
        same_repo_check = gate_step.index("pr.head.repo?.full_name !== expectedRepo")
        dispatch = gate_step.index("github.rest.actions.createWorkflowDispatch")
        self.assertLess(same_repo_check, dispatch)
        self.assertIn("return", gate_step[same_repo_check:dispatch])
        self.assertIn("workflow_id: 'pr-loop.yml'", gate_step[dispatch:])
        self.assertIn("ref: pr.head.ref", gate_step[dispatch:])
        for name in ("pr_number", "trigger_kind", "trigger_source_id"):
            self.assertIn(f"{name}:", gate_step[dispatch:])

    def test_public_self_gate_keeps_untrusted_events_off_persistent_runner(self):
        self.assertIn("runs-on: ubuntu-latest", SELF_GATE)
        self.assertNotIn("runs-on: [self-hosted", SELF_GATE)
        self.assertIn("github.event.sender.type != 'Bot'", SELF_GATE)
        self.assertIn("github.event.comment.user.type != 'Bot'", SELF_GATE)
        self.assertIn("<!-- gitkeepr:no-build -->", SELF_GATE)
        self.assertIn("<!-- gitkeepr-system:", SELF_GATE)

    def test_build_uses_configured_model_and_variant(self):
        build = CORE.split("- name: Run first Build turn", 1)[1]
        self.assertIn('--model "$GITKEEPR_BUILD_MODEL"', build)
        self.assertIn('--variant "$GITKEEPR_BUILD_VARIANT"', build)

    def test_build_does_not_own_git_operations(self):
        build = CORE.split("- name: Run first Build turn", 1)[1]
        self.assertIn("Do not commit, push, create branches, or modify GitHub metadata", build)
        self.assertIn('git commit -m "gitkeepr: build"', build)
        self.assertIn('git push origin "HEAD:${HEAD_REF}"', build)


if __name__ == "__main__":
    unittest.main()
