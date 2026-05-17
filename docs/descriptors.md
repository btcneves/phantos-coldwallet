# Descriptors

PhantOS prioriza output descriptors:

- Legacy: `pkh(...)`.
- Nested SegWit: `sh(wpkh(...))`.
- Native SegWit: `wpkh(...)`.
- Taproot: `tr(...)`.

Descriptors incluem fingerprint, caminho de conta, xpub canonico e checksum
alfanumerico de 8 caracteres no formato `SCRIPT#CHECKSUM` quando suportado.
