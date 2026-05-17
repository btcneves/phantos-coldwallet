#!/usr/bin/env bash
set -euo pipefail

echo "Interfaces de rede:"
ip link show || true

echo
echo "Regras nftables:"
nft list ruleset || true

echo
echo "Servicos de rede conhecidos:"
systemctl --no-pager --type=service --state=running \
  | grep -Ei 'network|wpa|bluetooth|ssh|avahi|cups|tor|browser' || true

echo
echo "Teste de saida TCP para 1.1.1.1:443 (deve falhar):"
timeout 3 bash -c '</dev/tcp/1.1.1.1/443' && {
  echo "ALERTA: conexao externa funcionou." >&2
  exit 2
} || echo "OK: conexao externa indisponivel."

