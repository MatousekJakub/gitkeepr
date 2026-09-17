# Testing Strategy

> Automation-owned working document. Prefer tests that protect observed behavior; avoid building a testing framework for its own sake.

## Principles

- Keep ordinary repository CI separate from GitKeepr AI Review verdicts.
- Build should run relevant project tests based on the repository/task.
- GitKeepr V1 does not impose a universal deterministic verification command.
- Test shell/CLI behavior with small focused tests where they pay for themselves.
- Validate workflow YAML and important trust/idempotence conditions before relying on them.

## High-value scenarios

- Project init creates only `.github/workflows/gitkeepr.yml` and variables, with no Git commit/stage.
- Repeated init preserves existing variable values as defaults.
- Different existing caller workflow requires explicit replace confirmation.
- Public standard target repository is rejected.
- Missing App-install confirmation stops local init with instructions.
- Fork PR cannot reach checkout/OpenCode in standard core.
- Bot synchronize does not auto-trigger.
- `gitkeepr:no-build` suppresses triggering while remaining in discussion context.
- Duplicate successful trigger skips model work.
- Failed/blocked trigger is not falsely marked processed.
- No-progress Review CONTINUE becomes `gitkeepr:blocked` with a clear comment.
- Runner add is repeatable and unhealthy reconfiguration uses fresh API tokens.
- Public GitKeepr self-dogfood gate never dispatches a fork PR branch to the persistent runner.
