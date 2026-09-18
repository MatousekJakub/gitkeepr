# Known Issues / Validation Gaps

> Automation-owned working list. Remove items only when they are actually resolved.

There are currently no known missing V1 implementation blocks in the repository. Static contract tests and shell syntax checks are green. Before calling V1 operationally validated, complete these real-environment checks:

- Run `gitkeepr server init` on the actual Ubuntu VPS and verify a repeat run is safe, preserves existing repository runners, reopens OpenCode authentication as designed, and reuses the cached Actions runner package.
- Run `gitkeepr server doctor` after initialization and confirm the real server config, PEM path, OpenCode model listing, cache, filesystem, and runner-service diagnostics.
- Exercise `gitkeepr runner add` on a private test repository, including initial registration, a healthy repeat run, and an intentionally unhealthy/reconfigure path. Exercise `runner remove` and confirm repository variables, secrets, and workflow files remain intact.
- Run a real private-repository PR through Build → Review → CONTINUE → Build → Review → PASS, plus a no-code direct comment reply, a blocked/no-progress case, and duplicate-trigger idempotence.
- Validate GitKeepr's public `.github/workflows/self-gate.yml` end to end after its own five model variables, App credentials, and repository runner are configured.

Any issue found by those smoke tests should be fixed directly and accompanied by the smallest useful regression test.
