# Known Issues / Validation Gaps

> Automation-owned working list. Remove items only when they are actually resolved.

There are currently no known missing V1 implementation blocks in the repository. Static contract tests and shell syntax checks are green.

Live validation completed on the actual Ubuntu VPS for:
- repeated `gitkeepr server init` and `gitkeepr server doctor`;
- private-repository init/doctor, GitHub App credential sync, runner add, healthy repeat, unhealthy/reconfigure, remove, and clean re-add;
- real private PR Build → Review → CONTINUE → Build → Review → PASS;
- bot-synchronize suppression, no-code direct reply, `gitkeepr:no-build` suppression, duplicate-trigger idempotence, no-progress blocking, retryability without a processed marker, and blocked-message deduplication.

Before calling V1 fully operationally validated, complete the public GitKeepr self-development smoke test: configure GitKeepr's own variables/App credentials/runner, verify a same-repository PR is dispatched through the GitHub-hosted `.github/workflows/self-gate.yml`, and verify a fork PR never reaches the persistent runner.
