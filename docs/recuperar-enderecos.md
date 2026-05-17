# Recuperar enderecos

A tela de recuperacao deriva os principais padroes:

- BIP84 Native SegWit: `m/84'/0'/0'`, enderecos `bc1q`.
- BIP49 Nested SegWit: `m/49'/0'/0'`, enderecos `3`.
- BIP44 Legacy: `m/44'/0'/0'`, enderecos `1`.
- BIP86 Taproot: `m/86'/0'/0'`, enderecos `bc1p`.

O PhantOS nao consulta saldo. Exporte uma carteira observadora para encontrar
enderecos usados em um dispositivo online.

