# Audit Readiness

Status: beta preparado para revisão técnica. Este documento não declara auditoria concluída.

## Escopo Sugerido

- Geração e restauração BIP39 com passphrase opcional.
- Derivação BIP44, BIP49, BIP84 e BIP86 experimental.
- Exportação watch-only por descriptors e chaves públicas estendidas.
- Parse, revisão e assinatura de PSBT.
- Gate offline antes da assinatura.
- QR e UR `crypto-psbt` para entrada e saída de PSBT.
- Build da ISO Debian live e hardening operacional.
- Higiene de logs, stdout/stderr e arquivos públicos.

## Componentes Críticos

- `app/wallet/core.py`: seed, BIP32, endereços e exports.
- `app/psbt/core.py`: parse, revisão, taxa, warnings e assinatura.
- `app/security/core.py`: verificação offline e redação de eventos.
- `app/ur/core.py`: UR `crypto-psbt`.
- `app/ui/main_window.py`: fluxo de seed, export e assinatura.
- `scripts/build_iso.sh`: composição do sistema live.
- `scripts/harden_network.sh`: bloqueio de rede em runtime.
- `scripts/verify_live_hardening.sh`: verificação runtime dentro da ISO.
- `scripts/validate_iso_artifact.sh`: inspeção de ISO, boot entries e conteúdo squashfs.
- `scripts/regtest_psbt_roundtrip.sh`: roundtrip PSBT Bitcoin Core em regtest.
- `scripts/write_usb.sh`: gravação física de USB com confirmação explícita.
- `.github/workflows/`: CI, segurança e análise estática.

## Ameaças Cobertas

- Assinatura com rede ativa: bloqueada pelo core.
- Troco não reconhecido: alerta explícito.
- PSBT sem UTXO válido: bloqueio.
- Fingerprint ou path divergente: bloqueio.
- PSBTv2 e Taproot: alertas fortes e tratamento experimental.
- Debug output em UR multipart: removido e coberto por teste.
- Swap e core dumps na ISO: desabilitados no live system.
- Dependências Python: lockfile com hashes.

## Fora de Escopo Atual

- Garantia contra hardware, firmware, BIOS/UEFI, teclado ou câmera comprometidos.
- Zeroização forte de strings Python em RAM.
- Persistência criptografada.
- Multisig.
- Build bit-a-bit reprodutível.
- Auditoria externa independente.
- PSBTs reais de todas as carteiras populares.

## Evidências Locais

Comandos esperados antes de PR ou release:

```bash
git status
git diff
ruff check .
ruff format --check .
mypy app/
pytest
scripts/check_public_clean.sh
python scripts/validate_wallet_flow.py
```

Quando disponíveis:

```bash
shellcheck scripts/*.sh
bandit -q -r app scripts
pip-audit -r requirements.lock
osv-scanner --lockfile=requirements.lock
gitleaks detect --no-git --redact
```

Validações de produto:

```bash
bash scripts/regtest_psbt_roundtrip.sh
sudo bash scripts/build_iso.sh
bash scripts/validate_iso_artifact.sh phantos-coldwallet-<versão>-amd64.iso
bash scripts/test_iso_qemu.sh phantos-coldwallet-<versão>-amd64.iso
bash scripts/release_artifacts.sh phantos-coldwallet-<versão>-amd64.iso
```

Dentro do live system:

```bash
sudo /usr/local/bin/phantos-verify-live-hardening
```

## Pendências Antes de v1.0

- Fixtures reais em regtest/signet para Sparrow, Electrum e BlueWallet.
- Verificação manual documentada de import/export com cada carteira.
- Release assinado com chave pública publicada.
- SBOM anexado a cada release.
- Teste de boot BIOS/UEFI em QEMU no mesmo artefato do release e hardware real.
- Validação física de pendrive com dispositivo autorizado.
- Revisão externa independente do core de carteira e assinatura.
