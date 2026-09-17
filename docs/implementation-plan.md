# Implementation Plan

> Automation-owned working plan. Keep this synchronized with reality while respecting human-owned decisions.

## Bootstrap priorities

1. Establish the clean repository, documentation, MIT license, installer, and shell CLI.
2. Implement a useful `gitkeepr init` matching the approved project-side contract.
3. Port the tested PR Build/Review behavior from the PoC into reusable `.github/workflows/pr-loop.yml`, including the idempotence failure-marker fix and `gitkeepr:*` labels.
4. Add the small target caller template with the tested event set and cheap trust filtering.
5. Implement `server init` for supported Ubuntu/Debian hosts.
6. Implement automated `runner add`, runner health/reconfigure, and `runner remove`.
7. Implement project/server doctors.
8. Implement the public-repository self-dogfood safety gate for GitKeepr itself.
9. Add focused tests for CLI parsing, template generation, trust conditions, and shell behavior where practical.
10. Tighten documentation from real usage rather than speculative abstractions.

## Important implementation constraints

- Do not add a generic verification-command framework in V1.
- Do not add global concurrency locking until there is an observed problem.
- Do not add Dependabot-specific logic.
- Do not require a clean working tree for project init.
- Do not copy model discovery over SSH.
- Do not automate GitHub App creation/installation.
