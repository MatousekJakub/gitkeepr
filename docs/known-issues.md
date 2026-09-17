# Known Issues / Bootstrap Gaps

> Automation-owned working list. Remove items when they are actually resolved.

- The new repository bootstrap implementation is intentionally incomplete; follow `docs/implementation-plan.md` rather than inventing parallel architecture.
- The reusable PR loop now has the minimal reusable-workflow contract, authoritative pre-checkout trigger authorization, trusted PR context loading, exact-HEAD checkout, and a first Build turn that can commit/push through the GitHub App. It is **not yet a complete Build ↔ Review loop**: Review/verdict cycles, no-progress protection, direct comment replies, final status transitions, blocked UX, and successful trigger markers still need to be ported. Until those are present, the workflow deliberately fails after Build and never marks a trigger processed.
- Server and runner lifecycle commands need implementation and real VPS validation.
- Public repository visibility/default-branch administration may require a manual GitHub setting during bootstrap when the available API tooling does not expose that repository-admin mutation.
