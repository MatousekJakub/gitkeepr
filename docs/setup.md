# Setup Contract

This document describes the intended V1 user experience. Exact commands may evolve while the bootstrap implementation is being completed.

## 1. Install the CLI

The intended distribution flow is:

```bash
curl -fsSL https://raw.githubusercontent.com/<owner>/gitkeepr/main/install.sh | bash
```

`install.sh` only installs/updates `gitkeepr` in `~/.local/bin` and prints a PATH hint when necessary.

## 2. Prepare the VPS once

```bash
gitkeepr server init
```

Server init should:

- verify Ubuntu/Debian + systemd + supported architecture;
- install basic apt prerequisites;
- create `github-runner` when missing;
- ensure the admin user's `gh` is authenticated (interactive `gh auth login` when needed);
- install OpenCode for `github-runner` when missing;
- run interactive `opencode auth login` as `github-runner`;
- print `opencode models`;
- download/cache the current stable GitHub Actions runner package;
- ask for GitHub App Client ID and private-key path;
- store those values in `/etc/gitkeepr/config` with restrictive permissions.

GitHub App creation remains a documented manual step.

## 3. Create/install the GitHub App

Create a GitHub App with repository permissions:

- Contents RW
- Issues RW
- Pull requests RW
- Workflows RW

Install it using **Only selected repositories** and add each managed repository before running `gitkeepr init`.

## 4. Initialize a private project

Inside the project checkout:

```bash
gitkeepr init
```

The command should:

- require `git`, `gh`, and authenticated `gh`;
- detect the repository from the current checkout;
- reject standard V1 initialization for public repositories;
- require explicit confirmation that the GitHub App has already been added;
- load existing model/max-cycle variables when present;
- interactively configure the five `GITKEEPR_*` model/loop variables;
- fetch the current caller template from GitKeepr `main`;
- create only `.github/workflows/gitkeepr.yml`;
- never commit or stage;
- print `git status --short` and the exact VPS `runner add owner/repo` command.

If the workflow already exists and differs, show a diff and ask before replacement.

## 5. Add the per-repository runner

On the VPS:

```bash
gitkeepr runner add owner/repo
```

Normal operation must acquire GitHub registration/remove tokens automatically, configure a repository-level runner, install/start the systemd service, synchronize App credentials, and verify health.

The target workflow does not have to be pushed before `runner add`; if it is not yet visible on the default branch, print a warning instead of failing.

## Diagnostics

Project side:

```bash
gitkeepr doctor
```

Server side:

```bash
gitkeepr server doctor
```

Doctors diagnose and recommend commands; they do not silently auto-repair.
