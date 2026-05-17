# Validation Report

Date: 2026-05-15

Target branch: `final-product-readiness`

Scope: offline wallet flow, PSBT review/signing, UR handling, public repository hygiene, release tooling, ISO artifact tooling, QEMU smoke testing and audit-readiness documentation.

Status values: PASS, FAIL, SKIPPED, MANUAL REQUIRED, PARTIAL.

## Results

| Category | Test | Command | Environment | Result | Status | Evidence | Observation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Code | Whitespace diff check | `git diff --check` | Local workstation | No whitespace errors | PASS | Command completed | Re-run before PR |
| Code | Lint | `ruff check .` | Local `.venv` | No issues | PASS | Command completed | Ruff 0.14.8 |
| Code | Format | `ruff format --check .` | Local `.venv` | No formatting drift after formatting edits | PASS | Command completed | Re-run before PR |
| Code | Type check | `mypy app/` | Local `.venv` | No issues in app modules | PASS | Command completed | Python 3.12 |
| Code | Unit/integration tests | `pytest -q` | Local `.venv` | 70 tests passed after product-readiness additions | PASS | Test suite | Includes wallet flow script smoke test |
| Security | Public repository hygiene | `scripts/check_public_clean.sh` | Local workstation | No blocked terms, secrets or dangerous paths | PASS | Command completed | Script now checks tracked and selected local paths |
| Security | Shell scripts | `shellcheck scripts/*.sh` | Local workstation | No findings after source annotations | PASS | Command completed | ShellCheck present |
| Security | Python static scan | `bandit -r app` | Local `.venv` | No issues identified | PASS | Command completed | Low-risk findings removed or narrowly annotated |
| Security | Dependency audit | `pip-audit` | Local `.venv` | No known vulnerabilities found | PASS | Command completed | Local package itself is not on PyPI |
| Security | OSV Scanner | `osv-scanner scan source .` | Local workstation | Tool not installed | SKIPPED | `command -v osv-scanner` empty | GitHub security workflow should still run |
| Security | Secret scan | `gitleaks detect --source . --no-git` | Local workstation | Tool not installed | SKIPPED | `command -v gitleaks` empty | Public hygiene script ran locally |
| Wallet | Full offline wallet flow | `python scripts/validate_wallet_flow.py` | Local `.venv`, offscreen Qt | Script completed | PASS | PASS lines for BIP39, BIP44/49/84/86, watch-only, UR, UI lock | Uses public deterministic vectors only |
| Wallet | BIP39 generation | `pytest tests/test_bip39.py` | Local `.venv` | Covered by full suite | PASS | 12/24 word generation tests | Uses system entropy |
| Wallet | Watch-only export safety | `python scripts/validate_wallet_flow.py` | Local `.venv` | Exports omit private material and input secrets | PASS | Script output | Descriptors and xpub variants exported |
| PSBT | Malicious fixtures | `pytest tests/test_psbt.py` | Local `.venv` | Covered missing UTXO, negative fee, wrong path, duplicate prevout, script mismatch and dust | PASS | 33 PSBT tests | Synthetic and deterministic |
| PSBT | Bitcoin Core regtest roundtrip | `PHANTOS_REGTEST_OUT=/tmp/phantos-regtest-psbt bash scripts/regtest_psbt_roundtrip.sh` | Docker daemon, regtest | PSBT signed, finalized and broadcast in regtest | PASS | Script printed PASS and regtest txid | Regtest funds only; image is configurable |
| PSBT | Cross-wallet desktop/mobile fixtures | Manual external wallets | Not executed | No Sparrow/Electrum/BlueWallet fixture produced | MANUAL REQUIRED | See `PSBT_COMPATIBILITY.md` | Required before stable compatibility claims |
| UR/QR | UR multipart robustness | `pytest tests/test_ur.py` | Local `.venv` | Shuffled, duplicate, missing, mixed and corrupted parts covered | PASS | UR tests | UI animated collection remains PARTIAL |
| UR/QR | QR static encode/decode | `pytest tests/test_qr.py` | Local `.venv` | Covered by full suite | PASS | Test suite | Uses local image decode |
| UI | Signing confirmation summary | `pytest tests/test_ui_review.py` | Local `.venv` | Summary includes fingerprint, profile, paths, outputs, change and fee | PASS | Test suite | Formatting logic is Qt-free |
| UI | Lock clears sensitive fields | `python scripts/validate_wallet_flow.py` | Offscreen Qt | Context, seed, passphrase, PSBT and output cleared | PASS | Script output | Python RAM zeroization remains a limitation |
| ISO | Build current ISO | `sudo -n bash scripts/build_iso.sh` | Local workstation | Sudo password required | SKIPPED | `sudo: a password is required` | Current ISO could not be rebuilt here |
| ISO | Existing ISO artifact validation | `bash scripts/validate_iso_artifact.sh phantos-coldwallet-0.1.0-amd64.iso` | Existing local ISO | Base ISO structure PASS; current hardening files missing | FAIL | 4 missing current hardening artifacts | Existing ISO is stale relative to this branch |
| QEMU | BIOS boot smoke | `PHANTOS_QEMU_OUT=/tmp/phantos-qemu-validation bash scripts/test_iso_qemu.sh phantos-coldwallet-0.1.0-amd64.iso` | Existing local ISO, QEMU | Reached timeout window after boot start | PASS | QEMU summary | Smoke only, not current rebuilt ISO |
| QEMU | UEFI boot smoke | Same command | Existing local ISO, OVMF present | Reached timeout window after boot start | PASS | QEMU summary | Smoke only, not current rebuilt ISO |
| Live hardening | Runtime verifier script | `scripts/verify_live_hardening.sh` | Not inside live system | Not executed in target environment | MANUAL REQUIRED | Script added | Run from booted ISO as root |
| USB | Guarded writer | `bash scripts/write_usb.sh /tmp/missing.iso /dev/sdz` | Local workstation | Refused without root/confirmation | PASS | Product script test | Physical write not attempted |
| USB | Physical USB write | `sudo PHANTOS_CONFIRM_WIPE=... bash scripts/write_usb.sh ISO /dev/sdX` | Requires operator-selected USB | No device confirmation supplied | MANUAL REQUIRED | Not executed | Do not mark PASS until written and verified |
| Release | Checksums and SBOM | `PHANTOS_RELEASE_DIR=/tmp/phantos-release bash scripts/release_artifacts.sh phantos-coldwallet-0.1.0-amd64.iso` | Existing local ISO | SHA256/SHA512 PASS, SBOM PASS | PASS | `/tmp/phantos-release/RELEASE_VALIDATION.md` | Artifact is stale relative to branch |
| Release | GPG signature | Same command | Local GPG without secret key configured for release | Not created | SKIPPED | RELEASE_VALIDATION.md | Publish only after signing key is configured |
| Release | minisign signature | Same command | minisign unavailable/key unset | Not created | SKIPPED | RELEASE_VALIDATION.md | Optional path |
| SBOM | CycloneDX | `cyclonedx-py environment` via release script | Local `.venv` | SBOM generated | PASS | `/tmp/phantos-release/sbom.cdx.json` | For local environment dependencies |
| Reproducibility | Double clean ISO build | `scripts/reproducible_build_check.sh` | Requires root live-build execution | Not executed | SKIPPED | Root required | Do not claim reproducible builds |
| Audit | Audit package | Docs and scripts in repo | Local review | Prepared, not audited | PARTIAL | `AUDIT_READINESS.md` | External independent audit still required |

## Current Blockers Before a Release Candidate

1. Rebuild the ISO from this branch on a host with root access.
2. Run `scripts/validate_iso_artifact.sh` against the rebuilt ISO and require PASS.
3. Boot the rebuilt ISO in QEMU and run `scripts/verify_live_hardening.sh` inside the live system.
4. Generate release artifacts from the rebuilt ISO, with signed checksums if a release key is available.
5. Record physical USB write/boot only after an operator provides the exact device and wipe confirmation.
6. Produce real Sparrow, Electrum and BlueWallet PSBT fixtures on regtest or signet.
7. Keep Taproot/BIP86, PSBTv2 and external UR interoperability marked PARTIAL until real fixtures pass.

## Notes

- The existing local ISO boots in QEMU smoke mode, but it is stale relative to this branch and fails current artifact validation because new hardening verifier/service files are absent.
- The Bitcoin Core roundtrip used regtest only and did not touch real funds.
- The project remains unaudited externally and must not be called v1.0.
