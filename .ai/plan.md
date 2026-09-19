# Public self-development smoke test

## Goal

Document the safety boundary of GitKeepr's public self-development path.

## Task

- [ ] Add a short section to `docs/testing.md` explaining that public self-development PR events are first handled by the GitHub-hosted `self-gate.yml`, that only same-repository PRs may dispatch `pr-loop.yml` to the persistent self-hosted runner, and that fork PRs must never reach the persistent runner.

Keep the change documentation-only and concise.
