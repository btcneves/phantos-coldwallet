# Build da ISO — PhantOS ColdWallet

Guia completo para gerar a ISO bootável do PhantOS ColdWallet em ambientes Linux.

---

## Pré-requisitos

- Sistema operacional: **Ubuntu 22.04+ ou Debian Bookworm**
- Acesso root (sudo)
- Conexão com a internet **apenas durante o build** — a ISO gerada funciona completamente offline
- Espaço em disco: mínimo 4 GB livres

### Pacotes necessários

```bash
sudo apt install live-build debootstrap xorriso grub-efi-amd64-bin grub-pc-bin dosfstools rsync dpkg-dev
```

| Pacote               | Finalidade                                         |
| -------------------- | -------------------------------------------------- |
| `live-build`         | Ferramenta Debian para construção de sistemas live |
| `xorriso`            | Criação e manipulação de imagens ISO               |
| `grub-efi-amd64-bin` | Bootloader para UEFI (64-bit)                      |
| `grub-pc-bin`        | Bootloader para BIOS legado                        |
| `dosfstools`         | Suporte ao sistema de arquivos FAT (ESP)           |

---

## Windows

Build nativo **não é suportado**. Use uma das alternativas:

- **WSL2** com Ubuntu instalado (execute todos os passos dentro do WSL2)
- **VM Ubuntu** via VirtualBox ou VMware

---

## macOS

Build nativo **não é suportado**. Use uma das alternativas:

- **VM Ubuntu** via VirtualBox, UTM ou Parallels
- **Docker** com imagem Debian Bookworm (xorriso e grub-pc-bin disponíveis)

---

## Passo a passo

### 1. Clonar o repositório

```bash
git clone https://github.com/btcneves/phantos-coldwallet.git
cd phantos-coldwallet
```

### 2. Executar o script de build

```bash
sudo ./scripts/build_iso.sh
```

O script requer root porque o `live-build` monta sistemas de arquivos durante a construção.

### 3. Localizar a ISO gerada

Ao final do build, a ISO estará na raiz do projeto:

```text
phantos-coldwallet-<versao>-amd64.iso
```

### 4. Verificar integridade

```bash
sha256sum phantos-coldwallet-<versao>-amd64.iso
```

Se estiver usando uma ISO baixada, compare o hash com o valor publicado na [página de releases](https://github.com/btcneves/phantos-coldwallet/releases) antes de gravar no pendrive. Para builds locais, gere e guarde o hash junto do commit usado.

---

## O que o script faz

O `build_iso.sh` utiliza o `live-build` para:

1. Configurar um sistema Debian Bookworm mínimo
2. Instalar Python, PySide6 e as dependências do PhantOS ColdWallet
3. Configurar o ambiente kiosk para inicialização automática da interface
4. Gerar a imagem ISO híbrida compatível com BIOS e UEFI

Em build limpo, nenhuma chave privada, seed ou dado sensível deve ser incluído na ISO. Antes de publicar, valide o artefato e inspecione o conteúdo com:

```bash
bash scripts/validate_iso_artifact.sh phantos-coldwallet-<versao>-amd64.iso
```

O sistema é gerado do zero a partir dos pacotes oficiais Debian e das dependências Python fixadas no lockfile.

---

## Tempo estimado

| Conexão             | Tempo aproximado |
| ------------------- | ---------------- |
| Rápida (100 Mbps+)  | 10–15 minutos    |
| Média (10–50 Mbps)  | 20–30 minutos    |
| Lenta (< 10 Mbps)   | 30+ minutos      |

O tempo varia conforme a velocidade de download dos pacotes e o desempenho do processador.

---

## Aviso de segurança

- A ISO gerada localmente ainda **não possui assinatura reproduzível verificável**
- Trate builds locais como artefatos de desenvolvimento até a existência de um release assinado e validado para o mesmo commit
- Verifique sempre o hash SHA-256 antes de usar em produção
- A ISO **não requer internet** em uso — nunca conecte a máquina da cold wallet à rede

---

## Próximo passo

Com a ISO em mãos, siga o guia [Gravando no Pendrive](instalacao-pendrive.md) para gravar e inicializar o sistema.
