# Visão Geral — PhantOS ColdWallet v1.0.0

PhantOS ColdWallet é um ambiente offline e bootável via pendrive USB para criar
ou restaurar carteiras Bitcoin, derivar endereços, exportar carteiras observadoras
e assinar PSBTs — tudo sem contato com a internet.

O sistema roda Debian Bookworm live (não persiste dados em disco). A cada boot
começa do zero. A interface é construída em Python/PySide6 e inicializada
automaticamente via openbox kiosk.

**O PhantOS não:**

- Consulta saldo ou preços online.
- Transmite transações para a rede Bitcoin.
- É um nó Bitcoin completo.
- Armazena seeds ou chaves privadas em disco.

**Fluxo típico de uso:**

1. Boot pelo pendrive USB em um computador air-gapped.
2. Gerar nova seed (12 ou 24 palavras BIP39) ou restaurar backup.
3. Derivar endereços de recebimento (BIP44/49/84/86).
4. Exportar xpub ou descriptor para a carteira observadora online.
5. Quando necessário: importar PSBT via QR ou arquivo, revisar e assinar.
6. Exportar PSBT assinada via QR animado UR `crypto-psbt`.
7. Transmitir a PSBT assinada pela carteira observadora (Sparrow, Electrum, BlueWallet).
8. Desligar — nenhum dado permanece no disco.

