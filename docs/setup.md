# Setup

## 1. Install the CLI

```bash
curl -fsSL https://raw.githubusercontent.com/MatousekJakub/gitkeepr/main/install.sh | bash
```

`install.sh` only installs/updates `gitkeepr` in `~/.local/bin` and prints a PATH hint when necessary.

## 2. Prepare the VPS once

```bash
gitkeepr server init
```

Server init verifies Ubuntu/Debian + systemd + supported architecture, installs prerequisites, creates `github-runner` if needed, ensures the admin `gh` login, installs OpenCode if missing, always runs `opencode auth login` as `github-runner`, displays `opencode models`, caches the stable Actions runner package, and writes the GitHub App Client ID plus PEM path to root-owned `/etc/gitkeepr/config` mode 0600. Existing repository runners are not modified.

## 3. Create/install the GitHub App

Create the App manually with repository permissions:

- Contents: Read and write
- Issues: Read and write
- Pull requests: Read and write
- Workflows: Read and write
- Metadata: Read (implicit)

Install it using **Only selected repositories**. Add each managed repository before initialization.

## 4. Initialize a project

### Standard private target repository

Inside its checkout:

```bash
gitkeepr init
```

Standard V1 target repositories are private and trusted. Init asks you to confirm App installation, configures the five model/loop variables, and downloads the current caller template. The only versioned file it creates/replaces is `.github/workflows/gitkeepr.yml`; it never stages, commits, pushes, stashes, or resets.

Commit/push the caller yourself after inspection.

### GitKeepr public self-development

The public upstream GitKeepr repository is a narrow V1 exception. Running `gitkeepr init` inside `MatousekJakub/gitkeepr` configures the same model/loop variables but does **not** create `.github/workflows/gitkeepr.yml`.

Self-development uses the existing:

- `.github/workflows/self-gate.yml` on a GitHub-hosted runner;
- `.github/workflows/pr-loop.yml` on the persistent runner only after the gate proves the PR is same-repository.

Other public target repositories remain unsupported by the standard V1 persistent-runner setup.

## 5. Add the repository runner

On the VPS:

```bash
gitkeepr runner add owner/repo
```

The command verifies project variables and App access, synchronizes App credentials, acquires a fresh registration token, installs one repository-level runner with label `gitkeepr`, starts its systemd service, and waits for GitHub to report it online.

A healthy repeated `runner add` does not reconfigure the runner and resynchronizes credentials. An unhealthy/incomplete runner asks before automated reconfiguration.

Remove only runner/service/directory with:

```bash
gitkeepr runner remove owner/repo
```

Repository variables, secrets, and workflow files are deliberately retained.

## Diagnostics

```bash
gitkeepr doctor
gitkeepr server doctor
```

Doctors are diagnostic and recommend action rather than silently repairing state. GitHub Settings → Actions → Runners → New self-hosted runner remains the manual troubleshooting fallback.
