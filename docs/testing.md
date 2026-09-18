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

1. Install/update the CLI from `main`.
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

After configuring GitKeepr's own vars/secret/runner, verify a same-repo PR is dispatched by the GitHub-hosted self-gate and a fork PR never reaches the persistent runner.

Record only observed failures in `docs/known-issues.md`.
