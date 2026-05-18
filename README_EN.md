# PhantOS ColdWallet

[![🇧🇷 Português](https://img.shields.io/badge/🇧🇷-Português-009C3B?style=flat-square)](README.md) [![🇺🇸 English](https://img.shields.io/badge/🇺🇸-English-3C3B6E?style=flat-square)](README_EN.md)

![PhantOS ColdWallet Banner](assets/logo/banner.gif)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Bitcoin](https://img.shields.io/badge/Bitcoin-F7931A?logo=bitcoin&logoColor=white)](https://bitcoin.org)
[![Tests: 188 passing](https://img.shields.io/badge/Tests-188%20passing-brightgreen.svg)](tests/)
[![Status: v1.0.0](https://img.shields.io/badge/Status-v1.0.0%20stable-green.svg)](CHANGELOG.md)

---

> *"The root problem with conventional currency is all the trust that's required to make it work."*     —  Satoshi Nakamoto, 2008

**Open-source Bitcoin cold wallet for anyone. Boot from USB, restore your seed, derive addresses, sign transactions offline and shut down. Nothing saved to disk. Everything offline.**

---

## Screenshots

![Initial screen](assets/screenshots/01-tela-inicial.png)

![BIP39 seed input — 24 fields with autocomplete and validation](assets/screenshots/02-seed-inserida.png)

![Wallet restored — BIP84 Native SegWit addresses](assets/screenshots/03-carteira-restaurada.png)

![Recover addresses across all standards (BIP44/49/84/86)](assets/screenshots/04-recuperar-enderecos.png)

![Watch-only export — descriptor and xpub for watch-only wallet](assets/screenshots/05-watch-only-export.png)

![Wallet QR — zpub / descriptor for Sparrow or Electrum](assets/screenshots/07-qr-carteira.png)

![PSBT review — fee, destinations and security warnings](assets/screenshots/08-psbt-review.png)

---

## Description

PhantOS ColdWallet is an offline Bitcoin cold wallet that runs directly from a bootable USB drive (Debian Bookworm live). It generates and restores BIP39 seeds, derives addresses across multiple standards (Legacy, SegWit, Taproot), signs PSBTs offline, and exports QR/UR codes for integration with hot wallets such as BlueWallet and Sparrow.

---

## Key Features

- **BIP39 seed generation** — 12 or 24 words using system entropy (`secrets.token_bytes()`)
- **Wallet restore** — seed + optional BIP39 passphrase
- **Multi-standard derivation** — BIP44 (Legacy), BIP49 (Nested SegWit), BIP84 (Native SegWit, default), BIP86 (Taproot, experimental)
- **Watch-only export** — fingerprint, xpub/zpub/ypub, full descriptors
- **Offline PSBT signing** — parse, review, and sign with security alerts
- **PSBT alerts** — high fee, unrecognized change, fingerprint mismatch
- **Static QR** — xpub and descriptor export as static QR codes
- **UR `crypto-psbt`** — single-part and multipart in core; external interoperability still being validated
- **Camera QR scan** — import PSBT directly via webcam
- **Bitcoin dark UI** — orange `#F7931A`, background `#0A0A0A`, monospace typography
- **Bilingual** — Portuguese (pt_BR) and English (en_US) switchable at runtime
- **Network hardening** — Wi-Fi and Bluetooth disabled, `nftables` drop-all
- **Bootable USB drive** — Debian Bookworm live, openbox kiosk, autologin
- **188 automated tests** — ruff, mypy and pytest in local validation and CI, 0 warnings

---

## Security Model

![Security Model — Air-gap](assets/diagrams/security-model.svg)

PhantOS implements air-gap isolation: private keys **never leave** the offline device. Communication with online wallets happens exclusively via QR code or USB file.

**Protection layers:**

| Protection | Description |
| --- | --- |
| Seed in protected memory | `bytearray` + `mlock()` — prevents swap to disk |
| Guaranteed zeroization | `zero_bytearray()` in `finally` block |
| Signing gate | Blocks if any network interface is active |
| Log redaction | `safe_event()` removes sensitive terms from all logs |
| embit v0.8.0 patch | 40+ vulnerabilities fixed (A-01 to A-09, CRYPTO-01 to CRYPTO-09) |
| Hardened OS | swap off, core dumps off, sysctl hardening, `/tmp` in tmpfs |

---

## Usage Flow

![Usage flow](assets/diagrams/usage-flow.svg)

1. **Write ISO to USB** — use `dd` or Balena Etcher with the generated ISO
2. **Boot the computer** from the USB drive (F12/F2/Del for boot menu)
3. **Select an operation** on the home screen: new seed, restore, or review PSBT
4. **Generate or restore seed** — displayed on screen only, never written to disk
5. **Verify addresses** and confirm the desired derivation standard
6. **Export watch-only** — scan descriptor or xpub with a watch-only wallet
7. **Receive Bitcoin** via the internet-connected hot wallet
8. **Import PSBT** for signing — via camera or USB file
9. **Review and sign** — verify amounts, fee, and destinations before signing
10. **Export signed PSBT** — base64 and UR `crypto-psbt` for broadcast by the online wallet

---

## Architecture

![Project Architecture](assets/diagrams/architecture.svg)

```text
app/
  descriptors/   — Bitcoin descriptor assembly (BIP44/49/84/86)
  i18n/          — internationalization (pt_BR, en_US)
  psbt/          — PSBT parse, review and signing
  qr/            — QR generation and reading (qrcode, zxing-cpp)
  security/      — offline status, mlock, safe_event
  ui/            — PySide6 interface (dark Bitcoin theme); dialogs.py — centralized frameless wrappers
  ur/            — UR encoding crypto-psbt (Foundation Devices)
  wallet/        — BIP39/BIP32 core
assets/
  diagrams/      — architecture.svg · usage-flow.svg · security-model.svg
  screenshots/   — real captures of all screens
  logo/          — banner.gif
docs/            — tutorials, integration guides, threat model
scripts/         — build_iso.sh · write_usb.sh · harden_network.sh
patches/         — embit-0.8.0-phantos-security.patch (40+ fixes)
tests/           — 188 automated tests (0 warnings)
```

---

## Quick Start (Development)

### Prerequisites

- Python >= 3.11 (CI and the development version use Python 3.12)
- Git

### Installation

```bash
git clone https://github.com/btcneves/phantos-coldwallet.git
cd phantos-coldwallet

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

# Apply embit security patch (required)
bash scripts/apply_embit_patch.sh
```

### Run the application

```bash
python -m app.main
```

### Run tests

```bash
pytest tests/ -v
```

### Lint and type checking

```bash
ruff check .
mypy app/
```

---

## Build Bootable ISO

> Requires Ubuntu or Debian with `live-build` installed.

```bash
sudo apt install live-build debootstrap xorriso grub-efi-amd64-bin grub-pc-bin dosfstools rsync dpkg-dev
sudo bash scripts/build_iso.sh
```

The ISO will be generated as `phantos-coldwallet-1.0.0-amd64.iso` in the repository root.

> See `docs/` for details on customizing the live environment.

---

## Write to USB Drive

Replace `/dev/sdX` with the correct device (check with `lsblk`).

```bash
sudo PHANTOS_CONFIRM_WIPE="CONFIRMO APAGAR ESTE DISPOSITIVO" \
     PHANTOS_ISO_SHA256="<iso sha256>" \
  bash scripts/write_usb.sh phantos-coldwallet-1.0.0-amd64.iso /dev/sdX
```

Or use [Balena Etcher](https://etcher.balena.io/) for a graphical interface.

---

## Compatibility

| Wallet | Validated status | Notes |
| --- | --- | --- |
| Bitcoin Core | PASS on Docker regtest | PSBT roundtrip |
| Sparrow Wallet | MANUAL REQUIRED | Real descriptor/PSBT flow pending |
| Electrum | MANUAL REQUIRED | xpub/ypub/zpub import pending |
| BlueWallet | MANUAL REQUIRED | Mobile flow pending |
| Keystone/Passport/Specter | SKIPPED | External UR flow not yet validated |

---

## Tech Stack

| Component | Library |
| --- | --- |
| UI | PySide6 6.11.1 |
| BIP32/BIP39 | embit 0.8.0 (+ security patch) |
| Bitcoin | btclib, python-bitcointx |
| QR | qrcode, Pillow, zxing-cpp |
| UR encoding | urtypes |
| Tests | pytest |
| Lint/types | ruff, mypy |

---

## CI/CD

The project runs the following checks on every push and pull request:

| Job | Tool | Description |
| --- | --- | --- |
| Lint | ruff | Python formatting and static analysis |
| Types | mypy | Static type checking |
| Tests | pytest 3.11/3.12 | 188 tests in Python matrix |
| Shell | ShellCheck | Shell script static analysis |
| SAST | Bandit | Python security analysis |
| Deps | pip-audit | Dependency audit |
| Deps | OSV Scanner | Known vulnerabilities |
| Secrets | gitleaks | Secret detection |

---

## ⚠️ Security Notice

> **READ CAREFULLY BEFORE USE**

- **v1.0.0** — first stable public release; manually tested on real hardware
- Difference from hardware wallets: they use dedicated hardware, and some use a *secure element*; PhantOS uses hardened OS isolation (no disk, no network, no swap, app-controlled seed buffer zeroed after use). Both are legitimate cold wallet models, with different risks
- **Lost passphrase = unrecoverable funds** — no recovery possible
- **Taproot (BIP86)** and **UR multipart** are experimental features
- PSBTv2, Taproot, and unrecognized change require careful manual review
- See [AUDIT_READINESS.md](AUDIT_READINESS.md), [VERIFY_RELEASE.md](VERIFY_RELEASE.md), and [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)
- Always verify USB drive integrity before use in a production environment
- Operate exclusively on computers **without internet access** during signing
- Validate receiving addresses on an independent device

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for code guidelines, testing, and pull request instructions.

```bash
# Before submitting a PR
ruff check .
mypy app/
pytest tests/ -v
```

---

## License

Distributed under the [MIT](LICENSE) license.

Portions of the UR encoding code (`app/ur/`) use components derived from open-source libraries by [Foundation Devices](https://github.com/Foundation-Devices), distributed under the BSD license. See file headers for attribution details.

---

*PhantOS ColdWallet — full control of your keys, no internet required.*
