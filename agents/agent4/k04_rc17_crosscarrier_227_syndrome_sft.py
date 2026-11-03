"""Original 4-byte cross-carrier MT227 parity-syndrome donor search.

Run: python agents/agent4/k04_rc17_crosscarrier_227_syndrome_sft.py
Selected printer ACK and K04/K08 commitments are not loaded.
"""
import hashlib
import importlib.util
import json
import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "resources"
spec = importlib.util.spec_from_file_location("mt", ROOT / "agents/agent49/k04_p951_symbolic_basis.py")
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
basis, states = mt.source(RES)
assert basis.rank == 15365
fields = {}


def add(label, data):
    assert len(data) == 4
    fields[label] = data


raw = (RES / "evidence/procedures/RC-17-scans.txt").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d"
for match in re.finditer(
        rb"DOCUMENT RC-17 / REV (B|C|D-draft) / SECTION (\w+)"
        rb".*?Footer control strip: ([0-9A-F]{8})", raw, re.S):
    add("RC17:" + match[1].decode() + ":" + match[2].decode(),
        bytes.fromhex(match[3].decode()))

tr = (RES / "evidence/recorder/trip-recorder.raw").read_bytes()
assert hashlib.sha256(tr).hexdigest() == "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
for i in range(88):
    off = 16 + 24 * i
    time, node, event, latch, seq, word, aux, crc = struct.unpack_from(
        "<IHBBI4sII", tr, off)
    if (zlib.crc32(tr[off:off + 20]) & 0xFFFFFFFF) == crc:
        add("TRP2:" + str(i), word)

seals = (RES / "evidence/maintenance/seal-receipts.jsonl").read_text().splitlines()
for i, line in enumerate(seals):
    h = json.loads(line)["serial"].split("-")[-1]
    if re.fullmatch("[0-9a-fA-F]{8}", h):
        add("SEAL:" + str(i), bytes.fromhex(h))
for label, h in (("A", "049AAB2E"), ("B", "1CDE7A82"),
                 ("C", "CD7C6023"), ("D", "4303C91A")):
    add("WN14:" + label, bytes.fromhex(h))
route = json.loads((RES / "evidence/recovery-routing.json").read_text())
for k, field in (("K04", "masked_component"), ("K08", "desk_nonce")):
    data = bytes.fromhex(route[k][field])
    for i in range(4):
        add("ROUTE:" + k + ":" + str(i), data[i * 4:(i + 1) * 4])
assert len(fields) == 152


def reduce_source(v):
    residual = rhs = 0
    while v:
        p = v.bit_length() - 1
        if p in basis.rows:
            x, c = basis.rows[p]
            v ^= x
            rhs ^= c
        else:
            residual |= 1 << p
            v ^= 1 << p
    return residual, rhs


def constraints(bits):
    pivots = {}
    relations = []
    for bit, (v, rhs) in enumerate(bits):
        mask = 1 << bit
        while v:
            p = v.bit_length() - 1
            if p not in pivots:
                pivots[p] = (v, mask, rhs)
                break
            w, prior, c = pivots[p]
            v ^= w
            mask ^= prior
            rhs ^= c
        if not v:
            relations.append((mask, rhs))
    return relations


rows = {}
for mode in ("native", "tempered"):
    rows[mode] = [
        [reduce_source(x) for x in (
            mt.get(states, stage) if mode == "native"
            else mt.temper(mt.get(states, stage))
        )]
        for stage in range(mt.ORIGIN, mt.LAST + 1)
    ]

tested = 0
matched = []
counts = {}
positive_done = False
for mode, sequence in rows.items():
    sites = 0
    for stage in range(mt.ORIGIN, mt.LAST - 227 + 1):
        left = sequence[stage - mt.ORIGIN]
        right = sequence[stage + 227 - mt.ORIGIN]
        if sum(v == 0 for v, _ in left) > 12 or sum(v == 0 for v, _ in right) > 12:
            continue
        checks = constraints(left + right)
        cross = sum(bool(mask & 0xFFFFFFFF) and bool(mask >> 32)
                    for mask, c in checks)
        if cross < 24:
            continue
        sites += 1
        if not positive_done:
            # Synthetic paired output from source-fixed parities, free bits zero.
            planted = sum(rhs << i for i, (vec, rhs) in enumerate(left + right))
            assert all(((planted & mask).bit_count() & 1) == rhs
                       for mask, rhs in checks)
            bit_to_flip = (next(mask for mask, rhs in checks if mask).bit_length() - 1)
            assert any(((planted ^ (1 << bit_to_flip)) & mask).bit_count() % 2 != rhs
                       for mask, rhs in checks)
            positive_done = True
        for endian in ("little", "big"):
            lookup = {}
            for key, data in fields.items():
                x = int.from_bytes(data, endian)
                syndrome = sum(((x & (mask & 0xFFFFFFFF)).bit_count() & 1) << bit
                               for bit, (mask, rhs) in enumerate(checks))
                lookup.setdefault(syndrome, []).append(key)
            for key, data in fields.items():
                y = int.from_bytes(data, endian)
                syndrome = sum(((((y & (mask >> 32)).bit_count() & 1) ^ rhs) << bit)
                               for bit, (mask, rhs) in enumerate(checks))
                for left_key in lookup.get(syndrome, []):
                    if left_key != key:
                        matched.append((mode, stage, endian, left_key, key))
            tested += len(fields) * (len(fields) - 1)
    counts[mode] = sites
    print("VIEW", mode, "SOURCE-CROSS-DONOR_PAIR_SITES", sites)
assert counts == {"native": 143, "tempered": 145}, counts
assert tested == 13220352, tested
assert not matched, matched
assert positive_done
print("ORIGINAL_CONTROL_WORDS", len(fields))
print("INFORMATIVE_PAIR_ASSIGNMENTS", tested, "ORIGINAL_MATCHES", len(matched))
print("SYNTHETIC_POSITIVE_AND_SINGLE_BIT_NEGATIVE PASS")
print("NO_AUTHENTIC_K04_BITS; COMPLEMENTARY_CARRIER_WITNESS_NEEDED")
