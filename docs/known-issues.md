# Known Issues / Bootstrap Gaps

> Automation-owned working list. Remove items when they are actually resolved.

- The new repository bootstrap implementation is intentionally incomplete at first; follow `docs/implementation-plan.md` rather than inventing parallel architecture.
- Public GitKeepr self-dogfood gate still needs implementation and validation before its self-hosted runner can be considered safely usable from public-repository events.
- The reusable PR loop still needs to be ported from the tested PoC and adapted to reusable-workflow inputs and generic App identity.
- Server and runner lifecycle commands need implementation and real VPS validation.
- Public repository visibility/default-branch administration may require a manual GitHub setting during bootstrap when the available API tooling does not expose that repository-admin mutation.
