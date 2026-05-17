# PhantOS ColdWallet

[![🇧🇷 Português](https://img.shields.io/badge/🇧🇷-Português-009C3B?style=flat-square)](README.md) [![🇺🇸 English](https://img.shields.io/badge/🇺🇸-English-3C3B6E?style=flat-square)](README_EN.md)

![PhantOS ColdWallet Banner](assets/logo/banner.gif)

[![Licença: MIT](https://img.shields.io/badge/Licença-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Bitcoin](https://img.shields.io/badge/Bitcoin-F7931A?logo=bitcoin&logoColor=white)](https://bitcoin.org)
[![Testes: pytest](https://img.shields.io/badge/Testes-pytest-brightgreen.svg)](tests/)
[![Status: Beta](https://img.shields.io/badge/Status-Beta-orange.svg)](CHANGELOG.md)

---

> *"The root problem with conventional currency is all the trust that's required to make it work."*
> — Satoshi Nakamoto, 2009

**Cold wallet Bitcoin open-source para qualquer pessoa. Boot do pendrive, restaure sua seed, derive endereços, assine transações offline e desligue. Nada salvo em disco. Tudo offline.**

---

## Screenshots

![Tela inicial](assets/screenshots/01-tela-inicial.png)

![Carteira carregada](assets/screenshots/03-carteira-restaurada.png)

![Recuperar endereços](assets/screenshots/04-recuperar-enderecos.png)

![Watch-only export](assets/screenshots/05-watch-only-export.png)

---

## Descrição

PhantOS ColdWallet é uma carteira fria Bitcoin para uso offline, executada diretamente de um pendrive bootável (Debian Bookworm live). Gera e restaura seeds BIP39, deriva endereços em múltiplos padrões (Legacy, SegWit, Taproot), assina PSBTs offline e exporta QR/UR para integração com carteiras quentes como BlueWallet e Sparrow.

---

## Recursos Principais

- 🔑 **Geração de seed BIP39** — 12 ou 24 palavras com entropia do sistema (`secrets.token_bytes()`)
- 🔄 **Restauração de carteira** — seed + passphrase BIP39 opcional
- 📐 **Derivação multi-padrão** — BIP44 (Legacy), BIP49 (Nested SegWit), BIP84 (Native SegWit, padrão), BIP86 (Taproot, experimental)
- 📤 **Exportação watch-only** — fingerprint, xpub/zpub/ypub, descriptors completos
- ✍️ **Assinatura PSBT offline** — parse, revisão e assinatura com alertas de segurança
- 🚨 **Alertas de PSBT** — taxa alta, troco não reconhecido, fingerprint divergente
- 📷 **QR simples** — exportação de xpub e descriptors como QR estático
- 🎞️ **UR `crypto-psbt`** — single-part e multipart no core; interoperabilidade externa ainda em validação
- 📸 **Scan QR por câmera** — importação de PSBT diretamente pela webcam
- 🎨 **Interface dark Bitcoin** — laranja `#F7931A`, fundo `#0A0A0A`, tipografia monospace
- 🔒 **Hardening de rede** — Wi-Fi e Bluetooth desabilitados, `nftables` drop-all
- 💾 **Bootável via pendrive** — live Debian Bookworm, openbox kiosk, autologin
- ✅ **Testes automatizados** — ruff, mypy e pytest na validação local e no CI

---

## Fluxo de Uso

1. **Gravar ISO no pendrive** — use `dd` ou Balena Etcher com a ISO gerada
2. **Bootar o computador** pelo pendrive (F12/F2/Del para menu de boot)
3. **Selecionar operação** na tela inicial: nova seed, restaurar ou revisar PSBT
4. **Gerar ou restaurar seed** — exibida apenas na tela, nunca salva em disco
5. **Verificar endereços** gerados e confirmar o padrão de derivação desejado
6. **Exportar watch-only** — escanear descriptor ou xpub em carteira observadora
7. **Receber Bitcoin** via carteira quente conectada à internet
8. **Importar PSBT** para assinatura — via câmera ou arquivo USB
9. **Revisar e assinar** — conferir valores, taxa e destinos antes de assinar
10. **Exportar PSBT assinada** — base64 e UR `crypto-psbt` para transmissão pela carteira online

---

## Início Rápido (Desenvolvimento)

### Pré-requisitos

- Python >= 3.11 (o CI e a versão de desenvolvimento usam Python 3.12)
- Git

### Instalação

```bash
git clone https://github.com/btcneves/phantos-coldwallet.git
cd phantos-coldwallet

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

### Executar a aplicação

```bash
python -m app.main
```

### Executar testes

```bash
pytest tests/ -v
```

### Lint e verificação de tipos

```bash
ruff check .
mypy app/
```

---

## Gerar ISO Bootável

> Requer Ubuntu ou Debian com `live-build` instalado.

```bash
sudo apt install live-build debootstrap xorriso grub-efi-amd64-bin grub-pc-bin dosfstools rsync dpkg-dev
sudo bash scripts/build_iso.sh
```

A ISO será gerada em `phantos-coldwallet-<versão>-amd64.iso` na raiz do repositório.

> Consulte `docs/` para detalhes sobre personalização do ambiente live.

---

## Gravar no Pendrive

Substitua `/dev/sdX` pelo dispositivo correto (verifique com `lsblk`).

```bash
sudo PHANTOS_CONFIRM_WIPE="CONFIRMO APAGAR ESTE DISPOSITIVO" \
  bash scripts/write_usb.sh phantos-coldwallet-<versão>-amd64.iso /dev/sdX
```

Ou use [Balena Etcher](https://etcher.balena.io/) para uma interface gráfica.

---

## Compatibilidade

| Carteira       | Status validado                              | Observação     |
|----------------|----------------------------------------------|----------------|
| Bitcoin Core   | PASS em regtest via Docker                   | PSBT roundtrip |
| Sparrow Wallet | MANUAL REQUIRED                              | Descriptor/PSBT real pendente |
| Electrum       | MANUAL REQUIRED                              | Import xpub/ypub/zpub pendente |
| BlueWallet     | MANUAL REQUIRED                              | Fluxo mobile pendente |
| Keystone/Passport/Specter | SKIPPED                         | UR externo ainda não validado |

---

## Estrutura do Projeto

```text
app/
  descriptors/   — montagem de descriptors Bitcoin
  i18n/          — internacionalização inicial (en_US, pt_BR)
  psbt/          — parse, revisão e assinatura de PSBT
  qr/            — geração e leitura de QR
  security/      — status offline e redação de eventos
  ui/            — interface PySide6
  ur/            — UR encoding (crypto-psbt)
  wallet/        — núcleo BIP39/BIP32
assets/          — logos, screenshots, diagramas
docs/            — documentação técnica
scripts/         — build ISO, hardening, desenvolvimento
tests/           — testes automatizados
```

---

## Stack Técnica

| Componente  | Biblioteca                   |
|-------------|------------------------------|
| Interface   | PySide6 6.11.1               |
| BIP32/BIP39 | embit                        |
| Bitcoin     | btclib, python-bitcointx     |
| QR          | qrcode, Pillow, zxing-cpp    |
| UR encoding | urtypes                      |
| Testes      | pytest                       |
| Lint/tipos  | ruff, mypy                   |

---

## ⚠️ Aviso de Segurança

> **LEIA COM ATENÇÃO ANTES DE USAR**

- **v1.0.0** — primeira release pública estável; testada manualmente em hardware real
- Diferença em relação a hardware wallets: elas usam hardware dedicado, e algumas usam *secure element*; o PhantOS usa isolamento por SO endurecido (sem disco, sem rede, sem swap, buffer de seed controlado pelo app zerado após uso). Ambos são modelos legítimos de cold wallet, com riscos distintos
- **Passphrase perdida = fundos irrecuperáveis** — sem recuperação possível
- **Taproot (BIP86)** e **UR multipart** são funcionalidades experimentais
- PSBTv2, Taproot e troco não reconhecido exigem revisão manual cuidadosa
- Consulte [AUDIT_READINESS.md](AUDIT_READINESS.md), [VERIFY_RELEASE.md](VERIFY_RELEASE.md) e [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)
- Sempre verifique a integridade do pendrive antes de usar em ambiente de produção
- Execute exclusivamente em computadores **sem conexão à internet** durante a operação
- Valide endereços de recebimento em um dispositivo independente

---

## Contribuição

Contribuições são bem-vindas. Consulte o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes de código, testes e pull requests.

```bash
# Antes de enviar um PR
ruff check .
mypy app/
pytest tests/ -v
```

---

## Licença

Distribuído sob a licença [MIT](LICENSE).

Partes do código UR encoding (`app/ur/`) utilizam componentes derivados de bibliotecas open-source de [Foundation Devices](https://github.com/Foundation-Devices), distribuídas sob licença BSD. Consulte os cabeçalhos dos arquivos para detalhes de atribuição.

---

*PhantOS ColdWallet — controle total das suas chaves, sem compromisso com a internet.*
