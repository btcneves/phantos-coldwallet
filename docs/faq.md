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

## Por que não há barra de título nas janelas?

Por design de segurança e estabilidade no ambiente kiosk do pendrive bootável.

O PhantOS roda em openbox configurado como kiosk, onde decorações de janela
(barra de título, botões de minimizar/maximizar) causam comportamentos
imprevisíveis e podem expor controles operáveis por outros processos.

Todas as janelas — incluindo diálogos de QR, câmera e mensagens de sistema —
aplicam `Qt.WindowType.FramelessWindowHint`, removendo a decoração
completamente. O openbox reforça isso com `<decor>no</decor>` globalmente.

Para fechar uma janela ou diálogo, use o botão correspondente dentro da própria
interface (ex.: botão **Fechar**, **Cancelar** ou **OK**).

## Por que é v1.0.0 e não requer auditoria externa para uso?

A v1.0.0 completou 4 rodadas de endurecimento interno (memória, rede, SO, CI) e 188+
testes automatizados. As principais proteções estão implementadas e validadas:

- Isolamento de rede verificado em runtime (gate de assinatura)
- Patch de segurança embit v0.8.0 (40+ vulnerabilidades corrigidas)
- Seed em memória protegida (mlock + zeroização)
- CI completo: bandit, pip-audit, OSV Scanner, gitleaks, ShellCheck

Para uso com valores significativos, consulte [AUDIT_READINESS.md](../AUDIT_READINESS.md)
e [KNOWN_LIMITATIONS.md](../KNOWN_LIMITATIONS.md). Auditoria externa está prevista para
uma release futura. Veja [ROADMAP.md](../ROADMAP.md).
