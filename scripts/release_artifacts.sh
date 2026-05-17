#!/usr/bin/env bash
set -euo pipefail

ISO="${1:-}"
OUT_DIR="${PHANTOS_RELEASE_DIR:-build/release}"
STATUS_FILE="$OUT_DIR/RELEASE_VALIDATION.md"

if [ -z "$ISO" ]; then
  echo "Uso: $0 caminho/phantos.iso" >&2
  exit 2
fi

if [ ! -f "$ISO" ] || [ ! -s "$ISO" ]; then
  echo "ISO inválida: $ISO" >&2
  exit 2
fi

mkdir -p "$OUT_DIR"
ISO_NAME="$(basename "$ISO")"
cp "$ISO" "$OUT_DIR/$ISO_NAME"

(
  cd "$OUT_DIR"
  sha256sum "$ISO_NAME" > SHA256SUMS
  sha512sum "$ISO_NAME" > SHA512SUMS
  sha256sum -c SHA256SUMS
  sha512sum -c SHA512SUMS
)

GPG_STATUS="SKIPPED"
if command -v gpg >/dev/null 2>&1 && gpg --list-secret-keys --with-colons 2>/dev/null | grep -q '^sec'; then
  (cd "$OUT_DIR" && gpg --batch --yes --armor --detach-sign SHA256SUMS)
  GPG_STATUS="PASS"
fi

MINISIGN_STATUS="SKIPPED"
if command -v minisign >/dev/null 2>&1 && [ -n "${MINISIGN_KEY:-}" ]; then
  (cd "$OUT_DIR" && minisign -Sm SHA256SUMS -s "$MINISIGN_KEY")
  MINISIGN_STATUS="PASS"
fi

SBOM_STATUS="SKIPPED"
if command -v cyclonedx-py >/dev/null 2>&1; then
  cyclonedx-py environment --output-format JSON --output-file "$OUT_DIR/sbom.cdx.json"
  SBOM_STATUS="PASS"
fi

cat > "$STATUS_FILE" <<EOF
# Release Validation

| Check | Status | Evidence |
| --- | --- | --- |
| ISO copied | PASS | \`$OUT_DIR/$ISO_NAME\` |
| SHA256SUMS | PASS | \`$OUT_DIR/SHA256SUMS\` |
| SHA512SUMS | PASS | \`$OUT_DIR/SHA512SUMS\` |
| GPG signature | $GPG_STATUS | \`$OUT_DIR/SHA256SUMS.asc\` when present |
| minisign signature | $MINISIGN_STATUS | \`$OUT_DIR/SHA256SUMS.minisig\` when present |
| SBOM | $SBOM_STATUS | \`$OUT_DIR/sbom.cdx.json\` when present |

This script prepares local release artifacts only. It does not publish releases or tags.
EOF

cat "$STATUS_FILE"
