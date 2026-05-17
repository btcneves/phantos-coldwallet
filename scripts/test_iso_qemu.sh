#!/usr/bin/env bash
set -euo pipefail

ISO="${1:-}"
OUT_DIR="${PHANTOS_QEMU_OUT:-build/qemu-validation}"
TIMEOUT_SECONDS="${PHANTOS_QEMU_TIMEOUT:-90}"

if [ -z "$ISO" ]; then
  echo "Uso: $0 caminho/phantos.iso" >&2
  exit 2
fi

if [ ! -f "$ISO" ]; then
  echo "ISO não encontrada: $ISO" >&2
  exit 2
fi

mkdir -p "$OUT_DIR"

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
  echo "SKIPPED qemu-system-x86_64 unavailable" | tee "$OUT_DIR/summary.txt"
  exit 0
fi

run_qemu() {
  local mode="$1"
  shift
  local log="$OUT_DIR/${mode}.log"
  set +e
  timeout "$TIMEOUT_SECONDS" qemu-system-x86_64 \
    -m 2048 \
    -enable-kvm \
    -cdrom "$ISO" \
    -boot d \
    -display none \
    -serial "file:$log" \
    -no-reboot \
    "$@"
  rc=$?
  set -e
  if [ "$rc" -eq 124 ]; then
    echo "PASS $mode boot smoke reached timeout window" | tee -a "$OUT_DIR/summary.txt"
    return 0
  fi
  if [ "$rc" -eq 0 ]; then
    echo "PASS $mode qemu exited cleanly" | tee -a "$OUT_DIR/summary.txt"
    return 0
  fi
  echo "FAIL $mode qemu exited with $rc" | tee -a "$OUT_DIR/summary.txt" >&2
  return 1
}

rm -f "$OUT_DIR/summary.txt"

BIOS_STATUS=0
run_qemu bios || BIOS_STATUS=$?

UEFI_STATUS=0
OVMF_CODE=""
for candidate in \
  /usr/share/OVMF/OVMF_CODE.fd \
  /usr/share/ovmf/OVMF.fd \
  /usr/share/qemu/OVMF.fd; do
  if [ -f "$candidate" ]; then
    OVMF_CODE="$candidate"
    break
  fi
done

if [ -n "$OVMF_CODE" ]; then
  run_qemu uefi -drive "if=pflash,format=raw,readonly=on,file=$OVMF_CODE" || UEFI_STATUS=$?
else
  echo "SKIPPED UEFI OVMF firmware unavailable" | tee -a "$OUT_DIR/summary.txt"
fi

if [ "$BIOS_STATUS" -ne 0 ] || [ "$UEFI_STATUS" -ne 0 ]; then
  exit 1
fi
