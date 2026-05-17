# Testes

Automatizados:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

Cobertura inicial:

- BIP39 valido/invalido;
- passphrase altera carteira;
- BIP44, BIP49, BIP84 e BIP86;
- descriptors e checksum;
- PSBT valida/invalida;
- assinatura PSBT;
- carteira errada;
- QR;
- UR single e multipart;
- status offline.

