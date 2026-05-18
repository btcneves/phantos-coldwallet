# Changelog

Todas as mudanças notáveis neste projeto são documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
A versão segue [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [1.0.0] — 2026-05-18

### Adicionado

#### Interface completamente frameless — PR #6

- Todas as janelas e diálogos agora usam `FramelessWindowHint`: barra de título removida em
  `MainWindow`, `QRDisplayDialog`, `AnimatedQRDialog` e `CameraDialog`
- `app/ui/dialogs.py` — novo módulo com wrappers centralizados (`msg_warning`, `msg_critical`,
  `msg_information`, `msg_question`, `file_open_dialog`) que aplicam flags frameless e centralizam
  o dialog em relação à janela pai
- Stylesheet global corrigido em `app/main.py` para eliminar fundos cinza do sistema operacional
  em todos os diálogos Qt
- `tests/test_window_flags.py` — 12 testes headless (offscreen) verificando `FramelessWindowHint`
  e ausência de decorações de janela em todos os diálogos

#### Auditoria de segurança interna — 4 rodadas

- Patch de segurança do embit v0.8.0 versionado em `patches/embit-0.8.0-phantos-security.patch`
  (24 arquivos, 40+ vulnerabilidades corrigidas — A-01 a A-09, B-01 a B-09, CRYPTO-01 a CRYPTO-09)
- Script `scripts/apply_embit_patch.sh` para reaplicar patch após reinstalação do embit
- `patches/README.md` documenta todas as correções por ID, severidade e arquivo

#### Verificação de ISO obrigatória no write_usb.sh

- Variável `PHANTOS_ISO_SHA256` habilita verificação obrigatória antes da gravação (SYS-15)
- Sem a variável, script avisa e exibe SHA256 calculado para conferência manual

### Corrigido

- Overflow do label "HOT WALLET" no diagrama SVG do modelo de segurança (`assets/diagrams/security-model.svg`)
  corrigido — texto truncado e `viewBox` ajustado para acomodar o rótulo sem corte — PR #5
- Patches do embit aplicados corretamente pelo `scripts/build_iso.sh` durante o build da ISO — PR #5
- Todos os 188 testes agora passam sem nenhum warning (0 warnings, down from 91)
- Fixtures PSBT em todos os arquivos de teste usam `non_witness_utxo` com txid correspondente,
  eliminando o UserWarning do embit sobre ausência de previous transaction (mitigação fee-drain)
- Imports não utilizados removidos de `test_psbt_production.py`, `test_psbt_security.py`,
  `test_security_hardening.py`

---

## [0.2.1] — 2026-05-16

### Adicionado

#### Word picker BIP39 com autocomplete

- `app/ui/bip39_input.py` — novo widget `Bip39SeedWidget` substitui o `QTextEdit` simples
  de entrada de seed por uma grade de 12 ou 24 campos individuais, cada um com:
  - **Autocomplete** em tempo real a partir das 2048 palavras BIP39 oficiais (inglês)
  - **Tab / Espaço / Enter** move o foco automaticamente para o próximo campo,
    igual ao comportamento do Electrum e do Sparrow Wallet
  - **Validação visual**: borda verde quando a palavra é BIP39 válida;
    sem destaque enquanto o prefixo ainda pode produzir uma palavra válida;
    borda vermelha quando nenhuma palavra BIP39 começa com o texto digitado
  - **Status de checksum em tempo real**: contador `X/24` abaixo da grade evolui
    para `✓ checksum OK` (verde) ou `✗ checksum inválido` (vermelho) ao preencher
    todos os campos
  - Mudança de 24 → 12 palavras preserva as primeiras 12 entradas; 12 → 24 mantém
    os 12 campos existentes e adiciona campos vazios
- `tests/test_bip39_input.py` — 26 testes headless (offscreen) cobrindo:
  wordlist (2048 entradas, sem duplicatas, todas minúsculas, começa em "abandon",
  termina em "zoo"), API do widget (set/get, clear, compat QTextEdit, checksum,
  troca de contagem de palavras, sinal `mnemonic_changed`, normalização de case)

### Corrigido

- `scripts/validate_wallet_flow.py`: referência a `mnemonic_edit` atualizada
  para `mnemonic_input` (API do novo widget)

---

## [0.2.0] — 2026-05-15

Ciclo de endurecimento P0: segurança real e funcional antes da auditoria externa.

### Adicionado

#### Segurança de memória

- `app/security/memory.py`: `zero_bytearray()` zera bytearray in-place; `try_mlock()` / `try_munlock()` bloqueiam páginas de RAM no Linux via `ctypes` (sem swap, sem falha silenciosa)
- `create_wallet_context()` agora mantém o seed em `bytearray`, aplica `mlock` e zera com `finally` garantido — seed não persiste em memória após a função retornar

#### Verificação offline real

- `current_offline_status()` lê `/sys/class/net`, `/proc/net/route`, `rfkill` e `systemctl is-active` em vez de retornar hardcoded
- Gate de assinatura em `sign_psbt()` bloqueia com `PSBTError` quando `verified=False`

#### CI de segurança

- ShellCheck, Bandit, pip-audit, OSV-Scanner, CodeQL e gitleaks em `.github/workflows/security.yml`
- Validação de hashes no lockfile

#### Interface

- Confirmação de assinatura com `format_psbt_confirmation()` (fingerprint, taxa, destinos, paths)
- Aviso explícito ao selecionar BIP86 Taproot (experimental, não auditado)
- Intercepção PSBTv2 com caixa de alerta antes de assinar

### Corrigido

- `_estimate_vbytes()` usa peso witness real (segwit discount correto) por tipo de script
- Prints de debug UR (`fountain_decoder.py`) silenciados em produção
- Remoção de `|| true` em `lb build` e `xorriso` no script de ISO — falhas agora abortam o build
- Caminho do script de build corrigido nos READMEs

### Segurança

- OS hardening na ISO: swap desativado, core dumps bloqueados, sysctl endurecido, `/tmp` em tmpfs
- `check_public_clean.sh` verifica que nenhum dado sensível ou referência indevida existe nos arquivos versionados

---

## [0.1.0] — 2026-05-13

Primeira versão funcional do núcleo Bitcoin e da interface PySide6.

### Adicionado

#### Núcleo Bitcoin

- Geração de seed BIP39 de 12 ou 24 palavras com entropia do sistema (`secrets`)
- Validação de mnemônico com checksum BIP39
- Suporte a passphrase opcional (BIP39)
- Derivação HD: BIP44 (Legacy `1…`), BIP49 (Nested SegWit `3…`), BIP84 (Native SegWit `bc1q…`), BIP86 (Taproot `bc1p…` — experimental)
- BIP84 Native SegWit como padrão recomendado
- Exportação watch-only: fingerprint, xpub/zpub/ypub, descriptors externos e internos
- Checksums de descriptor quando `urtypes.descriptor_checksum` disponível

#### PSBT

- Parse de PSBT a partir de base64, hex, binário ou UR `crypto-psbt`
- Revisão de PSBT: inputs, outputs, taxa, troco, fingerprint
- Alertas: taxa acima de 100 000 sats, taxa acima de 200 sats/vB, troco não reconhecido
- Bloqueio de assinatura por carteira errada, passphrase errada ou inputs não assináveis
- Assinatura offline com exportação em base64

#### QR e UR

- Geração de QR PNG para payloads pequenos (xpub, descriptor)
- Leitura de QR por câmera (zxing-cpp) ou arquivo de imagem
- Codificação e decodificação UR `crypto-psbt` single-part e multipart (fountain codes)
- QR animado para exportação de PSBT assinada (AnimatedQRDialog)

#### Interface

- UI PySide6 dark Bitcoin: fundo `#0A0A0A`, laranja `#F7931A`, verde terminal `#00FF88`
- Bitcoin rain animado no header (estilo Matrix com caracteres Bitcoin)
- Barra de status offline permanente
- Modo kiosk fullscreen para boot via pendrive
- Campos de seed com altura fixa e passphrase com máscara

#### Segurança e infraestrutura

- `WalletContext` com `repr=False` para root_key, account_key e account_public_key
- `safe_event()` redige eventos que contenham termos sensíveis
- Script `harden_network.sh`: bloqueia Wi-Fi, Bluetooth e tráfego nftables drop-all
- Script `verify_offline.sh`: verifica isolamento de rede
- Build ISO Debian Bookworm live com `live-build` (kiosk openbox, autologin, pip venv)

#### Testes

- 27 testes automatizados cobrindo: BIP39, derivação HD, descriptors, PSBT, QR, UR e segurança
- Vetores determinísticos validados (BIP44/49/84/86)
- `ruff check` e `mypy` limpos

---

## Próximas versões

Veja [ROADMAP.md](ROADMAP.md).
