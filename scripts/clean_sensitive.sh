#!/usr/bin/env bash
set -euo pipefail

rm -rf /tmp/phantos-* 2>/dev/null || true
rm -rf "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/phantos" 2>/dev/null || true
sync
echo "Arquivos temporarios conhecidos removidos."

