#!/usr/bin/env bash
set -euo pipefail

FAIL=0

pass() { printf 'PASS %s\n' "$1"; }
fail() {
  printf 'FAIL %s\n' "$1" >&2
  FAIL=$((FAIL + 1))
}
skip() { printf 'SKIPPED %s\n' "$1"; }

check_empty_swapon() {
  if ! command -v swapon >/dev/null 2>&1; then
    skip "swapon command unavailable"
    return
  fi
  if [ -z "$(swapon --show --noheadings 2>/dev/null)" ]; then
    pass "swap disabled"
  else
    fail "swap active"
  fi
}

check_ulimit_core() {
  if [ "$(ulimit -c)" = "0" ]; then
    pass "ulimit core dumps disabled"
  else
    fail "ulimit core dumps enabled"
  fi
}

check_sysctl_value() {
  local key="$1"
  local expected="$2"
  local actual
  actual="$(sysctl -n "$key" 2>/dev/null || true)"
  if [ "$actual" = "$expected" ]; then
    pass "sysctl $key=$expected"
  else
    fail "sysctl $key expected $expected got ${actual:-missing}"
  fi
}

check_tmpfs_mount() {
  if findmnt -rn -T /tmp -o FSTYPE,OPTIONS 2>/dev/null | grep -q '^tmpfs'; then
    pass "/tmp is tmpfs"
  else
    fail "/tmp is not tmpfs"
  fi
}

check_service_inactive() {
  local svc="$1"
  if ! command -v systemctl >/dev/null 2>&1; then
    skip "systemctl unavailable for $svc"
    return
  fi
  if systemctl is-active --quiet "$svc" 2>/dev/null; then
    fail "$svc active"
  else
    pass "$svc inactive"
  fi
}

check_no_default_route() {
  if ip route show default 2>/dev/null | grep -q .; then
    fail "default route present"
  else
    pass "no default route"
  fi
}

check_interfaces_down() {
  local active
  active="$(
    for path in /sys/class/net/*; do
      [ -e "$path" ] || continue
      iface="$(basename "$path")"
      [ "$iface" = "lo" ] && continue
      state="$(cat "$path/operstate" 2>/dev/null || true)"
      flags="$(cat "$path/flags" 2>/dev/null || echo 0)"
      if [ "$state" = "up" ] || [ $((flags & 1)) -eq 1 ]; then
        printf '%s\n' "$iface"
      fi
    done
  )"
  if [ -z "$active" ]; then
    pass "external interfaces down"
  else
    fail "external interfaces up: $active"
  fi
}

check_rfkill_blocked() {
  if ! command -v rfkill >/dev/null 2>&1; then
    skip "rfkill unavailable"
    return
  fi
  if rfkill list 2>/dev/null | grep -E 'Soft blocked: no|Hard blocked: no' >/dev/null; then
    fail "rfkill reports unblocked wireless device"
  else
    pass "rfkill blocks wireless devices or no devices present"
  fi
}

check_nft_policy() {
  if ! command -v nft >/dev/null 2>&1; then
    skip "nft unavailable"
    return
  fi
  if nft list ruleset 2>/dev/null | grep -q 'table inet phantos' \
    && nft list ruleset 2>/dev/null | grep -q 'policy drop'; then
    pass "nftables drop policy present"
  else
    fail "nftables drop policy missing"
  fi
}

check_absent_or_inactive() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    fail "$name installed"
  else
    pass "$name not installed"
  fi
}

check_empty_swapon
check_ulimit_core
check_sysctl_value kernel.core_pattern /dev/null
check_sysctl_value fs.suid_dumpable 0
check_sysctl_value vm.swappiness 0
check_sysctl_value kernel.dmesg_restrict 1
check_sysctl_value kernel.perf_event_paranoid 3
check_sysctl_value kernel.unprivileged_bpf_disabled 1
check_sysctl_value net.core.bpf_jit_harden 2
# SYS-13: ptrace_scope=3 proíbe qualquer uso de ptrace, incluindo por root sem CAP_SYS_PTRACE
check_sysctl_value kernel.yama.ptrace_scope 3
check_tmpfs_mount

for svc in NetworkManager wpa_supplicant bluetooth ssh sshd avahi-daemon cups tor; do
  check_service_inactive "$svc"
done

check_no_default_route
check_interfaces_down
check_rfkill_blocked
check_nft_policy
check_absent_or_inactive tor
check_absent_or_inactive firefox
check_absent_or_inactive chromium

if [ "$FAIL" -gt 0 ]; then
  printf 'Live hardening verification failed: %s issue(s)\n' "$FAIL" >&2
  exit 1
fi

printf 'Live hardening verification completed.\n'
