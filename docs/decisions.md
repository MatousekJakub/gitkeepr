# Approved Decisions

> Human-owned source of truth. These are deliberate product decisions, not suggestions. Automation must not reverse them without an explicit human instruction.

## Repository and distribution

- GitKeepr starts from a clean orphan `main`; legacy GitKeepr code/history is not part of the new project.
- The project is MIT licensed.
- Public documentation, CLI output, prompts, generated system text, and repository content are English.
- GitKeepr is intended to be public from the start.
- Standard target-repository V1 support is private/trusted repositories only.
- Published distribution is release-based. Standard target callers pin the reusable core to the same release tag as the CLI that generated them rather than `@main`.
- `VERSION` is the repository source of truth for release preparation. `scripts/prepare-release.py` synchronizes release-coupled files and creates release notes, but never commits, tags, or publishes.
- v0.2 changes behavior before structure. Do not modularize the reusable core merely for style, but later extraction of deterministic orchestration from YAML/Bash is allowed when it improves testability or harness interchangeability.

## CLI UX

- Distribution is a small shell CLI plus `install.sh`, not npm or a package manager.
- The public install command downloads `install.sh` from the latest GitHub Release; that installer downloads the matching versioned `gitkeepr` release asset.
- `install.sh` only installs/updates the CLI; it does not initialize projects or servers.
- `gitkeepr init` operates on the current local Git repository.
- `gitkeepr init` never commits, pushes, stages, stashes, or resets.
- A dirty working tree is allowed.
- For standard private target repositories, the only versioned project file created by `init` is `.github/workflows/gitkeepr.yml`.
- The public upstream GitKeepr self-development exception configures variables but does not create the standard caller; it uses the committed `self-gate.yml` + `pr-loop.yml` path.
- The caller template is downloaded from the installed CLI's own release tag on every `init`; release upgrades are therefore explicit.
- If the target workflow exists and differs, show the diff and ask `Replace? [y/N]`.
- Local missing `git`, `gh`, or `gh` authentication produces an error plus instructions; local init does not auto-install/login.
- `init` asks the user to confirm that the GitHub App was already added to the target repository. If not, stop with instructions.
- `init` does not technically verify App installation because App credentials live only on the server.

## Repository configuration

Variables configured by `gitkeepr init`:

- `GITKEEPR_BUILD_MODEL`
- `GITKEEPR_BUILD_VARIANT`
- `GITKEEPR_REVIEW_MODEL`
- `GITKEEPR_REVIEW_VARIANT`
- `GITKEEPR_FINALIZATION_CYCLES`

Suggested defaults when no value exists:

- Build model: `openai/gpt-5.6-luna`
- Build variant: `high`
- Review model: `openai/gpt-5.6-sol`
- Review variant: `high`
- Finalization cycles: `2`

Existing variable values become defaults on repeated `init`; Enter preserves them.

The UI should mention that available models can be checked on the VPS with:

`sudo -iu github-runner opencode models`

No remote model discovery is required in V1.

## Server setup

- `gitkeepr server init` supports Ubuntu/Debian + systemd on amd64/arm64.
- It automatically installs basic apt prerequisites such as `curl`, `git`, `jq`, `tar`, `ca-certificates`, and `gh`.
- It creates `github-runner` if missing.
- Administrative `gitkeepr server/runner` commands run as the normal sudo-capable admin user.
- Actions and OpenCode run as `github-runner`; that user does not need general sudo access.
- `gh auth login` belongs to the admin user and is required for runner lifecycle/API operations.
- `opencode auth login` runs as `github-runner` every time `server init` runs.
- After auth, print `opencode models`; do not make a test inference.
- If OpenCode is missing, install current stable. If it already exists, print the version and do not auto-upgrade it.
- Store server-wide configuration in root-owned `/etc/gitkeepr/config`.
- Server config stores the GitHub App Client ID and the path to the private key, not the key contents.
- Client ID and private key path are entered once during `server init`.
- `server init` is safe to repeat and must not disturb existing repository runners.

## Runner lifecycle

- Actions runner package download/cache is server-wide; the binary archive is not conceptually per repository.
- `runner add owner/repo` is as automated as practical.
- It gets fresh GitHub registration tokens programmatically through authenticated `gh`/GitHub API; users do not copy the token from the UI during normal operation.
- Each repository gets its own runner directory/service, using the `gitkeepr` label.
- Before registration, verify that project variables exist and GitHub App access works.
- `runner add` synchronizes `GITKEEPR_APP_CLIENT_ID` and `GITKEEPR_APP_PRIVATE_KEY` into the target repository.
- Re-running `runner add` on a healthy runner is safe and may resync server-side App credentials.
- If an existing runner is unhealthy, offer reconfiguration; on approval automate remove-token → removal → registration-token → configure → service start → health check.
- `runner remove owner/repo` removes only the runner/service/directory. It does not remove project variables, secrets, or workflow files.
- There is no project `uninstall` command in V1.
- Documentation should include GitHub Settings → Actions → Runners → New self-hosted runner as a manual fallback/troubleshooting path.

## Trigger policy

GitKeepr v0.2 is explicit-only.

The supported activation paths are:

- an exact trusted top-level PR comment: `/gitkeepr run`;
- manual `workflow_dispatch`.

PR creation, PR synchronize/push events, submitted reviews, and ordinary comments do not start Build/Review work. They remain normal GitHub activity and may become context for a later explicit run.

The command must come from a trusted human repository relationship (OWNER/MEMBER/COLLABORATOR). Bot comments are not generic activation commands.

The v0.2 core may temporarily recognize v0.1 automatic trigger kinds only as no-ops so the first breaking self-development PR can be opened and synchronized while the v0.1 default-branch gate is still active.

## Supervisor model

GitKeepr is a bounded finalization worker, not the main orchestrator.

- ChatGPT/user normally performs planning and most initial implementation.
- GitHub PR/branch is the durable shared source of truth.
- Build/Review are used for real-environment work such as shell/tests/runtime/browser/MCP validation and independent review.
- Default finalization budget is two Build -> Review cycles.
- Review `PASS` produces `gitkeepr:ready`.
- Exhausted bounded work with unresolved findings produces `gitkeepr:needs-supervisor` and is not an infrastructure failure.
- Technical failures are represented by the Actions run, not a persistent failure label.
- A changed external PR HEAD supersedes the current worker run. GitKeepr must never rebase/merge/overwrite the newer branch automatically.
- ChatGPT Scheduled Tasks or a human may actively supervise, fix, restart, and finish the PR outside GitKeepr.

The v0.1 external-helper, `gitkeepr:no-build`, direct-reply, and ambient-comment-trigger protocols are retired in v0.2.

## GitKeepr development workflow

After the `v0.1.0` release, normal GitKeepr development uses GitKeepr's own public self-development path.

- Changes are prepared on same-repository branches and opened as pull requests; direct pushes to `main` are not the normal development path.
- The assistant normally prepares the branch changes and opens the pull request. Human review/merge and release decisions remain explicit.
- Each same-repository PR must pass through the GitHub-hosted `self-gate.yml` before the candidate `pr-loop.yml` may run on the persistent self-hosted runner.
- GitKeepr Build/Review may correct blocking findings on the PR branch before returning `PASS`.
- Published release tags remain immutable. Development on `main` does not change repositories pinned to an existing release.
- A direct `main` repair is reserved for an exceptional recovery case where the self-development path itself is broken and cannot be used to restore service.

The earlier scheduled direct-to-`main` bootstrap process is historical only; see `docs/automation/continuous-development.md`.
