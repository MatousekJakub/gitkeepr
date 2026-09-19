# Releasing GitKeepr

GitKeepr releases are explicit promotions of tested `main` state. Release preparation is automated, but tagging and publishing remain deliberate human decisions.

## Prepare a release

Start from an up-to-date same-repository branch created from `main`, then run:

```bash
python3 scripts/prepare-release.py 0.1.1
```

The script validates the current version wiring before changing anything. It prepares the complete update set before writing and rolls back already-written files if a later write fails. It updates only the release-coupled files:

- `VERSION`;
- `bin/gitkeepr`;
- `install.sh`;
- `templates/gitkeepr.yml`;
- a new `docs/releases/vX.Y.Z.md` skeleton.

It does not stage, commit, push, tag, or publish anything.

Use `--dry-run` to validate and preview the update set without writing files:

```bash
python3 scripts/prepare-release.py --dry-run 0.1.1
```

Complete the generated release notes, run the normal test suite and shell syntax checks, inspect the diff, and open a normal GitKeepr self-development PR. The PR must reach Review `PASS` before merge.

## Publish after merge

After the release-preparation PR is merged, update the local `main` checkout and verify that it exactly matches the current remote `main`:

```bash
git switch main
git fetch origin main

if [[ -n "$(git status --porcelain)" ]]; then
  printf '%s\n' 'Refusing to release: the worktree is not clean.' >&2
  exit 1
fi

if [[ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]]; then
  printf '%s\n' 'Refusing to release: HEAD does not match origin/main.' >&2
  exit 1
fi
```

Only after those checks pass, read the version, record that exact commit, and publish it using the prepared files as release assets:

```bash
VERSION="$(cat VERSION)"
SHA="$(git rev-parse HEAD)"

gh release create "v$VERSION" \
  --repo MatousekJakub/gitkeepr \
  --target "$SHA" \
  --title "GitKeepr v$VERSION" \
  --notes-file "docs/releases/v$VERSION.md" \
  install.sh \
  bin/gitkeepr
```

Verify the published path:

```bash
gh release view "v$(cat VERSION)" --repo MatousekJakub/gitkeepr

curl -fsSL \
  https://github.com/MatousekJakub/gitkeepr/releases/latest/download/install.sh \
  | bash

gitkeepr version
```

## Upgrade a managed repository

Installing a newer release updates the CLI, not existing repository callers. In each managed private repository:

```bash
gitkeepr init
```

Review the caller diff and accept the replacement when appropriate. Commit the updated `.github/workflows/gitkeepr.yml` through the repository's normal PR process.

A healthy repository runner does not need to be re-registered solely because GitKeepr was upgraded. Run `gitkeepr doctor` and `gitkeepr server doctor` when validating the upgrade.

## Release invariants

- Published tags are immutable.
- Standard callers pin `pr-loop.yml` to the same release version as the CLI that generated them.
- The installer for a release downloads the matching CLI release asset.
- `main` may continue developing after a release without changing existing released installations.
- The release-preparation script never publishes on its own.
