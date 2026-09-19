# Approved Decisions

> Human-owned source of truth. These are deliberate product decisions, not suggestions. Automation must not reverse them without an explicit human instruction.

## Repository and distribution

- GitKeepr starts from a clean orphan `main`; legacy GitKeepr code/history is not part of the new project.
- The project is MIT licensed.
- Public documentation, CLI output, prompts, generated system text, and repository content are English.
- GitKeepr is intended to be public from the start.
- Standard target-repository V1 support is private/trusted repositories only.
- Published V1 distribution is release-based. The current stable release is `v0.1.0`, and standard target callers pin the reusable core to that release tag rather than `@main`.
- The reusable core may remain monolithic indefinitely if that stays practical.

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
- `GITKEEPR_MAX_CYCLES`

Suggested defaults when no value exists:

- Build model: `openai/gpt-5.6-luna`
- Build variant: `high`
- Review model: `openai/gpt-5.6-sol`
- Review variant: `high`
- Max cycles: `15`

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

Keep the tested trigger set:

- PR opened;
- PR synchronize;
- submitted review;
- trusted top-level PR comment;
- manual workflow dispatch.

Bot-created `synchronize` events do not auto-trigger. A trusted human comment can explicitly trigger work afterward.

Trusted comment/review filtering remains conservative. No polling, schedules, labels-as-triggers, or command parser is part of the core loop.

## External helpers

External helpers are optional supplements, not part of GitKeepr core. In the intended V1 model they act through the user's GitHub identity, as if the user posted the interaction.

`<!-- gitkeepr:no-build -->` is used only when a helper is intentionally leaving information/PASS and no further Build action is required.

External-review marker format:

`<!-- gitkeepr-external-review:v1 source=<source> head=<sha> -->`

The marker is audit/deduplication metadata for helpers; it is not a security credential.

## Continuous bootstrap development

During the temporary bootstrap phase, scheduled ChatGPT development may commit directly to `main`. This is intentionally simpler than introducing a long-lived automation PR. It does not change the product rule that target repositories use PR-based Build/Review loops.
