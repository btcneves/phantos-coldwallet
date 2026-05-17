# Guia para Usuário Iniciante

Este guia explica o conceito de cold wallet e como usar o PhantOS de forma segura,
sem pressupor conhecimento técnico avançado.

---

## O que é o PhantOS ColdWallet?

É uma carteira Bitcoin que roda num **pendrive bootável**. Você liga o computador
pelo pendrive, assina transações **completamente offline** e desliga. Seus bitcoins
nunca ficam expostos a um computador conectado à internet.

---

## Os dois computadores

O modelo de segurança usa dois dispositivos:

| Dispositivo | Conexão | Função |
| --- | --- | --- |
| **Pendrive PhantOS** | Sempre offline | Guarda a seed, assina PSBTs |
| **Celular ou PC online** | Conectado | Vê saldo, monta PSBTs, transmite |

O celular/PC online **nunca vê sua seed**. Ele só vê sua chave pública (xpub), que é segura de compartilhar.

---

## Fluxo básico — passo a passo

### 1. Criar a carteira (uma vez)

1. Boot pelo pendrive PhantOS (com rede desligada)
2. Clique em **⊕ Criar Carteira**
3. Anote as 24 palavras **em papel** — nunca foto, nunca nuvem
4. Clique em **▦ QR Carteira** e escaneie o QR com seu app online
5. Clique em **🔒 Bloquear** e desligue

### 2. Receber bitcoins

Faça no celular/PC online (o PhantOS não é necessário):

1. Abra o app online (BlueWallet, Sparrow, Electrum)
2. Gere um endereço de recebimento
3. Compartilhe com quem vai te enviar

### 3. Enviar bitcoins (requer o pendrive)

1. No app online, monte a transação e exporte como **PSBT**
2. Boot pelo pendrive PhantOS
3. Carregue a PSBT (QR, arquivo ou texto)
4. Revise os destinos, valores e taxa na tela
5. Clique em **✎ Assinar PSBT** e confirme
6. Exporte a PSBT assinada (QR animado) de volta ao celular
7. No celular, transmita a transação para a rede Bitcoin
8. Clique em **🔒 Bloquear** e desligue

---

## Regras de ouro

- **Nunca fotografe** a seed ou a tela com as palavras visíveis
- **Nunca envie** a seed por mensagem, e-mail ou qualquer canal
- **Nunca digite** as 24 palavras em nenhum site ou app online
- **Anote a passphrase** separadamente, se usou uma — passphrase perdida = fundos perdidos para sempre
- Use o pendrive **apenas para o PhantOS** — não guarde outros arquivos nele
- Após cada uso, clique em **🔒 Bloquear** antes de desligar

---

## Como usar o word picker (entrada de seed)

Ao restaurar a seed, cada palavra é digitada em um campo separado:

1. Clique no campo **#1** e comece a digitar
2. Selecione a palavra no menu de sugestões (clique ou Tab/Enter)
3. O foco vai automaticamente para o campo **#2** e assim por diante
4. Quando todos os 24 campos estiverem verdes e o status mostrar `✓ checksum OK`, a seed está correta

---

## Aplicativos online recomendados

| App | iOS | Android | Desktop | Tipo |
| --- | --- | --- | --- | --- |
| BlueWallet | ✓ | ✓ | — | Mobile, simples |
| Sparrow Wallet | — | — | ✓ | Desktop, avançado |
| Electrum | — | — | ✓ | Desktop, clássico |
| Nunchuk | ✓ | ✓ | ✓ | Multi-plataforma |

Todos suportam importar xpub / descriptor e transmitir PSBTs assinadas.

---

## Dúvidas frequentes

**Posso usar o PhantOS em qualquer computador?**
Sim. A ISO roda em qualquer PC ou notebook com boot por USB. Não instala nada no computador.

**O que acontece se eu perder o pendrive?**
Nada. Seus bitcoins estão na blockchain, não no pendrive. Desde que você tenha a seed anotada,
pode restaurar em qualquer PhantOS (ou qualquer carteira Bitcoin compatível com BIP39).

**Preciso de internet para usar o PhantOS?**
Não — e nem deve ter. O PhantOS verifica que a rede está desligada antes de permitir assinar.

**Posso usar minha seed atual de outra carteira?**
Sim. O PhantOS aceita qualquer seed BIP39 de 12 ou 24 palavras em inglês.
