#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_RAW="${GITKEEPR_RAW_BASE:-https://raw.githubusercontent.com/MatousekJakub/gitkeepr/main}"
INSTALL_DIR="${GITKEEPR_INSTALL_DIR:-$HOME/.local/bin}"
TARGET="$INSTALL_DIR/gitkeepr"

mkdir -p "$INSTALL_DIR"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

curl -fsSL "$UPSTREAM_RAW/bin/gitkeepr" -o "$tmp"
chmod +x "$tmp"
mv "$tmp" "$TARGET"
trap - EXIT

printf 'Installed GitKeepr to %s\n' "$TARGET"
case ":$PATH:" in
  *":$INSTALL_DIR:"*) ;;
  *) printf 'NOTE: %s is not in PATH. Add it before running gitkeepr.\n' "$INSTALL_DIR" ;;
esac
