# Arquitetura

Camadas principais:

- `app/wallet`: BIP39, BIP32, derivacao e watch-only.
- `app/descriptors`: descriptors e checksum.
- `app/psbt`: parser, revisao e assinatura offline.
- `app/qr`: QR simples.
- `app/ur`: UR `crypto-psbt` single/multipart.
- `app/security`: status offline e redacao de logs.
- `app/ui`: interface PySide6.

Segredos ficam em memoria e nao devem atravessar logs ou arquivos persistentes.

