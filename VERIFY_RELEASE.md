# Verify a Release

Use apenas artefatos obtidos da página oficial de releases do projeto.

## 1. Baixar Artefatos

Baixe, no mínimo:

- ISO ou pacote a verificar.
- `SHA256SUMS`.
- `SHA512SUMS`.
- Arquivo de assinatura, quando publicado.
- SBOM, quando publicado.

## 2. Verificar Checksums

```bash
sha256sum -c SHA256SUMS
sha512sum -c SHA512SUMS
```

Todos os arquivos devem retornar `OK`.

## 3. Verificar Assinatura

Com GPG:

```bash
gpg --verify SHA256SUMS.asc SHA256SUMS
```

Com minisign:

```bash
minisign -Vm SHA256SUMS -P "<public-key>"
```

Confirme a fingerprint da chave por um canal independente antes de confiar no artefato.

## 4. Verificar Tag

```bash
git fetch --tags origin
git tag -v v0.x.y
git checkout v0.x.y
```

Se a tag não for assinada ou se a assinatura não for verificável, trate o release como artefato de desenvolvimento.

## 5. Gravar ISO

Identifique o dispositivo com `lsblk`. Substitua `/dev/sdX` pelo dispositivo inteiro, não por uma partição.

Prefira o script protegido:

```bash
sudo PHANTOS_CONFIRM_WIPE="CONFIRMO APAGAR ESTE DISPOSITIVO" \
  bash scripts/write_usb.sh phantos-coldwallet-0.x.y-amd64.iso /dev/sdX
```

Remova e reconecte o pendrive após a gravação.

## 6. Confirmar Uso Offline

Após bootar:

- Não conecte cabo de rede.
- Não conecte Wi-Fi.
- Verifique a barra de status offline da aplicação.
- Execute `/usr/local/bin/phantos-harden-network` se estiver em terminal root.
- Execute `/usr/local/bin/phantos-verify-live-hardening` para validar swap, core dumps, rede, serviços e nftables.
- Assinatura deve ser recusada se rede, rota padrão, Wi-Fi ou Bluetooth estiverem ativos.

## Limitação

Checksums e assinaturas verificam integridade do artefato publicado. Eles não comprovam segurança do hardware, firmware, cadeia de build completa ou ausência de vulnerabilidades.
