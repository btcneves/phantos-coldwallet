#!/usr/bin/env bash
set -euo pipefail

ISO="${1:-}"
MIN_BYTES="${PHANTOS_MIN_ISO_BYTES:-200000000}"
FAIL=0
TMP_DIR=""

pass() { printf 'PASS %s\n' "$1"; }
fail() {
  printf 'FAIL %s\n' "$1" >&2
  FAIL=$((FAIL + 1))
}
skip() { printf 'SKIPPED %s\n' "$1"; }

cleanup() {
  if [ -n "$TMP_DIR" ]; then
    rm -rf "$TMP_DIR"
  fi
}
trap cleanup EXIT

iso_has_path() {
  local path="$1"
  xorriso -indev "$ISO" -find "$path" -maxdepth 0 -exec echo -- 2>/dev/null \
    | sed "s/^'//;s/'$//" \
    | grep -qx "$path"
}

if [ -z "$ISO" ]; then
  echo "Uso: $0 caminho/phantos.iso" >&2
  exit 2
fi

if [ -f "$ISO" ]; then
  pass "ISO exists"
else
  fail "ISO missing"
fi

if [ -s "$ISO" ]; then
  pass "ISO is not empty"
else
  fail "ISO empty"
fi

if [ -f "$ISO" ]; then
  size="$(stat -c '%s' "$ISO")"
  if [ "$size" -ge "$MIN_BYTES" ]; then
    pass "ISO size >= $MIN_BYTES bytes"
  else
    fail "ISO size too small: $size"
  fi
  sha256sum "$ISO" | tee "${ISO}.sha256"
  sha512sum "$ISO" | tee "${ISO}.sha512"
  pass "checksums calculated"
fi

if command -v xorriso >/dev/null 2>&1 && [ -f "$ISO" ]; then
  report="$(xorriso -indev "$ISO" -pvd_info 2>/dev/null || true)"
  if printf '%s\n' "$report" | grep -q 'Volume Id.*PHANTOS'; then
    pass "volume id PHANTOS"
  else
    fail "volume id PHANTOS missing"
  fi

  for path in \
    /live/filesystem.squashfs \
    /EFI/BOOT/bootx64.efi \
    /boot/grub/grub.cfg; do
    if iso_has_path "$path"; then
      pass "contains $path"
    else
      fail "missing $path"
    fi
  done

  live_paths="$(xorriso -indev "$ISO" -find /live -exec echo -- 2>/dev/null | sed "s/^'//;s/'$//")"
  if printf '%s\n' "$live_paths" | grep -Eq '^/live/vmlinuz'; then
    pass "kernel present"
  else
    fail "kernel missing"
  fi
  if printf '%s\n' "$live_paths" | grep -Eq '^/live/initrd'; then
    pass "initrd present"
  else
    fail "initrd missing"
  fi

  eltorito="$(xorriso -indev "$ISO" -report_el_torito plain 2>/dev/null || true)"
  if printf '%s\n' "$eltorito" | grep -qi 'El Torito'; then
    pass "El Torito boot catalog readable"
  else
    fail "El Torito boot catalog missing"
  fi
else
  skip "xorriso unavailable"
fi

if command -v xorriso >/dev/null 2>&1 && command -v unsquashfs >/dev/null 2>&1 && [ -f "$ISO" ]; then
  TMP_DIR="$(mktemp -d)"
  fs_img="$TMP_DIR/filesystem.squashfs"
  if xorriso -osirrox on -indev "$ISO" -extract /live/filesystem.squashfs "$fs_img" >/dev/null 2>&1; then
    fs_listing_file="$TMP_DIR/fs-listing.txt"
    fs_paths_file="$TMP_DIR/fs-paths.txt"
    unsquashfs -ll "$fs_img" > "$fs_listing_file" 2>/dev/null || true
    awk '{print $NF}' "$fs_listing_file" | sed "s/^'//;s/'$//" > "$fs_paths_file"
    for path in \
      squashfs-root/usr/local/bin/phantos-harden-network \
      squashfs-root/usr/local/bin/phantos-verify-offline \
      squashfs-root/usr/local/bin/phantos-verify-live-hardening \
      squashfs-root/opt/phantos/requirements.lock \
      squashfs-root/opt/phantos/app/main.py \
      squashfs-root/etc/systemd/system/phantos-network-hardening.service \
      squashfs-root/etc/sysctl.d/99-phantos-hardening.conf \
      squashfs-root/etc/security/limits.d/phantos-coredump.conf; do
      if grep -Fx "$path" "$fs_paths_file" >/dev/null; then
        pass "squashfs contains ${path#squashfs-root}"
      else
        fail "squashfs missing ${path#squashfs-root}"
      fi
    done
  else
    fail "could not extract live filesystem"
  fi
else
  skip "squashfs content inspection unavailable"
fi

if [ "$FAIL" -gt 0 ]; then
  printf 'ISO validation failed: %s issue(s)\n' "$FAIL" >&2
  exit 1
fi

printf 'ISO validation completed.\n'
