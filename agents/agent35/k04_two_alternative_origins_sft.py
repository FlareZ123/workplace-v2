"""SFT: two source-grounded alternative origins of H-17 printer coupon K04.

The receipt hash-chain model is source-heldout only; the transfer-chain model
constructs whole K04 candidates with the original unmodified mask and SHA256.
Neither model asserts the historical producer or the disputed ACK integrity.
"""
from collections import defaultdict
import hashlib
import hmac
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / "resources/evidence/print/spool-reconstruction.log"
AX = ROOT / "resources/evidence/transfers/transfer-audit.jsonl"
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(AX.read_bytes()).hexdigest() == "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
original_k04_sha = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")


def metadata(row):
    job, attempt, kind, dest, stamp = (
        row["JOB"].encode(), row["ATTEMPT"].encode(),
        row["CLASS"].encode(), row["DEST"].encode(), row["time"].encode()
    )
    return (
        b"", job, str(int(job.rsplit(b"-", 1)[1])).encode(), stamp,
        attempt, kind, dest, job + b"|" + attempt,
        job + b"|" + stamp, b"|".join((job, attempt, kind, dest, stamp)),
    )


def hashes(previous, message):
    return (
        hashlib.sha256(previous + message).digest(),
        hashlib.sha256(message + previous).digest(),
        hashlib.sha256(b"H17-REC8|" + previous + message).digest(),
        hashlib.sha512(previous + message).digest(),
        hashlib.blake2s(previous + message).digest(),
        hashlib.blake2s(message + previous).digest(),
        hmac.digest(previous, message, "sha256"),
        hmac.digest(message, previous, "sha256"),
        hashlib.md5(previous + message).digest(),
        hashlib.md5(message + previous).digest(),
    )


printer = []
for line in SPOOL.read_text().splitlines():
    if line.startswith("#") or not line:
        continue
    fields = line.split()
    row = {"time": fields[0]}
    row.update(item.split("=", 1) for item in fields[1:])
    row["bytes"] = bytes.fromhex(row["PAYLOAD"])
    printer.append(row)
assert len(printer) == 133
assert printer[129]["time"] == "2026-10-03T18:02:00Z"
assert printer[129]["STATE"] == "ACK" and printer[129]["ATTEMPT"] == "2"

chain_checks = 0
chain_hits = 0
for i in range(1, 128):
    before, after = printer[i - 1], printer[i]
    for msg in metadata(after):
        for idx, digest in enumerate(hashes(before["bytes"], msg)):
            views = (digest,) if idx >= 8 else (digest[:16], digest[-16:])
            for view in views:
                chain_checks += 1
                chain_hits += view == after["bytes"]
assert chain_checks == 22860
before, after = printer[0], printer[1]
planted_msg = metadata(after)[8]
planted_next = hmac.digest(before["bytes"], planted_msg, "sha256")[:16]
assert any(hmac.digest(before["bytes"], m, "sha256")[:16] == planted_next for m in metadata(after))
print("RECEIPT_HASH_CHAIN: withheld_pairs=127 checks=22860 original_hits=", chain_hits,
      "synthetic_hmac_heldout=PASS")

transfer = defaultdict(dict)
for line in AX.read_text().splitlines():
    row = json.loads(line)
    if row["kind"] == "CHUNK":
        transfer[row["transfer"]][row["seq"], row["attempt"]] = bytes.fromhex(row["checkpoint"])
assert sorted(transfer) == ["AX-7778", "AX-7781", "AX-7782", "AX-7783"]
assert all(len(x) == 16 and all(len(y) == 2 for y in x.values()) for x in transfer.values())
planted_raw = b"".join(transfer["AX-7782"][i, 2] for i in range(8))
planted_sha = hashlib.sha256(bytes(x ^ y for x, y in zip(planted_raw, mask))).digest()
original_hits = 0
planted_hits = 0
checks = 0
for name, chunks in sorted(transfer.items()):
    for retry_selection in range(256):
        words = [chunks[i, 1 + ((retry_selection >> i) & 1)] for i in range(8)]
        for endian_selection in range(256):
            adjusted = [w[::-1] if ((endian_selection >> i) & 1) else w for i, w in enumerate(words)]
            for reverse in (False, True):
                sequence = adjusted[::-1] if reverse else adjusted
                for rotation in range(8):
                    coupon = b"".join(sequence[rotation:] + sequence[:rotation])
                    component = bytes(x ^ y for x, y in zip(coupon, mask))
                    digest = hashlib.sha256(component).digest()
                    original_hits += digest == original_k04_sha
                    planted_hits += digest == planted_sha
                    checks += 1
assert checks == 4_194_304 and planted_hits >= 1
print("AX_CHECKPOINT_COUPON: complete_candidates=", checks,
      "original_hits=", original_hits, "planted_hits=", planted_hits)
