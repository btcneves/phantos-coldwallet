# UR Encoding

Para QR animado moderno, PhantOS usa UR Encoding `ur:crypto-psbt/...`.

QR simples funciona para payloads pequenos. PSBTs grandes devem usar UR multipart
com fountain codes para tolerar perda de frames.

O codigo multipart inicial e vendorizado da Foundation Devices e preserva a
licenca original em `app/ur/vendor/foundation_ur/LICENSE`.

