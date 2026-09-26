# Development Workflow

GitKeepr develops itself through a public-repository gate plus the same bounded finalization worker used by managed repositories.

## Normal change flow

1. Start from current `main`.
2. Prepare the change on a same-repository branch.
3. Open a pull request into `main`. Opening or updating the PR does **not** intentionally start GitKeepr v0.2.
4. Run normal GitHub-hosted CI and perform any ChatGPT/human edits or reviews needed.
5. When real-environment agent finalization is useful, post exactly `/gitkeepr run` on the PR.
6. The default-branch `.github/workflows/self-gate.yml` verifies that the PR head belongs to `MatousekJakub/gitkeepr`, then dispatches the candidate branch's `pr-loop.yml`.
7. Build/Review run for the configured bounded budget and finish as `ready` or `needs-supervisor`; an external branch change produces `superseded`.
8. ChatGPT/human supervision performs the final review and decides whether another bounded run is useful.
9. A human decides whether to merge and whether the accumulated changes justify a release.

Fork PRs never reach the persistent runner. They remain ordinary GitHub-hosted CI/manual-review contributions.

## v0.1 -> v0.2 self-development transition

The first breaking v0.2 PR must coexist with the v0.1 default-branch gate while it is open. Candidate v0.2 core therefore recognizes old automatic trigger kinds only as clean no-ops. After the new gate is merged, those old trigger kinds are no longer emitted.

This is a bootstrap compatibility shim, not part of the intended v0.2 user workflow.

## Main and releases

Published tags are immutable distribution points. Existing installations remain pinned to their release until the newer CLI is installed and `gitkeepr init` is rerun to review the caller update.

## Exceptional recovery

Direct changes to `main` are reserved for recovery when the self-development path itself cannot restore service through a normal same-repository PR.
