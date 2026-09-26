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

Post-merge E2E on the actual persistent VPS runner additionally verified the v0.2 default-branch gate, ordinary-comment suppression, `ready`/PASS publication, duplicate command delivery suppression before agent work, and manual `workflow_dispatch`.

No known implementation or release blocker remains from the exercised paths. Intentional provider/App-auth failure injection and a fresh post-merge fork PR were not performed for this release candidate; those remaining gaps are tracked in `docs/testing.md` and are not required to damage a healthy installation merely to satisfy the checklist.

The following v0.1.x operational lessons are addressed structurally by the v0.2 design:

- ordinary pushes/reviews/comments no longer start agent work;
- the finalization budget defaults to 2 cycles instead of inheriting the v0.1 value 15;
- unresolved work becomes `gitkeepr:needs-supervisor` instead of requiring a complex blocked/no-progress state machine;
- transient building/reviewing labels are removed from the state model;
- external branch movement yields `superseded` rather than a stale push/review race;
- technical failures are represented by the Actions run rather than a persistent failure label.

GitHub App credential refresh/retry from v0.1.1 remains in place for long-running credentialed operations.
