# Release Process

Releases devem ser manuais, revisadas e sem publicação automática.

## Antes de Criar Release

```bash
git status
git diff
ruff check .
ruff format --check .
mypy app/
pytest
scripts/check_public_clean.sh
python scripts/validate_wallet_flow.py
```

Se scripts forem alterados:

```bash
shellcheck scripts/*.sh
```

Quando disponíveis:

```bash
bandit -q -r app scripts
pip-audit -r requirements.lock
osv-scanner --lockfile=requirements.lock
gitleaks detect --no-git --redact
```

## Tag

Use tag assinada:

```bash
git tag -s v<versão> -m "PhantOS ColdWallet v<versão>"
git tag -v v<versão>
```

## Artefatos

Gerar artefatos de release da ISO validada:

```bash
bash scripts/validate_iso_artifact.sh phantos-coldwallet-<versão>-amd64.iso
bash scripts/test_iso_qemu.sh phantos-coldwallet-<versão>-amd64.iso
bash scripts/release_artifacts.sh phantos-coldwallet-<versão>-amd64.iso
```

O script cria:

- `build/release/SHA256SUMS`
- `build/release/SHA512SUMS`
- `build/release/SHA256SUMS.asc` se GPG estiver configurado
- `build/release/SHA256SUMS.minisig` se minisign estiver configurado
- `build/release/sbom.cdx.json` se `cyclonedx-py` estiver instalado
- `build/release/RELEASE_VALIDATION.md`

Se assinatura não for gerada, registre como SKIPPED. Não marcar como PASS.

## Publicação

- Não publicar a partir de CI automaticamente.
- Revisar nomes, hashes e assinaturas antes de anexar artefatos.
- Incluir `VERIFY_RELEASE.md` no texto do release.
- Não declarar suporte estável, auditoria concluída ou compatibilidade total sem evidência.
