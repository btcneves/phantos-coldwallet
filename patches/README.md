# Patches de Segurança — embit v0.8.0

Este diretório contém correções de segurança aplicadas ao embit v0.8.0 como dependência
do PhantOS ColdWallet. As correções NÃO estão upstream — precisam ser reaplicadas após
qualquer `pip install` ou `pip install --upgrade`.

## Resumo das Correções

| ID | Arquivo | Severidade | Descrição |
|----|---------|-----------|-----------|
| A-01 | `util/key.py` | ALTO | `random.randrange` → `os.urandom(32)` |
| A-02 | `util/secp256k1.py` | ALTO | fallback silencioso → `warnings.warn` |
| A-03 | `util/ctypes_secp256k1.py` | ALTO | malleable ECDSA → `ecdsa_signature_normalize` |
| A-04 | `util/ctypes_secp256k1.py` | ALTO | `argtypes` faltando para `signature_normalize` |
| A-05 | `bip85.py` | ALTO | `assert` → `if/raise` |
| A-07 | `psbt.py` | ALTO | offset fixo substituído por parsing sequencial |
| A-08 | `psbtview.py` | ALTO | offset fixo de input → parsing sequencial |
| A-09 | `compact.py` + `script.py` | ALTO | varint com cap para evitar OOM |
| B-01–09 | vários | MÉDIO | ver audit report |
| M-01–14 | vários | MÉDIO/BAIXO | ver audit report |
| CRYPTO-01 | `util/ctypes_secp256k1.py` | MÉDIO | `ec_privkey_tweak_add` não mutava cópia |
| CRYPTO-02 | `util/ctypes_secp256k1.py` | ALTO | argtype errado → heap corruption |
| CRYPTO-03 | `util/py_secp256k1.py` | MÉDIO | `ec_privkey_negate(zero)` retornava ORDER |
| CRYPTO-07 | `util/key.py` + `util/py_secp256k1.py` | BAIXO | `sign_schnorr` retornava None silenciosamente |
| CRYPTO-08 | `bip39.py` | BAIXO | lookup O(n²) → O(n) com idx_map |
| CRYPTO-09 | `util/py_secp256k1.py` | MÉDIO | `ec_pubkey_add` retornava None em ponto no infinito |
| psbt.py | `psbt.py` | — | warning adicionado para `witness_utxo` sem `non_witness_utxo` |

## Aplicação do Patch

```bash
scripts/apply_embit_patch.sh
```

O script detecta automaticamente o `.venv` do projeto e aplica o patch.

## Verificação Pós-Aplicação

```bash
.venv/bin/python -m pytest tests/ -q --tb=short
# Esperado: 176 passed, 0 warnings
```

## Geração de Novo Patch (após modificações)

```bash
# 1. Baixar fonte original
pip download embit==0.8.0 --no-deps -d /tmp/embit_src
tar xzf /tmp/embit_src/embit-0.8.0.tar.gz -C /tmp/embit_orig

# 2. Gerar diff
diff -rpu --exclude="__pycache__" --exclude="*.pyc" \
    /tmp/embit_orig/embit-0.8.0/src/embit \
    .venv/lib/python*/site-packages/embit \
    > patches/embit-0.8.0-phantos-security.patch
```
