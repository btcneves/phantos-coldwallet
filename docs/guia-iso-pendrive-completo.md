# Guia Completo: ISO → Pendrive → Boot — PhantOS ColdWallet

Tutorial unificado cobrindo toda a jornada: build da ISO, gravação no pendrive, boot e uso inicial do PhantOS ColdWallet.

---

## Visão geral do processo

```text
[Build da ISO]  →  [Gravar no pendrive]  →  [Boot pelo pendrive]  →  [Uso da cold wallet]
```

A ISO gerada contém um sistema Debian Bookworm completo com a interface do PhantOS ColdWallet. Nenhuma instalação no disco rígido é necessária — o sistema roda inteiramente pelo pendrive.

---

## Parte 1: Obtendo a ISO

Você pode **gerar a ISO localmente** (recomendado para máxima confiança) ou **baixar um release** da página oficial.

### Opção A: Baixar release oficial

Acesse a [página de releases](https://github.com/btcneves/phantos-coldwallet/releases) e baixe a versão publicada mais recente. Em 2026-05-16, a release pública marcada como Latest no GitHub é a v0.1.0:

- `phantos-coldwallet-0.1.0-amd64.iso`
- `phantos-coldwallet-0.1.0-amd64.iso.sha256` (hash de verificação)

Verifique a integridade antes de prosseguir:

```bash
sha256sum -c phantos-coldwallet-0.1.0-amd64.iso.sha256
```

### Opção B: Gerar a ISO localmente

Consulte o guia completo em [build-iso.md](build-iso.md). Resumo rápido para Ubuntu/Debian:

```bash
# Instalar dependências
sudo apt install live-build debootstrap xorriso grub-efi-amd64-bin grub-pc-bin dosfstools rsync dpkg-dev

# Clonar e buildar
git clone https://github.com/btcneves/phantos-coldwallet.git
cd phantos-coldwallet
sudo ./scripts/build_iso.sh
```

A ISO será gerada na raiz do projeto como `phantos-coldwallet-<versao>-amd64.iso` (a versão vem do script de build do commit local).

> **Build não é suportado** nativamente no Windows ou macOS. Use WSL2 ou VM Ubuntu.

---

## Parte 2: Gravando no pendrive

Use um pendrive de **pelo menos 2 GB**. Todo o conteúdo existente será apagado.

### Ubuntu / Debian / Linux

**Via dd (linha de comando):**

```bash
# Identificar o dispositivo do pendrive
lsblk

# Desmontar partições (substitua sdX pelo dispositivo correto)
sudo umount /dev/sdX* 2>/dev/null || true

# Gravar — ATENÇÃO: substitua /dev/sdX pelo dispositivo correto
sudo dd if=phantos-coldwallet-<versao>-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

> Verifique o dispositivo duas vezes com `lsblk` antes de executar o `dd`. Gravar no disco errado apaga os dados permanentemente.

**Via Balena Etcher (interface gráfica):**

1. Baixe em [etcher.balena.io](https://etcher.balena.io)
1. Selecione a ISO, o pendrive e clique em **Flash!**

### Windows

**Via Rufus (recomendado):**

1. Baixe o Rufus em [rufus.ie](https://rufus.ie)
1. Abra o Rufus e selecione o pendrive em **Dispositivo**
1. Clique em **SELECIONAR** e escolha a ISO
1. Clique em **INICIAR**
1. Quando perguntado pelo modo de escrita, selecione **Escrever em modo Imagem DD**
1. Confirme e aguarde

**Via Balena Etcher:**

1. Baixe em [etcher.balena.io](https://etcher.balena.io) e siga os mesmos passos do Linux

### macOS

**Via dd (linha de comando):**

```bash
# Identificar o disco do pendrive
diskutil list

# Desmontar (substitua N pelo número correto)
diskutil unmountDisk /dev/diskN

# Gravar usando /dev/rdiskN (raw — mais rápido)
sudo dd if=phantos-coldwallet-<versao>-amd64.iso of=/dev/rdiskN bs=4m
sync
```

**Via Balena Etcher:**

Disponível para macOS em [etcher.balena.io](https://etcher.balena.io).

---

## Parte 3: Boot pelo pendrive

### Acessar o menu de boot

1. Conecte o pendrive ao computador
1. Reinicie o computador
1. Pressione a tecla de boot assim que a tela do fabricante aparecer:

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

1. Selecione o pendrive USB na lista e pressione Enter

### Secure Boot

A ISO publicada atualmente não possui assinatura para Secure Boot. Se o computador não iniciar:

1. Acesse o setup da BIOS/UEFI (F2, Del ou F10 durante o boot)
1. Localize **Secure Boot** e desabilite
1. Salve e reinicie

### O que esperar durante o boot

- Tela do GRUB por alguns segundos (seleção automática)
- Carregamento do kernel Linux (~20–40 segundos)
- Inicialização do ambiente Debian
- Interface do PhantOS ColdWallet abre automaticamente em modo kiosk

Nenhum login é necessário. O sistema está pronto para uso assim que a interface aparecer.

---

## Parte 4: Uso inicial

### Antes de qualquer operação

- **Desconecte o cabo de rede e desative o Wi-Fi** do computador antes de iniciar
- Confirme que não há conectividade de rede ativa

### Gerando uma carteira

1. Na tela inicial, selecione **Nova Carteira**
1. O sistema gera uma seed de 12 ou 24 palavras (BIP-39)
1. Anote as palavras em papel — nunca fotografe ou salve digitalmente
1. Confirme a seed digitando-a de volta para verificação
1. A carteira é criada localmente, sem transmissão de dados

### Exportando endereços via QR Code

1. Selecione **Receber** para visualizar endereços Bitcoin
1. O QR Code pode ser escaneado com outro dispositivo para receber fundos
1. QRs de recebimento contêm apenas endereço público; QRs watch-only podem conter xpub/descriptors públicos, que não gastam fundos, mas expõem privacidade e histórico da carteira

### Assinando transações (air-gap)

1. Crie a transação não assinada em um dispositivo online (watch-only wallet)
1. Transfira para o PhantOS via QR Code ou arquivo no pendrive
1. Assine a transação no PhantOS ColdWallet (offline)
1. Exporte a transação assinada via QR Code para o dispositivo online
1. Transmita a transação assinada para a rede Bitcoin

---

## Boas práticas de segurança

- Use o pendrive exclusivamente para o PhantOS ColdWallet
- Nunca conecte o computador da cold wallet à internet durante o uso
- Armazene a seed em local físico seguro (papel, metal gravado)
- Use computadores de confiança — de preferência dedicados
- Nunca insira o pendrive em computadores que possam estar comprometidos
- Verifique o hash SHA-256 da ISO antes de cada uso em produção

---

## Solução de problemas

| Sintoma                              | Possível causa              | Solução                                      |
| ------------------------------------ | --------------------------- | -------------------------------------------- |
| Computador não inicia pelo pendrive  | Secure Boot ativo           | Desabilite Secure Boot na BIOS/UEFI          |
| Computador não inicia pelo pendrive  | Pendrive não bootável       | Regrave a ISO usando Rufus em modo DD        |
| Interface não abre após boot         | ISO corrompida              | Verifique o SHA-256 e regrave                |
| Tela preta após GRUB                 | Incompatibilidade de GPU    | Aguarde 60s; se persistir, registre modelo da GPU e teste em outra máquina |
| QR Code não aparece                  | Resolução de tela baixa     | Ajuste a resolução nas configurações         |

---

## Links úteis

- [Build da ISO](build-iso.md) — guia detalhado de build
- [Gravando no Pendrive](instalacao-pendrive.md) — guia detalhado de gravação
- [Releases oficiais](https://github.com/btcneves/phantos-coldwallet/releases)
- [Repositório](https://github.com/btcneves/phantos-coldwallet)
