# Tutorial — iOS (iPhone e iPad)

O PhantOS ColdWallet não roda nativamente no iOS — ele é uma ISO para PC.
Este tutorial mostra como usar o **iPhone ou iPad como carteira observadora online**,
em conjunto com o PhantOS offline no pendrive.

---

## Modelo de uso

```text
[iPhone/iPad — BlueWallet]          [PC com pendrive PhantOS]
  Conectado à internet                    Sempre offline
        |                                       |
  Vê saldo, gera endereços             Guarda seed, assina PSBTs
  Monta PSBT (QR)  ──────────────────►  Assina PSBT
                   ◄──────────────────  PSBT assinada (QR animado)
  Transmite para a rede Bitcoin
```

O iPhone **nunca vê sua seed**. Ele só conhece o xpub (chave pública estendida),
que é seguro de usar em dispositivos conectados.

---

## Passo 1 — Instalar BlueWallet no iPhone/iPad

1. Abra a App Store
2. Busque **BlueWallet** (desenvolvedor: BlueWallet Services S.R.L.)
3. Instale e abra o app

> BlueWallet é gratuito e de código aberto. Outras opções compatíveis:
> **Nunchuk** e **Blue Wallet** (ambos suportam PSBT via QR).

---

## Passo 2 — Exportar a carteira observadora do PhantOS

1. Boot pelo pendrive PhantOS (com rede desligada)
2. Crie ou restaure sua seed
3. Clique em **▦ QR Carteira**
4. O PhantOS exibe um QR Code com o xpub ou descriptor da sua carteira

---

## Passo 3 — Importar no BlueWallet (iOS)

1. No BlueWallet, toque em **+** (Adicionar carteira)
2. Selecione **Importar carteira**
3. Toque em **Escanear ou importar arquivo**
4. Aponte a câmera do iPhone para o QR do PhantOS
5. O BlueWallet importa automaticamente como carteira **somente leitura (watch-only)**

> A carteira importada mostrará seus endereços e saldo, mas **não tem acesso à seed**.

---

## Passo 4 — Receber bitcoins (somente no iPhone)

1. No BlueWallet, abra a carteira importada
2. Toque em **Receber**
3. Compartilhe o endereço gerado com quem vai te enviar

---

## Passo 5 — Enviar bitcoins (requer o pendrive PhantOS)

### No iPhone (BlueWallet)

1. Abra a carteira watch-only no BlueWallet
2. Toque em **Enviar**
3. Informe o endereço de destino e o valor
4. Toque em **Avançar** — o BlueWallet monta a transação como **PSBT**
5. Toque em **Exibir QR** para mostrar a PSBT não assinada

### No pendrive PhantOS (offline)

1. Boot pelo pendrive PhantOS
2. Clique em **◉ Escanear QR** e aponte a câmera para o iPhone
3. O PhantOS carrega a PSBT e exibe a revisão: destinos, valores, taxa
4. Verifique tudo cuidadosamente
5. Clique em **✎ Assinar PSBT** e confirme
6. O PhantOS exibe o QR animado com a PSBT assinada

### De volta ao iPhone (BlueWallet)

1. No BlueWallet, toque em **Escanear QR animado** (ou equivalente)
2. Escaneie o QR animado exibido pelo PhantOS
3. Toque em **Transmitir** para enviar a transação à rede Bitcoin
4. Aguarde a confirmação na blockchain

---

## Passo 6 — Bloquear e encerrar

Após assinar, no PhantOS:

1. Clique em **🔒 Bloquear**
2. Desligue o computador completamente
3. Remova o pendrive

---

## Outras opções de app no iOS

| App | Suporte PSBT/QR | Notas |
| --- | --- | --- |
| BlueWallet | ✓ | Mais simples, recomendado para iniciantes |
| Nunchuk | ✓ | Suporte a multisig e QR animado (UR) |
| Sparrow (iPad via Sideload) | Limitado | Não oficial no iOS |

---

## Dúvidas comuns

**Posso usar o Face ID ou Touch ID com o BlueWallet?**
Sim. O BlueWallet usa a autenticação do iOS para proteger o app.
Mas lembre: o app é watch-only — ele não tem sua seed.

**E se eu perder o iPhone?**
Seus bitcoins continuam seguros. O iPhone só tem o xpub (público).
Sem a seed (que está anotada em papel), ninguém pode gastar seus fundos.

**O BlueWallet pode gastar meus bitcoins?**
Não. A carteira importada do PhantOS é watch-only no BlueWallet.
Para gastar, é necessária a assinatura do PhantOS, que exige a seed física.

**Posso usar o iCloud Backup com o BlueWallet?**
A carteira watch-only do BlueWallet não contém a seed, então o backup é de baixo risco.
Mesmo assim, revise as configurações de backup do BlueWallet em Configurações → iCloud.
