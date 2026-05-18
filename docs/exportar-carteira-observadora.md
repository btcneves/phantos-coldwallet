# Exportar Carteira Observadora

A carteira observadora (watch-only) permite acompanhar saldo e histórico e criar
transações não assinadas (PSBTs) em um dispositivo online, **sem expor a seed** ao
dispositivo conectado à internet.

---

## O que é exportado

O QR Code gerado pelo PhantOS contém:

- **Master fingerprint** — identificador único da carteira raiz
- **Caminho de derivação** — ex.: `m/84'/0'/0'`
- **xpub / zpub / ypub** — chave pública estendida no formato compatível com o tipo de carteira
- **Output descriptors** — externo (`/0/*`) e de troco (`/1/*`), no formato aceito por Sparrow e Bitcoin Core
- **Rede e tipo de script** — mainnet, Native SegWit / Nested SegWit / Legacy / Taproot

> **Descriptors** são o formato moderno e são preferidos para Sparrow Wallet e Bitcoin Core.
> xpub/zpub/ypub existem por compatibilidade com apps que ainda dependem deles (ex.: BlueWallet).

---

## Passo a passo

### 1. Carregar a seed no PhantOS

1. Boot pelo pendrive PhantOS (com rede desligada)
2. Restaure ou crie a carteira com a seed de 12 ou 24 palavras
3. Se a carteira usa passphrase, informe no campo "Passphrase"
4. Selecione o tipo de carteira correto (padrão: BIP84 Native SegWit)

### 2. Gerar o QR da carteira observadora

1. Clique em **▦ QR Carteira**
2. O PhantOS exibe o QR Code com os dados públicos da carteira

### 3. Importar no app online

Escaneie o QR com o app de sua escolha:

**BlueWallet (iOS / Android):**

1. Toque em **+** → **Importar carteira**
2. Toque em **Escanear ou importar arquivo**
3. Aponte a câmera para o QR do PhantOS
4. O app importa como carteira somente leitura (watch-only)

**Sparrow Wallet (desktop):**

1. Vá em **File → New Wallet**
2. Selecione **Airgapped Hardware Wallet**
3. Clique em **Scan…** e aponte a câmera para o QR
4. O Sparrow importa o descriptor completo, incluindo troco

**Electrum (desktop):**

1. Crie uma nova carteira do tipo **Standard wallet**
2. Escolha **Use a master key**
3. Cole o zpub/xpub manualmente (copie da tela do PhantOS, se necessário)

**Nunchuk (iOS / Android / desktop):**

1. Adicione uma nova chave → **Airgap**
2. Escaneie o QR animado ou estático do PhantOS

### 4. Bloquear

Após exportar, clique em **🔒 Bloquear** para limpar a seed da memória.

---

## Segurança

- O xpub exportado **não permite gastar fundos** — somente ver o saldo e gerar endereços
- O xpub **expõe o histórico e todos os endereços futuros** da carteira. Compartilhe apenas
  com dispositivos/apps de sua confiança
- Para gastar, é sempre necessária a assinatura do PhantOS com a seed física

---

## Apps compatíveis

| App | Plataforma | Formato suportado |
| --- | --- | --- |
| BlueWallet | iOS, Android | xpub / zpub / descriptor |
| Sparrow Wallet | Windows, macOS, Linux | Descriptor (recomendado) |
| Electrum | Windows, macOS, Linux | xpub / zpub |
| Nunchuk | iOS, Android, desktop | Descriptor / QR animado |
| Bitcoin Core (com descriptors) | Windows, macOS, Linux | Descriptor |
