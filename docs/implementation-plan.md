# Implementation Plan

> Automation-owned working plan. Keep this synchronized with reality while respecting human-owned decisions.

## V1 implementation status

The planned implementation blocks are present:

1. Clean repository, source-of-truth documentation, MIT license, installer, and shell CLI.
2. `gitkeepr init` with the approved project-side contract and no Git-history ownership.
3. Complete reusable Build ↔ Review loop with configured models/variants, max cycles, no-progress protection, direct replies, status labels, blocked UX, and success-only processed markers.
4. Small target caller with the tested event set and conservative cheap trust filtering.
5. `gitkeepr server init` for Ubuntu/Debian + systemd on amd64/arm64.
6. Automated `runner add`, healthy repeat behavior, unhealthy reconfiguration, and `runner remove`.
7. Project/server doctors.
8. Public GitKeepr self-development gate on a GitHub-hosted runner before candidate core dispatch.
9. Focused CLI/workflow contract tests and shell syntax CI.
10. Third-party GitHub Actions pinned to full commit SHAs.

## Operational validation

V1 live validation is complete for the tested Ubuntu/ARM64 server and repository workflows. The exercised matrix is recorded in `docs/testing.md`, with the current validation state in `docs/known-issues.md`.

Future work should be driven by observed defects, operational needs, or explicit product decisions rather than by inventing another V1 implementation phase.

## Constraints that remain deliberate

- No generic verification-command framework.
- No global concurrency lock without an observed problem.
- No Dependabot-specific integration.
- No clean-working-tree requirement for project init.
- No SSH model discovery from project init.
- No automated GitHub App creation/installation.
- No polling, custom dispatcher, database, or queue.
