from __future__ import annotations

_PT_BR: dict[str, str] = {
    # ── Botões ──────────────────────────────────────────────────────────
    "btn.new_wallet": "⊕  Criar Carteira",
    "btn.restore_seed": "⟲  Restaurar Seed",
    "btn.recover_addresses": "⊙  Recuperar Endereços",
    "btn.export_watch_only": "⤴  Exportar Observadora",
    "btn.qr_wallet": "▦  QR Carteira",
    "btn.sign_psbt": "✎  Assinar PSBT",
    "btn.lock": "🔒  Bloquear",
    "btn.load_psbt": "⊞  Carregar .psbt",
    "btn.scan_qr": "◉  Escanear QR",
    # ── Formulário ──────────────────────────────────────────────────────
    "form.words": "Palavras:",
    "form.type": "Tipo:",
    "form.seed": "Seed BIP39:",
    "form.passphrase": "Passphrase:",
    # ── Placeholders ────────────────────────────────────────────────────
    "ph.mnemonic": "Digite as palavras BIP39 em inglês (seed phrase).",
    "ph.passphrase": "Opcional. Deixe vazio se não usava passphrase.",
    # ── Word picker ─────────────────────────────────────────────────────
    "seed.status.empty": "",
    "seed.status.progress": "{filled}/{total}",
    "seed.status.ok": "{total}/{total}  ✓  checksum OK",
    "seed.status.bad": "{filled}/{total}  ✗  checksum inválido",
    "ph.output": "Os resultados aparecerão aqui…",
    "ph.psbt": "Cole aqui a PSBT em base64, hex ou UR crypto-psbt.",
    # ── Cabeçalho ───────────────────────────────────────────────────────
    "hdr.subtitle": "por  btcneves  ·  Carteira Bitcoin offline de código aberto",
    # ── Barra de segurança ──────────────────────────────────────────────
    "sec.terminal": "₿  PHANTOS SECURE TERMINAL",
    "sec.net_blocked": "REDE: BLOQUEADA",
    "sec.net_nft_drop": "REDE: UP/NFT-DROP",
    "sec.net_active": "REDE: ATIVA",
    "sec.net_inactive": "REDE: INATIVA",
    "sec.wifi_blocked": "WiFi: BLOQUEADO",
    "sec.wifi_active": "WiFi: ATIVO",
    "sec.bt_blocked": "BT: BLOQUEADO",
    "sec.bt_active": "BT: ATIVO",
    "sec.offline_verified": "OFFLINE VERIFICADO",
    "sec.online_warning": "ATENÇÃO: ONLINE — assinatura bloqueada",
    # ── Diálogos de mensagem ─────────────────────────────────────────────
    "msg.write_down.title": "⚠  Anote em papel",
    "msg.write_down.body": (
        "Estas palavras controlam seus bitcoins.\n\n"
        "NUNCA tire foto. NUNCA salve em nuvem. NUNCA envie para ninguém.\n\n"
        "Anote em papel agora e guarde em local seguro.\n\n"
        "Após anotar, clique em '🔒 Bloquear' para limpar a tela."
    ),
    "msg.restore_error.title": "Erro — Não foi possível restaurar",
    "msg.locked.title": "🔒  Carteira bloqueada",
    "msg.locked.body": (
        "Todos os dados foram removidos da tela.\n\n"
        "Nota: Python não garante zeroização imediata de strings na memória RAM. "
        "Para segurança máxima, encerre a aplicação e reinicie o sistema após uso."
    ),
    "msg.recovery_error.title": "Erro — Recuperação falhou",
    "msg.psbt_invalid.title": "PSBT inválida",
    "msg.signing_blocked.title": "Assinatura bloqueada — dispositivo online",
    "msg.signing_blocked.body": (
        "A assinatura só é permitida quando o dispositivo está offline verificado.\n\n"
        "Problemas detectados:\n{detail}\n\n"
        "Execute scripts/harden_network.sh e tente novamente."
    ),
    "msg.cannot_sign.title": "Não foi possível assinar",
    "msg.psbtv2_warn.title": "PSBTv2 — Funcionalidade Experimental",
    "msg.psbtv2_warn.body": (
        "Esta PSBT usa o formato PSBTv2, que está em modo experimental.\n\n"
        "Suporte a PSBTv2 não foi auditado externamente.\n"
        "Não use com valores significativos até auditoria concluída.\n\n"
        "Deseja continuar mesmo assim?"
    ),
    "msg.confirm_sign.title": "₿  Confirmar Assinatura",
    "msg.sign_failed.title": "Assinatura falhou",
    "msg.taproot_warn.title": "Taproot — Modo Avançado Experimental",
    "msg.taproot_warn.body": (
        "BIP86 Taproot está em modo experimental e não foi auditado externamente.\n\n"
        "Limitações conhecidas:\n"
        "  • PSBTv2 (frequentemente usado com Taproot) também é experimental.\n"
        "  • Compatibilidade com todas as carteiras externas não está garantida.\n"
        "  • Não use com valores significativos até auditoria concluída.\n\n"
        "Se não souber o que é Taproot, selecione BIP84 Native SegWit (padrão)."
    ),
    "msg.qr_scanned.title": "QR escaneado",
    "msg.qr_scanned.body": "Conteúdo recebido mas não é PSBT válida: {exc}\n\n{text}",
    # ── Diálogos de arquivo ──────────────────────────────────────────────
    "dlg.load_psbt": "Carregar PSBT",
    "dlg.psbt_filter": "PSBT (*.psbt *.txt);;Todos (*)",
    # ── Saída de texto ───────────────────────────────────────────────────
    "out.wallet_loaded": "  CARTEIRA CARREGADA — MODO OFFLINE",
    "out.recv_addresses": "  ── Endereços de recebimento ──",
    "out.ext_descriptor": "  ── Descriptor externo ──",
    "out.ext_pubkey": "  ── Chave pública estendida ──",
    "out.fingerprint": "Fingerprint",
    "out.type": "Tipo",
    "out.path": "Caminho",
    "out.recovery": "  RECUPERAÇÃO DE ENDEREÇOS — TODOS OS TIPOS",
    "out.recovery_addr": "Endereço",
    "out.recovery_xpub": "XPub",
    "out.recovery_warning": (
        "  ⚠  Esta cold wallet não consulta saldo.\n     Use uma carteira observadora online."
    ),
    "out.psbt_signed": "  PSBT ASSINADA — PRONTO PARA TRANSMITIR",
    "out.sigs_added": "  Assinaturas adicionadas:",
    "out.ur_crypto": "  ── UR crypto-psbt (QR animado) ──",
    "out.psbt_review": "  REVISÃO DA PSBT",
    "out.inputs": "  Inputs :",
    "out.outputs": "  Outputs:",
    "out.sent": "  Enviado:",
    "out.fee": "  Taxa   :",
    "out.fee_rate": "  sat/vB :",
    "out.destinations": "  ── Destinos ──",
    "out.change_tag": "TROCO",
    "out.dest_tag": "DESTINO",
    "out.unknown_addr": "endereço desconhecido",
    "out.fee_unknown": "desconhecida",
    "out.warnings": "  ⚠  Alertas:",
    "out.errors": "  ✖  Bloqueios:",
    # ── Problemas na assinatura ──────────────────────────────────────────
    "iss.net_active": "interface de rede ativa",
    "iss.default_route": "rota padrão presente",
    "iss.wifi_unblocked": "Wi-Fi não bloqueado",
    "iss.bt_unblocked": "Bluetooth não bloqueado",
    "iss.services": "serviços: ",
    "iss.status_unverified": "status não verificado",
    # ── QR de carteira ───────────────────────────────────────────────────
    "qr.wallet.title": "QR — Carteira Observadora",
    "qr.wallet.scan_with": "Escaneie com Sparrow, BlueWallet ou Electrum.",
    "qr.wallet.type_kind": "Tipo: {profile}  ·  {kind}",
    "qr.wallet.kind_xpub": "xpub",
    "qr.wallet.kind_descriptor": "descriptor externo",
    "qr.animated.scan": (
        "Escaneie este QR animado com Sparrow, BlueWallet ou outra\n"
        "carteira online para transmitir a transação Bitcoin."
    ),
    # ── Diálogo de câmera ────────────────────────────────────────────────
    "cam.title": "Escanear QR Code com Câmera",
    "cam.no_multimedia": "QtMultimedia não disponível.\nInstale gstreamer1.0-plugins-good.",
    "cam.no_camera": "Nenhuma câmera detectada.\nConecte uma webcam USB e tente novamente.",
    "cam.status": "Aponte a câmera para o QR Code ou QR animado (UR)…",
    "cam.cancel": "Cancelar",
    "cam.ur_parts": "QR animado: {n} partes coletadas… continue escaneando",
    # ── Diálogos QR ──────────────────────────────────────────────────────
    "qr.close": "Fechar",
    "qr.animated.title": "QR Animado — PSBT Assinada",
    "qr.error_generate": "Erro ao gerar QR: ",
    "qr.animated.error": "Erro ao gerar QR animado.",
    "qr.animated.frame": "Frame {n} / {total}  —  Escaneie com a carteira observadora",
    # ── Confirmação de assinatura ────────────────────────────────────────
    "pres.sign_only_if": "Assine SOMENTE se todos os campos abaixo estiverem corretos.",
    "pres.fingerprint": "  Fingerprint :",
    "pres.profile": "  Perfil      :",
    "pres.path": "  Caminho     :",
    "pres.signable": "  Assináveis  :",
    "pres.spent": "  Valor enviado  :",
    "pres.change": "  Troco          :",
    "pres.fee": "  Taxa           :",
    "pres.fee_rate": "  Taxa/vB        :",
    "pres.size": "  Tamanho est.   :",
    "pres.destinations": "Destinos:",
    "pres.change_section": "Troco:",
    "pres.input_paths": "Paths dos inputs:",
    "pres.warnings": "Alertas:",
    "pres.confirm_question": "Deseja assinar offline agora?",
    "pres.unknown_addr": "endereço não reconhecido",
    "pres.unknown_val": "desconhecido",
    "pres.signable_yes": "sim",
    "pres.signable_no": "NÃO",
    "pres.input_path_unknown": "não reconhecido",
    "pres.fee_rate_suffix": " sat/vB",
    "pres.vbytes": "~{n} vB",
}

_EN_US: dict[str, str] = {
    # ── Buttons ──────────────────────────────────────────────────────────
    "btn.new_wallet": "⊕  New Wallet",
    "btn.restore_seed": "⟲  Restore Seed",
    "btn.recover_addresses": "⊙  Recover Addresses",
    "btn.export_watch_only": "⤴  Export Watch-Only",
    "btn.qr_wallet": "▦  QR Wallet",
    "btn.sign_psbt": "✎  Sign PSBT",
    "btn.lock": "🔒  Lock",
    "btn.load_psbt": "⊞  Load .psbt",
    "btn.scan_qr": "◉  Scan QR",
    # ── Form labels ──────────────────────────────────────────────────────
    "form.words": "Words:",
    "form.type": "Type:",
    "form.seed": "BIP39 Seed:",
    "form.passphrase": "Passphrase:",
    # ── Placeholders ─────────────────────────────────────────────────────
    "ph.mnemonic": "Enter BIP39 words here (seed phrase — English words).",
    "ph.passphrase": "Optional. Leave empty if no passphrase was used.",
    # ── Word picker ───────────────────────────────────────────────────────
    "seed.status.empty": "",
    "seed.status.progress": "{filled}/{total}",
    "seed.status.ok": "{total}/{total}  ✓  checksum OK",
    "seed.status.bad": "{filled}/{total}  ✗  invalid checksum",
    "ph.output": "Results will appear here…",
    "ph.psbt": "Paste PSBT here in base64, hex, or UR crypto-psbt format.",
    # ── Header ───────────────────────────────────────────────────────────
    "hdr.subtitle": "by  btcneves  ·  Open-source offline Bitcoin wallet",
    # ── Security status bar ───────────────────────────────────────────────
    "sec.terminal": "₿  PHANTOS SECURE TERMINAL",
    "sec.net_blocked": "NET: BLOCKED",
    "sec.net_nft_drop": "NET: UP/NFT-DROP",
    "sec.net_active": "NET: ACTIVE",
    "sec.net_inactive": "NET: INACTIVE",
    "sec.wifi_blocked": "WiFi: BLOCKED",
    "sec.wifi_active": "WiFi: ACTIVE",
    "sec.bt_blocked": "BT: BLOCKED",
    "sec.bt_active": "BT: ACTIVE",
    "sec.offline_verified": "OFFLINE VERIFIED",
    "sec.online_warning": "WARNING: ONLINE — signing blocked",
    # ── Message boxes ────────────────────────────────────────────────────
    "msg.write_down.title": "⚠  Write Down Now",
    "msg.write_down.body": (
        "These words control your bitcoins.\n\n"
        "NEVER take a photo. NEVER save to the cloud. NEVER share with anyone.\n\n"
        "Write them down on paper now and store in a safe place.\n\n"
        "After writing, click '🔒 Lock' to clear the screen."
    ),
    "msg.restore_error.title": "Error — Unable to Restore",
    "msg.locked.title": "🔒  Wallet Locked",
    "msg.locked.body": (
        "All data has been removed from the screen.\n\n"
        "Note: Python does not guarantee immediate zeroing of strings in RAM. "
        "For maximum security, close the application and restart the system after use."
    ),
    "msg.recovery_error.title": "Error — Recovery Failed",
    "msg.psbt_invalid.title": "Invalid PSBT",
    "msg.signing_blocked.title": "Signing Blocked — Device Online",
    "msg.signing_blocked.body": (
        "Signing is only allowed when the device is verified offline.\n\n"
        "Issues detected:\n{detail}\n\n"
        "Run scripts/harden_network.sh and try again."
    ),
    "msg.cannot_sign.title": "Unable to Sign",
    "msg.psbtv2_warn.title": "PSBTv2 — Experimental Feature",
    "msg.psbtv2_warn.body": (
        "This PSBT uses the PSBTv2 format, which is in experimental mode.\n\n"
        "PSBTv2 support has not been externally audited.\n"
        "Do not use with significant amounts until an audit is complete.\n\n"
        "Do you want to continue anyway?"
    ),
    "msg.confirm_sign.title": "₿  Confirm Signature",
    "msg.sign_failed.title": "Signing Failed",
    "msg.taproot_warn.title": "Taproot — Experimental Advanced Mode",
    "msg.taproot_warn.body": (
        "BIP86 Taproot is in experimental mode and has not been externally audited.\n\n"
        "Known limitations:\n"
        "  • PSBTv2 (frequently used with Taproot) is also experimental.\n"
        "  • Compatibility with all external wallets is not guaranteed.\n"
        "  • Do not use with significant amounts until an audit is complete.\n\n"
        "If you are unsure about Taproot, select BIP84 Native SegWit (default)."
    ),
    "msg.qr_scanned.title": "QR Scanned",
    "msg.qr_scanned.body": "Content received but not a valid PSBT: {exc}\n\n{text}",
    # ── File dialogs ─────────────────────────────────────────────────────
    "dlg.load_psbt": "Load PSBT",
    "dlg.psbt_filter": "PSBT (*.psbt *.txt);;All Files (*)",
    # ── Output text ──────────────────────────────────────────────────────
    "out.wallet_loaded": "  WALLET LOADED — OFFLINE MODE",
    "out.recv_addresses": "  ── Receive Addresses ──",
    "out.ext_descriptor": "  ── External Descriptor ──",
    "out.ext_pubkey": "  ── Extended Public Key ──",
    "out.fingerprint": "Fingerprint",
    "out.type": "Type",
    "out.path": "Path",
    "out.recovery": "  ADDRESS RECOVERY — ALL TYPES",
    "out.recovery_addr": "Address",
    "out.recovery_xpub": "XPub",
    "out.recovery_warning": (
        "  ⚠  This cold wallet does not check balances.\n     Use an online watch-only wallet."
    ),
    "out.psbt_signed": "  SIGNED PSBT — READY TO BROADCAST",
    "out.sigs_added": "  Signatures added:",
    "out.ur_crypto": "  ── UR crypto-psbt (animated QR) ──",
    "out.psbt_review": "  PSBT REVIEW",
    "out.inputs": "  Inputs :",
    "out.outputs": "  Outputs:",
    "out.sent": "  Sent   :",
    "out.fee": "  Fee    :",
    "out.fee_rate": "  sat/vB :",
    "out.destinations": "  ── Destinations ──",
    "out.change_tag": "CHANGE",
    "out.dest_tag": "DEST",
    "out.unknown_addr": "unknown address",
    "out.fee_unknown": "unknown",
    "out.warnings": "  ⚠  Warnings:",
    "out.errors": "  ✖  Blockers:",
    # ── Signing issues ────────────────────────────────────────────────────
    "iss.net_active": "active network interface",
    "iss.default_route": "default route present",
    "iss.wifi_unblocked": "Wi-Fi not blocked",
    "iss.bt_unblocked": "Bluetooth not blocked",
    "iss.services": "services: ",
    "iss.status_unverified": "status unverified",
    # ── QR wallet ────────────────────────────────────────────────────────
    "qr.wallet.title": "QR — Watch-Only Wallet",
    "qr.wallet.scan_with": "Scan with Sparrow, BlueWallet or Electrum.",
    "qr.wallet.type_kind": "Type: {profile}  ·  {kind}",
    "qr.wallet.kind_xpub": "xpub",
    "qr.wallet.kind_descriptor": "external descriptor",
    "qr.animated.scan": (
        "Scan this animated QR with Sparrow, BlueWallet or another\n"
        "online wallet to broadcast the Bitcoin transaction."
    ),
    # ── Camera dialog ─────────────────────────────────────────────────────
    "cam.title": "Scan QR Code with Camera",
    "cam.no_multimedia": "QtMultimedia not available.\nInstall gstreamer1.0-plugins-good.",
    "cam.no_camera": "No camera detected.\nConnect a USB webcam and try again.",
    "cam.status": "Point the camera at the QR Code or animated QR (UR)…",
    "cam.cancel": "Cancel",
    "cam.ur_parts": "Animated QR: {n} parts collected… keep scanning",
    # ── QR dialogs ────────────────────────────────────────────────────────
    "qr.close": "Close",
    "qr.animated.title": "Animated QR — Signed PSBT",
    "qr.error_generate": "Error generating QR: ",
    "qr.animated.error": "Error generating animated QR.",
    "qr.animated.frame": "Frame {n} / {total}  —  Scan with watch-only wallet",
    # ── Signing confirmation ───────────────────────────────────────────────
    "pres.sign_only_if": "Sign ONLY if all fields below are correct.",
    "pres.fingerprint": "  Fingerprint  :",
    "pres.profile": "  Profile      :",
    "pres.path": "  Path         :",
    "pres.signable": "  Signable     :",
    "pres.spent": "  Amount sent     :",
    "pres.change": "  Change          :",
    "pres.fee": "  Fee             :",
    "pres.fee_rate": "  Fee/vB          :",
    "pres.size": "  Est. size       :",
    "pres.destinations": "Destinations:",
    "pres.change_section": "Change:",
    "pres.input_paths": "Input paths:",
    "pres.warnings": "Warnings:",
    "pres.confirm_question": "Do you want to sign offline now?",
    "pres.unknown_addr": "unrecognized address",
    "pres.unknown_val": "unknown",
    "pres.signable_yes": "yes",
    "pres.signable_no": "NO",
    "pres.input_path_unknown": "unrecognized",
    "pres.fee_rate_suffix": " sat/vB",
    "pres.vbytes": "~{n} vB",
}

STRINGS: dict[str, dict[str, str]] = {
    "pt_BR": _PT_BR,
    "en_US": _EN_US,
}
