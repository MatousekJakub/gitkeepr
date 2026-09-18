# Known Issues / Bootstrap Gaps

> Automation-owned working list. Remove items when they are actually resolved.

- The new repository bootstrap implementation is intentionally incomplete; follow `docs/implementation-plan.md` rather than inventing parallel architecture.
- The reusable PR loop now has the minimal reusable-workflow contract, authoritative pre-checkout trigger authorization, trusted PR context loading, exact-HEAD checkout, and a first Build turn that can commit/push through the GitHub App. It is **not yet a complete Build ↔ Review loop**: Review/verdict cycles, no-progress protection, direct comment replies, final status transitions, blocked UX, and successful trigger markers still need to be ported. Until those are present, the workflow deliberately fails after Build and never marks a trigger processed.
- Server and runner lifecycle commands need implementation and real VPS validation.
- `gitkeepr server doctor` currently reads the root-owned `/etc/gitkeepr/config` and App private-key path directly as the invoking admin user. Once `server init` creates the documented root-owned/restrictive files, a normal sudo-capable admin can therefore get false `missing or unreadable` failures. The doctor should use privileged read-only access (root directly or interactive `sudo`) for these checks without weakening file permissions or becoming mutating.
- Public repository visibility/default-branch administration may require a manual GitHub setting during bootstrap when the available API tooling does not expose that repository-admin mutation.
