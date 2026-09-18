# GitKeepr

GitKeepr is a small, GitHub-native AI PR loop built around GitHub Actions, a persistent self-hosted runner, OpenCode, and a GitHub App.

GitHub PRs are the control plane. Build edits and tests the PR branch, the workflow owns Git/GitHub mutations, and Review independently checks the current HEAD until it returns `PASS` or the loop reaches a clear blocked state.

## V1 status

The documented V1 implementation is feature-complete in the repository and its contract CI is green. The remaining release work is live validation on the real VPS and end-to-end PR flows; see `docs/known-issues.md` and `docs/testing.md`.

Standard V1 target repositories are **private and trusted**. GitKeepr itself is public and uses a separate GitHub-hosted self-development gate so fork code never reaches the persistent runner.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/MatousekJakub/gitkeepr/main/install.sh | bash
```

Then prepare the VPS once:

```bash
gitkeepr server init
```

Inside a private target repository:

```bash
gitkeepr init
```

On the VPS:

```bash
gitkeepr runner add owner/repo
```

Start with `docs/goal.md`, `docs/architecture.md`, `docs/decisions.md`, and `docs/setup.md`.
