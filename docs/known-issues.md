# Known Issues / Bootstrap Gaps

> Automation-owned working list. Remove items when they are actually resolved.

- The new repository bootstrap implementation is intentionally incomplete; follow `docs/implementation-plan.md` rather than inventing parallel architecture.
- Public GitKeepr self-dogfood gate still needs implementation and validation before its self-hosted runner can be considered safely usable from public-repository events.
- The reusable PR loop now has the minimal reusable-workflow contract, authoritative pre-checkout trigger authorization, trusted PR context loading, exact-HEAD checkout, and a first Build turn that can commit/push through the GitHub App. It is **not yet a complete Build ↔ Review loop**: Review/verdict cycles, no-progress protection, direct comment replies, final status transitions, blocked UX, and successful trigger markers still need to be ported. Until those are present, the workflow deliberately fails after Build and never marks a trigger processed.
- Manual `workflow_dispatch` of `.github/workflows/pr-loop.yml` is currently broken: the core reads `secrets.app_private_key`, which is a `workflow_call` secret alias supplied by the target caller, but a direct dispatch has no caller that can populate that alias. Before relying on manual dispatch or the public self-dogfood gate, the core needs a safe direct-dispatch credential path using the repository's `GITKEEPR_APP_PRIVATE_KEY` secret while preserving the existing reusable-workflow contract.
- Server and runner lifecycle commands need implementation and real VPS validation.
- Public repository visibility/default-branch administration may require a manual GitHub setting during bootstrap when the available API tooling does not expose that repository-admin mutation.
