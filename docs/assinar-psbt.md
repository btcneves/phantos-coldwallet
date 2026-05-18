# Assinar PSBT

PSBT (Partially Signed Bitcoin Transaction) é o formato padrão para transações
não assinadas em fluxos air-gap. A transação é montada em um dispositivo online,
transferida para o PhantOS ColdWallet offline via QR ou arquivo, assinada localmente
e devolvida ao dispositivo online para transmissão.

---

## O que o PhantOS revisa antes de assinar

Antes de permitir a assinatura, o PhantOS exibe para revisão:

- **Inputs assináveis** — entradas que pertencem à sua carteira
- **Destinos e valores** — endereços de destino e quanto é enviado para cada um
- **Taxa total** e **taxa estimada em sats/vB**
- **Troco reconhecido** — se o endereço de troco pertence à sua carteira
- **Fingerprint e caminho de derivação** — confirma que a chave correta está sendo usada
- **Alertas** — Taproot/PSBTv2 quando aplicável

> **Regra de ouro:** nunca assine se o destino, o valor, a taxa ou o troco
> estiverem estranhos ou diferentes do que você configurou no app online.

---

## Pré-requisito

A assinatura fica **bloqueada** enquanto o PhantOS detectar conectividade de rede ativa.
Antes de prosseguir, confirme que o indicador de status da interface mostra o dispositivo como offline.

---

## Passo a passo

### 1. Montar a PSBT no dispositivo online

No app online (BlueWallet, Sparrow, Electrum, Nunchuk ou similar):

1. Abra a carteira watch-only importada do PhantOS
2. Crie a transação informando o endereço de destino e o valor
3. Exporte como **PSBT** — o app exibirá um QR Code ou permitirá salvar um arquivo

### 2. Transferir a PSBT para o PhantOS

**Via QR Code (recomendado):**

1. No PhantOS, clique em **◉ Escanear QR**
2. Aponte a câmera para o QR Code exibido no dispositivo online
3. O PhantOS carrega a PSBT automaticamente

**Via arquivo no pendrive:**

1. Salve o arquivo `.psbt` no pendrive (em um segundo pendrive ou partição separada)
2. No PhantOS, use a opção de carregar arquivo PSBT
3. Selecione o arquivo `.psbt`

### 3. Revisar a transação

O PhantOS exibe o resumo da transação:

- Confira cada endereço de destino — verifique caractere por caractere se necessário
- Confirme os valores e que a taxa está dentro do esperado
- Confirme que o troco retorna para um endereço da sua carteira

### 4. Assinar

1. Clique em **✎ Assinar PSBT**
2. O PhantOS assina com a chave derivada da seed (e passphrase, se configurada)
3. A PSBT assinada é exibida como QR animado (UR/BC-UR)

### 5. Transmitir a transação

**De volta ao dispositivo online:**

1. No app online, use a opção de escanear QR animado
2. Aponte a câmera para o QR do PhantOS
3. O app reconstrói a PSBT assinada
4. Toque/clique em **Transmitir** — a transação é enviada para a rede Bitcoin

### 6. Bloquear

Após a assinatura, clique em **🔒 Bloquear** para limpar todos os dados da memória
antes de desligar o computador.

---

## Solução de problemas

| Sintoma | Causa provável | Solução |
| --- | --- | --- |
| Botão Assinar desabilitado | Rede ativa detectada | Desconecte a rede; aguarde o status mudar para offline |
| "Nenhum input assinável" | Seed ou passphrase incorreta | Confirme a seed e a passphrase |
| "Fingerprint não corresponde" | Carteira diferente carregada | Verifique se a seed restaurada é a mesma usada ao exportar o xpub |
| QR animado não escaneado | App online não suporta UR | Use um app compatível (BlueWallet, Nunchuk, Sparrow) |
