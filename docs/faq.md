# FAQ

## O que é o PhantOS ColdWallet?

Uma cold wallet Bitcoin que roda de um pendrive. Você boota, restaura sua seed (ou
gera uma nova), deriva endereços, assina transações offline e desliga. Nada é salvo
em disco. A cada boot o sistema começa do zero — é assim por design.

Serve para qualquer pessoa: desde quem nunca usou Bitcoin até quem quer verificar
cada detalhe técnico do código.

## O PhantOS mostra saldo?

Não. A carteira opera offline. Instale uma carteira observadora online (Sparrow,
Electrum, BlueWallet) com o xpub ou descriptor exportado pelo PhantOS para acompanhar
saldo e criar PSBTs para assinar.

## O PhantOS transmite transações?

Não. Ele assina PSBTs offline. A transmissão ocorre em outro dispositivo com acesso à
rede — geralmente a carteira observadora que criou a transação.

## Posso perder fundos se esquecer a passphrase?

Sim. Passphrase perdida não tem recuperação. Guarde a seed e a passphrase em locais
físicos separados e seguros — papel, metal, cofre.

## A carteira observadora pode gastar?

Não. Ela contém apenas dados públicos (xpub, descriptors) usados para monitorar saldo
e criar transações não assinadas. Sem a seed, nenhum gasto é possível.

## PhantOS é uma cold wallet de verdade?

Sim. O modelo de segurança é isolamento por SO endurecido:

- Sistema live sem disco — nada persiste após o desligamento
- Rede desativada — Wi-Fi, Bluetooth e todas as interfaces bloqueadas
- Sem swap — reduz o risco de dados sensíveis irem para disco
- Buffer de seed controlado pelo PhantOS zerado após derivar as chaves (`bytearray` + `mlock`); cópias internas de Python/bibliotecas continuam sendo limitação conhecida
- Todo o código é aberto e auditável linha a linha

A diferença em relação a hardware wallets (Coldcard, Ledger, Trezor) é o mecanismo
de isolamento: elas usam hardware dedicado, e algumas usam *secure element* ou chips
seguros para reduzir a exposição das chaves. PhantOS usa isolamento por SO sobre
hardware de uso geral. Ambos são cold wallets legítimos com modelos distintos.

Quem prefere hardware wallet: quem quer hardware dedicado de único propósito e não
quer manter software próprio.

Quem prefere PhantOS: quem quer código aberto, auditável, que roda em qualquer
computador com um pendrive, sem custo adicional de hardware.

## Para que serve exatamente?

- **Gerar nova seed** — entropia do sistema (`secrets`), 12 ou 24 palavras BIP39
- **Restaurar backup** — inserir seed + passphrase para recuperar a carteira
- **Derivar endereços** — BIP84 (bc1q), BIP44 (1…), BIP49 (3…), BIP86 Taproot (bc1p)
- **Exportar watch-only** — xpub/descriptor para a carteira observadora online
- **Assinar transações** — importar PSBT via câmera ou arquivo, revisar e assinar
- **Exportar PSBT assinada** — QR animado UR `crypto-psbt` para transmissão

## Por que ainda é beta?

O código de desenvolvimento 0.2.0 completou o endurecimento interno (memória, rede, SO, CI). Falta para a
v1.0.0 estável:

- Auditoria de segurança externa com relatório publicado
- Validação de PSBT com Sparrow, Electrum e BlueWallet em ambiente real
- Build da ISO bit-a-bit reprodutível
- Assinatura GPG do release verificável

Veja [ROADMAP.md](../ROADMAP.md) e [AUDIT_READINESS.md](../AUDIT_READINESS.md).
