# Known Issues / Validation Gaps

> Automation-owned working list. Add items only when they are actually observed.

## v0.2 validation status

The v0.2 bounded-finalizer behavior is under implementation and has not yet completed the live smoke matrix in `docs/testing.md`.

The following v0.1.x operational lessons are already addressed structurally by the v0.2 design:

- ordinary pushes/reviews/comments no longer start agent work;
- the default loop budget is reduced from 15 to 2 cycles;
- unresolved work becomes `gitkeepr:needs-supervisor` instead of requiring a complex blocked/no-progress state machine;
- transient building/reviewing labels are removed from the state model;
- external branch movement yields `superseded` rather than a stale push/review race;
- technical failures are represented by the Actions run rather than a persistent failure label.

GitHub App credential refresh/retry from v0.1.1 remains in place for long-running credentialed operations.

Do not mark v0.2 operationally validated until the explicit-trigger, bounded-loop, supersede, failure, and public self-development smoke cases have run on the actual VPS.
