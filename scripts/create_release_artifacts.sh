#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Uso: $0 <arquivo-ou-diretorio> [mais arquivos...]" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="$REPO_ROOT/dist/release"

mkdir -p "$OUT_DIR"

FILES=()
for item in "$@"; do
  if [ -f "$item" ]; then
    FILES+=("$(realpath "$item")")
  elif [ -d "$item" ]; then
    while IFS= read -r -d '' file; do
      FILES+=("$(realpath "$file")")
    done < <(find "$item" -maxdepth 1 -type f -print0 | sort -z)
  else
    echo "AVISO: ignorando caminho inexistente: $item" >&2
  fi
done

if [ "${#FILES[@]}" -eq 0 ]; then
  echo "Nenhum arquivo válido encontrado." >&2
  exit 1
fi

(
  cd "$OUT_DIR"
  : > SHA256SUMS
  : > SHA512SUMS
)

for file in "${FILES[@]}"; do
  name="$(basename "$file")"
  cp -f "$file" "$OUT_DIR/$name"
done

(
  cd "$OUT_DIR"
  sha256sum -- * | grep -v -E 'SHA(256|512)SUMS|\\.asc$|\\.minisig$' > SHA256SUMS
  sha512sum -- * | grep -v -E 'SHA(256|512)SUMS|\\.asc$|\\.minisig$' > SHA512SUMS
)

if command -v gpg >/dev/null 2>&1; then
  gpg --armor --detach-sign --yes "$OUT_DIR/SHA256SUMS" || {
    echo "AVISO: assinatura GPG não criada." >&2
  }
fi

if command -v minisign >/dev/null 2>&1; then
  minisign -Sm "$OUT_DIR/SHA256SUMS" || {
    echo "AVISO: assinatura minisign não criada." >&2
  }
fi

if command -v cyclonedx-py >/dev/null 2>&1; then
  cyclonedx-py requirements "$REPO_ROOT/requirements.lock" \
    --output-format JSON \
    --output-file "$OUT_DIR/sbom.cdx.json" || {
      echo "AVISO: SBOM CycloneDX não criado." >&2
    }
fi

echo "Artefatos preparados em: $OUT_DIR"
