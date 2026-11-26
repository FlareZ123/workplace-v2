#!/usr/bin/env python3
"""Bounded RN-052 / PS-0365 counter-producer and window screen.

Reads only supplied repository resources. Prints counts and hit labels, never
payloads, masks, components, or commitments. Requires cryptography for AES
and ChaCha20 tests; hashlib and hmac are standard library.
"""
import csv
import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "resources"
SPOOL = RES / "evidence/print/spool-reconstruction.log"
ROUTING = RES / "evidence/recovery-routing.json"
ACCEPTANCE = RES / "acceptance.json"
DOCKET = RES / "evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv"

def load_job(spool_text, job, attempt, state, cls, dest):
    pat = re.compile(
        rf"JOB=PS-261003-{job:04d}\s+ATTEMPT=(\d+)\s+STATE=(\w+)\s+"
        rf"CLASS=(\w+)\s+PAYLOAD=([0-9A-Fa-f]{{32}})\s+DEST=(\w+)"
    )
    found = []
    for line in spool_text.splitlines():
        if f"JOB=PS-261003-{job:04d}" not in line:
            continue
        m = pat.search(line)
        if m:
            a, st, cl, payload, destination = m.groups()
            if (int(a), st, cl, destination) == (attempt, state, cls, dest):
                found.append(bytes.fromhex(payload))
    if len(found) != 1:
        raise RuntimeError(f"expected one matching row for PS-{job:04d}, got {len(found)}")
    return found[0]

def matches(coupon, mask, commitment):
    if len(coupon) != 16:
        return False
    component = bytes(a ^ b for a, b in zip(coupon, mask))
    return hashlib.sha256(component).hexdigest().lower() == commitment.lower()

def main():
    routing = json.loads(ROUTING.read_text())
    acceptance = json.loads(ACCEPTANCE.read_text())
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    commitment = acceptance["slot_sha256"]["K04"]
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    spool_text = SPOOL.read_text()

    with DOCKET.open(newline="") as f:
        rows = list(csv.DictReader(
            line for line in f if not line.lstrip().startswith("#")
        ))
    rn052 = next(r for r in rows if r["line_ref"] == "RN-052")
    if (rn052["account"], rn052["folio_or_jacket"], rn052["posting"]) != ("FA-17", "BX25/08", "FILED"):
        raise RuntimeError("RN-052 locator fields differ from source")

    seed = load_job(spool_text, 365, 1, "ACK", "RECOVER", "bench")
    target = load_job(spool_text, 417, 2, "ACK", "RECOVER", "bench")
    if any(len(x) != 16 for x in (mask, nonce, seed, target)):
        raise RuntimeError("unexpected source byte length")

    # Validate the commitment predicate with a synthetic positive control.
    synthetic = bytes(range(16))
    if not matches(bytes(a ^ b for a, b in zip(synthetic, mask)), mask,
                   hashlib.sha256(synthetic).hexdigest()):
        raise RuntimeError("synthetic positive control failed")

    candidates = []

    def add(label, value):
        if len(value) == 16:
            candidates.append((label, value))

    # AES-128 with PS-0365 as key/seed and source-derived counters.
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        def aes(mode, data, decrypt=False):
            ctx = Cipher(algorithms.AES(seed), mode)
            op = ctx.decryptor() if decrypt else ctx.encryptor()
            return op.update(data) + op.finalize()

        for n in (52, 365, 417, 0):
            for endian in ("big", "little"):
                iv = n.to_bytes(16, endian)
                add(f"AES-CTR-stream-{n}-{endian}", aes(modes.CTR(iv), b"\x00" * 16))
                add(f"AES-CTR-target-{n}-{endian}", aes(modes.CTR(iv), target))
        for label, value, decrypt in (
            ("AES-ECB-target-decrypt", target, True),
            ("AES-ECB-seed-encrypt", seed, False),
            ("AES-ECB-seed-decrypt", seed, True),
            ("AES-ECB-mask-encrypt", mask, False),
            ("AES-ECB-mask-decrypt", mask, True),
        ):
            add(label, aes(modes.ECB(), value, decrypt))
        for n in (52, 365, 417, 0):
            for endian in ("big", "little"):
                iv = n.to_bytes(16, endian)
                add(f"AES-CBC-target-decrypt-{n}-{endian}", aes(modes.CBC(iv), target, True))
                add(f"AES-CBC-target-encrypt-{n}-{endian}", aes(modes.CBC(iv), target, False))

        # ChaCha20 requires 256-bit keys; use two conventional expansions.
        for key_name, key in (
            ("sha256-seed", hashlib.sha256(seed).digest()),
            ("seed-repeated", seed + seed),
        ):
            for n in (52, 365, 417):
                for endian in ("big", "little"):
                    nonce16 = n.to_bytes(4, endian) + b"\x00" * 12
                    stream = Cipher(algorithms.ChaCha20(key, nonce16), None).encryptor().update(b"\x00" * 16)
                    plain = Cipher(algorithms.ChaCha20(key, nonce16), None).encryptor().update(target)
                    add(f"ChaCha20-stream-{key_name}-{n}-{endian}", stream)
                    add(f"ChaCha20-target-{key_name}-{n}-{endian}", plain)
        crypto_available = True
    except ImportError:
        crypto_available = False

    # Compact hash/MAC producers over exact source-linked contexts.
    contexts = (
        b"52", b"RN-052", b"PS-261003-0365", b"PS-261003-0417",
        b"RN-052|PS-261003-0417",
        b"RN-052|FA-17|BX25/08|PS-261003-0417",
        b"RECOVER|bench|ACK|2|52",
        b"ESC-N|PS-261003-0417|RECOVER|ACK|2",
    )
    for msg in contexts:
        digests = (
            ("SHA256-seed-message", hashlib.sha256(seed + msg).digest()),
            ("SHA256-message-seed", hashlib.sha256(msg + seed).digest()),
            ("HMAC-SHA256", hmac.new(seed, msg, hashlib.sha256).digest()),
            ("BLAKE2s-keyed", hashlib.blake2s(msg, key=seed, digest_size=32).digest()),
        )
        for name, digest in digests:
            add(f"{name}-{msg.decode('ascii')}-first", digest[:16])
            add(f"{name}-{msg.decode('ascii')}-last", digest[16:32])

    # The RN-052 suffix gives a 52-job gap between PS-0365 and PS-0417.
    ack_pat = re.compile(
        r"JOB=PS-261003-(\d{4})\s+ATTEMPT=(\d+)\s+STATE=(\w+)\s+"
        r"CLASS=(\w+)\s+PAYLOAD=([0-9A-Fa-f]{32})\s+DEST=(\w+)"
    )
    ack_rows = {}
    for line in spool_text.splitlines():
        m = ack_pat.search(line)
        if not m:
            continue
        job, attempt, state, cls, payload, dest = m.groups()
        if 365 <= int(job) <= 416 and state == "ACK":
            row = (int(attempt), cls, bytes.fromhex(payload), dest)
            if int(job) not in ack_rows or row[0] > ack_rows[int(job)][0]:
                ack_rows[int(job)] = row
    if set(ack_rows) != set(range(365, 417)):
        raise RuntimeError("expected 52 acknowledged jobs PS-0365..PS-0416")
    window_payloads = [ack_rows[j][2] for j in range(365, 417)]
    window_blob = b"".join(window_payloads)
    window_plus_target = window_blob + target

    def xor_many(values):
        out = bytearray(16)
        for value in values:
            for i, byte in enumerate(value):
                out[i] ^= byte
        return bytes(out)

    def sum_many(values):
        return bytes(sum(value[i] for value in values) & 0xff for i in range(16))

    window_candidates = {
        "window-xor-all-52": xor_many(window_payloads),
        "window-sum-all-52": sum_many(window_payloads),
        "window-xor-all-52-plus-target": xor_many(window_payloads + [target]),
    }
    predicates = (
        ("RECOVER", lambda row: row[1] == "RECOVER"),
        ("bench", lambda row: row[3] == "bench"),
        ("RECOVER-bench", lambda row: row[1] == "RECOVER" and row[3] == "bench"),
        ("LABEL", lambda row: row[1] == "LABEL"),
        ("STORES", lambda row: row[1] == "STORES"),
    )
    for tag, predicate in predicates:
        selected = [ack_rows[j][2] for j in range(365, 417) if predicate(ack_rows[j])]
        if selected:
            window_candidates[f"window-xor-{tag}-{len(selected)}"] = xor_many(selected)
            window_candidates[f"window-sum-{tag}-{len(selected)}"] = sum_many(selected)
    for residue in range(4):
        selected = [window_payloads[i] for i in range(52) if i % 4 == residue]
        window_candidates[f"window-xor-index-mod4-{residue}-{len(selected)}"] = xor_many(selected)

    for suffix, blob in (("52", window_blob), ("52-plus-target", window_plus_target)):
        digests = (
            ("SHA256", hashlib.sha256(blob).digest()),
            ("MD5", hashlib.md5(blob).digest()),
            ("BLAKE2s", hashlib.blake2s(blob, digest_size=32).digest()),
            ("HMAC-mask", hmac.new(mask, blob, hashlib.sha256).digest()),
            ("HMAC-nonce", hmac.new(nonce, blob, hashlib.sha256).digest()),
            ("HMAC-seed", hmac.new(seed, blob, hashlib.sha256).digest()),
        )
        for name, digest in digests:
            if len(digest) == 16:
                window_candidates[f"window-{name}-{suffix}"] = digest
            else:
                window_candidates[f"window-{name}-{suffix}-first"] = digest[:16]
                window_candidates[f"window-{name}-{suffix}-last"] = digest[16:32]
    candidates.extend(window_candidates.items())

    # Stateful NIST AES-128 CTR_DRBG: PS-0365 is the cross-job seed;
    # generate one 16-byte block for each of the 52 subsequent jobs.
    stateful_models = 0
    stateful_row_matches = 0
    stateful_full_sequences = 0
    stateful_target_matches = 0
    if crypto_available:
        def bxor(a, b):
            return bytes(x ^ y for x, y in zip(a, b))

        def aes128(key, block):
            op = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
            return op.update(block) + op.finalize()

        class CTRDRBG:
            def __init__(self, entropy):
                if len(entropy) != 32:
                    raise RuntimeError("CTR_DRBG seed material must be 32 bytes")
                self.key = bytes(16)
                self.v = bytes(16)
                self.update(entropy)

            def update(self, provided):
                value = int.from_bytes(self.v, "big")
                stream = []
                for _ in range(2):
                    value = (value + 1) & ((1 << 128) - 1)
                    stream.append(aes128(self.key, value.to_bytes(16, "big")))
                material = bxor(b"".join(stream), provided)
                self.key, self.v = material[:16], material[16:]

            def generate(self, additional=None):
                if additional is not None:
                    self.update(additional)
                value = (int.from_bytes(self.v, "big") + 1) & ((1 << 128) - 1)
                packet = aes128(self.key, value.to_bytes(16, "big"))
                self.v = value.to_bytes(16, "big")
                self.update(additional if additional is not None else bytes(32))
                return packet

        row_pat = re.compile(
            r"^(\S+)\s+JOB=PS-261003-(\d{4})\s+ATTEMPT=(\d+)\s+STATE=(\w+)\s+"
            r"CLASS=(\w+)\s+PAYLOAD=([0-9A-Fa-f]{32})\s+DEST=(\w+)"
        )
        spool_rows = []
        for line in spool_text.splitlines():
            m = row_pat.search(line)
            if m:
                timestamp, job, attempt, state, cls, payload, dest = m.groups()
                spool_rows.append({
                    "time": timestamp,
                    "JOB": "PS-261003-" + job,
                    "ATTEMPT": attempt,
                    "STATE": state,
                    "CLASS": cls,
                    "bytes": bytes.fromhex(payload),
                    "DEST": dest,
                    "jobnum": int(job),
                })
        seed_row = next(r for r in spool_rows if
                        r["jobnum"] == 365 and r["ATTEMPT"] == "1" and
                        r["STATE"] == "ACK" and r["CLASS"] == "RECOVER" and
                        r["DEST"] == "bench")
        sequence_rows = []
        for job in range(366, 417):
            matches_for_job = [r for r in spool_rows if
                               r["jobnum"] == job and r["STATE"] == "ACK"]
            if len(matches_for_job) != 1:
                raise RuntimeError("expected one ACK row for PS-%04d" % job)
            sequence_rows.append(matches_for_job[0])
        sequence_rows.append(next(r for r in spool_rows if
                                   r["jobnum"] == 417 and r["ATTEMPT"] == "2" and
                                   r["STATE"] == "ACK" and r["CLASS"] == "RECOVER" and
                                   r["DEST"] == "bench"))
        if len(sequence_rows) != 52:
            raise RuntimeError("expected 52 subsequent job outputs")

        second_halves = (
            nonce,
            mask,
            hashlib.sha256(seed_row["JOB"].encode()).digest()[:16],
            hashlib.sha256(seed_row["time"].encode()).digest()[:16],
            hashlib.md5(seed_row["JOB"].encode()).digest(),
            hashlib.sha256(seed).digest()[:16],
            bytes(16),
            seed,
        )

        def additional_input(row, mode):
            if mode == 0:
                return None
            if mode == 1:
                return bytes(32)
            if mode == 2:
                text = row["JOB"]
            elif mode == 3:
                text = "|".join(row[k] for k in ("JOB", "ATTEMPT", "STATE", "CLASS", "DEST"))
            elif mode == 4:
                text = row["time"]
            elif mode == 5:
                text = row["JOB"] + "|" + row["time"]
            else:
                return hashlib.sha256(bytes([int(row["ATTEMPT"])] )).digest()
            return hashlib.sha256(text.encode()).digest()

        for second in second_halves:
            for order in ("first-seed", "second-seed"):
                entropy = seed + second if order == "first-seed" else second + seed
                for context_mode in range(7):
                    for reverse in (False, True):
                        drbg = CTRDRBG(entropy)
                        outputs = [
                            drbg.generate(additional_input(row, context_mode))
                            for row in sequence_rows
                        ]
                        if reverse:
                            outputs = [value[::-1] for value in outputs]
                        row_matches = sum(
                            output == row["bytes"]
                            for output, row in zip(outputs, sequence_rows)
                        )
                        stateful_row_matches += row_matches
                        stateful_full_sequences += int(row_matches == 52)
                        stateful_target_matches += int(outputs[-1] == target)
                        stateful_models += 1
                        candidates.append((
                            "CTR-DRBG-PS0365-%d-%s-%d-%s" %
                            (second_halves.index(second), order, context_mode, "rev" if reverse else "fwd"),
                            outputs[-1],
                        ))

    commitment_hits = [
        label for label, candidate in candidates
        if matches(candidate, mask, commitment)
    ]
    payload_matches = [label for label, candidate in candidates if candidate == target]
    print(json.dumps({
        "locator": "RN-052 / FA-17 / BX25/08",
        "unverified_index_hypothesis": "PS suffix = 417 - RN suffix = 365",
        "source_roles": {
            "seed": "PS-0365 / RECOVER / bench / ACK / attempt 1",
            "target": "PS-0417 / RECOVER / bench / ACK / attempt 2",
        },
        "crypto_dependency_available": crypto_available,
        "candidate_variants": len(candidates),
        "source_window_jobs": len(ack_rows),
        "window_candidate_variants": len(window_candidates),
        "stateful_drbg_models": stateful_models,
        "stateful_drbg_row_matches_total": stateful_row_matches,
        "stateful_drbg_full_sequence_matches": stateful_full_sequences,
        "stateful_drbg_target_payload_matches": stateful_target_matches,
        "K04_commitment_hits": commitment_hits,
        "selected_payload_exact_matches": payload_matches,
        "raw_values_emitted": False,
    }, indent=2))

if __name__ == "__main__":
    main()
