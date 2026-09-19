# Architecture

> Human-owned source of truth. Preserve the approved architecture unless a human explicitly changes it.

## Components

### Target repository

For a standard private target repository, `gitkeepr init` creates exactly one versioned file:

- `.github/workflows/gitkeepr.yml`

It also configures repository variables. It does not create `.ai/plan.md`, `AGENTS.md`, a `.gitkeepr/` directory, or any other project files.

The public upstream GitKeepr repository is a narrow self-development exception: `gitkeepr init` configures variables but creates no standard caller, because `.github/workflows/self-gate.yml` and `.github/workflows/pr-loop.yml` already define its gated execution path.

The target caller listens to:

- `pull_request`: `opened`, `synchronize`;
- `pull_request_review`: `submitted`;
- `issue_comment`: `created`;
- `workflow_dispatch`.

The caller is a cheap first trust/filter layer and invokes the reusable core at:

`MatousekJakub/gitkeepr/.github/workflows/pr-loop.yml@v0.1.0`

The core repeats authoritative security checks before checkout or OpenCode execution. Standard target callers are release-pinned; upgrading the CLI and rerunning `gitkeepr init` is the explicit path to a newer core version.

### Reusable core

`.github/workflows/pr-loop.yml` is intentionally allowed to remain a large, monolithic workflow. Do not modularize it merely for style.

Its minimal trigger contract is:

- `pr_number`;
- `trigger_kind`;
- `trigger_source_id`.

The core loads the actual PR/comment/review context through GitHub APIs.

### GitHub App

Required repository permissions:

- Contents: read/write;
- Issues: read/write;
- Pull requests: read/write;
- Workflows: read/write;
- Metadata: implicit read.

Installation policy: **Only selected repositories**.

The App is created manually. GitKeepr does not automate App creation or installation in V1.

The App identity must never be hardcoded. The workflow derives the bot identity from the created App token.

### Persistent runner

V1 supports Ubuntu/Debian Linux with systemd on amd64 or arm64.

One Linux user, `github-runner`, owns OpenCode auth and runs all Actions runner services. One repository-level Actions runner installation exists per managed repository. All use the custom label `gitkeepr`; workflows do not route on ARM64/X64.

There is no global concurrency lock in V1. If real contention appears, solve the observed problem later.

### OpenCode

OpenCode is installed for `github-runner`. `gitkeepr server init` always opens `opencode auth login`, then prints `opencode models` and stops. GitKeepr does not try to infer whether a specific provider is authenticated because OpenCode may also expose free models.

## Build / Review loop

Build:

- reads the current repository and `.ai/plan.md` if present;
- reads current trusted trigger feedback and trusted PR discussion;
- verifies stale review findings against current HEAD;
- implements only the first unfinished logical planned task unless the latest trusted instruction changes scope;
- runs relevant tests;
- never owns Git metadata or GitHub metadata.

Workflow:

- detects Build file changes;
- commits and pushes them using the GitHub App identity;
- runs Review.

Review:

- does not edit files;
- independently checks the full current PR scope;
- returns `CONTINUE` when correctness/testing problems remain or planned work remains;
- returns `PASS` only when the full current scope is complete and no still-relevant blocking feedback remains.

No-progress protection stops the loop when Review says `CONTINUE` but no repository progress was made.

## Status labels

- `gitkeepr:building`
- `gitkeepr:reviewing`
- `gitkeepr:waiting-human`
- `gitkeepr:blocked`

The core creates them when needed.

## Idempotence

Triggers get deterministic keys. A successful handling writes a hidden processed marker. A blocked or failed run must **not** mark the source trigger as successfully processed.

System comments and hidden markers are part of the protocol, not security credentials.

## `no-build`

A trusted top-level comment containing:

`<!-- gitkeepr:no-build -->`

must not start a new Build loop. The comment still remains part of trusted PR discussion context for later runs.
