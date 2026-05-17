#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute como root dentro da ISO/sistema live." >&2
  exit 1
fi

systemctl disable --now NetworkManager.service 2>/dev/null || true
systemctl disable --now wpa_supplicant.service 2>/dev/null || true
systemctl disable --now bluetooth.service 2>/dev/null || true
rfkill block wifi 2>/dev/null || true
rfkill block bluetooth 2>/dev/null || true

nft flush ruleset
nft add table inet phantos
nft add chain inet phantos input '{ type filter hook input priority 0 ; policy drop ; }'
nft add chain inet phantos forward '{ type filter hook forward priority 0 ; policy drop ; }'
nft add chain inet phantos output '{ type filter hook output priority 0 ; policy drop ; }'
nft add rule inet phantos input iif lo accept
nft add rule inet phantos output oif lo accept

# Bring all non-loopback interfaces down so the OS detector confirms no active interface.
for iface in /sys/class/net/*; do
  name="$(basename "$iface")"
  [ "$name" = "lo" ] && continue
  ip link set "$name" down 2>/dev/null || true
done

# Prevent USB network adapters (tethering, USB-Ethernet) plugged in after hardening
# from creating new active interfaces. nftables drop-all mitigates but blacklisting
# the kernel modules eliminates the vector entirely.
cat >> /etc/modprobe.d/phantos-network.conf <<'MODPROBE'
blacklist cdc_ether
blacklist rndis_host
blacklist cdc_ncm
blacklist cdc_mbim
blacklist ipheth
MODPROBE

echo "Rede bloqueada: Wi-Fi, Bluetooth, USB-net, entrada, saida e encaminhamento."

