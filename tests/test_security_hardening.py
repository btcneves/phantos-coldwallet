"""Testes de segurança de sistema e hardening — rodada 3 de auditoria.

Cobre SYS-01 a SYS-18: detecção de interfaces, nftables, rfkill, memória.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch


from app.security.core import (
    _find_suspicious_services,
    _has_active_network_interface,
    _has_nftables_drop_all,
    current_offline_status,
)
from app.security.memory import try_mlockall, zero_bytearray


# ---------------------------------------------------------------------------
# SYS-01 — WireGuard e PPP: operstate "unknown" deve ser detectado como ativo
# ---------------------------------------------------------------------------


def test_wireguard_interface_detected_as_active(tmp_path: Path) -> None:
    """SYS-01: WireGuard reporta operstate='unknown' — deve ser detectado como ativo."""
    net_dir = tmp_path / "sys" / "class" / "net"
    wg0 = net_dir / "wg0"
    wg0.mkdir(parents=True)
    (wg0 / "operstate").write_text("unknown\n")

    with patch("app.security.core.Path") as mock_path:
        mock_net = MagicMock()
        mock_net.exists.return_value = True
        mock_net.iterdir.return_value = [wg0]

        wg0_mock = MagicMock()
        wg0_mock.name = "wg0"
        wg0_mock.__truediv__ = lambda self, x: (wg0 / x)

        real_path = Path

        def path_side_effect(p):
            if str(p) == "/sys/class/net":
                entries = []
                for d in wg0.parent.iterdir() if wg0.parent.exists() else []:
                    entries.append(d)

                class FakeNetDir:
                    def exists(self):
                        return True

                    def iterdir(self):
                        return [wg0]

                return FakeNetDir()
            return real_path(p)

        mock_path.side_effect = path_side_effect

    # Teste direto: ler o operstate "unknown" de um dir simulado
    with patch("app.security.core.Path") as MockPath:
        fake_iface = MagicMock()
        fake_iface.name = "wg0"
        fake_operstate = MagicMock()
        fake_operstate.read_text.return_value = "unknown\n"
        fake_iface.__truediv__ = lambda self, key: fake_operstate

        fake_net_dir = MagicMock()
        fake_net_dir.exists.return_value = True
        fake_net_dir.iterdir.return_value = [fake_iface]

        MockPath.return_value = fake_net_dir

        result = _has_active_network_interface()

    assert result is True, (
        "Interface WireGuard com operstate='unknown' deve ser detectada como ativa"
    )


def test_ppp_interface_detected_as_active() -> None:
    """SYS-01: PPP com operstate 'unknown' deve ser detectado como ativo."""
    with patch("app.security.core.Path") as MockPath:
        fake_iface = MagicMock()
        fake_iface.name = "ppp0"
        fake_operstate = MagicMock()
        fake_operstate.read_text.return_value = "unknown\n"
        fake_iface.__truediv__ = lambda self, key: fake_operstate

        fake_net_dir = MagicMock()
        fake_net_dir.exists.return_value = True
        fake_net_dir.iterdir.return_value = [fake_iface]

        MockPath.return_value = fake_net_dir

        result = _has_active_network_interface()

    assert result is True


def test_down_interface_not_reported_as_active() -> None:
    """SYS-01: Interface com operstate='down' não deve ser reportada como ativa."""
    with patch("app.security.core.Path") as MockPath:
        fake_iface = MagicMock()
        fake_iface.name = "eth0"
        fake_operstate = MagicMock()
        fake_operstate.read_text.return_value = "down\n"
        fake_iface.__truediv__ = lambda self, key: fake_operstate

        fake_net_dir = MagicMock()
        fake_net_dir.exists.return_value = True
        fake_net_dir.iterdir.return_value = [fake_iface]

        MockPath.return_value = fake_net_dir

        result = _has_active_network_interface()

    assert result is False


def test_dormant_interface_not_reported_as_active() -> None:
    """SYS-01: Interface com operstate='dormant' não deve ser reportada como ativa."""
    with patch("app.security.core.Path") as MockPath:
        fake_iface = MagicMock()
        fake_iface.name = "eth0"
        fake_operstate = MagicMock()
        fake_operstate.read_text.return_value = "dormant\n"
        fake_iface.__truediv__ = lambda self, key: fake_operstate

        fake_net_dir = MagicMock()
        fake_net_dir.exists.return_value = True
        fake_net_dir.iterdir.return_value = [fake_iface]

        MockPath.return_value = fake_net_dir

        result = _has_active_network_interface()

    assert result is False


# ---------------------------------------------------------------------------
# SYS-02 — nftables: verificação dos 3 hooks obrigatórios
# ---------------------------------------------------------------------------


def test_nftables_requires_all_three_hooks() -> None:
    """SYS-02: Apenas 2 de 3 hooks com policy drop → deve retornar False."""
    ruleset_missing_forward = (
        "table inet phantos {\n"
        "  chain input { type filter hook input priority 0; policy drop; }\n"
        "  chain output { type filter hook output priority 0; policy drop; }\n"
        "}\n"
    )
    mock_result = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=ruleset_missing_forward, stderr=""
    )
    with (
        patch("shutil.which", return_value="/usr/sbin/nft"),
        patch("subprocess.run", return_value=mock_result),
    ):
        assert _has_nftables_drop_all() is False, "Falta hook forward → deve retornar False"


def test_nftables_all_three_hooks_returns_true() -> None:
    """SYS-02: Todos os 3 hooks com policy drop → deve retornar True."""
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


def test_nftables_scoped_to_phantos_table() -> None:
    """SYS-02: Deve chamar 'nft list table inet phantos', não 'list ruleset'."""
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
        patch("subprocess.run", return_value=mock_result) as mock_run,
    ):
        _has_nftables_drop_all()
        args_called = mock_run.call_args[0][0]
        assert "list" in args_called
        assert "table" in args_called
        assert "inet" in args_called
        assert "phantos" in args_called
        assert "ruleset" not in args_called, "Não deve usar 'list ruleset' — escopo muito amplo"


def test_nftables_phantos_table_not_found_returns_false() -> None:
    """SYS-02: Se 'nft list table inet phantos' retornar erro (tabela inexistente) → False."""
    mock_result = subprocess.CompletedProcess(
        args=[], returncode=1, stdout="", stderr="Error: No such file or directory"
    )
    with (
        patch("shutil.which", return_value="/usr/sbin/nft"),
        patch("subprocess.run", return_value=mock_result),
    ):
        assert _has_nftables_drop_all() is False


# ---------------------------------------------------------------------------
# SYS-03 — Serviços suspeitos: ssh.socket, systemd-networkd, iwd
# ---------------------------------------------------------------------------


def test_ssh_socket_detected_as_suspicious() -> None:
    """SYS-03: ssh.socket via socket activation deve ser detectado."""

    def mock_run(cmd, **kwargs):
        svc = cmd[-1]
        if svc == "ssh.socket":
            return subprocess.CompletedProcess(args=cmd, returncode=0)
        return subprocess.CompletedProcess(args=cmd, returncode=1)

    with (
        patch("shutil.which", return_value="/usr/bin/systemctl"),
        patch("subprocess.run", side_effect=mock_run),
    ):
        active = _find_suspicious_services()

    assert "ssh.socket" in active


def test_systemd_networkd_detected_as_suspicious() -> None:
    """SYS-03: systemd-networkd deve ser detectado como serviço suspeito."""

    def mock_run(cmd, **kwargs):
        svc = cmd[-1]
        if svc == "systemd-networkd":
            return subprocess.CompletedProcess(args=cmd, returncode=0)
        return subprocess.CompletedProcess(args=cmd, returncode=1)

    with (
        patch("shutil.which", return_value="/usr/bin/systemctl"),
        patch("subprocess.run", side_effect=mock_run),
    ):
        active = _find_suspicious_services()

    assert "systemd-networkd" in active


def test_iwd_detected_as_suspicious() -> None:
    """SYS-03: iwd (daemon Wi-Fi moderno) deve ser detectado."""

    def mock_run(cmd, **kwargs):
        svc = cmd[-1]
        if svc == "iwd":
            return subprocess.CompletedProcess(args=cmd, returncode=0)
        return subprocess.CompletedProcess(args=cmd, returncode=1)

    with (
        patch("shutil.which", return_value="/usr/bin/systemctl"),
        patch("subprocess.run", side_effect=mock_run),
    ):
        active = _find_suspicious_services()

    assert "iwd" in active


# ---------------------------------------------------------------------------
# SYS-06 — try_mlockall: não deve lançar exceção
# ---------------------------------------------------------------------------


def test_try_mlockall_does_not_raise() -> None:
    """SYS-06: try_mlockall() nunca deve lançar exceção (retorna bool)."""
    result = try_mlockall()
    assert isinstance(result, bool)


def test_try_mlockall_returns_false_on_non_linux() -> None:
    """SYS-06: try_mlockall() retorna False em plataformas não-Linux."""
    import sys as _sys

    with patch.object(_sys, "platform", "darwin"):
        result = try_mlockall()
    assert result is False


# ---------------------------------------------------------------------------
# SYS — zero_bytearray: deve zerar todos os bytes
# ---------------------------------------------------------------------------


def test_zero_bytearray_zeros_all_bytes() -> None:
    """zero_bytearray deve sobrescrever todo o conteúdo com zeros."""
    buf = bytearray(b"secret_seed_data_here_64_bytes!!")
    assert any(b != 0 for b in buf)
    zero_bytearray(buf)
    assert all(b == 0 for b in buf), "Todos os bytes devem ser zero após zero_bytearray()"


def test_zero_bytearray_handles_empty() -> None:
    """zero_bytearray não deve lançar exceção em bytearray vazio."""
    buf = bytearray(b"")
    zero_bytearray(buf)  # não deve lançar


# ---------------------------------------------------------------------------
# SYS — offline verificado quando WireGuard ativo mas nftables drop e sem rota
# ---------------------------------------------------------------------------


def test_offline_verified_wireguard_with_nftables_drop() -> None:
    """WireGuard ativo (network_active=True) + nftables drop + sem rota → verified=True."""
    with (
        patch("app.security.core._has_active_network_interface", return_value=True),
        patch("app.security.core._has_default_route", return_value=False),
        patch("app.security.core._is_rfkill_blocked", return_value=True),
        patch("app.security.core._has_nftables_drop_all", return_value=True),
        patch("app.security.core._find_suspicious_services", return_value=[]),
    ):
        status = current_offline_status()

    assert status.verified, "nftables drop-all deve compensar interface WireGuard ativa"
    assert status.network_active
    assert status.nftables_drop_active


def test_offline_not_verified_wireguard_without_nftables() -> None:
    """WireGuard ativo sem nftables → verified=False."""
    with (
        patch("app.security.core._has_active_network_interface", return_value=True),
        patch("app.security.core._has_default_route", return_value=False),
        patch("app.security.core._is_rfkill_blocked", return_value=True),
        patch("app.security.core._has_nftables_drop_all", return_value=False),
        patch("app.security.core._find_suspicious_services", return_value=[]),
    ):
        status = current_offline_status()

    assert not status.verified
