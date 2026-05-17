#!/usr/bin/env bash
# Aplica patches de segurança ao embit v0.8.0.
# Funciona tanto no .venv local quanto em ambientes CI (Python do sistema).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PATCH_FILE="$PROJECT_ROOT/patches/embit-0.8.0-phantos-security.patch"

if [ ! -f "$PATCH_FILE" ]; then
  echo "Patch não encontrado: $PATCH_FILE" >&2
  exit 1
fi

# Detecta onde o embit está instalado (venv local ou Python do sistema)
SITE_PACKAGES=$(python3 -c "
import sysconfig, os
p = sysconfig.get_path('purelib')
if os.path.isdir(p):
    print(p)
else:
    import site
    print(site.getsitepackages()[0])
" 2>/dev/null || true)

if [ -z "$SITE_PACKAGES" ] || [ ! -d "$SITE_PACKAGES/embit" ]; then
  SITE_PACKAGES=$(python3 -c "import embit, os; print(os.path.dirname(os.path.dirname(embit.__file__)))" 2>/dev/null || true)
fi

if [ -z "$SITE_PACKAGES" ] || [ ! -d "$SITE_PACKAGES/embit" ]; then
  echo "embit não encontrado. Execute: pip install embit==0.8.0" >&2
  exit 1
fi

embit_version=$(python3 -c "import importlib.metadata; print(importlib.metadata.version('embit'))" 2>/dev/null || echo "desconhecida")
if [ "$embit_version" != "0.8.0" ]; then
  echo "Aviso: versão do embit instalada é '$embit_version', patch foi gerado para 0.8.0." >&2
  echo "Continuando — verifique os testes após aplicação." >&2
fi

echo "Aplicando $PATCH_FILE em $SITE_PACKAGES ..."

if patch \
  --directory="$SITE_PACKAGES" \
  --strip=5 \
  --forward \
  --reject-file=/tmp/embit_patch_rejects.txt \
  < "$PATCH_FILE"; then
  echo "Patch aplicado com sucesso."
else
  echo "Erros ao aplicar patch. Verifique /tmp/embit_patch_rejects.txt" >&2
  exit 1
fi

echo ""
echo "Executando testes para verificar integridade..."
python3 -m pytest "$PROJECT_ROOT/tests/" -q --tb=short
