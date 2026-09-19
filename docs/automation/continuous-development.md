# Archived Bootstrap Development

This file records the temporary bootstrap automation used while GitKeepr V1 was being built. It is historical documentation, not the active development policy.

The hourly ChatGPT Scheduled task committed directly to `main`. It was useful for early incremental work, but its one-small-iteration-per-run behavior became inefficient once the remaining work was known. The task was disabled on 2026-09-18.

Starting after the `v0.1.0` release, normal GitKeepr development moved to the repository's own public self-development workflow: prepare a same-repository branch, open a pull request, pass the GitHub-hosted self-gate, and let the candidate Build/Review loop run on the persistent runner. Direct commits to `main` are no longer the normal development path.

The product does **not** depend on the old scheduler. If a temporary scheduled hardening task is created later, it should still work through normal pull requests unless the self-development infrastructure itself is unavailable and requires explicit recovery.
