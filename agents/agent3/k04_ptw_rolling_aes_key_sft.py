"""K04 complete-coupon AES-128 issuer: changing PTW four-bay key, common hidden block.
Requires cryptography. python k04_ptw_rolling_aes_key_sft.py --archive h17-archive-dump.zip
Or: python k04_ptw_rolling_aes_key_sft.py --root <repo-root>
All source, candidate, commitment, and verifier files are read-only.
"""
import argparse
import hashlib
import itertools
import json
import re
import zipfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SEALS_SHA = "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ZIP_SHA = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"


def cipher_block(key, block, encrypt):
    c = Cipher(algorithms.AES(key), modes.ECB())
    context = c.encryptor() if encrypt else c.decryptor()
    return context.update(block) + context.finalize()


def transform(data, reverse_words, reverse_bytes):
    words = [data[i:i+4] for i in range(0, 16, 4)]
    if reverse_words:
        words.reverse()
    return b"".join(w[::-1] if reverse_bytes else w for w in words)


def read_inputs(archive, root):
    if archive:
        blob = Path(archive).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == ZIP_SHA
        with zipfile.ZipFile(archive) as z:
            seals = z.read("evidence/maintenance/seal-receipts.jsonl")
            spool = z.read("evidence/print/spool-reconstruction.log")
    else:
        base = Path(root) / "resources" / "evidence"
        seals = (base / "maintenance" / "seal-receipts.jsonl").read_bytes()
        spool = (base / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(seals).hexdigest() == SEALS_SHA
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    return seals, spool


def sources(seals, spool):
    by_permit = {}
    for line in seals.splitlines():
        r = json.loads(line)
        if r["state"] == "CLOSED" and r["fitment"] == "AS_LEFT" and r["signed"]:
            by_permit.setdefault(int(r["permit"][-3:]), []).append(r)
    state = {}
    latest = {}
    for permit in range(390, 418):
        for bay in "ABCD":
            options = [r for r in by_permit.get(permit, []) if r["bay"] == bay]
            if options:
                latest[bay] = max(options, key=lambda r: r["revision"])["serial"][3:]
        if len(latest) == 4:
            state[permit] = dict(latest)
    assert len(state) == 23 and min(state) == 395 and max(state) == 417
    assert "".join(state[417][b] for b in "BDAC") == "D7DAD6BC9714519B7DAD0AD4BE8E87FD"
    packets = {}
    for line in spool.decode("ascii").splitlines():
        if not line.startswith("2026-"):
            continue
        m = re.search(
            r"JOB=PS-261003-(\d{4}) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32})",
            line,
        )
        assert m, line
        n, attempt, status, _, payload = m.groups()
        n = int(n)
        if n <= 427 and attempt == "1" and status == "ACK":
            assert n not in packets
            packets[n] = bytes.fromhex(payload)
    assert len(packets) == 128
    assert all(n in packets and n in state for n in range(395, 417))
    return state, packets


def run(seals, spool):
    state, packets = sources(seals, spool)
    tested = positive = hits = all_holdouts = 0
    max_holdouts = 0
    for order in ("ABCD", "BDAC"):
        for kw, kb, pw, pb, encrypt in itertools.product((False, True), repeat=5):
            keys = {
                n: transform(bytes.fromhex("".join(state[n][bay] for bay in order)), kw, kb)
                for n in range(395, 418)
            }
            source = transform(packets[395], pw, pb)
            common = cipher_block(keys[395], source, not encrypt)
            holdouts = sum(
                transform(cipher_block(keys[n], common, encrypt), pw, pb) == packets[n]
                for n in range(396, 417)
            )
            max_holdouts = max(max_holdouts, holdouts)
            all_holdouts += holdouts == 21
            coupon = transform(cipher_block(keys[417], common, encrypt), pw, pb)
            component = bytes(x ^ y for x, y in zip(coupon, MASK))
            hits += hashlib.sha256(component).hexdigest() == TARGET
            # An independent hidden-common-block positive control for this
            # exact key, orientation and historical 21-packet source geometry.
            planted = bytes.fromhex("5E3F7AE8B44172DC0102030405060708")
            synthetic = {
                n: transform(cipher_block(keys[n], planted, encrypt), pw, pb)
                for n in range(395, 418)
            }
            recovered = cipher_block(keys[395], transform(synthetic[395], pw, pb), not encrypt)
            good = recovered == planted and all(
                transform(cipher_block(keys[n], recovered, encrypt), pw, pb) == synthetic[n]
                for n in range(396, 418)
            ) and transform(cipher_block(keys[417], recovered, encrypt), pw, pb) == synthetic[417]
            positive += bool(good)
            tested += 1
    outcome = {
        "models": tested,
        "historical_holdout_count": 21,
        "max_exact_heldout_packets": max_holdouts,
        "all_21_holdout_fits": all_holdouts,
        "original_k04_sha256_matches": hits,
        "planted_full_coupon_positives": positive,
    }
    assert outcome == {
        "models": 64,
        "historical_holdout_count": 21,
        "max_exact_heldout_packets": 0,
        "all_21_holdout_fits": 0,
        "original_k04_sha256_matches": 0,
        "planted_full_coupon_positives": 64,
    }
    print(json.dumps(outcome, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.add_mutually_exclusive_group(required=True)
    args.add_argument("--archive")
    args.add_argument("--root")
    options = parser.parse_args()
    run(*read_inputs(options.archive, options.root))
