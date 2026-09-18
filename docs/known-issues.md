# Known Issues / Bootstrap Gaps

> Automation-owned working list. Remove items when they are actually resolved.

- The new repository bootstrap implementation is intentionally incomplete; follow `docs/implementation-plan.md` rather than inventing parallel architecture.
- The reusable PR loop now has the minimal reusable-workflow contract, authoritative pre-checkout trigger authorization, trusted PR context loading, exact-HEAD checkout, and a first Build turn that can commit/push through the GitHub App. It is **not yet a complete Build ↔ Review loop**: Review/verdict cycles, no-progress protection, direct comment replies, final status transitions, blocked UX, and successful trigger markers still need to be ported. Until those are present, the workflow deliberately fails after Build and never marks a trigger processed.
- Server and runner lifecycle commands need implementation and real VPS validation.
- `gitkeepr server doctor` currently probes OpenCode as `github-runner` with `sudo -n` for non-root admins. A normal sudo-capable admin whose sudo policy requires password entry can therefore get a false `OpenCode is not available` failure even when OpenCode is installed correctly. The probe should remain read-only but use the normal interactive sudo path (or another reliable user-switch mechanism) instead of requiring passwordless sudo.
- Public repository visibility/default-branch administration may require a manual GitHub setting during bootstrap when the available API tooling does not expose that repository-admin mutation.
