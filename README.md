# GitKeepr

GitKeepr is a small, GitHub-native AI PR loop built around GitHub Actions, a persistent self-hosted runner, OpenCode, and a GitHub App.

GitHub PRs are the control plane. Build edits and tests the PR branch, the workflow owns Git/GitHub mutations, and Review independently checks the current HEAD until it returns `PASS` or the loop reaches a clear blocked state.

## V1 status

GitKeepr V1 is operationally validated for the tested Ubuntu/ARM64 server and repository workflows. Contract CI is green, and live smoke testing covered server/bootstrap lifecycle, private-repository runner lifecycle, real multi-cycle Build ↔ Review PR flows, no-code replies, trigger idempotence/suppression, blocked/retry behavior, public self-development, and fork isolation.

Standard V1 target repositories are **private and trusted**. GitKeepr itself is public and uses a separate GitHub-hosted self-development gate so fork code never reaches the persistent runner.

See `docs/testing.md` for the validated smoke matrix and `docs/known-issues.md` for the current validation status.

## Install

Install or update to the latest published release:

```bash
curl -fsSL https://github.com/MatousekJakub/gitkeepr/releases/latest/download/install.sh | bash
```

Prepare the Ubuntu/Debian VPS once:

```bash
gitkeepr server init
```

Inside a private target repository:

```bash
gitkeepr init
```

The generated caller is pinned to the CLI's release tag (for V1, `v0.1.0`), so future changes on `main` do not silently change managed repositories. Commit the generated `.github/workflows/gitkeepr.yml` after inspection, then on the VPS:

```bash
gitkeepr runner add owner/repo
```

Verify both sides:

```bash
gitkeepr doctor
gitkeepr server doctor
```

Useful lifecycle commands:

```bash
gitkeepr runner add owner/repo
gitkeepr runner remove owner/repo
gitkeepr version
```

`runner remove` removes only the runner/service/directory; repository variables, secrets, and workflow files are intentionally retained.

## Public self-development

The public `MatousekJakub/gitkeepr` repository is the only V1 public persistent-runner exception. Its `gitkeepr init` path configures variables but does **not** create the standard caller. Public PR events first pass through `.github/workflows/self-gate.yml` on a GitHub-hosted runner; only same-repository PRs may dispatch the candidate `pr-loop.yml` to the persistent runner. Fork PRs are ignored by GitKeepr AI automation.

## Documentation

Start with:

- `docs/goal.md` — product scope and non-goals;
- `docs/architecture.md` — components and Build/Review loop;
- `docs/security.md` — trust boundaries, App permissions, and public self-gate;
- `docs/setup.md` — installation and repository setup;
- `docs/operations.md` — recovery and operational semantics;
- `docs/testing.md` — automated contracts and live smoke checklist;
- `docs/decisions.md` — approved product decisions.
