# Testing Strategy

> Automation-owned working document. Prefer tests that protect observed behavior; avoid building a testing framework for its own sake.

## Automated contract CI

Every push to `main` and pull request runs:

```bash
python3 -m unittest discover -s tests -v
bash -n bin/gitkeepr
bash -n install.sh
```

The tests protect the high-value contracts: project-init mutation boundaries, server/runner lifecycle structure, trust-before-checkout, same-repository execution, configured Build/Review models, exact-HEAD Review verdicts, max-cycle/no-progress behavior, success-only trigger markers, public self-gate behavior, and full-SHA third-party Action pinning.

Ordinary repository CI remains independent of the AI Review verdict. GitKeepr V1 deliberately does not impose a universal deterministic verification command on target projects; Build chooses relevant tests for the current repository/task.

## Live smoke checklist

### Server

1. Install/update the CLI from the published GitHub Release asset and verify `gitkeepr version`.
2. Run `gitkeepr server init`.
3. Run `gitkeepr server doctor`.
4. Repeat `server init` and confirm existing runner services remain untouched.

### Private target repository

1. Add the repo to the GitHub App.
2. Run `gitkeepr init`, inspect and commit the caller.
3. Run `gitkeepr runner add owner/repo`.
4. Run `gitkeepr doctor`; expect caller, variables, App Client ID/secret, and an online `gitkeepr` runner.
5. Repeat `runner add`; expect no healthy-runner re-registration.
6. Exercise disposable unhealthy/reconfigure and remove paths.

### PR loop

Verify PR-opened Build, App push, Review CONTINUE/PASS, multi-cycle progress, PASS → `gitkeepr:waiting-human`, no-code direct reply, no-progress → blocked, failure without processed marker, duplicate-trigger skip, no-build suppression, and bot-synchronize suppression.

### Public GitKeepr self-development

Public self-development PR events are first handled by the GitHub-hosted
`.github/workflows/self-gate.yml`. Only same-repository PRs may dispatch
`.github/workflows/pr-loop.yml` to the persistent self-hosted runner; fork PRs
must never reach that runner.

Live validation confirmed both paths: a same-repository PR dispatched the candidate
`pr-loop.yml` and completed Build → Review → CONTINUE → Build → Review → PASS on
the persistent runner, while a fork PR was stopped by the GitHub-hosted self-gate
with no `workflow_dispatch` created for the persistent runner.

Record only observed failures in `docs/known-issues.md`.
