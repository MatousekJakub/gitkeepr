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

## v0.2 implementation-PR live evidence

The breaking v0.2 implementation was dogfooded on PR #13 on the actual persistent VPS runner on 2026-09-26.

Observed behavior:

- an exact trusted `/gitkeepr run` passed through the public self-development gate and dispatched the candidate branch workflow;
- ordinary pushes made while developing the PR started CI only and did not start additional GitKeepr runs;
- run #25 began on one PR HEAD, the branch was changed externally, and the stale worker exited as `superseded` without publishing stale result state;
- a fresh explicit run then continued normally on the newer HEAD;
- run #27 used `GITKEEPR_FINALIZATION_CYCLES=2`, executed exactly two Build -> Review cycles, and stopped successfully as `gitkeepr:needs-supervisor` after two `CONTINUE` verdicts;
- Build-owned workflow commits triggered CI but did not recursively trigger GitKeepr;
- the finalizer published the `gitkeepr:needs-supervisor` result label on the reviewed current HEAD;
- current-HEAD contract CI and shell syntax checks passed.

These observations are sufficient to validate the new v0.2 behavioral contract for merging the implementation PR. They do **not** mean every release/rollout smoke scenario below has been exercised.

## Pre-release / rollout smoke checklist

Before calling a v0.2 release operationally validated, exercise the remaining paths that are useful to validate independently of the implementation PR.

### Explicit triggering

- [x] Exact trusted `/gitkeepr run` dispatches one bounded run.
- [x] Development pushes do not automatically start GitKeepr.
- [x] After the v0.2 default-branch gate is active, confirm an ordinary trusted comment only produces a skipped gate job and never reaches the persistent runner.
- [x] Redeliver the same successful command trigger and confirm processed-trigger idempotence skips model work.
- [x] Verify the public self-gate `workflow_dispatch` manual path.

### Bounded loop

- [x] Exercise Build -> Review `PASS` and expect `gitkeepr:ready`.
- [ ] Exercise Build -> Review `CONTINUE` -> Build -> Review `PASS`.
- [x] Exercise two Review `CONTINUE` verdicts and expect a successful workflow with `gitkeepr:needs-supervisor`.
- [x] Confirm the live run uses the default two-cycle budget when `GITKEEPR_FINALIZATION_CYCLES` is not configured.

### HEAD ownership

- [x] Start GitKeepr at HEAD A and externally push HEAD B while Build or Review is running.
- [x] Confirm the stale run becomes `superseded`.
- [x] Confirm it does not overwrite HEAD B or publish stale Review output/result state.
- [x] Start a fresh explicit run on the newer HEAD and confirm normal operation.

### Failures

- [ ] Intentionally exercise a harness/provider failure and confirm Actions fails without a persistent failure label or successful trigger marker.
- [ ] Intentionally exercise invalid Review output and confirm the same.
- [ ] Exercise an unrecoverable push/auth failure only in a safe test repository if useful; do not damage the working GitHub App installation merely to satisfy a checklist.

### Public self-development / isolation

- [x] Same-repository explicit commands reach the persistent runner through the GitHub-hosted gate.
- [ ] Reconfirm fork PR isolation after the v0.2 gate is on the default branch.

## Post-merge release-candidate evidence

On 2026-09-26, PR #14 was used as a disposable post-merge smoke PR against the v0.2 default-branch gate and the real persistent VPS runner:

- PR open produced CI only;
- a second ordinary push produced CI only;
- an ordinary trusted comment produced a skipped GitHub-hosted self-gate job and no persistent-runner dispatch;
- exact `/gitkeepr run` dispatched PR Loop #29 and reached Review `PASS` on the same HEAD;
- rerunning the same original gate event dispatched PR Loop #30, which recognized the existing `gitkeepr-trigger:v2` marker and skipped checkout, Build, Review, and finalization work;
- manual self-gate `workflow_dispatch` dispatched PR Loop #31 and reached Review `PASS` on the same HEAD.

The smoke PR was closed without merge.

Record only observed failures in `docs/known-issues.md`. Unchecked release smoke items are rollout validation, not evidence that the implementation PR is incomplete.
