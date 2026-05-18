# USB Install

## Gravar em Linux

Identifique o dispositivo:

```bash
lsblk
```

Use o gravador protegido:

```bash
sudo PHANTOS_CONFIRM_WIPE="CONFIRMO APAGAR ESTE DISPOSITIVO" \
  bash scripts/write_usb.sh phantos-coldwallet-<versão>-amd64.iso /dev/sdX
```

Use `/dev/sdX`, não `/dev/sdX1`.

O script recusa partições, discos internos comuns, dispositivos não removíveis, mounts críticos e gravação sem confirmação textual.

## Gravar com Interface Gráfica

Balena Etcher ou Fedora Media Writer podem ser usados. Verifique o checksum antes de gravar.

## Boot

- Abra o boot menu do computador.
- Selecione o pendrive.
- Prefira máquina sem cabo de rede conectado.
- Não conecte Wi-Fi ou Bluetooth durante o uso.
- Rode `/usr/local/bin/phantos-verify-live-hardening` no live system para registrar o estado offline.

## Status de Validação

Nesta rodada, nenhum pendrive físico foi gravado porque não houve confirmação explícita de dispositivo. O item permanece **MANUAL REQUIRED** até gravação e boot reais.

## Depois do Uso

- Bloqueie a carteira pela UI.
- Desligue o sistema.
- Remova o pendrive.
- Reinicie a máquina antes de voltar ao uso normal.
