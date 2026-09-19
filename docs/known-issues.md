# Known Issues / Validation Gaps

> Automation-owned working list. Add items only when they are actually observed.

There are currently no known V1 implementation blockers or remaining live-validation gaps.

Static contract tests and shell syntax checks are green. Live validation on the actual Ubuntu VPS covered:
- repeated `gitkeepr server init` and `gitkeepr server doctor`;
- private-repository init/doctor, GitHub App credential sync, runner add, healthy repeat, unhealthy/reconfigure, remove, and clean re-add;
- real private PR Build → Review → CONTINUE → Build → Review → PASS;
- bot-synchronize suppression, no-code direct reply, `gitkeepr:no-build` suppression, duplicate-trigger idempotence, no-progress blocking, retryability without a processed marker, and blocked-message deduplication;
- public GitKeepr self-development through the GitHub-hosted self-gate;
- same-repository self-development dispatch to the persistent runner, including a Review-detected cleanup cycle before PASS;
- fork-PR isolation: the self-gate emitted `Ignoring fork PR …; persistent runner will not execute it` and created no `workflow_dispatch` for the persistent runner.

GitKeepr V1 is operationally validated for the tested Ubuntu/ARM64 server and repository workflows.
