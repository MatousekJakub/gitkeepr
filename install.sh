#!/usr/bin/env bash
set -euo pipefail

VERSION="${GITKEEPR_VERSION:-0.1.1}"
TAG="${GITKEEPR_TAG:-v${VERSION}}"
RELEASE_BASE="${GITKEEPR_RELEASE_BASE:-https://github.com/MatousekJakub/gitkeepr/releases/download/${TAG}}"
INSTALL_DIR="${GITKEEPR_INSTALL_DIR:-$HOME/.local/bin}"
TARGET="$INSTALL_DIR/gitkeepr"

mkdir -p "$INSTALL_DIR"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

curl -fsSL "$RELEASE_BASE/gitkeepr" -o "$tmp"
chmod +x "$tmp"

downloaded_version="$("$tmp" version)"
[[ "$downloaded_version" == "$VERSION" ]] || {
  printf 'ERROR: downloaded GitKeepr reports version %s, expected %s.\n' "$downloaded_version" "$VERSION" >&2
  exit 1
}

mv "$tmp" "$TARGET"
trap - EXIT

printf 'Installed GitKeepr %s to %s\n' "$VERSION" "$TARGET"
case ":$PATH:" in
  *":$INSTALL_DIR:"*) ;;
  *) printf 'NOTE: %s is not in PATH. Add it before running gitkeepr.\n' "$INSTALL_DIR" ;;
esac
