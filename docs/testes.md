# Testes — PhantOS ColdWallet v1.0.0

Suite automatizada com 188+ testes pytest, cobrindo wallet, PSBT, QR/UR,
segurança de sistema e flags de janela.

## Executar a suite completa

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

Testes de UI requerem `QT_QPA_PLATFORM=offscreen` (definido automaticamente
nos arquivos de teste que dependem de PySide6).

## Arquivos de teste

| Arquivo | Cobertura |
| --- | --- |
| `test_bip39.py` | Validação BIP39, geração 12/24 palavras, passphrase altera carteira |
| `test_bip39_input.py` | Widget de entrada de mnemônica |
| `test_derivation.py` | BIP44, BIP49, BIP84, BIP86 — endereços e xpubs |
| `test_descriptors.py` | Descriptors e checksum de 8 caracteres |
| `test_memory.py` | Zeroização de `bytearray`, `mlock`/`mlockall` |
| `test_psbt.py` | Parser, revisão e assinatura de PSBT; fixtures sintéticos |
| `test_psbt_production.py` | Fluxo de produção de PSBT |
| `test_psbt_security.py` | Casos de segurança: UTXO ausente, fee negativa, script mismatch, dust, prevout duplicado |
| `test_qr.py` | Codificação e decodificação de QR estático |
| `test_security.py` | Status offline, detecção de interfaces e rotas |
| `test_security_hardening.py` | Hardening SYS-01 a SYS-18: WireGuard, nftables, rfkill, memória |
| `test_ui_review.py` | Revisão de PSBT na UI: fingerprint, perfil, caminhos, saídas, troco, taxa |
| `test_ur.py` | UR single e multipart, tolerância a frames ausentes, corrompidos e duplicados |
| `test_window_flags.py` | 12 testes de flags de janela: `FramelessWindowHint` em todos os diálogos |
| `test_product_readiness_scripts.py` | Scripts de validação de artefato e produto |

## Script de validação de fluxo completo

```bash
python scripts/validate_wallet_flow.py
```

Executa o fluxo completo offline em modo headless: BIP39, derivação BIP44/49/84/86,
exportação watch-only, UR, lock da UI. Usa vetores determinísticos públicos.
