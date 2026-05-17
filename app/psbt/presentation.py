from __future__ import annotations

from app.i18n import tr
from app.psbt.models import PsbtReview
from app.wallet.models import WalletContext


def format_psbt_confirmation(review: PsbtReview, ctx: WalletContext) -> str:
    """Build the text shown in the final signing confirmation dialog."""
    change_sats = sum(output.value_sats for output in review.outputs if output.is_change)
    spend_sats = review.total_output_sats - change_sats
    fee = _fmt_sats(review.fee_sats)
    fee_rate = (
        f"{review.fee_rate_sat_vb}{tr('pres.fee_rate_suffix')}"
        if review.fee_rate_sat_vb is not None
        else tr("pres.unknown_val")
    )
    vbytes = (
        tr("pres.vbytes", n=review.estimated_vbytes)
        if review.estimated_vbytes is not None
        else tr("pres.unknown_val")
    )

    lines = [
        tr("pres.sign_only_if"),
        "",
        f"{tr('pres.fingerprint')} {ctx.fingerprint}",
        f"{tr('pres.profile')} {ctx.profile.name}",
        f"{tr('pres.path')} {ctx.profile.account_path}",
        f"{tr('pres.signable')} {review.signable_inputs}/{review.input_count} input(s)",
        "",
        f"{tr('pres.spent')} {_fmt_sats(spend_sats)}",
        f"{tr('pres.change')} {_fmt_sats(change_sats)}",
        f"{tr('pres.fee')} {fee}",
        f"{tr('pres.fee_rate')} {fee_rate}",
        f"{tr('pres.size')} {vbytes}",
        "",
        tr("pres.destinations"),
    ]

    for output in review.outputs:
        if output.is_change:
            continue
        address = output.address or tr("pres.unknown_addr")
        lines.append(f"  [{output.index}] {_fmt_sats(output.value_sats)}  →  {address}")

    if change_sats:
        lines.append("")
        lines.append(tr("pres.change_section"))
        for output in review.outputs:
            if output.is_change:
                address = output.address or tr("pres.unknown_addr")
                lines.append(f"  [{output.index}] {_fmt_sats(output.value_sats)}  →  {address}")

    lines.append("")
    lines.append(tr("pres.input_paths"))
    for item in review.inputs:
        path = item.derivation_path or tr("pres.input_path_unknown")
        owner = tr("pres.signable_yes") if item.fingerprint_matches else tr("pres.signable_no")
        value = _fmt_sats(item.value_sats)
        lines.append(f"  [{item.index}] signable={owner}  value={value}  path={path}")

    if review.warnings:
        lines.append("")
        lines.append(tr("pres.warnings"))
        lines.extend(f"  ⚠ {w}" for w in review.warnings)

    lines.append("")
    lines.append(tr("pres.confirm_question"))
    return "\n".join(lines)


def _fmt_sats(value: int | None) -> str:
    if value is None:
        return tr("pres.unknown_val")
    return f"{value:,} sats".replace(",", ".")
