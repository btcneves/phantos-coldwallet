#!/usr/bin/env bash
set -euo pipefail

ISO="${1:-}"
DEVICE="${2:-}"
CONFIRM_TEXT="CONFIRMO APAGAR ESTE DISPOSITIVO"

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute como root." >&2
  exit 2
fi

if [ -z "$ISO" ] || [ -z "$DEVICE" ]; then
  echo "Uso: PHANTOS_CONFIRM_WIPE=\"$CONFIRM_TEXT\" $0 caminho.iso /dev/sdX" >&2
  exit 2
fi

if [ "${PHANTOS_CONFIRM_WIPE:-}" != "$CONFIRM_TEXT" ]; then
  echo "Confirmação ausente. Exporte PHANTOS_CONFIRM_WIPE=\"$CONFIRM_TEXT\"." >&2
  exit 2
fi

if [ ! -f "$ISO" ] || [ ! -s "$ISO" ]; then
  echo "ISO inválida: $ISO" >&2
  exit 2
fi

if [ ! -b "$DEVICE" ]; then
  echo "Dispositivo não existe ou não é bloco: $DEVICE" >&2
  exit 2
fi

dev_type="$(lsblk -dn -o TYPE "$DEVICE" 2>/dev/null | tr -d ' ')"
if [ "$dev_type" != "disk" ]; then
  echo "Use o disco inteiro, não uma partição: $DEVICE (TYPE=$dev_type)" >&2
  exit 2
fi

base="$(basename "$DEVICE")"
case "$base" in
  nvme*|mmcblk0)
    echo "Recusando dispositivo potencialmente interno: $DEVICE" >&2
    exit 2
    ;;
esac

tran="$(lsblk -dn -o TRAN "$DEVICE" 2>/dev/null | tr -d ' ')"
rm_flag="$(lsblk -dn -o RM "$DEVICE" 2>/dev/null | tr -d ' ')"
if [ "$tran" != "usb" ] && [ "$rm_flag" != "1" ]; then
  echo "Recusando disco não removível/não USB: $DEVICE (TRAN=${tran:-unknown}, RM=${rm_flag:-unknown})" >&2
  exit 2
fi

echo "Dispositivos detectados:"
lsblk -o NAME,SIZE,MODEL,SERIAL,TRAN,TYPE,MOUNTPOINTS

mounts="$(lsblk -rn -o MOUNTPOINTS "$DEVICE" | sed '/^$/d' || true)"
if printf '%s\n' "$mounts" | grep -Eq '^/$|^/home$|^/boot$|^/boot/efi$'; then
  echo "Recusando dispositivo com ponto de montagem crítico." >&2
  exit 2
fi

while read -r part; do
  [ -n "$part" ] || continue
  umount "/dev/$part" 2>/dev/null || true
done < <(lsblk -ln -o NAME "$DEVICE" | tail -n +2)

iso_size="$(stat -c '%s' "$ISO")"
echo "Gravando $ISO em $DEVICE ($iso_size bytes)."
dd if="$ISO" of="$DEVICE" bs=4M status=progress conv=fsync
sync

iso_hash="$(sha256sum "$ISO" | awk '{print $1}')"

# SYS-15: verificar hash contra valor esperado, se fornecido
if [ -n "${PHANTOS_ISO_SHA256:-}" ]; then
  if [ "$iso_hash" != "${PHANTOS_ISO_SHA256,,}" ]; then
    echo "ERRO: SHA256 da ISO não confere!" >&2
    echo "  Esperado: ${PHANTOS_ISO_SHA256,,}" >&2
    echo "  Calculado: $iso_hash" >&2
    echo "A ISO pode estar corrompida ou adulterada. Interrompendo." >&2
    exit 1
  fi
  echo "SHA256 verificado: $iso_hash"
else
  echo "Aviso: PHANTOS_ISO_SHA256 não definido — hash não verificado contra valor esperado." >&2
  echo "SHA256 calculado: $iso_hash"
  echo "Compare manualmente com o hash publicado antes de usar."
fi

if ! cmp -n "$iso_size" "$ISO" "$DEVICE" >/dev/null; then
  echo "Falha de validação pós-gravação: bytes lidos diferem da ISO." >&2
  exit 1
fi

echo "Gravação concluída e validada."
echo "Reinicie o computador, selecione boot por USB e mantenha rede física desconectada."
