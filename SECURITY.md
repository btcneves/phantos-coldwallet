# Política de Segurança

## Versões suportadas

| Versão | Suporte de segurança |
| ------ | -------------------- |
| 0.2.x  | Sim, no branch de desenvolvimento beta |
| 0.1.x  | Sim, para a release pública atual enquanto 0.2.x não for publicado |

## Reportando vulnerabilidades

**Não abra issues públicas para vulnerabilidades de segurança.**

Use um dos canais abaixo:

1. **GitHub Security Advisory (preferencial):** Acesse a aba *Security* do repositório e clique em *Report a vulnerability* para abrir um advisory privado.
2. **Contato direto:** Envie mensagem ao mantenedor listado no perfil do repositório.

### O que incluir no relatório

- Descrição clara da vulnerabilidade
- Passos para reproduzir
- Impacto estimado (ex: exposição de seed, bypass de validação)
- Versão afetada

### O que NÃO incluir

- Seeds reais, xpubs reais, chaves privadas ou PSBTs com fundos reais
- Transações Bitcoin reais
- Dados pessoais de terceiros

## Princípios de segurança do projeto

- **Offline por padrão:** a aplicação não faz requisições de rede, não consulta saldo e não transmite transações.
- **Amnésico por padrão:** nenhuma informação sensível é persistida em disco sem consentimento explícito.
- **Seed nunca em log:** o código não usa `logging` na aplicação; `safe_event()` redige termos sensíveis em eventos de UI.
- **Assinatura sempre revisada:** toda PSBT exige revisão humana antes da assinatura.
- **Validação offline:** a ISO deve executar `/usr/local/bin/phantos-harden-network` como root e pode ser verificada com `/usr/local/bin/phantos-verify-live-hardening`.
- **Taproot/PSBTv2 experimentais:** não recomendados para valores altos até auditoria externa.

## Documentos relacionados

- [AUDIT_READINESS.md](AUDIT_READINESS.md)
- [VERIFY_RELEASE.md](VERIFY_RELEASE.md)
- [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)
- [PSBT_COMPATIBILITY.md](PSBT_COMPATIBILITY.md)
- [docs/VALIDATION_REPORT.md](docs/VALIDATION_REPORT.md)

## Aviso importante

O código de desenvolvimento 0.2.0 concluiu o ciclo de endurecimento interno: zeroização real de seed com
`bytearray` + `mlock`, verificação offline real via `/sys/class/net` e `rfkill`,
gate de assinatura no core, e hardening do SO na ISO (swap, core dumps, sysctl).

O projeto **ainda não foi auditado externamente**. A v1.0.0 estável só será declarada
após auditoria independente publicada. Evite valores que não pode perder até lá.

A segurança de uma cold wallet depende também do ambiente de execução (hardware,
firmware, BIOS/UEFI, teclado, câmera). O PhantOS não pode garantir a integridade
do hardware subjacente — use hardware de confiança e verifique o pendrive antes de cada uso.
