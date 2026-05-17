#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

ERRORS=0

tracked_files() {
  git ls-files -z \
    ':!*.png' ':!*.gif' ':!*.jpg' ':!*.ico' ':!*.pdf' ':!*.whl' \
    ':!app/ur/vendor/' \
    ':!requirements.lock'
}

report_error() {
  echo "ERRO: $1" >&2
  ERRORS=$((ERRORS + 1))
}

check_content() {
  local label="$1"
  local pattern="$2"
  local hits
  hits="$(tracked_files | xargs -0 rg -n -i "$pattern" 2>/dev/null || true)"
  if [ "$label" = "blocked-tooling-07" ]; then
    bip39_word="ag""ent"
    hits="$(printf '%s\n' "$hits" | rg -v "^app/ui/bip39_input\\.py:[0-9]+:[[:space:]]*\"${bip39_word}\",?$" || true)"
  fi
  if [ -n "$hits" ]; then
    report_error "termo bloqueado encontrado ($label):"
    printf '%s\n' "$hits" >&2
  fi
}

check_path() {
  local label="$1"
  local pattern="$2"
  local hits
  hits="$(git ls-files -co --exclude-standard | rg -n -i "$pattern" 2>/dev/null || true)"
  if [ -n "$hits" ]; then
    report_error "caminho bloqueado encontrado ($label):"
    printf '%s\n' "$hits" >&2
  fi
}

check_local_path() {
  local label="$1"
  shift
  local found=()
  for path in "$@"; do
    # Only flag if the path would actually be committed (not gitignored).
    if [ -e "$path" ] && git ls-files --error-unmatch "$path" >/dev/null 2>&1; then
      found+=("$path")
    fi
  done
  if [ "${#found[@]}" -gt 0 ]; then
    report_error "artefato local privado encontrado ($label):"
    printf '  %s\n' "${found[@]}" >&2
  fi
}

check_content "blocked-tooling-01" '\b[c]laude\b'
check_content "blocked-tooling-02" '\b[c]odex\b'
check_content "blocked-tooling-03" '\b[c]hatgpt\b'
check_content "blocked-tooling-04" '\b[o]penai\b'
check_content "blocked-tooling-05" '\b[I]A\b'
check_content "blocked-tooling-06" '\ba[i][ -]?generated\b|[g]enerated[[:space:]]+by[[:space:]]+a[i]|[g]enerated[[:space:]]+with[[:space:]]+a[i]'
check_content "blocked-tooling-07" '\b[a]gents?\b|\b[a]gentes?\b'
check_content "blocked-tooling-08" '\b[p]rompts?\b'
check_content "blocked-tooling-09" '\b[s]cratchpad\b'
check_content "blocked-tooling-10" '[c]o-authored-by'
check_content "blocked-tooling-11" '[g]enerated[[:space:]]+by|[g]enerated[[:space:]]+with'
check_content "blocked-tooling-12" '[p]lano interno|[r]acioc[ií]nio interno|[f]erramentas internas|[i]nstru[cç][oõ]es privadas'

check_content "wallet-secret-01" '\b[xytz]prv[A-Za-z0-9]{80,}\b'
check_content "wallet-secret-02" 'BEGIN (RSA|OPENSSH|EC|DSA|PGP)? ?PRIVATE KEY'
# SYS-16: padrão inclui WIF mainnet (L/K/5) e WIF testnet comprimido (c-prefix, 52 chars base58)
check_content "wallet-secret-03" '\b(W[I]F|L[1-9A-HJ-NP-Za-km-z]{50,51}|K[1-9A-HJ-NP-Za-km-z]{50,51}|5[HJK][1-9A-HJ-NP-Za-km-z]{49}|c[1-9A-HJ-NP-Za-km-z]{51})\b'
check_content "credential-01" '\b(ghp|github_pat|glpat|xox[baprs]|sk_live|sk_test)_[A-Za-z0-9_=-]{20,}\b'

check_path "env-or-secret-file" '(^|/)\.env($|[./])|(^|/)(secrets?|credentials?|tokens?)(\.|/|$)'
check_path "private-key-file" '\.(pem|key|p12|pfx|kdbx)$'
check_path "dump-or-log-file" '\.(dump|core|log)$'

blocked_c="c"
check_local_path "private-local-config" \
  ".${blocked_c}laude" \
  ".env" \
  ".env.local" \
  "settings.local.json"

echo ""
echo "Verificação pública concluída."

if [ "$ERRORS" -gt 0 ]; then
  echo "FALHOU: $ERRORS violação(ões) encontradas." >&2
  exit 1
fi

echo "OK: nenhum termo, segredo ou caminho bloqueado encontrado."
