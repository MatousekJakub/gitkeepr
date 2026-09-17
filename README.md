# GitKeepr

GitKeepr is a small, GitHub-native AI PR loop built around GitHub Actions, a persistent self-hosted runner, OpenCode, and a GitHub App.

The project is intentionally simple: GitHub PRs are the control plane, OpenCode provides Build and Review agents, and a GitHub App performs repository mutations. The standard V1 target is a **private, trusted repository**. GitKeepr itself is intended to be public and uses a separate trust gate for self-development.

## Status

GitKeepr is in bootstrap development. The documents in `docs/` are the source of truth. The implementation must follow them without inventing new product requirements or adding unnecessary infrastructure.

## Core idea

1. A trusted PR event, review, or comment triggers the caller workflow in a target repository.
2. The caller invokes the reusable GitKeepr PR loop.
3. Build works on the checked-out PR branch and pushes changes through a GitHub App.
4. Review independently checks the current HEAD and returns `CONTINUE` or `PASS`.
5. `CONTINUE` loops back to Build. `PASS` moves the PR to `gitkeepr:waiting-human`.
6. Human comments can restart the loop. External helpers may also interact as the human account.

Start with `docs/goal.md`, `docs/architecture.md`, and `docs/decisions.md`.
