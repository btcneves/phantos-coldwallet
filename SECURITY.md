# Política de Segurança

## Versões suportadas

| Versão | Suporte de segurança          |
| ------ | ----------------------------- |
| 1.0.0  | Sim — release estável atual   |
| 0.2.x  | Não — substituída por v1.0.0  |
| 0.1.x  | Não — substituída por v1.0.0  |

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

A v1.0.0 concluiu quatro rodadas de auditoria de segurança interna: zeroização real de seed com
`bytearray` + `mlock`, verificação offline real via `/sys/class/net` e `rfkill`,
gate de assinatura no core, hardening do SO na ISO (swap, core dumps, sysctl) e
aplicação de 40+ patches no embit v0.8.0.

O projeto **ainda não foi auditado externamente**. A auditoria independente está prevista
antes da v2.0.0. Evite valores que não pode perder até a conclusão dessa auditoria.

A segurança de uma cold wallet depende também do ambiente de execução (hardware,
firmware, BIOS/UEFI, teclado, câmera). O PhantOS não pode garantir a integridade
do hardware subjacente — use hardware de confiança e verifique o pendrive antes de cada uso.
