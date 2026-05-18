# Recuperar Endereços

A função **Recuperar Endereços** deriva e exibe o primeiro endereço de recebimento
de cada padrão suportado a partir da seed carregada. Use-a quando não souber qual
tipo de carteira foi usado originalmente ou para confirmar que a seed restaurada
corresponde à carteira esperada.

---

## Padrões derivados

| Tipo | Caminho de derivação | Endereços |
| --- | --- | --- |
| BIP84 Native SegWit | `m/84'/0'/0'` | `bc1q…` |
| BIP49 Nested SegWit | `m/49'/0'/0'` | `3…` |
| BIP44 Legacy | `m/44'/0'/0'` | `1…` |
| BIP86 Taproot | `m/86'/0'/0'` | `bc1p…` |

---

## Passo a passo

1. Restaure a seed no word picker (veja [Restaurar Seed e Passphrase](restaurar-seed-passphrase.md))
2. Se a carteira usava **passphrase**, informe no campo "Passphrase" antes de prosseguir
3. Clique em **⊙ Recuperar Endereços**
4. A tela exibe o primeiro endereço de cada tipo lado a lado
5. Compare com o endereço que você anotou ao criar a carteira — eles devem ser idênticos
6. Identifique o tipo correto e utilize-o ao restaurar a carteira completa

---

## Observações importantes

- O PhantOS **não consulta saldo**. A recuperação de endereços é local e offline.
- Para encontrar endereços usados e saldos, exporte a carteira observadora
  e importe-a em um app online (BlueWallet, Sparrow, Electrum).
  Veja [Exportar Carteira Observadora](exportar-carteira-observadora.md).
- Se nenhum dos endereços exibidos corresponder ao que você tem anotado,
  verifique se a **passphrase** está correta ou se a seed foi digitada na ordem certa.
- A derivação usa sempre a rede principal (mainnet). Endereços testnet não são exibidos nesta função.
