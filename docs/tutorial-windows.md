# Tutorial — Windows

O PhantOS ColdWallet **não é instalado no Windows**. Você grava a ISO num pendrive
e inicia o computador por ele. O Windows do computador não é alterado.

---

## Pré-requisitos

- Pendrive USB de pelo menos 2 GB (dedicado exclusivamente ao PhantOS)
- ISO do PhantOS (`phantos-coldwallet-<versao>-amd64.iso`)
- Rufus (gratuito, sem instalação)

---

## Passo 1 — Baixar e verificar a ISO

1. Baixe a ISO na [página de releases do GitHub](https://github.com/btcneves/phantos-coldwallet/releases)
2. Baixe o arquivo `.sha256` correspondente
3. Verifique a integridade no PowerShell:

```powershell
Get-FileHash .\phantos-coldwallet-<versao>-amd64.iso -Algorithm SHA256
```

Compare o hash exibido com o publicado no release. Para a v1.0.0, o valor esperado é:

```text
SHA256: 58b3abf4a772f4311e34d028fc45f43bb713923d88cbe5224caa35c7bd0b7040
```

Se forem idênticos, a ISO é autêntica.

---

## Passo 2 — Gravar no pendrive com Rufus

1. Baixe o Rufus em [rufus.ie](https://rufus.ie) (versão portátil, sem instalação)
2. Conecte o pendrive e abra o Rufus
3. Configure:
   - **Dispositivo:** selecione o pendrive correto
   - **Seleção de boot:** clique em SELECIONAR e escolha a ISO
   - **Esquema de partição:** MBR (compatível com BIOS e UEFI)
   - **Sistema de destino:** BIOS ou UEFI
4. Clique em **INICIAR**
5. Quando perguntado pelo modo de escrita, selecione **Escrever em modo Imagem DD** e confirme
6. Aguarde a conclusão

> **Alternativa:** Balena Etcher ([etcher.balena.io](https://etcher.balena.io)) — interface mais simples, funciona igualmente bem.

---

## Passo 3 — Desligar a rede antes do boot

Para máxima segurança:

- Desconecte o cabo Ethernet
- Desative o Wi-Fi no Windows antes de reiniciar
- Ou simplesmente use um computador sem conexão física

---

## Passo 4 — Boot pelo pendrive

### Acessar o menu de boot

1. Com o pendrive conectado, reinicie o computador
2. Durante a tela inicial do fabricante, pressione a tecla de boot:

| Fabricante | Tecla |
| --- | --- |
| Dell | F12 |
| HP | F9 ou Esc |
| Lenovo | F12 |
| ASUS | F8 ou Esc |
| Acer | F12 |
| MSI | F11 |
| Gigabyte | F12 |

3. Selecione o pendrive USB na lista

### Se o computador não iniciar pelo pendrive

**Cause mais comum: Secure Boot ativado.**

1. Reinicie e acesse a BIOS/UEFI (geralmente F2, Del ou F10)
2. Localize a opção **Secure Boot** e **desabilite**
3. Salve e reinicie
4. Tente o boot pelo pendrive novamente

> Reabilite o Secure Boot após o uso se necessário para o Windows.

---

## Passo 5 — Usar o PhantOS

Após o boot (~30–60 s), o PhantOS abre automaticamente.

Siga o [Guia do Usuário Iniciante](guia-usuario-leigo.md) para:

- Criar ou restaurar sua seed com o word picker
- Exportar a carteira observadora via QR
- Assinar PSBTs offline

---

## Passo 6 — Retornar ao Windows

1. Clique em **🔒 Bloquear** no PhantOS para limpar a memória
2. Desligue o computador completamente (não reinicie — desligue)
3. Remova o pendrive
4. Ligue novamente — o Windows inicializa normalmente

---

## Integração com carteiras online no Windows

Após exportar o xpub/descriptor do PhantOS via QR, instale um dos apps abaixo no mesmo
computador Windows (online) para montar transações:

| App | Download |
| --- | --- |
| Sparrow Wallet | [sparrowwallet.com](https://sparrowwallet.com) |
| Electrum | [electrum.org](https://electrum.org) |

Importe o xpub ou descriptor exportado pelo PhantOS. O app online nunca vê sua seed —
apenas a chave pública, que é segura de usar em ambiente conectado.

---

## Dúvidas comuns

**O PhantOS altera alguma coisa no meu Windows?**
Não. A ISO roda completamente na memória RAM. O disco do computador não é tocado.

**Posso usar o mesmo pendrive que uso para outros arquivos?**
Não. Grave o PhantOS num pendrive **dedicado exclusivamente** a ele.
O processo de gravação apaga todo o conteúdo anterior.

**Preciso de antivírus ou firewall especial?**
Não. O PhantOS roda isolado, sem acesso à internet. Verifique sempre o hash SHA256 da ISO antes de gravar.
