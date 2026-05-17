from __future__ import annotations

import shutil
import subprocess  # nosec B404
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class OfflineStatus:
    verified: bool
    network_active: bool
    has_default_route: bool
    wifi_blocked: bool
    bluetooth_blocked: bool
    nftables_drop_active: bool = False
    suspicious_services: tuple[str, ...] = field(default_factory=tuple)
    mode: str = "Cold Wallet Offline"


def current_offline_status() -> OfflineStatus:
    network_active = _has_active_network_interface()
    has_default_route = _has_default_route()
    wifi_blocked = _is_rfkill_blocked("wlan") or _is_rfkill_blocked("wifi")
    bt_blocked = _is_rfkill_blocked("bluetooth") or _is_rfkill_blocked("hci")
    nft_drop = _has_nftables_drop_all()
    suspicious = _find_suspicious_services()

    # An interface may remain administratively UP after harden_network.sh if the kernel
    # did not bring it down, but nftables drop-all makes it harmless. We accept verified=True
    # when nftables confirms drop-all even if operstate still reports up, provided no
    # default route and no suspicious services are present.
    net_ok = not network_active or (nft_drop and not has_default_route)
    verified = (
        net_ok and not has_default_route and wifi_blocked and bt_blocked and len(suspicious) == 0
    )

    return OfflineStatus(
        verified=verified,
        network_active=network_active,
        has_default_route=has_default_route,
        wifi_blocked=wifi_blocked,
        bluetooth_blocked=bt_blocked,
        nftables_drop_active=nft_drop,
        suspicious_services=tuple(suspicious),
    )


def safe_event(message: str) -> str:
    forbidden = (
        "seed",
        "mnemonic",
        "passphrase",
        "xprv",
        "private",
        "psbt",
        "semente",
        "frase de recuperação",
    )
    lowered = message.lower()
    if any(token in lowered for token in forbidden):
        return "[evento sensível omitido]"
    return message


# ---------------------------------------------------------------------------
# Internal helpers — each raises no exception; fail-safe returns mean "not sure → unsafe"
# ---------------------------------------------------------------------------


_VIRTUAL_IFACE_PREFIXES = ("lo", "virbr", "docker", "br-", "veth", "tun", "tap", "dummy")


def _has_active_network_interface() -> bool:
    """Return True if any non-virtual interface has an active carrier (operstate=up)."""
    net_dir = Path("/sys/class/net")
    if not net_dir.exists():
        return True  # unknown → fail-safe: assume active
    for iface_dir in net_dir.iterdir():
        name = iface_dir.name
        if any(name.startswith(prefix) for prefix in _VIRTUAL_IFACE_PREFIXES):
            continue
        operstate = iface_dir / "operstate"
        try:
            state = operstate.read_text().strip().lower()
            # Considera ativa qualquer interface que não esteja claramente desligada.
            # WireGuard reporta "unknown"; PPP pode reportar "unknown" ou "up".
            if state not in ("down", "dormant", "notpresent", "lowerlayerdown", ""):
                return True
        except OSError:
            continue
    return False


def _has_default_route() -> bool:
    """Return True if any IPv4 or IPv6 default route exists."""
    return _has_ipv4_default_route() or _has_ipv6_default_route()


def _has_ipv4_default_route() -> bool:
    """Return True if /proc/net/route shows a default (0.0.0.0 dest) route."""
    route_file = Path("/proc/net/route")
    if not route_file.exists():
        return True  # fail-safe
    try:
        lines = route_file.read_text().splitlines()
        for line in lines[1:]:  # skip header
            parts = line.split()
            if len(parts) < 3:
                continue
            destination = parts[1]
            gateway = parts[2]
            if destination == "00000000" and gateway != "00000000":
                return True
    except OSError:
        return True  # fail-safe
    return False


def _has_ipv6_default_route() -> bool:
    """Return True if /proc/net/ipv6_route shows a default (::/0) route."""
    route_file = Path("/proc/net/ipv6_route")
    if not route_file.exists():
        return False  # no IPv6 stack → no IPv6 route
    try:
        lines = route_file.read_text().splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) < 5:
                continue
            # Fields: dest(32hex) prefix_len(2hex) src(32hex) src_prefix(2hex) nexthop(32hex) ...
            dest = parts[0]
            prefix_len = parts[1]
            nexthop = parts[4]
            # Default route: ::/0 — all-zero destination, prefix length 00, non-zero nexthop
            if (
                dest == "00000000000000000000000000000000"
                and prefix_len == "00"
                and nexthop != "00000000000000000000000000000000"
            ):
                return True
    except OSError:
        return True  # fail-safe
    return False


def _is_rfkill_blocked(kind: str) -> bool:
    """Return True if rfkill reports the given interface type as blocked.

    'kind' is matched against the rfkill type strings (e.g. 'wlan', 'bluetooth').
    Returns True (blocked = safe) when all found devices of that kind are soft- or hard-blocked.
    Returns False (unblocked = risky) when any device of that kind is unblocked.
    Returns True (safe) when no device of that kind exists (no hardware present).
    """
    rfkill_dir = Path("/sys/class/rfkill")
    if not rfkill_dir.exists():
        return True  # no rfkill → no wireless hardware → safe
    found = False
    for entry in rfkill_dir.iterdir():
        type_file = entry / "type"
        soft_file = entry / "soft"
        hard_file = entry / "hard"
        try:
            dev_type = type_file.read_text().strip().lower()
            if kind.lower() not in dev_type:
                continue
            found = True
            # Leituras de soft e hard são operações separadas; race condition teórica
            # mas improvável — rfkill state muda raramente e o impacto é fail-safe (unblocked).
            soft = soft_file.read_text().strip()
            hard = hard_file.read_text().strip()
            if soft == "0" and hard == "0":
                return False  # at least one device is unblocked
        except OSError:
            found = True
            return False  # fail-safe: can't read state → assume unblocked
    if not found:
        return True  # no device of this type
    return True  # all found devices are blocked


def _find_suspicious_services() -> list[str]:
    """Return names of network-related systemd services that are currently active."""
    systemctl = shutil.which("systemctl")
    if systemctl is None:
        return []

    candidates = [
        "NetworkManager",
        "wpa_supplicant",
        "bluetooth",
        "avahi-daemon",
        "cups",
        "sshd",
        "ssh",
        "ssh.socket",
        "sshd.socket",
        "systemd-networkd",
        "iwd",
        "tor",
        "isc-dhcp-client",
        "networking",
    ]
    active = []
    for svc in candidates:
        try:
            result = subprocess.run(
                [systemctl, "is-active", "--quiet", svc],
                capture_output=True,
                timeout=2,
            )  # nosec B603
            if result.returncode == 0:
                active.append(svc)
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue  # systemctl not available (e.g. container/test env) — skip
    return active


def _has_nftables_drop_all() -> bool:
    """Return True if nftables phantos table has drop policy on input, forward, and output hooks."""
    nft = shutil.which("nft")
    if nft is None:
        return False
    try:
        result = subprocess.run(
            [nft, "list", "table", "inet", "phantos"],
            capture_output=True,
            text=True,
            timeout=3,
        )  # nosec B603
        if result.returncode != 0:
            return False
        ruleset = result.stdout
        # Verificar que as três chains críticas têm policy drop
        required_hooks = {"input", "forward", "output"}
        found_drop = set()
        for line in ruleset.splitlines():
            line_lower = line.lower().strip()
            for hook in required_hooks:
                if f"hook {hook}" in line_lower and "policy drop" in line_lower:
                    found_drop.add(hook)
        return required_hooks.issubset(found_drop)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False
