# Testing Strategy

> Automation-owned working document. Prefer tests that protect observed behavior; avoid building a testing framework for its own sake.

## Automated contract CI

Every push to `main` and pull request runs:

```bash
python3 -m unittest discover -s tests -v
bash -n bin/gitkeepr
bash -n install.sh
```

The tests protect the high-value contracts: release-pinned installation, trust-before-checkout, explicit-only triggering, same-repository public self-development, configured Build/Review models, exact-HEAD Review verdicts, bounded-cycle outcomes, PR-HEAD ownership/supersede behavior, success-only trigger markers, credential isolation/refresh, and full-SHA third-party Action pinning.

Ordinary repository CI remains independent of the AI Review verdict. GitKeepr does not impose a universal verification command on target projects; Build chooses relevant tests for the current repository/task.

## v0.2 live smoke checklist

### Explicit triggering

1. Open a same-repository PR and confirm GitKeepr agent work does not start from PR open alone after the v0.2 gate is active.
2. Push one or more commits and confirm they do not start GitKeepr.
3. Add ordinary trusted comments and reviews and confirm they do not start GitKeepr.
4. Post exact `/gitkeepr run` and confirm one bounded run starts.
5. Redeliver the same command trigger and confirm processed-trigger idempotence skips model work.
6. Verify `workflow_dispatch` starts a manual run.

### Bounded loop

1. Exercise Build -> Review PASS and expect `gitkeepr:ready`.
2. Exercise Build -> Review CONTINUE -> Build -> Review PASS with the default two-cycle budget.
3. Exercise two Review CONTINUE verdicts and expect a successful workflow with `gitkeepr:needs-supervisor`, not a technical failure.
4. Confirm Build is asked to resolve all safely actionable remaining work in each turn.

### HEAD ownership

1. Start GitKeepr at HEAD A and externally push HEAD B while Build or Review is running.
2. Confirm the stale run becomes `superseded`.
3. Confirm it does not overwrite HEAD B, change durable result labels, or publish stale Review output.
4. Start a fresh explicit run on HEAD B and confirm normal operation.

### Failures

Confirm harness/provider failure, invalid Review output, and unrecoverable push/auth failure produce an Actions failure without writing a persistent failure label or successful trigger marker.

### Public GitKeepr self-development

Confirm the GitHub-hosted gate dispatches only exact trusted `/gitkeepr run` commands or manual dispatch for same-repository PRs. Fork PRs must never reach the persistent runner.

Record only observed failures in `docs/known-issues.md`.
