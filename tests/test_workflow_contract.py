#!/usr/bin/env python3
"""Focused static contract tests for GitKeepr workflow security invariants."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = (ROOT / ".github/workflows/pr-loop.yml").read_text()
CALLER = (ROOT / "templates/gitkeepr.yml").read_text()


class WorkflowContractTests(unittest.TestCase):
    def test_core_has_minimal_reusable_contract(self):
        call_block = CORE.split("workflow_call:", 1)[1].split("workflow_dispatch:", 1)[0]
        for name in ("pr_number", "trigger_kind", "trigger_source_id"):
            self.assertIn(f"{name}:", call_block)
        for forbidden in ("build_model:", "review_model:", "max_cycles:"):
            self.assertNotIn(forbidden, call_block)

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
