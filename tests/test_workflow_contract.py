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
        self.assertEqual(CORE.count(fallback), 2)

        validation = CORE.split("- name: Validate repository configuration", 1)[1].split(
            "- name: Add OpenCode to PATH", 1
        )[0]
        token = CORE.split("- name: Create GitKeepr App token", 1)[1].split(
            "- name: Resolve GitKeepr bot identity", 1
        )[0]
        self.assertIn(f"APP_PRIVATE_KEY: {fallback}", validation)
        self.assertIn(f"private-key: {fallback}", token)
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

    def test_caller_rejects_forks_and_bot_sync_without_hardcoded_identity(self):
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", CALLER)
        self.assertIn("github.event.sender.type != 'Bot'", CALLER)
        self.assertNotIn("gitkeepr-githubapp[bot]", CALLER)

    def test_caller_comment_trust_is_conservative(self):
        self.assertIn("github.event.comment.user.type != 'Bot'", CALLER)
        self.assertIn('[\"OWNER\",\"MEMBER\",\"COLLABORATOR\"]', CALLER)
        self.assertIn("<!-- gitkeepr:no-build -->", CALLER)

    def test_public_self_gate_checks_same_repo_before_candidate_dispatch(self):
        gate_step = SELF_GATE.split(
            "- name: Verify same-repository PR and dispatch candidate core", 1
        )[1]
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

    def test_complete_loop_uses_configured_models_and_variants(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        self.assertIn('--model "$GITKEEPR_BUILD_MODEL"', loop)
        self.assertIn('--variant "$GITKEEPR_BUILD_VARIANT"', loop)
        self.assertIn('--model "$GITKEEPR_REVIEW_MODEL"', loop)
        self.assertIn('--variant "$GITKEEPR_REVIEW_VARIANT"', loop)
        self.assertIn('for cycle in $(seq 1 "$GITKEEPR_MAX_CYCLES")', loop)

    def test_build_does_not_own_git_operations(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        self.assertIn(
            "Do not commit, push, create branches, or modify GitHub metadata",
            loop,
        )
        self.assertIn('git commit -m "gitkeepr: build cycle ${cycle}"', loop)
        self.assertIn('git push origin "HEAD:${HEAD_REF}"', loop)

    def test_review_is_read_only_and_verdict_is_bound_to_current_head(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        self.assertIn("Do not edit repository files.", loop)
        self.assertIn("gitkeepr-system-review:v1 head=${current_head} verdict=continue", loop)
        self.assertIn("gitkeepr-system-review:v1 head=${current_head} verdict=pass", loop)
        self.assertIn('git diff --exit-code || block "Review agent modified tracked repository files', loop)
        self.assertIn("review.count(\"<!-- gitkeepr-system-review:v1\") != 1", loop)

    def test_new_continue_review_gets_build_opportunity_before_no_progress_block(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        self.assertIn("build_had_continue_review=false", loop)
        self.assertIn(
            'grep -Fq "<!-- gitkeepr-system-review:v1 head=${start_head} verdict=continue -->"',
            loop,
        )
        self.assertIn(
            'python3 -c \'import pathlib, sys; previous = pathlib.Path(sys.argv[1]).read_text().strip(); current = pathlib.Path(sys.argv[2]).read_text().strip(); raise SystemExit(0 if previous == current else 1)\' "$review_context" "$review_file"',
            loop,
        )
        self.assertIn("read_text().strip()", loop)
        self.assertIn(
            'if [[ "$build_had_continue_review" == "true" && "$current_head" == "$start_head" && "$review_unchanged" == "true" ]]',
            loop,
        )
        self.assertIn("review_unchanged=false", loop)
        self.assertIn("review_unchanged=true", loop)
        self.assertNotIn(
            'if [[ "$changed" == "false" || "$current_head" == "$start_head" ]]',
            loop,
        )
        self.assertIn('review_context="$review_file"', loop)
        self.assertIn("stopping to avoid an infinite loop", loop)
        self.assertIn("exhausted GITKEEPR_MAX_CYCLES", loop)
        self.assertIn('set_gitkeepr_status "gitkeepr:building"', loop)
        self.assertIn('set_gitkeepr_status "gitkeepr:reviewing"', loop)

    def test_review_comparison_ignores_only_trailing_formatting(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        match = re.search(
            r'''python3 -c '(?P<script>[^']+)' "\\$review_context" "\\$review_file"''',
            loop,
        )
        self.assertIsNotNone(match)
        comparison_script = match.group("script")

        with tempfile.TemporaryDirectory() as directory:
            previous = Path(directory) / "previous.md"
            current = Path(directory) / "current.md"
            previous.write_text("review body\\n")
            current.write_text("review body\\n\\n")

            result = subprocess.run(
                [sys.executable, "-c", comparison_script, str(previous), str(current)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            current.write_text("changed review body\\n")
            result = subprocess.run(
                [sys.executable, "-c", comparison_script, str(previous), str(current)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)

    def test_build_review_run_block_is_valid_bash(self):
        step = CORE.split("      - name: Run Build Review loop", 1)[1].split(
            "      - name: Publish result and finalize status", 1
        )[0]
        script = step.split("        run: |\\n", 1)[1]
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

    def test_successful_handling_writes_processed_marker_only_in_success_path(self):
        publish = CORE.split("- name: Publish result and finalize status", 1)[1]
        self.assertIn("PR_NUMBER: ${{ inputs.pr_number }}", publish)
        self.assertIn("const prNumber = Number(process.env.PR_NUMBER)", publish)
        self.assertIn("const succeeded = process.env.LOOP_OUTCOME === 'success'", publish)
        self.assertIn("<!-- gitkeepr-trigger:v1 key=${triggerKey} -->", publish)
        success_block = publish.split("if (succeeded) {", 1)[1].split(
            "for (const file of reviewFiles)", 1
        )[0]
        self.assertIn("triggerMarker", success_block)
        failure_block = publish.split("for (const file of reviewFiles)", 1)[1]
        self.assertNotIn("triggerMarker", failure_block.split("let message =", 1)[0])
        self.assertIn("gitkeepr-system-blocked:v1", failure_block)

    def test_direct_comment_reply_preserves_unresolved_review_status(self):
        authorize = CORE.split("- name: Resolve and authorize trigger", 1)[1].split(
            "- name: Duplicate trigger already handled", 1
        )[0]
        self.assertIn("const stableStatuses = new Set(['gitkeepr:waiting-human', 'gitkeepr:blocked'])", authorize)
        self.assertIn("core.setOutput('prior_status', priorStatus)", authorize)
        self.assertIn("core.setOutput('initial_review_verdict', initialReviewVerdict)", authorize)

        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        self.assertIn(
            'if [[ "$changed" == "false" && "$TRIGGER_KIND" == "comment" && "$cycle" -eq 1 ]]',
            loop,
        )
        self.assertIn('if [[ "$INITIAL_REVIEW_VERDICT" == "continue" ]]', loop)
        self.assertIn('final_status="gitkeepr:blocked"', loop)
        self.assertIn('printf \'final_status=%s\\n\' "$final_status" >> "$GITHUB_OUTPUT"', loop)
        self.assertIn('cp "$build_text_file" "$DIRECT_REPLY_FILE"', loop)

        publish = CORE.split("- name: Publish result and finalize status", 1)[1]
        self.assertIn("REQUESTED_FINAL_STATUS: ${{ steps.loop.outputs.final_status }}", publish)
        self.assertIn("gitkeepr-system-reply:v1", publish)

    def test_initial_review_marker_requires_gitkeepr_bot_provenance(self):
        authorize = CORE.split("- name: Resolve and authorize trigger", 1)[1].split(
            "- name: Duplicate trigger already handled", 1
        )[0]
        marker_lookup = authorize.split("const reviewPrefix", 1)[1].split(
            "core.setOutput('prior_status'", 1
        )[0]
        provenance = "loginOf(comment) === process.env.BOT_LOGIN"
        self.assertIn(provenance, marker_lookup)
        reply_marker = (
            r"const systemReplyMarker = /(?:^|\n\n)<!-- gitkeepr-system-reply:v1 "
            r"source-comment=\d+ head=[0-9a-f]{40} -->(?=\n\n|$)/"
        )
        self.assertIn(reply_marker, marker_lookup)
        self.assertIn("!systemReplyMarker.test(body)", marker_lookup)
        self.assertLess(
            marker_lookup.index(provenance),
            marker_lookup.index("body.includes(reviewPrefix)"),
        )
        self.assertLess(
            marker_lookup.index("body.includes(reviewPrefix)"),
            marker_lookup.index("!systemReplyMarker.test(body)"),
        )

        reply_pattern = re.compile(
            r"(?:^|\n\n)<!-- gitkeepr-system-reply:v1 source-comment=\d+ "
            r"head=[0-9a-f]{40} -->(?=\n\n|$)"
        )
        self.assertIsNone(reply_pattern.search("A review mentions <!-- gitkeepr-system-reply:v1.\n"))
        self.assertIsNotNone(
            reply_pattern.search(
                "Review body\n\n"
                "<!-- gitkeepr-system-reply:v1 source-comment=123 head="
                "0123456789abcdef0123456789abcdef01234567 -->\n\n"
                "<!-- gitkeepr-trigger:v1 key=comment:123 -->"
            )
        )

    def test_comment_only_status_transition_prioritizes_review_verdict_then_prior_status(self):
        loop = CORE.split("- name: Run Build Review loop", 1)[1]
        transition = loop.split(
            'if [[ "$changed" == "false" && "$TRIGGER_KIND" == "comment" && "$cycle" -eq 1 ]]',
            1,
        )[1].split("printf 'final_status=%s", 1)[0]

        continue_transition = transition.index('if [[ "$INITIAL_REVIEW_VERDICT" == "continue" ]]')
        pass_transition = transition.index('elif [[ "$INITIAL_REVIEW_VERDICT" == "pass" ]]')
        prior_transition = transition.index(
            'elif [[ "$PRIOR_STATUS" == "gitkeepr:blocked" || "$PRIOR_STATUS" == "gitkeepr:waiting-human" ]]'
        )
        self.assertLess(continue_transition, pass_transition)
        self.assertLess(pass_transition, prior_transition)
        self.assertIn('final_status="gitkeepr:blocked"', transition)
        self.assertIn('final_status="gitkeepr:waiting-human"', transition)
        self.assertIn('final_status="$PRIOR_STATUS"', transition)

    def test_final_status_accepts_preserved_stable_status_only_on_success(self):
        publish = CORE.split("- name: Publish result and finalize status", 1)[1]
        self.assertIn("const requestedFinalStatus = String(process.env.REQUESTED_FINAL_STATUS || '')", publish)
        self.assertIn(
            "const allowedFinalStatuses = new Set(['gitkeepr:waiting-human', 'gitkeepr:blocked'])",
            publish,
        )
        self.assertIn(
            "const target = succeeded && allowedFinalStatuses.has(requestedFinalStatus)",
            publish,
        )
        self.assertIn(
            ": succeeded ? 'gitkeepr:waiting-human' : 'gitkeepr:blocked'",
            publish,
        )


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


if __name__ == "__main__":
    unittest.main()
