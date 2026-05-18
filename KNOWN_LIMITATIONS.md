# Known Limitations

## Auditoria e versão

- **Sem auditoria externa concluída.** A v1.0.0 foi lançada após ciclo interno de endurecimento e cobertura
  de testes, mas sem revisão de segurança independente publicada. Não deve ser usada para custodiar valores
  altos sem revisão externa realizada. Veja [AUDIT_READINESS.md](AUDIT_READINESS.md) para o escopo preparado.

## Diferença em relação a hardware wallets

PhantOS usa isolamento por SO endurecido (sistema live, sem disco, sem swap, sem rede).
Hardware wallets dedicadas usam hardware de propósito específico; algumas usam
*secure element* ou chips seguros para reduzir a exposição das chaves.

Ambos são modelos legítimos de cold wallet. A diferença é o mecanismo de isolamento,
não a capacidade de uso.

## Memória Python

- `str` e `bytes` são imutáveis em CPython — não é possível zerá-los diretamente.
- **Mitigado em v0.2.0:** o seed é mantido em `bytearray`, bloqueado em RAM com
  `mlock` e zerado no bloco `finally` de `create_wallet_context()`.
- Cópias internas da biblioteca `embit` (objetos `bytes`) permanecem fora deste
  controle. O sistema live desativa swap, reduzindo o risco de exposição em disco.

## Compatibilidade PSBT

- Bitcoin Core regtest roundtrip: **passou**.
- Sparrow, Electrum e BlueWallet: exigem validação com fixtures reais em
  regtest/signet (item P1 — pendente de ambiente externo).
- PSBTv2 e Taproot/BIP86: **experimentais**, interceptados pela UI com aviso.

## Build e release

- Build da ISO exige root e `live-build`; não é bit-a-bit reprodutível (item P1).
- Assinatura GPG/minisign do release depende de chave de mantenedor configurada.
- A UI suporta PT-BR e EN-US; traduções adicionais não estão planejadas para v1.x.

## Multisig

- Multisig ainda não é suportado nativamente. PSBT de multisig pode ser importado
  para revisão, mas assinatura como co-assinante M-de-N não foi implementada.
