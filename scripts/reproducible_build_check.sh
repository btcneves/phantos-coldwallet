#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${PHANTOS_REPRO_OUT:-build/reproducibility}"
BUILD_SCRIPT="${PHANTOS_BUILD_SCRIPT:-scripts/build_iso.sh}"

mkdir -p "$OUT_DIR"

if [ "$(id -u)" -ne 0 ]; then
  echo "SKIPPED reproducibility check requires root live-build execution." | tee "$OUT_DIR/summary.txt"
  exit 0
fi

if [ ! -x "$BUILD_SCRIPT" ]; then
  echo "FAIL build script not executable: $BUILD_SCRIPT" | tee "$OUT_DIR/summary.txt" >&2
  exit 1
fi

run_build() {
  local index="$1"
  rm -rf build/iso /tmp/phantos-coldwallet-build
  bash "$BUILD_SCRIPT"
  iso="$(find . -maxdepth 1 -name 'phantos-coldwallet-*-amd64.iso' -type f | sort | tail -1)"
  if [ -z "$iso" ]; then
    echo "FAIL build $index produced no ISO" >&2
    exit 1
  fi
  cp "$iso" "$OUT_DIR/build-$index.iso"
  sha256sum "$OUT_DIR/build-$index.iso" | tee "$OUT_DIR/build-$index.sha256"
}

run_build 1
run_build 2

hash1="$(awk '{print $1}' "$OUT_DIR/build-1.sha256")"
hash2="$(awk '{print $1}' "$OUT_DIR/build-2.sha256")"

if [ "$hash1" = "$hash2" ]; then
  echo "PASS bit-for-bit reproducible ISO build: $hash1" | tee "$OUT_DIR/summary.txt"
else
  {
    echo "PARTIAL reproducibility not proven"
    echo "build-1: $hash1"
    echo "build-2: $hash2"
    echo "Likely causes: live mirrors, package timestamps, filesystem ordering, pip wheel metadata."
  } | tee "$OUT_DIR/summary.txt"
  exit 1
fi
