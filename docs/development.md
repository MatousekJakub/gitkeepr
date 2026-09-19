# Development Workflow

GitKeepr develops itself through the same PR loop it provides to managed repositories, with an additional GitHub-hosted gate because the GitKeepr repository is public.

## Normal change flow

1. Start from the current `main`.
2. Prepare the change on a same-repository branch.
3. Open a pull request into `main`. The assistant normally prepares the branch changes and opens this PR.
4. GitHub-hosted `.github/workflows/self-gate.yml` verifies that the PR head belongs to `MatousekJakub/gitkeepr`.
5. Only after that check may the candidate branch's `.github/workflows/pr-loop.yml` be dispatched to the persistent `gitkeepr` runner.
6. Build/Review may iterate on the branch until Review returns `PASS` or the loop reaches a blocked state.
7. A human decides whether to merge and whether the accumulated changes justify a release.

Fork PRs never reach the persistent runner. They remain ordinary GitHub-hosted CI/manual-review contributions.

## Main and releases

`main` is the development line after `v0.1.0`. Published tags are immutable distribution points.

Changing `main` does not silently change existing installations:

- the installer is published as a GitHub Release asset;
- an installed CLI reads its project template from its own release tag;
- generated target callers pin the reusable workflow to that release tag.

A later release is therefore an explicit promotion of tested `main` state. Release preparation and publication are documented in `docs/releasing.md`. Managed repositories upgrade explicitly by installing the newer CLI and rerunning `gitkeepr init` to review the caller diff.

## Exceptional recovery

Direct changes to `main` are reserved for recovery when the self-development path itself is broken badly enough that a normal same-repository PR cannot restore it. Such a repair should be minimal, documented, and followed by a normal PR-based verification as soon as the path is healthy again.

## Scope discipline

Post-V1 work should be driven by observed defects, operational needs, or explicit product decisions. The V1 non-goals in `docs/goal.md` remain non-goals until deliberately changed.
