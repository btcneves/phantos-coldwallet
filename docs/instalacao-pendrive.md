# Gravando no Pendrive — PhantOS ColdWallet

Tutorial para gravar a ISO do PhantOS ColdWallet em um pendrive USB e inicializar o sistema.

> **Pré-requisito:** gere ou baixe a ISO antes de seguir este guia.
> Consulte [Build da ISO](build-iso.md) para gerar localmente.

---

## Aviso de segurança

- Use um pendrive **dedicado exclusivamente** ao PhantOS ColdWallet
- **Desconecte o computador da rede** antes de iniciar pelo pendrive
- De preferência, use um computador limpo que nunca foi comprometido
- Nunca use o pendrive em computadores com suspeita de malware

---

## Linux

### Opção 1: dd (linha de comando)

```bash
# 1. Identificar o dispositivo do pendrive
lsblk

# 2. Desmontar partições existentes (substitua sdX pelo dispositivo correto)
sudo umount /dev/sdX* 2>/dev/null || true

# 3. Gravar a ISO — ATENÇÃO: substitua /dev/sdX pelo dispositivo correto
#    Todo o conteúdo do pendrive será apagado
sudo dd if=phantos-coldwallet-<versao>-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync

# 4. Garantir que todos os dados foram escritos
sync
```

> **Cuidado:** o `dd` não pede confirmação. Verifique duas vezes o dispositivo com `lsblk` antes de executar. Gravar no disco errado apaga os dados.

### Opção 2: Balena Etcher (interface gráfica)

1. Baixe o Balena Etcher em [etcher.balena.io](https://etcher.balena.io)
2. Abra o Etcher e clique em **Flash from file**
3. Selecione `phantos-coldwallet-<versao>-amd64.iso`
4. Clique em **Select target** e escolha o pendrive
5. Clique em **Flash!** e aguarde a conclusão

### Opção 3: GNOME Disks

1. Abra **Discos** (GNOME Disks) no menu de aplicativos
2. Selecione o pendrive no painel esquerdo
3. Clique no menu (três pontos) e escolha **Restaurar imagem de disco**
4. Selecione a ISO e confirme

---

## Windows

### Rufus (recomendado)

1. Baixe o Rufus em [rufus.ie](https://rufus.ie)
2. Conecte o pendrive e abra o Rufus
3. Em **Dispositivo**, selecione o pendrive correto
4. Em **Seleção de boot**, clique em **SELECIONAR** e escolha a ISO
5. Em **Esquema de partição**, selecione **MBR** ou **GPT** conforme seu hardware
6. Em **Sistema de destino**, selecione **BIOS ou UEFI**
7. Clique em **INICIAR** — quando perguntado pelo modo de escrita, selecione **Escrever em modo Imagem DD**
8. Confirme e aguarde

> **Importante:** selecione **Imagem DD** (não ISO) para preservar a estrutura exata da ISO bootável.

### Balena Etcher (alternativo)

1. Baixe em [etcher.balena.io](https://etcher.balena.io)
2. Siga os mesmos passos da seção Linux — a interface é idêntica

---

## macOS

### dd (linha de comando)

```bash
# 1. Identificar o disco do pendrive
diskutil list

# 2. Desmontar o disco (substitua N pelo número correto)
diskutil unmountDisk /dev/diskN

# 3. Gravar a ISO — use /dev/rdiskN (raw disk, mais rápido)
sudo dd if=phantos-coldwallet-<versao>-amd64.iso of=/dev/rdiskN bs=4m

# 4. Sincronizar
sync
```

> **Nota:** `/dev/rdiskN` (com 'r') é o acesso raw ao disco, significativamente mais rápido que `/dev/diskN` no macOS.

### Balena Etcher (alternativo — macOS)

Disponível para macOS em [etcher.balena.io](https://etcher.balena.io). Siga os mesmos passos da seção Linux.

---

## Verificar integridade antes de gravar

```bash
sha256sum phantos-coldwallet-<versao>-amd64.iso
```

Compare o resultado com o hash publicado na [página de releases](https://github.com/btcneves/phantos-coldwallet/releases) quando estiver usando uma ISO baixada. Para ISO gerada localmente, registre o hash junto do commit usado.

---

## Iniciando pelo pendrive (boot)

### Acessar o menu de boot

1. Conecte o pendrive ao computador
1. Reinicie o computador
1. Durante a POST (tela inicial do fabricante), pressione a tecla de boot:

| Fabricante  | Tecla comum |
| ----------- | ----------- |
| Dell        | F12         |
| HP          | F9 ou Esc   |
| Lenovo      | F12         |
| ASUS        | F8 ou Esc   |
| Acer        | F12         |
| MSI         | F11         |
| Gigabyte    | F12         |
| Apple (Mac) | Option (⌥)  |

1. Selecione o pendrive USB na lista de dispositivos de boot

### Secure Boot

A ISO publicada atualmente **não é assinada digitalmente** para Secure Boot. Se o computador não iniciar pelo pendrive:

1. Acesse o setup da BIOS/UEFI (geralmente F2, Del ou F10 durante o boot)
2. Localize a opção **Secure Boot** e **desabilite**
3. Salve e reinicie

> Reabilite o Secure Boot após o uso se necessário para o sistema operacional principal.

### Primeiro boot

Após selecionar o pendrive, o sistema inicializa automaticamente:

- Carregamento do kernel e sistema Debian (~30–60 segundos)
- Interface do PhantOS ColdWallet abre automaticamente em modo kiosk
- Nenhum login é necessário

---

## Próximo passo

Com o sistema rodando, consulte o [Guia Completo ISO + Pendrive](guia-iso-pendrive-completo.md) para instruções de uso inicial da cold wallet.
