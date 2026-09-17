# Operations and Recovery

## Status semantics

- `gitkeepr:building`: Build is working.
- `gitkeepr:reviewing`: Review is checking the current PR.
- `gitkeepr:waiting-human`: the core loop is idle and waiting for external/human action. This does **not** mean CI is green or the PR is approved for merge.
- `gitkeepr:blocked`: the core loop stopped because it cannot safely progress.

## Recovery principles

A blocked/failing source trigger is not marked successfully processed. A later trusted comment can start a fresh trigger.

A blocked state does not mean "AI may never touch this again". It means the core loop stopped and needs an external intervention. The intervention can be a human or an optional external helper when the helper can resolve the block without inventing a human product decision.

Examples:

- Infrastructure/transient error: rerun after correcting infrastructure.
- Missing human choice A/B: helper must not choose for the human.
- Clear actionable code/test finding: a trusted actionable comment may restart Build.
- OAuth/provider issue: rerun `opencode auth login` as `github-runner`.
- GitHub App key rotation: update the PEM file/server config as needed, then rerun `gitkeepr runner add owner/repo` to resync project credentials.
- Broken runner: rerun `runner add`; unhealthy existing installation should offer automated reconfiguration.

## Manual runner fallback

GitHub Settings → Actions → Runners → New self-hosted runner shows the official Download and Configure commands. This is a troubleshooting/bootstrap fallback, not the standard per-repository workflow.

## Resource contention

V1 deliberately has no global concurrency control. If jobs overlap and problems appear, look for:

- large run-time increases only under overlap;
- sustained CPU/load pressure;
- swap/memory pressure;
- timeouts;
- OOM kills.

Only then add the smallest appropriate control.
