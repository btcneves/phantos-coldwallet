#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${PHANTOS_REGTEST_OUT:-build/regtest-psbt}"
IMAGE="${PHANTOS_BITCOIN_IMAGE:-ruimarinho/bitcoin-core:latest}"
CONTAINER="phantos-bitcoind-regtest"

mkdir -p "$OUT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "SKIPPED docker unavailable" | tee "$OUT_DIR/summary.txt"
  exit 0
fi

if ! docker info >/dev/null 2>&1; then
  echo "SKIPPED docker daemon unavailable" | tee "$OUT_DIR/summary.txt"
  exit 0
fi

cleanup() {
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

docker run -d --name "$CONTAINER" "$IMAGE" \
  -regtest=1 \
  -server=1 \
  -rpcuser=phantos \
  -rpcpassword=phantos \
  -fallbackfee=0.0002 \
  -txindex=1 \
  -printtoconsole=1 >/dev/null

rpc() {
  docker exec "$CONTAINER" bitcoin-cli -regtest -rpcuser=phantos -rpcpassword=phantos "$@"
}

for _ in $(seq 1 60); do
  if rpc getblockchaininfo >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

rpc createwallet miner >/dev/null 2>&1 || true
miner_addr="$(rpc -rpcwallet=miner getnewaddress)"
rpc -rpcwallet=miner generatetoaddress 101 "$miner_addr" >/dev/null

# shellcheck source=/dev/null
source .venv/bin/activate
python - "$OUT_DIR/descriptors.json" <<'PY'
from pathlib import Path
import json
import sys

from app.wallet import create_wallet_context

mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
ctx = create_wallet_context(mnemonic, "", "bip84", "test")
Path(sys.argv[1]).write_text(
    json.dumps(
        {
            "external": ctx.external_descriptor,
            "internal": ctx.internal_descriptor,
        }
    ),
    encoding="utf-8",
)
PY

rpc createwallet phantos true true "" false true >/dev/null 2>&1 || true
external_desc="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["external"])' "$OUT_DIR/descriptors.json")"
internal_desc="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["internal"])' "$OUT_DIR/descriptors.json")"
import_payload="$(
  python - "$external_desc" "$internal_desc" <<'PY'
import json
import sys

external_desc, internal_desc = sys.argv[1], sys.argv[2]
print(json.dumps([
    {"desc": external_desc, "timestamp": "now", "active": True, "range": [0, 100], "internal": False},
    {"desc": internal_desc, "timestamp": "now", "active": True, "range": [0, 100], "internal": True},
]))
PY
)"
rpc -rpcwallet=phantos importdescriptors "$import_payload" >/dev/null
receive_addr="$(rpc -rpcwallet=phantos getnewaddress)"

rpc -rpcwallet=miner sendtoaddress "$receive_addr" 1.0 >/dev/null
rpc -rpcwallet=miner generatetoaddress 1 "$miner_addr" >/dev/null

dest_addr="$(rpc -rpcwallet=miner getnewaddress)"
utxo_json="$(rpc -rpcwallet=phantos listunspent 1 999999 "[\"$receive_addr\"]")"
python - "$utxo_json" "$dest_addr" "$OUT_DIR/unsigned.psbt" <<'PY'
import json
import subprocess
import sys

utxos = json.loads(sys.argv[1])
dest = sys.argv[2]
out = sys.argv[3]
if not utxos:
    raise SystemExit("no UTXO received")
utxo = utxos[0]
inputs = [{"txid": utxo["txid"], "vout": utxo["vout"]}]
outputs = [{dest: 0.5}]
cmd = [
    "docker", "exec", "phantos-bitcoind-regtest",
    "bitcoin-cli", "-regtest", "-rpcuser=phantos", "-rpcpassword=phantos",
    "-rpcwallet=phantos", "walletcreatefundedpsbt",
    json.dumps(inputs), json.dumps(outputs), "0", '{"includeWatching":true}', "true",
]
result = subprocess.run(cmd, text=True, capture_output=True, check=True)
psbt = json.loads(result.stdout)["psbt"]
open(out, "w", encoding="utf-8").write(psbt)
PY

python - "$OUT_DIR/unsigned.psbt" "$OUT_DIR/signed.psbt" <<'PY'
from pathlib import Path
import sys
from unittest.mock import patch

from app.psbt import parse_psbt, review_psbt, sign_psbt
from app.security.core import OfflineStatus
from app.wallet import create_wallet_context

mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
ctx = create_wallet_context(mnemonic, "", "bip84", "test")
psbt = parse_psbt(Path(sys.argv[1]).read_text(encoding="utf-8").strip())
review = review_psbt(psbt, ctx)
if not review.can_sign:
    raise SystemExit("; ".join(review.errors))
offline = OfflineStatus(True, False, False, True, True, ())
with patch("app.psbt.core.current_offline_status", return_value=offline):
    result = sign_psbt(psbt, ctx)
Path(sys.argv[2]).write_text(result.signed_psbt_base64, encoding="utf-8")
print(f"fee_sats={review.fee_sats}")
print(f"fee_rate_sat_vb={review.fee_rate_sat_vb}")
PY

finalized="$(rpc finalizepsbt "$(cat "$OUT_DIR/signed.psbt")")"
complete="$(python -c 'import json,sys; print(json.loads(sys.stdin.read())["complete"])' <<<"$finalized")"
if [ "$complete" != "True" ] && [ "$complete" != "true" ]; then
  echo "FAIL signed PSBT did not finalize" | tee "$OUT_DIR/summary.txt" >&2
  exit 1
fi

txhex="$(python -c 'import json,sys; print(json.loads(sys.stdin.read())["hex"])' <<<"$finalized")"
txid="$(rpc sendrawtransaction "$txhex")"
rpc -rpcwallet=miner generatetoaddress 1 "$miner_addr" >/dev/null

cat > "$OUT_DIR/summary.txt" <<EOF
PASS Bitcoin Core regtest PSBT roundtrip
txid=$txid
network=regtest
funds=regtest only
EOF

cat "$OUT_DIR/summary.txt"
