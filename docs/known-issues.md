# Known Issues / Validation Gaps

> Automation-owned working list. Add items only when they are actually observed.

## v0.2 validation status

Automated contract CI is implemented in `.github/workflows/ci.yml` and covers the current workflow contracts and shell syntax checks.

The v0.2 implementation PR has been dogfooded on the actual persistent VPS runner. Live evidence now covers:

- explicit `/gitkeepr run` dispatch through the public self-development gate;
- ordinary development pushes not starting additional GitKeepr runs;
- the default two-cycle finalization budget;
- successful `gitkeepr:needs-supervisor` completion after two `CONTINUE` verdicts;
- Build workflow commits without recursive GitKeepr activation;
- real `superseded` handling when another actor changes the PR HEAD;
- final result publication on the reviewed current HEAD.

No remaining **implementation blocker** is known from those exercised paths.

The full v0.2 release/rollout smoke matrix is intentionally not complete yet. Remaining validation includes the `ready`/PASS path, manual dispatch and duplicate-delivery behavior, intentional technical-failure cases, and post-merge fork/default-gate checks. Those items are tracked in `docs/testing.md` and should be completed before calling the v0.2 release operationally validated.

The following v0.1.x operational lessons are addressed structurally by the v0.2 design:

- ordinary pushes/reviews/comments no longer start agent work;
- the finalization budget defaults to 2 cycles instead of inheriting the v0.1 value 15;
- unresolved work becomes `gitkeepr:needs-supervisor` instead of requiring a complex blocked/no-progress state machine;
- transient building/reviewing labels are removed from the state model;
- external branch movement yields `superseded` rather than a stale push/review race;
- technical failures are represented by the Actions run rather than a persistent failure label.

GitHub App credential refresh/retry from v0.1.1 remains in place for long-running credentialed operations.
