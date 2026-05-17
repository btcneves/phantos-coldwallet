# Contribuindo com o PhantOS ColdWallet

Obrigado pelo interesse em contribuir. Este projeto é uma Bitcoin cold wallet de uso real — qualquer mudança no núcleo criptográfico exige atenção redobrada.

## Antes de abrir uma issue ou PR

- Verifique se já existe uma issue aberta para o mesmo problema.
- Para mudanças grandes, abra uma issue primeiro para discutir a abordagem.
- Para correções de segurança, use um [Security Advisory privado](https://docs.github.com/pt/code-security/security-advisories) em vez de uma issue pública.

## Configurando o ambiente de desenvolvimento

```bash
git clone https://github.com/btcneves/phantos-coldwallet.git
cd phantos-coldwallet
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Ou simplesmente:

```bash
./scripts/run_dev.sh
```

## Antes de abrir um PR

1. Rode os testes: `pytest`
2. Rode o linter: `ruff check .`
3. Rode o type checker: `mypy app/`
4. Certifique-se de que nenhum teste novo ou existente falha.
5. Execute a verificação pública: `bash scripts/check_public_clean.sh`
6. Execute ShellCheck se modificar scripts: `shellcheck scripts/*.sh`

## Atualizar o lockfile de dependências

O `requirements.lock` contém todas as dependências de runtime com hashes SHA-256. Para atualizá-lo após mudanças no `pyproject.toml`:

```bash
source .venv/bin/activate
pip install pip-tools
pip-compile --generate-hashes --no-annotate --no-header pyproject.toml -o requirements.lock
```

Após regenerar, adicione o cabeçalho com comentário ao topo do arquivo e atualize `CHANGELOG.md`.

## Regras de segurança (obrigatórias)

- Nunca registre seeds, passphrases, xprvs, chaves privadas ou PSBTs completas em logs ou saídas de debug.
- Nunca adicione telemetria, serviços online, callbacks externos ou dependências que transmitam dados pela rede.
- Nunca inclua seeds reais, xpubs reais ou transações reais em testes — use apenas vetores públicos conhecidos (ex: BIP39 "abandon…").
- Prefira bibliotecas Bitcoin maduras e amplamente auditadas em vez de implementações manuais de criptografia.
- Mudanças em assinatura, PSBT, derivação HD, descriptors, seed ou passphrase exigem testes com vetores conhecidos e justificativa técnica explícita.

## Documentação de mudanças de segurança

Qualquer mudança que afete o modelo de segurança deve ser documentada em:

- [`docs/seguranca.md`](docs/seguranca.md)
- [`docs/threat-model.md`](docs/threat-model.md)

## Estilo de código

- Python 3.12+, tipagem estática via `mypy`.
- `ruff` para formatação e linting (configurado em `pyproject.toml`).
- Sem comentários que expliquem o óbvio — o código deve ser autoexplicativo.
- Sem features desnecessárias além do escopo do PR.

## Licença

Ao contribuir, você concorda que sua contribuição será licenciada sob a [MIT License](LICENSE).
