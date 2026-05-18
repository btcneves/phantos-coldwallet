# Validation Report — PhantOS ColdWallet v1.0.0

Data: 2026-05-18

Branch: `fix/security-model-hot-wallet-overflow-embit-build`

Escopo: fluxo completo de carteira offline, revisão e assinatura de PSBT,
UR/QR, hardening de sistema, flags de janela, artefato ISO v1.0.0, higiene
de repositório público e documentação de auditoria.

Valores de status: PASS, FAIL, SKIPPED, MANUAL REQUIRED, PARTIAL.

---

## Resultados

| Categoria | Teste | Comando | Ambiente | Resultado | Status | Observação |
| --- | --- | --- | --- | --- | --- | --- |
| Code | Whitespace diff | `git diff --check` | Workstation local | Sem erros de espaço | PASS | Re-executar antes de PR |
| Code | Lint | `ruff check .` | `.venv` local | Sem issues | PASS | |
| Code | Format | `ruff format --check .` | `.venv` local | Sem drift | PASS | |
| Code | Type check | `mypy app/` | `.venv` local | Sem issues em `app/` | PASS | Python 3.12 |
| Code | Suite de testes | `pytest -q` | `.venv` local | 188+ testes passaram | PASS | Inclui test_window_flags.py (12 testes) |
| Security | Higiene de repositório | `scripts/check_public_clean.sh` | Workstation local | Sem termos bloqueados, segredos ou paths perigosos | PASS | |
| Security | Shell scripts | `shellcheck scripts/*.sh` | Workstation local | Sem findings após anotações de source | PASS | |
| Security | Scan Python estático | `bandit -r app` | `.venv` local | Sem issues | PASS | Findings de baixo risco anotados |
| Security | Auditoria de dependências | `pip-audit` | `.venv` local | Sem vulnerabilidades conhecidas | PASS | |
| Security | OSV Scanner | `osv-scanner scan source .` | Workstation local | Executado no CI | PASS | GitHub Actions |
| Security | Secret scan | `gitleaks detect` | CI | Sem secrets detectados | PASS | Binário direto no CI (sem action) |
| Security | Patches embit v0.8.0 | Inspeção de build | ISO v1.0.0 | 40+ vulnerabilidades corrigidas; CRÍTICO fee drain (psbt/core.py:62) resolvido | PASS | Patches aplicados via build_iso.sh |
| Wallet | Fluxo offline completo | `python scripts/validate_wallet_flow.py` | `.venv` offscreen Qt | Script concluído | PASS | BIP39, BIP44/49/84/86, watch-only, UR, lock UI |
| Wallet | Geração BIP39 | `pytest tests/test_bip39.py` | `.venv` local | Coberto pela suite completa | PASS | Entropia do sistema (`secrets`) |
| Wallet | Exportação watch-only | `python scripts/validate_wallet_flow.py` | `.venv` local | Exportações omitem material privado | PASS | Descriptors e variantes xpub |
| PSBT | Fixtures de segurança | `pytest tests/test_psbt_security.py` | `.venv` local | UTXO ausente, fee negativa, path errado, prevout duplicado, script mismatch, dust cobertos | PASS | Sintéticos e determinísticos |
| PSBT | Roundtrip Bitcoin Core regtest | `scripts/regtest_psbt_roundtrip.sh` | Docker, regtest | PSBT assinada, finalizada e transmitida em regtest | PASS | Apenas fundos regtest |
| PSBT | Fixtures Sparrow/Electrum/BlueWallet | Wallets externas em mainnet/signet | Não executado | Sem fixtures reais produzidos | MANUAL REQUIRED | Ver `PSBT_COMPATIBILITY.md` antes de claims de compatibilidade |
| UR/QR | Robustez UR multipart | `pytest tests/test_ur.py` | `.venv` local | Embaralhados, duplicados, ausentes, mistos e corrompidos cobertos | PASS | |
| UR/QR | QR estático encode/decode | `pytest tests/test_qr.py` | `.venv` local | Coberto pela suite | PASS | |
| UI | Resumo de revisão de assinatura | `pytest tests/test_ui_review.py` | `.venv` local | Fingerprint, perfil, paths, saídas, troco e taxa presentes | PASS | Lógica Qt-free |
| UI | Flags de janela (FramelessWindowHint) | `pytest tests/test_window_flags.py` | `.venv` offscreen Qt | 12 testes passaram; todos os diálogos sem decoração | PASS | QRDisplayDialog, AnimatedQRDialog, CameraDialog, wrappers dialogs.py |
| UI | Lock limpa campos sensíveis | `python scripts/validate_wallet_flow.py` | `.venv` offscreen Qt | Contexto, seed, passphrase, PSBT e saída limpos | PASS | Limitação de zeroização Python RAM permanece documentada |
| ISO | Build da ISO v1.0.0 | `sudo bash scripts/build_iso.sh` | Workstation com root | ISO gerada: `phantos-coldwallet-1.0.0-amd64.iso` | PASS | |
| ISO | Verificação de integridade | `sha256sum` / `sha512sum` | Artefato v1.0.0 | SHA256: `58b3abf4a772f4311e34d028fc45f43bb713923d88cbe5224caa35c7bd0b7040` | PASS | SHA512: `406f5c13557381a2220192802ee18709bebc2f9c43a5689b074e7c4189d3dd2694afd2f9fa21578d4cf1285b4e8c2f1e65efe15db58b54b04fb111309d48f9b4` |
| ISO | Validação de artefato | `bash scripts/validate_iso_artifact.sh phantos-coldwallet-1.0.0-amd64.iso` | Artefato v1.0.0 | Estrutura e arquivos de hardening presentes | PASS | |
| QEMU | Boot BIOS smoke | `scripts/test_iso_qemu.sh phantos-coldwallet-1.0.0-amd64.iso` | ISO v1.0.0, QEMU | Boot smoke passou | PASS | |
| QEMU | Boot UEFI smoke | Mesmo comando, OVMF | ISO v1.0.0, OVMF presente | Boot smoke passou | PASS | |
| Live hardening | Verificador de runtime | `phantos-verify-live-hardening` | Sistema live booted | Swap, core dumps, rede, serviços e nftables validados | PASS | Executar como root no sistema booted |
| USB | Escritor protegido | `scripts/write_usb.sh` sem confirmação | Workstation local | Recusado sem root/confirmação | PASS | |
| USB | Gravação física USB | `scripts/write_usb.sh` com confirmação | Requer dispositivo físico | Não automatizado | MANUAL REQUIRED | Verificar com `sha256sum` após gravação |
| Release | Checksums e SBOM | `scripts/release_artifacts.sh phantos-coldwallet-1.0.0-amd64.iso` | Artefato v1.0.0 | SHA256/SHA512 e SBOM gerados | PASS | |
| Release | Assinatura GPG | Mesmo script | Chave de release configurada | A configurar no momento da publicação | SKIPPED | Não publicar sem assinatura verificável |
| Reproducibility | Build bit-a-bit reprodutível | `scripts/reproducible_build_check.sh` | Requer duas execuções com root | Não executado | SKIPPED | Não declarar builds reprodutíveis até evidência |
| Audit | Pacote de auditoria | Docs e scripts no repo | Revisão local | Preparado; auditoria externa não realizada | PARTIAL | Ver `AUDIT_READINESS.md` |

---

## Pendências antes de release público

1. Produzir fixtures reais de Sparrow, Electrum e BlueWallet em regtest ou signet e registrar resultado em `PSBT_COMPATIBILITY.md`.
2. Configurar chave de release GPG e gerar `SHA256SUMS.asc` antes de publicar artefatos.
3. Realizar gravação física de USB com confirmação explícita do operador e verificar checksum pós-gravação.
4. Conduzir auditoria externa independente antes de declarar suporte a valores significativos.

---

## Notas

- A suite de testes cobre 188+ casos, incluindo 12 testes de flags de janela (`test_window_flags.py`) adicionados neste branch.
- Os patches embit v0.8.0 estão aplicados no build ISO; o CRÍTICO fee drain (psbt/core.py:62) e os 9 ALTOS (PRNG inseguro, malleable signatures, entre outros) foram corrigidos.
- A ISO `phantos-coldwallet-1.0.0-amd64.iso` foi construída e validada neste branch.
- Builds não são bit-a-bit reprodutíveis; tratar como candidato de validação até assinatura e checklist completos.
- O roundtrip Bitcoin Core usou apenas fundos regtest — não foram tocados fundos reais.
- A limitação de zeroização de memória Python permanece documentada e conhecida; não é bloqueante para v1.0.0.
