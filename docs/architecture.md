# Architecture

> Human-owned source of truth. Preserve the approved architecture unless a human explicitly changes it.

## Role

GitKeepr v0.2 is an explicitly triggered, bounded PR finalization worker. It is not the primary product-planning or orchestration layer.

The normal control flow is:

1. ChatGPT/user prepares most of the change and opens or updates a PR.
2. GitHub PR/branch is the durable shared source of truth.
3. A trusted human or supervisor explicitly starts GitKeepr with `/gitkeepr run` or `workflow_dispatch`.
4. GitKeepr gives the real project environment to Build and independent Review agents for at most `GITKEEPR_MAX_CYCLES`.
5. The run finishes as `ready`, `needs-supervisor`, `superseded`, or a technical Actions failure.
6. ChatGPT/human supervision decides what happens next.

## Components

### Target repository

For a standard private target repository, `gitkeepr init` creates exactly one versioned file:

- `.github/workflows/gitkeepr.yml`

It also configures repository variables. It does not create `.ai/plan.md`, `AGENTS.md`, a `.gitkeepr/` directory, or any other project files.

The caller listens only to:

- trusted PR issue comments whose body is exactly `/gitkeepr run`;
- `workflow_dispatch`.

Ordinary PR creation, pushes, comments, and reviews are context only. They do not start GitKeepr.

The public upstream GitKeepr repository is a narrow self-development exception. `.github/workflows/self-gate.yml` runs on a GitHub-hosted runner, proves that the PR comes from the same repository, and only then dispatches the candidate `pr-loop.yml` to the persistent runner.

### Reusable core

The reusable core accepts:

- `pr_number`;
- `trigger_kind`;
- `trigger_source_id`.

For v0.2, the active trigger kinds are `comment` for the exact command and `manual` for workflow dispatch. The core temporarily recognizes the old automatic trigger kinds only to ignore them safely while the self-development gate transitions from v0.1.x to v0.2.

The core reloads authoritative PR/comment/review context through GitHub APIs before checkout.

### GitHub App

Required repository permissions:

- Contents: read/write;
- Issues: read/write;
- Pull requests: read/write;
- Workflows: read/write;
- Metadata: implicit read.

The App identity is derived dynamically. The private key is never exposed to Build/Review processes.

### Persistent runner

Ubuntu/Debian Linux with systemd on amd64 or arm64 is supported. One `github-runner` user owns the coding harness authentication and runs repository-level Actions runner services with the `gitkeepr` label.

### Coding harness

OpenCode remains the v0.2 implementation harness. Build/Review prompts are deliberately separated from workflow-owned Git/GitHub mutation. Harness replacement or abstraction is a later concern; the v0.2 behavioral contract must not depend on OpenCode-specific orchestration semantics.

## Bounded Build / Review finalization

Each cycle is:

`Build -> workflow-owned commit/push when needed -> independent Review`

Build:

- reads the current repository, optional plan, trusted human/Copilot discussion, and prior GitKeepr review;
- treats the PR as an already-started implementation that needs finalization;
- resolves all safely actionable remaining work it can identify in that turn;
- runs relevant tests;
- does not commit, push, create branches, or mutate GitHub metadata.

Review:

- is read-only;
- checks the full PR scope at the exact current HEAD;
- returns `PASS` or `CONTINUE`;
- binds its verdict marker to the reviewed HEAD.

The default cycle budget is **2**. Repositories may explicitly choose a higher positive integer, but v0.2 is designed around short runs and external supervision rather than long autonomous convergence.

After the final allowed `CONTINUE`, GitKeepr exits successfully as `needs-supervisor`. That is a normal checkpoint, not an infrastructure failure.

## PR HEAD ownership

The run records the PR HEAD it started from. Before credentialed branch writes, GitKeepr re-reads the remote branch HEAD.

If another actor changes the PR branch while the run is active, GitKeepr exits successfully as `superseded`. It does not rebase, merge, overwrite the newer branch, or publish stale review state.

After Review, finalization checks the live PR HEAD again before changing labels or posting review output. A stale result is discarded.

## Durable result labels

Only completed logical results are represented as PR labels:

- `gitkeepr:ready` — the last completed run reached Review `PASS`;
- `gitkeepr:needs-supervisor` — the last completed bounded run ended with unresolved work.

The labels are summaries, not independent source-of-truth for a later HEAD. Because pushes do not trigger GitKeepr, supervisors must pair a label with the HEAD-bound GitKeepr Review marker before acting on it.

Running/building/reviewing state belongs to GitHub Actions, not durable PR labels. Technical failures are Actions failures. `superseded` is recorded in the run only and does not mutate PR state.

The finalizer also removes legacy v0.1.x status labels when it publishes a current v0.2 result.

## Context and idempotence

Trusted human PR comments and trusted human/Copilot reviews are context. Their existence never starts work.

The exact `/gitkeepr run` command is excluded from agent discussion context. Successful command handling writes a deterministic hidden trigger marker so duplicate delivery does not repeat model work. Technical failures are retryable because they do not publish a successful trigger marker.
