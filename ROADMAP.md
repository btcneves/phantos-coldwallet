# Roadmap

Status atual: **Beta** — base funcional, não auditada para valores altos.

---

## v0.1.x — Estabilização

- [x] Bitcoin Core regtest PSBT roundtrip automatizado
- [x] Testes com PSBTs reais exportadas por Sparrow, Electrum e BlueWallet
- [x] Fixtures de PSBTs reais em signet para carteiras externas
- [ ] Verificação de compatibilidade de descriptors em Sparrow e Electrum
- [x] Silenciar prints de debug no vendor UR (`fountain_decoder.py`)
- [x] Hardening de memória de SO: swap, core dumps e tmpfs no live system
- [x] Melhoria da estimativa de vbytes por tipo de input, com aviso quando incerta
- [x] Matriz inicial de compatibilidade de PSBT cross-wallet
- [x] Preparar geração local de SBOM para releases
- [x] Scripts de validação de ISO, QEMU, release, USB protegido e hardening live
- [ ] Publicar releases assinadas com chave GPG pública verificável
- [x] Build da ISO como workflow manual/agendado no CI (não por PR — custo de tempo e recursos)

## v0.2.x — Interface e UX

- [ ] Fluxo guiado para BlueWallet, Sparrow e Electrum (capturas de tela inline)
- [x] Coleta interativa de QR animado multipart (UR fountain codes) na câmera
- [ ] Revisão melhorada de taxas (vbytes reais pós-assinatura)
- [ ] Reconhecimento automático de troco aprimorado
- [ ] Taproot/BIP86 em modo avançado com aviso explícito
- [x] Internacionalização EN-US completa na UI

## v0.3.0 — ISO e distribuição

- [ ] ISO Debian reconstruída e validada a partir do commit de release
- [ ] ISO Debian reprodutível (hash bit-a-bit verificável)
- [ ] Releases assinadas com chave GPG pública
- [ ] Pendrive físico gravado, lido, bootado e documentado
- [ ] Kiosk mode robusto: splash screen, timeout de sessão, limpeza de memória
- [ ] Suporte a Secure Boot (shim assinado)
- [ ] Script de geração de pendrive para Windows (via PowerShell ou GUI)

## v1.0.0 — Estável e auditado

- [ ] Auditoria de segurança externa e independente
- [ ] Persistência criptografada opcional (LUKS ou VeraCrypt)
- [ ] Suporte multisig (descriptors `multi()` e `sortedmulti()`)
- [ ] PSBTv2 estável
- [ ] Documentação completa PT-BR e EN-US
- [ ] Builds reprodutíveis verificados por terceiros

---

> Este roadmap é orientativo. Prioridades podem mudar conforme contribuições e feedback da comunidade.
> Contribuições são bem-vindas — veja [CONTRIBUTING.md](CONTRIBUTING.md).
