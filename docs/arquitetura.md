# Arquitetura — PhantOS ColdWallet v1.0.0

## Camadas principais

| Módulo | Responsabilidade |
| --- | --- |
| `app/wallet` | Geração de mnemônica BIP39, derivação BIP32/44/49/84/86, exportação watch-only |
| `app/psbt` | Parser, revisão e assinatura offline de PSBTs |
| `app/qr` | Codificação/decodificação QR estático |
| `app/ur` | UR encoding `crypto-psbt` single e multipart (fountain codes) |
| `app/security` | Verificação de status offline, detecção de interfaces e serviços de rede |
| `app/security/memory` | Zeroização de buffers (`bytearray`), `mlock`/`mlockall` |
| `app/i18n` | Strings de interface em português |
| `app/ui` | Interface PySide6 (janela principal e diálogos) |
| `app/ui/dialogs` | Centraliza todos os diálogos do sistema com `FramelessWindowHint` |

## Modelo de segurança de janela

Todas as janelas e diálogos aplicam `Qt.WindowType.FramelessWindowHint`.
Isso impede decoração pelo gerenciador de janelas (openbox kiosk) e elimina
barra de título, botões de minimizar e maximizar — comportamento intencionalmente
kiosk-safe para o ambiente live bootável.

O openbox é configurado com `<decor>no</decor>` globalmente como segunda camada
de defesa contra decorações indesejadas.

## Fluxo de inicialização

`app/main.py` inicializa o processo com:

- `PR_SET_DUMPABLE = 0` via `prctl` — impede core dumps e acesso a `/proc/PID/mem`.
- `QT_ACCESSIBILITY=0` e `NO_AT_BRIDGE=1` — desabilita AT-SPI para evitar que
  processos externos leiam campos de seed via D-Bus de acessibilidade.

## Princípio de segredos

Segredos (seed, passphrase, chaves privadas) ficam apenas em memória RAM e
não devem atravessar logs, arquivos persistentes, clipboard ou interfaces de rede.
O buffer de seed controlado pelo PhantOS usa `bytearray` com tentativa de `mlock`
e é zerado no bloco `finally` de `create_wallet_context()`.

Objetos `str`, `bytes` e cópias internas de bibliotecas de terceiros (embit, Qt)
estão fora de controle direto — ver `docs/seguranca.md` para a limitação completa.

