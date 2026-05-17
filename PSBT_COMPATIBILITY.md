# PSBT Compatibility

Status: product-readiness validation. This file is evidence-based and does not claim broad wallet interoperability until each flow is tested.

## Formats

| Format | Status | Evidence |
| --- | --- | --- |
| PSBT base64 | PASS | Unit tests and Bitcoin Core regtest roundtrip |
| PSBT binary | PASS | Unit parser tests |
| PSBT hex | PASS | Unit parser tests; hex is an accepted PhantOS input encoding, not a separate normative PSBT serialization |
| UR `crypto-psbt` single-part | PASS | Unit roundtrip |
| UR `crypto-psbt` multipart | PASS in core, PARTIAL in UI | Core handles shuffled/duplicate parts; animated QR collection still limited |
| PSBTv2 | PARTIAL | Detected and warned as experimental |
| Taproot/BIP86 | PARTIAL | Address derivation and warnings tested; real key-path signing still pending |

## Wallet Matrix

| Wallet | Status | Evidence | Notes |
| --- | --- | --- | --- |
| Bitcoin Core regtest | PASS | `bash scripts/regtest_psbt_roundtrip.sh` | Docker regtest only, no real funds |
| Sparrow | MANUAL REQUIRED | Not executed | Generate signet/regtest PSBT and record version |
| Electrum | MANUAL REQUIRED | Not executed | Validate xpub/ypub/zpub import and PSBT export |
| BlueWallet | MANUAL REQUIRED | Not executed | Validate mobile watch-only and PSBT file flow |
| Keystone | SKIPPED | Not available in this environment | External UR QR validation pending |
| Passport | SKIPPED | Not available in this environment | External UR QR validation pending |
| Specter | SKIPPED | Not available in this environment | External UR QR validation pending |

## Malicious and Edge Cases Covered

- Missing UTXO blocks signing.
- Negative fee blocks signing.
- Wrong fingerprint blocks signing.
- Correct fingerprint with wrong derivation path blocks signing.
- Signable input with mismatched UTXO script blocks signing.
- Duplicate prevout blocks signing.
- Partially signable PSBT warns.
- Unknown change warns.
- Dust output warns.
- OP_RETURN/non-address output warns.
- PSBTv2 warns.
- Taproot input warns.
- High absolute fee and high fee rate warn.
- UR multipart rejects missing, mixed-type or corrupted parts.

## Rules

- Use only regtest, signet or public deterministic fixtures.
- Do not add PSBTs with real funds.
- Do not claim wallet compatibility without a recorded PASS row.
- Keep Taproot, PSBTv2 and external UR interoperability marked PARTIAL until validated with real fixtures.
