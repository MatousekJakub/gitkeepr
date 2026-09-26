# Security Model

> Human-owned source of truth. Security boundaries may be strengthened by automation, but not weakened without explicit human approval.

## Standard target repositories

Standard setup supports private, trusted repositories only.

Before any checkout or OpenCode execution, the core must verify that the PR head repository is the same repository as the base repository. Fork code must not run on the persistent self-hosted runner.

The caller performs a cheap first filter; the reusable core repeats authoritative checks.

Only the exact `/gitkeepr run` command from a trusted human OWNER/MEMBER/COLLABORATOR may activate the normal comment path. Ordinary comments and reviews are context only. Bot comments do not become activation commands.

## GitHub App

The App has only the repository permissions needed by the loop:

- Contents RW
- Issues RW
- Pull requests RW
- Workflows RW
- Metadata R (implicit)

The private key is never committed. Project secrets receive the key through `runner add`. The server config stores only its filesystem path.

The App bot login is derived dynamically from the token and is not hardcoded.

## Public GitKeepr self-development

GitKeepr itself is intended to be public, but its persistent self-hosted runner must never execute arbitrary fork PR code.

The self-development design uses a small, stable GitHub-hosted gate from the default branch. The gate may dispatch the candidate `pr-loop.yml` on a branch only after proving that the PR head repository is the GitKeepr repository itself. Fork PRs are ignored by GitKeepr AI automation and may only use ordinary GitHub-hosted CI/manual review.

Minimal dispatch context:

- `pr_number`
- `trigger_kind`
- `trigger_source_id`

The candidate core then fetches current context through GitHub APIs.

## Self-hosted runner risk

Persistent self-hosted runners should be treated as trusted infrastructure. Do not broaden public-repository execution rules casually.

There is no global concurrency limiter. If parallel jobs later cause resource pressure, diagnose first and add the smallest observed solution.

Symptoms worth checking on a small VPS include unusually slow concurrent jobs, sustained load materially above available CPU, swap/memory pressure, timeouts, or OOM kills.


## Stale-run write protection

A v0.2 worker may write the PR branch only while the remote branch still equals the HEAD it expects. The worker checks the remote branch before credentialed pushes and treats any external change as `superseded`.

Before publishing labels or Review output, the finalizer reloads the PR and requires its live HEAD to match the reviewed result HEAD. Stale runs therefore do not publish authoritative state over newer work.
