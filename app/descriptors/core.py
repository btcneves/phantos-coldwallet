from __future__ import annotations

try:
    from urtypes import descriptor_checksum
except Exception:  # pragma: no cover - dependency failure is surfaced at runtime.
    descriptor_checksum = None


def add_checksum(descriptor: str) -> str:
    """Return a Bitcoin output descriptor with an 8-character checksum."""

    if "#" in descriptor:
        return descriptor
    if descriptor_checksum is None:
        return descriptor
    return f"{descriptor}#{descriptor_checksum(descriptor)}"


def descriptor_body(
    descriptor_function: str,
    fingerprint: str,
    account_path: str,
    account_xpub: str,
    branch: int,
) -> str:
    key = f"[{fingerprint}/{_descriptor_path(account_path)}]{account_xpub}/{branch}/*"
    if descriptor_function == "pkh":
        return f"pkh({key})"
    if descriptor_function == "sh-wpkh":
        return f"sh(wpkh({key}))"
    if descriptor_function == "wpkh":
        return f"wpkh({key})"
    if descriptor_function == "tr":
        return f"tr({key})"
    raise ValueError(f"Unsupported descriptor function: {descriptor_function}")


def descriptor_pair(
    descriptor_function: str,
    fingerprint: str,
    account_path: str,
    account_xpub: str,
) -> tuple[str, str]:
    external = add_checksum(
        descriptor_body(descriptor_function, fingerprint, account_path, account_xpub, 0)
    )
    internal = add_checksum(
        descriptor_body(descriptor_function, fingerprint, account_path, account_xpub, 1)
    )
    return external, internal


def _descriptor_path(path: str) -> str:
    return path.removeprefix("m/").replace("'", "h").replace("H", "h").replace(" ", "")
