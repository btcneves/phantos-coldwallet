# Tutorial — Linux

Este guia cobre duas formas de usar o PhantOS ColdWallet no Linux:

1. **Modo pendrive ISO** — recomendado para uso real com bitcoins
2. **Modo desenvolvimento** — para contribuidores e testes locais

---

## Modo 1: Pendrive bootável (recomendado)

### Pré-requisitos

- Pendrive USB de pelo menos 2 GB (dedicado exclusivamente ao PhantOS)
- ISO do PhantOS (`phantos-coldwallet-<versao>-amd64.iso`)
- Acesso root / sudo

### Baixar e verificar a ISO

```bash
# Baixe a ISO e o hash da página de releases do GitHub
# Verifique a integridade antes de gravar
sha256sum phantos-coldwallet-<versao>-amd64.iso
# Compare com o hash publicado no release
```

Para a v1.0.0, o hash esperado é:

```text
SHA256: 58b3abf4a772f4311e34d028fc45f43bb713923d88cbe5224caa35c7bd0b7040
```

### Gravar no pendrive

**Opção A — dd (linha de comando):**

```bash
# Identifique o dispositivo do pendrive
lsblk

# Desmonte partições existentes (substitua sdX pelo dispositivo correto)
sudo umount /dev/sdX* 2>/dev/null || true

# Grave a ISO (sdX = pendrive, NÃO o disco do sistema)
sudo dd if=phantos-coldwallet-<versao>-amd64.iso \
        of=/dev/sdX bs=4M status=progress conv=fsync

# Sincronize
sync
```

> **Atenção:** verifique `lsblk` duas vezes. Gravar no disco errado apaga dados.

**Opção B — script do projeto (com confirmação interativa):**

```bash
sudo PHANTOS_CONFIRM_WIPE="CONFIRMO APAGAR ESTE DISPOSITIVO" \
  bash scripts/write_usb.sh phantos-coldwallet-<versao>-amd64.iso /dev/sdX
```

**Opção C — Balena Etcher (interface gráfica):**

1. Baixe em [etcher.balena.io](https://etcher.balena.io)
2. Selecione a ISO → selecione o pendrive → Flash

### Boot pelo pendrive

1. Conecte o pendrive
2. Reinicie e pressione a tecla de boot (F12, F8 ou Esc — depende do fabricante)
3. Selecione o pendrive USB na lista

> Se o sistema não iniciar, desabilite o **Secure Boot** na BIOS/UEFI (F2, Del ou F10).

### Primeiro uso

Após o boot (~30–60 s), o PhantOS abre automaticamente em modo kiosk.
Siga o [Guia do Usuário Iniciante](guia-usuario-leigo.md).

---

## Modo 2: Desenvolvimento local

> Use somente com seeds de teste. **Nunca insira seeds reais num ambiente online.**

### Pré-requisitos

- Python 3.11 ou 3.12
- Git

### Instalação

```bash
git clone https://github.com/btcneves/phantos-coldwallet.git
cd phantos-coldwallet

python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Executar

```bash
# Modo janela normal
python -m app.main

# Modo kiosk fullscreen
python -m app.main --kiosk
```

### Testes

```bash
QT_QPA_PLATFORM=offscreen pytest
```

### Lint e typecheck

```bash
ruff check app tests
mypy app
```

---

## Hardening de rede (no pendrive)

Após o boot, execute para bloquear toda conectividade:

```bash
sudo /usr/local/bin/phantos-harden-network
# Ou: sudo bash scripts/harden_network.sh
```

Isso ativa:

- `rfkill` para Wi-Fi e Bluetooth
- `nftables` drop-all (sem tráfego de/para a internet)
- Desabilita swap e core dumps

O PhantOS verifica o isolamento e exibe o status na barra superior.
A assinatura de PSBTs fica **bloqueada** enquanto o dispositivo não estiver verificado como offline.

---

## Verificar isolamento manualmente

```bash
bash scripts/verify_offline.sh
```

Saída esperada num ambiente isolado:

```text
[OK] Sem interface de rede ativa
[OK] Sem rota padrão
[OK] Wi-Fi bloqueado (rfkill)
[OK] Bluetooth bloqueado (rfkill)
[OK] Sem serviços de rede suspeitos
RESULTADO: OFFLINE VERIFICADO
```
