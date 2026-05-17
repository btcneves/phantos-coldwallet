from __future__ import annotations

import base64
import binascii
from typing import Any

from embit import networks
from embit.psbt import PSBT, PSBTError
from embit.script import p2pkh, p2sh, p2tr, p2wpkh
from embit.transaction import SIGHASH

from app.psbt.models import PsbtInputReview, PsbtOutputReview, PsbtReview, SignedPsbtResult
from app.security.core import current_offline_status
from app.ur.core import decode_crypto_psbt_ur
from app.wallet.core import known_addresses
from app.wallet.models import WalletContext


_MAX_PSBT_BYTES = 1_000_000  # 1 MB — rejects malformed/oversized input before parsing
_MAX_PSBT_INPUTS = 500  # anti-DoS: prevents memory exhaustion from crafted PSBTs
_MAX_PSBT_OUTPUTS = 500  # anti-DoS


def parse_psbt(payload: str | bytes) -> PSBT:
    """Parse PSBT from binary, base64, hex or single/multipart UR text."""
    if isinstance(payload, (bytes, bytearray)) and len(payload) > _MAX_PSBT_BYTES:
        raise ValueError(f"PSBT excede o tamanho máximo permitido ({_MAX_PSBT_BYTES // 1000} KB).")
    if isinstance(payload, str) and len(payload) > _MAX_PSBT_BYTES:
        raise ValueError(f"PSBT excede o tamanho máximo permitido ({_MAX_PSBT_BYTES // 1000} KB).")

    if isinstance(payload, bytes):
        data = payload.strip()
        if data.startswith(b"psbt\xff"):
            return PSBT.parse(data)
        try:
            text = data.decode("utf-8").strip()
        except UnicodeDecodeError:
            return PSBT.parse(data)
    else:
        text = payload.strip()

    if text.lower().startswith("ur:"):
        parts = [line.strip() for line in text.splitlines() if line.strip()]
        if len(parts) > 1 and all(part.lower().startswith("ur:") for part in parts):
            raw = decode_crypto_psbt_ur(parts)
            if len(raw) > _MAX_PSBT_BYTES:
                raise ValueError(
                    f"PSBT decodificado excede o tamanho máximo ({_MAX_PSBT_BYTES // 1000} KB)."
                )
            return PSBT.parse(raw)
        raw = decode_crypto_psbt_ur(text)
        if len(raw) > _MAX_PSBT_BYTES:
            raise ValueError(
                f"PSBT decodificado excede o tamanho máximo ({_MAX_PSBT_BYTES // 1000} KB)."
            )
        return PSBT.parse(raw)
    if text.startswith("70736274ff"):
        raw = bytes.fromhex(text)
        if len(raw) > _MAX_PSBT_BYTES:
            raise ValueError(f"PSBT excede o tamanho máximo ({_MAX_PSBT_BYTES // 1000} KB).")
        return PSBT.parse(raw)
    import base64 as _b64

    try:
        raw = _b64.b64decode(text + "==", validate=False)
        if len(raw) > _MAX_PSBT_BYTES:
            raise ValueError(f"PSBT excede o tamanho máximo ({_MAX_PSBT_BYTES // 1000} KB).")
    except Exception:
        pass  # deixa PSBT.from_string tentar e lançar o erro adequado
    return PSBT.from_string(text)


def review_psbt(psbt: PSBT, ctx: WalletContext, change_scan_limit: int = 200) -> PsbtReview:
    warnings: list[str] = []
    errors: list[str] = []

    # PSBT-22: reject oversized PSBTs before doing any work (anti-DoS).
    # Check inputs first and return immediately — avoids accessing psbt.tx when inputs are invalid.
    n_inputs = len(psbt.inputs)
    if n_inputs > _MAX_PSBT_INPUTS:
        return PsbtReview(
            version=None,
            input_count=n_inputs,
            output_count=0,
            inputs=[],
            outputs=[],
            total_input_sats=None,
            total_output_sats=0,
            fee_sats=None,
            estimated_vbytes=None,
            fee_rate_sat_vb=None,
            signable_inputs=0,
            warnings=[],
            errors=[
                f"PSBT com {n_inputs} inputs excede o limite de segurança ({_MAX_PSBT_INPUTS}). "
                "Recuse esta transação."
            ],
        )
    n_outputs = len(psbt.tx.vout)
    if n_outputs > _MAX_PSBT_OUTPUTS:
        return PsbtReview(
            version=None,
            input_count=n_inputs,
            output_count=n_outputs,
            inputs=[],
            outputs=[],
            total_input_sats=None,
            total_output_sats=0,
            fee_sats=None,
            estimated_vbytes=None,
            fee_rate_sat_vb=None,
            signable_inputs=0,
            warnings=[],
            errors=[
                f"PSBT com {n_outputs} outputs excede o limite de segurança ({_MAX_PSBT_OUTPUTS}). "
                "Recuse esta transação."
            ],
        )

    net = networks.NETWORKS[ctx.network]
    change_addresses = known_addresses(ctx, change=1, limit=change_scan_limit)

    # PSBT-21: non-standard transaction version warning
    tx_version = getattr(psbt.tx, "version", None)
    if tx_version is not None and tx_version not in (1, 2):
        warnings.append(
            f"Versão de transação não-padrão: {tx_version}. "
            "Apenas versões 1 e 2 são amplamente suportadas pela rede Bitcoin."
        )

    # PSBT-23: nLockTime future warning
    locktime = getattr(psbt.tx, "locktime", 0) or 0
    if locktime > 500_000_000:
        import time as _time

        now = int(_time.time())
        if locktime > now:
            warnings.append(
                f"Transação com locktime futuro (Unix timestamp {locktime}). "
                "Não poderá ser transmitida antes desta data."
            )
    elif locktime > 0:
        warnings.append(
            f"Transação com locktime no bloco {locktime}. "
            "Não poderá ser transmitida antes deste bloco."
        )

    # PSBT-18: RBF detection (BIP125) — nSequence < 0xFFFFFFFE on any input.
    # Check psbt.inputs[i].sequence (InputScope) instead of psbt.tx.vin[i].sequence
    # because embit's InputScope.vin property applies `self.sequence or 0xFFFFFFFF`,
    # silently treating sequence=0 as 0xFFFFFFFF — we need the raw stored value.
    _RBF_THRESHOLD = 0xFFFFFFFE
    rbf_inputs = [
        i
        for i, inp_scope in enumerate(psbt.inputs)
        if inp_scope.sequence is not None and inp_scope.sequence < _RBF_THRESHOLD
    ]
    if rbf_inputs:
        warnings.append(
            f"Transação RBF-habilitada (BIP125): input(s) {rbf_inputs} com nSequence "
            "abaixo de 0xFFFFFFFE — pode ser substituída por versão de taxa maior antes "
            "de confirmar. Verifique o risco de double-spend."
        )

    inputs: list[PsbtInputReview] = []
    signable = 0
    total_input: int | None = 0
    seen_prevouts: set[tuple[bytes, int]] = set()
    for index, inp in enumerate(psbt.inputs):
        value = None
        utxo = None
        try:
            utxo = psbt.utxo(index)
            value = utxo.value
            total_input = (total_input or 0) + value
        except (PSBTError, ValueError, AttributeError):
            total_input = None
            errors.append(f"Input {index}: informação de UTXO ausente ou inválida.")
        # C-01: verificar non_witness_utxo para evitar fee drain attack
        if inp.non_witness_utxo is not None and not inp.is_verified:
            try:
                inp.verify()
            except PSBTError as exc:
                errors.append(f"Input {index}: verificação de non_witness_utxo falhou — {exc}.")
                total_input = None
        # A-07: bloquear sighash types não-standard
        if inp.sighash_type is not None and inp.sighash_type not in (SIGHASH.ALL, SIGHASH.DEFAULT):
            errors.append(
                f"Input {index}: sighash_type não permitido (valor={inp.sighash_type}). "
                "Apenas SIGHASH_ALL e SIGHASH_DEFAULT são aceitos."
            )
        prevout = _input_prevout_key(psbt, index)
        if prevout is not None:
            if prevout in seen_prevouts:
                errors.append(f"Input {index}: prevout duplicado detectado.")
            seen_prevouts.add(prevout)
        fingerprint_match, path, path_error = _input_matches_fingerprint(
            inp, ctx.fingerprint, ctx.profile.account_path
        )
        if fingerprint_match:
            signable += 1
            script_error = _signable_utxo_script_error(
                inp, utxo, ctx.profile.script_type, ctx.fingerprint
            )
            if script_error:
                errors.append(f"Input {index}: {script_error}")
        if path_error:
            errors.append(f"Input {index}: {path_error}")
        inputs.append(
            PsbtInputReview(
                index=index,
                value_sats=value,
                fingerprint_matches=fingerprint_match,
                derivation_path=path,
            )
        )

    outputs: list[PsbtOutputReview] = []
    total_output = 0
    _MAX_SATOSHIS = 2_100_000_000_000_000  # 21M BTC
    for index, out in enumerate(psbt.tx.vout):
        if out.value > _MAX_SATOSHIS:
            errors.append(
                f"Output {index}: valor {out.value} sats excede o supply máximo de Bitcoin."
            )
        total_output += out.value
        address = None
        script_bytes = bytes(getattr(out.script_pubkey, "data", b""))
        is_op_return = bool(script_bytes) and script_bytes[0] == 0x6A
        if is_op_return:
            if out.value > 0:
                # PSBT-20: OP_RETURN with value > 0 burns bitcoin irrecoverably
                errors.append(
                    f"Output {index}: OP_RETURN com valor {out.value} sats — "
                    "bitcoin enviado para saída unspendable é irrecuperável."
                )
            else:
                warnings.append(
                    f"Output {index}: OP_RETURN — saída de dados sem valor monetário. "
                    "Verifique o conteúdo gravado na blockchain."
                )
        else:
            try:
                address = out.script_pubkey.address(net)
            except Exception:
                warnings.append(f"Output {index}: endereço não reconhecido pela rede selecionada.")
        if out.value == 0 and not is_op_return:
            warnings.append(f"Output {index}: valor zero — verifique se é intencional.")
        elif out.value < 546 and not is_op_return:
            warnings.append(f"Output {index}: valor abaixo do limite de poeira comum (546 sats).")
        outputs.append(
            PsbtOutputReview(
                index=index,
                value_sats=out.value,
                address=address,
                is_change=address in change_addresses if address else False,
            )
        )

    fee = None
    try:
        fee = psbt.fee()
    except Exception:
        if total_input is not None:
            fee = total_input - total_output
    estimated_vbytes = _estimate_vbytes(psbt)
    fee_rate = round(fee / estimated_vbytes, 2) if fee is not None and estimated_vbytes else None

    missing_utxo = any(getattr(inp, "witness_utxo", None) is None for inp in psbt.inputs)
    if missing_utxo and estimated_vbytes is not None:
        warnings.append(
            "Estimativa de vbytes aproximada: um ou mais inputs sem witness_utxo. "
            "Confirme a taxa com a carteira de origem."
        )

    if signable == 0:
        errors.append("A PSBT não contém inputs assináveis por esta carteira.")
    if 0 < signable < len(psbt.inputs):
        warnings.append(
            f"Apenas {signable} de {len(psbt.inputs)} input(s) pertencem a esta carteira. "
            "A transação pode precisar de outras assinaturas."
        )
    if len(outputs) > 1 and not any(out.is_change for out in outputs):
        warnings.append("Nenhum endereço de troco foi reconhecido. Confira com atenção.")
    if fee is not None and fee < 0:
        errors.append("A taxa calculada é negativa. A PSBT está inconsistente.")
    if fee is not None and fee > 100_000:
        warnings.append("Taxa absoluta acima de 100.000 sats.")
    # PSBT-19: low fee rate may result in unconfirmed transaction
    if fee_rate is not None and 0 < fee_rate < 1.0:
        warnings.append(
            f"Taxa muito baixa ({fee_rate} sat/vB) — a transação pode não ser confirmada "
            "em tempo razoável. Considere aumentar a taxa."
        )
    if fee_rate is not None and fee_rate > 200:
        warnings.append("Taxa acima de 200 sats/vB.")
    if _looks_like_psbt_v2(psbt):
        warnings.append(
            "PSBTv2 detectada. Assinatura deve permanecer em modo avançado/experimental."
        )
    if any(getattr(inp, "taproot_internal_key", None) is not None for inp in psbt.inputs):
        warnings.append(
            "Input Taproot detectado. Revise suporte BIP86/PSBTv2 antes de assinar valores altos."
        )
    if ctx.profile.experimental:
        warnings.append(
            f"Perfil {ctx.profile.name} é experimental. Use apenas com valores de teste."
        )

    return PsbtReview(
        version=getattr(psbt.tx, "version", None),
        input_count=len(psbt.inputs),
        output_count=len(psbt.tx.vout),
        inputs=inputs,
        outputs=outputs,
        total_input_sats=total_input,
        total_output_sats=total_output,
        fee_sats=fee,
        estimated_vbytes=estimated_vbytes,
        fee_rate_sat_vb=fee_rate,
        signable_inputs=signable,
        warnings=warnings,
        errors=errors,
    )


def sign_psbt(psbt: PSBT, ctx: WalletContext) -> SignedPsbtResult:
    offline = current_offline_status()
    if not offline.verified:
        issues = []
        if offline.network_active:
            issues.append("interface de rede ativa")
        if offline.has_default_route:
            issues.append("rota padrão presente")
        if not offline.wifi_blocked:
            issues.append("Wi-Fi não bloqueado")
        if not offline.bluetooth_blocked:
            issues.append("Bluetooth não bloqueado")
        if offline.suspicious_services:
            issues.append(f"serviços ativos: {', '.join(offline.suspicious_services)}")
        detail = "; ".join(issues) or "status offline não verificado"
        raise PSBTError(
            f"Assinatura recusada: dispositivo não está offline verificado ({detail}). "
            "Execute /usr/local/bin/phantos-harden-network como root antes de assinar."
        )
    import copy as _copy

    psbt = _copy.deepcopy(psbt)
    review = review_psbt(psbt, ctx)
    if not review.can_sign:
        raise PSBTError("; ".join(review.errors) or "PSBT não assinável.")
    signatures = psbt.sign_with(ctx.root_key)
    if signatures <= 0:
        raise PSBTError("Nenhuma assinatura foi adicionada à PSBT.")
    return SignedPsbtResult(signed_psbt_base64=psbt.to_base64(), signatures_added=signatures)


def _input_matches_fingerprint(
    inp: Any, fingerprint_hex: str, account_path: str | None = None
) -> tuple[bool, str | None, str | None]:
    """Return (matches, path_str, error_msg).

    matches is True only when the fingerprint matches AND the derivation path
    is consistent with the wallet profile (if account_path is provided).
    error_msg is non-None when the fingerprint matched but the path did not.
    """
    expected = bytes.fromhex(fingerprint_hex)
    for derivation in getattr(inp, "bip32_derivations", {}).values():
        if getattr(derivation, "fingerprint", None) == expected:
            path = _path_to_string(derivation.derivation)
            if account_path is not None and not _path_matches_profile(
                derivation.derivation, account_path
            ):
                return (
                    False,
                    path,
                    f"derivation path {path} não corresponde ao perfil esperado {account_path}.",
                )
            return True, path, None
    for value in getattr(inp, "taproot_bip32_derivations", {}).values():
        derivation = value[1]
        if getattr(derivation, "fingerprint", None) == expected:
            path = _path_to_string(derivation.derivation)
            if account_path is not None and not _path_matches_profile(
                derivation.derivation, account_path
            ):
                return (
                    False,
                    path,
                    f"derivation path {path} não corresponde ao perfil esperado {account_path}.",
                )
            return True, path, None
    return False, None, None


def _input_prevout_key(psbt: PSBT, index: int) -> tuple[bytes, int] | None:
    try:
        txin = psbt.tx.vin[index]
        txid = bytes(txin.txid)
        vout = int(txin.vout)
    except Exception:
        return None
    return txid, vout


def _signable_utxo_script_error(
    inp: Any, utxo: Any, script_type: str, fingerprint_hex: str
) -> str | None:
    if utxo is None:
        return "UTXO ausente: não é possível validar o script do output."
    script_pubkey = getattr(utxo, "script_pubkey", None)
    script_data = getattr(script_pubkey, "data", None)
    if script_data is None:
        return "scriptPubKey da UTXO ausente ou inválido."

    expected_fingerprint = bytes.fromhex(fingerprint_hex)
    actual = bytes(script_data)
    for pubkey, derivation in getattr(inp, "bip32_derivations", {}).items():
        if getattr(derivation, "fingerprint", None) != expected_fingerprint:
            continue
        expected = _expected_script_for_pubkey(pubkey, script_type)
        if expected is None:
            return f"tipo de script {script_type} ainda não possui validação de UTXO."
        if actual != expected:
            return "scriptPubKey da UTXO não corresponde à chave/path assinável."
        if script_type == "p2sh-p2wpkh":
            redeem_script = getattr(inp, "redeem_script", None)
            if redeem_script is not None:
                from embit.script import p2wpkh as _p2wpkh

                expected_redeem = bytes(_p2wpkh(pubkey).data)
                if bytes(redeem_script.data) != expected_redeem:
                    return "redeem_script injetado não corresponde à chave P2SH-P2WPKH esperada."
        return None
    return None


def _expected_script_for_pubkey(pubkey: Any, script_type: str) -> bytes | None:
    if script_type == "p2wpkh":
        return bytes(p2wpkh(pubkey).data)
    if script_type == "p2sh-p2wpkh":
        return bytes(p2sh(p2wpkh(pubkey)).data)
    if script_type == "p2pkh":
        return bytes(p2pkh(pubkey).data)
    if script_type == "p2tr":
        return bytes(p2tr(pubkey).data)
    return None


def _path_matches_profile(derivation: list[int] | tuple[int, ...], account_path: str) -> bool:
    """Validate that a derivation path matches the wallet profile.

    account_path is like "m/84'/0'/0'". The full PSBT path must be
    account_path + change (0 or 1) + index (non-hardened).
    """
    hardened = 0x80000000
    parts = account_path.lstrip("m").lstrip("/").split("/")
    expected: list[int] = []
    for part in parts:
        if not part:
            continue
        if part.endswith("'"):
            expected.append(int(part[:-1]) + hardened)
        else:
            expected.append(int(part))
    if len(derivation) != len(expected) + 2:
        return False
    for got, want in zip(derivation[: len(expected)], expected):
        if got != want:
            return False
    change = derivation[len(expected)]
    index = derivation[len(expected) + 1]
    return change in (0, 1) and index < hardened


def _path_to_string(path: list[int] | tuple[int, ...]) -> str:
    parts = []
    hardened = 0x80000000
    for item in path:
        if item >= hardened:
            parts.append(f"{item - hardened}'")
        else:
            parts.append(str(item))
    return "m/" + "/".join(parts)


def _estimate_vbytes(psbt: PSBT) -> int | None:
    """Estimate virtual bytes using witness-weight-based calculation.

    For pre-signing PSBTs the witnesses are absent, so per-input overhead is
    added based on the detected script type of each UTXO.  Result may differ
    from the final signed size by 1–2 vbytes per input (DER signature length
    varies).  Returns None on serialization failure.
    """
    try:
        base_size = len(psbt.tx.serialize())
    except Exception:
        return None

    scriptsig_overhead = 0
    witness_size = 0
    has_segwit = False

    for inp in psbt.inputs:
        utxo = getattr(inp, "witness_utxo", None)

        stype = "p2wpkh"
        if utxo is not None:
            script_pubkey = getattr(utxo, "script_pubkey", None)
            script_data = getattr(script_pubkey, "data", None)
            if script_data is not None:
                stype = _script_type_from_bytes(bytes(script_data))

        if stype == "p2wpkh":
            # witness: stack_count(1) + sig_len(1) + sig(≤72) + pk_len(1) + pk(33) = 108
            witness_size += 108
            has_segwit = True
        elif stype == "p2tr":
            # key-path witness: stack_count(1) + sig_len(1) + schnorr_sig(64) = 66
            witness_size += 66
            has_segwit = True
        elif stype == "p2sh":
            # Assumed P2SH-P2WPKH: scriptSig = push(OP_0 + push(20-byte hash)) = 23 bytes
            scriptsig_overhead += 23
            witness_size += 108
            has_segwit = True
        elif stype == "p2wsh":
            # Conservative: 2-of-3 multisig witness estimate ≈ 254 bytes
            witness_size += 254
            has_segwit = True
        elif stype == "p2pkh":
            # Legacy: scriptSig = push(sig≤72) + push(pk33) ≈ 107 bytes (base weight)
            scriptsig_overhead += 107
        else:
            # Unknown type: fall back to P2WPKH estimate (conservative)
            witness_size += 108
            has_segwit = True

    if has_segwit:
        witness_size += 2  # SegWit marker + flag (weight 1 each)

    weight = 4 * (base_size + scriptsig_overhead) + witness_size
    return max(1, (weight + 3) // 4)


def _script_type_from_bytes(data: bytes) -> str:
    """Detect scriptPubKey type from raw bytes."""
    if len(data) == 22 and data[0] == 0x00 and data[1] == 0x14:
        return "p2wpkh"
    if len(data) == 34 and data[0] == 0x00 and data[1] == 0x20:
        return "p2wsh"
    if len(data) == 34 and data[0] == 0x51 and data[1] == 0x20:
        return "p2tr"
    if len(data) == 23 and data[0] == 0xA9 and data[-1] == 0x87:
        return "p2sh"
    if len(data) == 25 and data[0] == 0x76 and data[1] == 0xA9:
        return "p2pkh"
    return "unknown"


def _looks_like_psbt_v2(psbt: PSBT) -> bool:
    if getattr(psbt, "version", None) == 2:
        return True
    unknown = getattr(psbt, "unknown", {}) or {}
    for key, value in unknown.items():
        try:
            key_bytes = bytes(key)
        except (TypeError, ValueError):
            continue
        if key_bytes == b"\xfb" and value in {b"\x02\x00\x00\x00", b"\x02"}:
            return True
    return False


def psbt_to_binary(psbt_base64: str) -> bytes:
    try:
        return base64.b64decode(psbt_base64, validate=True)
    except binascii.Error as exc:
        raise ValueError("PSBT base64 inválida.") from exc
