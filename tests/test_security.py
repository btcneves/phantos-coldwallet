from __future__ import annotations

import subprocess
from unittest.mock import patch

from app.security import current_offline_status, safe_event
from app.security.core import OfflineStatus
from app.wallet import create_wallet_context

from tests.conftest import MNEMONIC

# ---------------------------------------------------------------------------
# current_offline_status — interface / route / rfkill / services
# ---------------------------------------------------------------------------


def test_offline_status_verified_when_all_checks_pass() -> None:
    with (
        patch("app.security.core._has_active_network_interface", return_value=False),
        patch("app.security.core._has_default_route", return_value=False),
        patch("app.security.core._is_rfkill_blocked", return_value=True),
        patch("app.security.core._has_nftables_drop_all", return_value=False),
        patch("app.security.core._find_suspicious_services", return_value=[]),
    ):
        status = current_offline_status()
    assert status.verified
    assert not status.network_active
    assert not status.has_default_route
    assert status.wifi_blocked
    assert status.bluetooth_blocked
    assert len(status.suspicious_services) == 0


def test_offline_status_not_verified_when_interface_is_up() -> None:
    with (
        patch("app.security.core._has_active_network_interface", return_value=True),
        patch("app.security.core._has_default_route", return_value=False),
        patch("app.security.core._is_rfkill_blocked", return_value=True),
        patch("app.security.core._has_nftables_drop_all", return_value=False),
        patch("app.security.core._find_suspicious_services", return_value=[]),
    ):
        status = current_offline_status()
    assert not status.verified
    assert status.network_active


def test_offline_status_not_verified_when_default_route_present() -> None:
    with (
        patch("app.security.core._has_active_network_interface", return_value=False),
        patch("app.security.core._has_default_route", return_value=True),
        patch("app.security.core._is_rfkill_blocked", return_value=True),
        patch("app.security.core._has_nftables_drop_all", return_value=False),
        patch("app.security.core._find_suspicious_services", return_value=[]),
    ):
        status = current_offline_status()
    assert not status.verified
    assert status.has_default_route


def test_offline_status_not_verified_when_wifi_unblocked() -> None:
    def rfkill_side(kind: str) -> bool:
        return kind not in ("wlan", "wifi")

    with (
        patch("app.security.core._has_active_network_interface", return_value=False),
        patch("app.security.core._has_default_route", return_value=False),
        patch("app.security.core._is_rfkill_blocked", side_effect=rfkill_side),
        patch("app.security.core._has_nftables_drop_all", return_value=False),
        patch("app.security.core._find_suspicious_services", return_value=[]),
    ):
        status = current_offline_status()
    assert not status.verified
    assert not status.wifi_blocked


def test_offline_status_not_verified_when_suspicious_service_active() -> None:
    with (
        patch("app.security.core._has_active_network_interface", return_value=False),
        patch("app.security.core._has_default_route", return_value=False),
        patch("app.security.core._is_rfkill_blocked", return_value=True),
        patch("app.security.core._has_nftables_drop_all", return_value=False),
        patch(
            "app.security.core._find_suspicious_services",
            return_value=["NetworkManager"],
        ),
    ):
        status = current_offline_status()
    assert not status.verified
    assert "NetworkManager" in status.suspicious_services


# ---------------------------------------------------------------------------
# _has_nftables_drop_all
# ---------------------------------------------------------------------------


def test_nftables_drop_all_returns_true_when_table_and_policy_present() -> None:
    from app.security.core import _has_nftables_drop_all

    ruleset = (
        "table inet phantos {\n"
        "  chain input { type filter hook input priority 0; policy drop; }\n"
        "  chain forward { type filter hook forward priority 0; policy drop; }\n"
        "  chain output { type filter hook output priority 0; policy drop; }\n"
        "}\n"
    )
    mock_result = subprocess.CompletedProcess(args=[], returncode=0, stdout=ruleset, stderr="")
    with (
        patch("shutil.which", return_value="/usr/sbin/nft"),
        patch("subprocess.run", return_value=mock_result),
    ):
        assert _has_nftables_drop_all() is True


def test_nftables_drop_all_returns_false_when_table_absent() -> None:
    from app.security.core import _has_nftables_drop_all

    ruleset = "table inet filter { chain input { policy accept; } }\n"
    mock_result = subprocess.CompletedProcess(args=[], returncode=0, stdout=ruleset, stderr="")
    with (
        patch("shutil.which", return_value="/usr/sbin/nft"),
        patch("subprocess.run", return_value=mock_result),
    ):
        assert _has_nftables_drop_all() is False


def test_nftables_drop_all_returns_false_when_nft_not_found() -> None:
    from app.security.core import _has_nftables_drop_all

    with patch("shutil.which", return_value=None):
        assert _has_nftables_drop_all() is False


def test_nftables_drop_all_returns_false_on_timeout() -> None:
    from app.security.core import _has_nftables_drop_all

    with (
        patch("shutil.which", return_value="/usr/sbin/nft"),
        patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="nft", timeout=3)),
    ):
        assert _has_nftables_drop_all() is False


def test_offline_verified_when_interface_up_but_nftables_drop_and_no_route() -> None:
    """Interface UP + nftables drop-all + no route → verified=True (defense-in-depth)."""
    with (
        patch("app.security.core._has_active_network_interface", return_value=True),
        patch("app.security.core._has_default_route", return_value=False),
        patch("app.security.core._is_rfkill_blocked", return_value=True),
        patch("app.security.core._has_nftables_drop_all", return_value=True),
        patch("app.security.core._find_suspicious_services", return_value=[]),
    ):
        status = current_offline_status()
    assert status.verified
    assert status.nftables_drop_active
    assert status.network_active  # interface still UP, but nftables covers it


def test_offline_not_verified_when_interface_up_nftables_but_has_route() -> None:
    """Interface UP + nftables + default route → verified=False (route is definitive risk)."""
    with (
        patch("app.security.core._has_active_network_interface", return_value=True),
        patch("app.security.core._has_default_route", return_value=True),
        patch("app.security.core._is_rfkill_blocked", return_value=True),
        patch("app.security.core._has_nftables_drop_all", return_value=True),
        patch("app.security.core._find_suspicious_services", return_value=[]),
    ):
        status = current_offline_status()
    assert not status.verified


# ---------------------------------------------------------------------------
# sign_psbt offline gate
# ---------------------------------------------------------------------------


def test_sign_psbt_blocked_when_not_offline_verified() -> None:
    from embit.psbt import PSBTError

    from app.psbt.core import sign_psbt
    from tests.test_psbt import build_signable_psbt

    ctx, psbt = build_signable_psbt()

    with patch("app.psbt.core.current_offline_status", return_value=_make_online_status()):
        try:
            sign_psbt(psbt, ctx)
            assert False, "Expected PSBTError"
        except PSBTError as exc:
            assert "offline" in str(exc).lower() or "assinatura recusada" in str(exc).lower()


def _make_online_status() -> OfflineStatus:
    return OfflineStatus(
        verified=False,
        network_active=True,
        has_default_route=True,
        wifi_blocked=False,
        bluetooth_blocked=False,
        suspicious_services=("NetworkManager",),
    )


# ---------------------------------------------------------------------------
# safe_event redaction — all forbidden terms
# ---------------------------------------------------------------------------


def test_safe_event_redacts_sensitive_terms() -> None:
    assert safe_event("seed criada") == "[evento sensível omitido]"
    assert safe_event("mnemonic gerado") == "[evento sensível omitido]"
    assert safe_event("passphrase incorreta") == "[evento sensível omitido]"
    assert safe_event("interface aberta") == "interface aberta"
    assert safe_event("bloco confirmado") == "bloco confirmado"


def test_safe_event_redacts_portuguese_terms() -> None:
    assert safe_event("semente gerada") == "[evento sensível omitido]"
    assert safe_event("frase de recuperação inválida") == "[evento sensível omitido]"


def test_safe_event_redacts_xprv_and_private() -> None:
    assert safe_event("chave xprv exposta") == "[evento sensível omitido]"
    assert safe_event("private key derivada") == "[evento sensível omitido]"


def test_safe_event_redacts_psbt_term() -> None:
    assert safe_event("psbt recebida para assinatura") == "[evento sensível omitido]"


def test_safe_event_passes_harmless_messages() -> None:
    assert safe_event("endereço exportado") == "endereço exportado"
    assert safe_event("carteira bloqueada") == "carteira bloqueada"
    assert safe_event("transação enviada") == "transação enviada"


# ---------------------------------------------------------------------------
# WalletContext repr privacy
# ---------------------------------------------------------------------------


def test_wallet_context_repr_does_not_expose_private_material() -> None:
    ctx = create_wallet_context(MNEMONIC, "TREZOR", "bip84")
    rendered = repr(ctx).lower()

    assert "xprv" not in rendered
    assert "zprv" not in rendered
    assert "mnemonic" not in rendered
    assert "passphrase" not in rendered
    assert MNEMONIC not in rendered
    assert "trezor" not in rendered


# ---------------------------------------------------------------------------
# mlock failure warning in stderr
# ---------------------------------------------------------------------------


def test_mlock_failure_emits_stderr_warning(capsys) -> None:
    with patch("app.wallet.core.try_mlock", return_value=False):
        create_wallet_context(MNEMONIC)
    captured = capsys.readouterr()
    assert "mlock" in captured.err.lower() or "aviso" in captured.err.lower()
