# Build ISO

Guia resumido. A documentação detalhada fica em `docs/build-iso.md`.

## Pré-requisitos

```bash
sudo apt install live-build debootstrap xorriso grub-efi-amd64-bin grub-pc-bin dosfstools rsync dpkg-dev
```

## Build

```bash
sudo ./scripts/build_iso.sh
```

O build requer internet para baixar pacotes Debian e dependências Python com hashes.

Valide o artefato gerado:

```bash
bash scripts/validate_iso_artifact.sh phantos-coldwallet-<versão>-amd64.iso
bash scripts/test_iso_qemu.sh phantos-coldwallet-<versão>-amd64.iso
```

Depois do boot, valide o live system:

```bash
sudo /usr/local/bin/phantos-verify-live-hardening
```

## Hardening Aplicado

O live system gerado:

- Desabilita serviços de rede desnecessários.
- Configura loopback apenas em `/etc/network/interfaces`.
- Desabilita swap.
- Remove entradas de swap em `/etc/fstab`.
- Bloqueia core dumps por `limits.d` e `sysctl`.
- Define `/tmp` em tmpfs com `nosuid,nodev,noexec`.
- Reduz superfície de kernel com sysctls conservadores.

## Limitações

- O build ainda não é bit-a-bit reprodutível.
- A ISO deve ser tratada como candidato de validação até checksums, assinatura, SBOM, validação de artefato e boot passarem no mesmo commit.
- Hardening de sistema não substitui hardware confiável.
