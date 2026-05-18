# Roadmap

Status atual: **v1.0.0 lançada** — base funcional com hardening interno completo. Auditoria de segurança externa ainda não realizada.

---

## v1.0.0 — Lançada

- [x] Bitcoin Core regtest PSBT roundtrip automatizado
- [x] Fixtures de PSBTs reais em signet para carteiras externas
- [x] Matriz inicial de compatibilidade de PSBT cross-wallet
- [x] Silenciar prints de debug no vendor UR (`fountain_decoder.py`)
- [x] Hardening de memória de SO: swap, core dumps e tmpfs no live system
- [x] Melhoria da estimativa de vbytes por tipo de input, com aviso quando incerta
- [x] Preparar geração local de SBOM para releases
- [x] Scripts de validação de ISO, QEMU, release, USB protegido e hardening live
- [x] Build da ISO como workflow manual/agendado no CI
- [x] Coleta interativa de QR animado multipart (UR fountain codes) na câmera
- [x] Internacionalização EN-US completa na UI
- [x] Janelas completamente frameless (FramelessWindowHint + openbox decor:no)
- [x] Dialogs centralizados em `app/ui/dialogs.py`
- [x] Fix overflow HOT WALLET na interface
- [x] Patches embit v0.8.0 aplicados no build ISO

## v1.1.x — Compatibilidade e UX

- [ ] Fluxo guiado para BlueWallet, Sparrow e Electrum (capturas de tela inline)
- [ ] Verificação manual documentada de import/export com Sparrow, Electrum e BlueWallet
- [ ] Revisão melhorada de taxas (vbytes reais pós-assinatura)
- [ ] Reconhecimento automático de troco aprimorado
- [ ] Taproot/BIP86 em modo avançado com aviso explícito
- [ ] Verificação de compatibilidade de descriptors em Sparrow e Electrum
- [ ] Release assinado com chave GPG pública verificável

## v1.2.x — ISO e distribuição

- [ ] ISO Debian reprodutível (hash bit-a-bit verificável)
- [ ] Pendrive físico gravado, lido, bootado e documentado
- [ ] Script de geração de pendrive para Windows (via PowerShell ou GUI)
- [ ] Suporte a Secure Boot (shim assinado)

## v2.0.0 — Multisig e auditoria

- [ ] Auditoria de segurança externa e independente
- [ ] Suporte multisig (descriptors `multi()` e `sortedmulti()`)
- [ ] PSBTv2 estável e totalmente suportado
- [ ] Persistência criptografada opcional (LUKS ou VeraCrypt)
- [ ] Builds reprodutíveis verificados por terceiros

---

> Este roadmap é orientativo. Prioridades podem mudar conforme contribuições e feedback da comunidade.
> Contribuições são bem-vindas — veja [CONTRIBUTING.md](CONTRIBUTING.md).
