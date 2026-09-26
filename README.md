# GitKeepr

GitKeepr is a small, explicitly triggered AI PR finalization worker built around GitHub Actions, a persistent self-hosted runner, OpenCode, and a GitHub App.

The intended v0.2 workflow is ChatGPT/user first, GitHub PR/branch as the durable shared source of truth, and GitKeepr only when real project-environment Build/Review work is useful. A trusted `/gitkeepr run` starts a short bounded finalization run; ordinary commits, reviews, and comments do not.

## Status

The latest released line is v0.1.x. `main` is developing the breaking v0.2 bounded-finalizer behavior.

v0.2 defaults to two Build -> Review cycles and finishes as `gitkeepr:ready` or `gitkeepr:needs-supervisor`. If another actor changes the PR branch during a run, the stale run becomes `superseded` instead of racing the newer work.

Standard target repositories are **private and trusted**. GitKeepr itself is public and uses a separate GitHub-hosted self-development gate so fork code never reaches the persistent runner.

See `docs/testing.md` for the smoke checklist and `docs/known-issues.md` for the current validation status.

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

The generated caller is pinned to the installed CLI's release tag, so future changes on `main` do not silently change managed repositories. Commit the generated `.github/workflows/gitkeepr.yml` after inspection, then on the VPS:

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

The public `MatousekJakub/gitkeepr` repository is the only public persistent-runner exception. Its `gitkeepr init` path configures variables but does **not** create the standard caller. Explicit `/gitkeepr run` commands and manual dispatches first pass through `.github/workflows/self-gate.yml` on a GitHub-hosted runner; only same-repository PRs may dispatch the candidate `pr-loop.yml` to the persistent runner. Fork PRs are ignored by GitKeepr AI automation.

## Documentation

Start with:

- `docs/goal.md` — product scope and non-goals;
- `docs/architecture.md` — components and Build/Review loop;
- `docs/development.md` — self-development PR workflow and release isolation;
- `docs/releasing.md` — deterministic release preparation, publishing, and upgrade flow;
- `docs/security.md` — trust boundaries, App permissions, and public self-gate;
- `docs/setup.md` — installation and repository setup;
- `docs/operations.md` — recovery and operational semantics;
- `docs/testing.md` — automated contracts and live smoke checklist;
- `docs/decisions.md` — approved product decisions.
