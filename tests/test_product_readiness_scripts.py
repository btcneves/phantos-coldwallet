from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_wallet_flow_validation_script_passes() -> None:
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    result = subprocess.run(
        [sys.executable, "scripts/validate_wallet_flow.py"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Wallet flow validation completed." in result.stdout


def test_build_iso_installs_root_network_hardening_service() -> None:
    build_script = read("scripts/build_iso.sh")
    assert "phantos-network-hardening.service" in build_script
    assert "ExecStart=/usr/local/bin/phantos-harden-network" in build_script
    assert "systemctl enable phantos-network-hardening.service" in build_script

    autostart = build_script.split("cat > config/includes.chroot/etc/xdg/openbox/autostart", 1)[1]
    assert "phantos-harden-network" not in autostart.split("EOF", 1)[0]


def test_build_iso_copies_live_hardening_verifier() -> None:
    build_script = read("scripts/build_iso.sh")
    assert "verify_live_hardening.sh" in build_script
    assert "phantos-verify-live-hardening" in build_script


def test_release_and_iso_scripts_exist_and_are_executable() -> None:
    scripts = [
        "scripts/validate_iso_artifact.sh",
        "scripts/test_iso_qemu.sh",
        "scripts/verify_live_hardening.sh",
        "scripts/write_usb.sh",
        "scripts/release_artifacts.sh",
        "scripts/reproducible_build_check.sh",
        "scripts/regtest_psbt_roundtrip.sh",
        "scripts/run_validation.sh",
    ]
    for script in scripts:
        path = ROOT / script
        assert path.exists(), script
        assert os.access(path, os.X_OK), script


def test_usb_writer_requires_explicit_confirmation() -> None:
    result = subprocess.run(
        ["bash", "scripts/write_usb.sh", "/tmp/missing.iso", "/dev/sdz"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "Execute como root" in result.stderr or "Confirmação ausente" in result.stderr
