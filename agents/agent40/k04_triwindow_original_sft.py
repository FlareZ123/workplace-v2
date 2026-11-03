"""Speculative full K04 coupon reconstruction from three original carriers.

Run at repository root: python agents/agent40/k04_triwindow_original_sft.py
Reads original source and the original K04 digest; never changes them.
"""
import hashlib
import importlib.util
import itertools
import json
import random
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "resources"
spec = importlib.util.spec_from_file_location("h17_mt", ROOT / "agents/agent49/k04_p951_symbolic_basis.py")
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
source, states = mt.source(SRC)
assert source.rank == 15365
route = json.loads((SRC / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((SRC / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target_digest = acceptance["slot_sha256"]["K04"]
assert len(mask) == 16 and acceptance["schema"] == "REC8/1"


def clone(system):
    out = mt.Basis()
    out.rows = system.rows.copy()
    out.rank = system.rank
    return out


def add_word(system, at, encoded):
    native = mt.untemper(encoded)
    for j, expr in enumerate(mt.get(states, at)):
        system.insert(expr, (native >> j) & 1)


def coupon_keys(system, digest):
    """Project all target outputs and enumerate the residual affine code."""
    output_bits = []
    for at in range(951, 955):
        for expr in mt.get(states, at):
            val, residue = 0, expr
            while residue:
                p = residue.bit_length() - 1
                if p not in system.rows:
                    break
                row, right = system.rows[p]
                residue ^= row
                val ^= right
            output_bits.append((residue, val))
    quotient, coords, dimension = {}, [], 0
    for residue, val in output_bits:
        expr, variable = residue, 0
        while expr:
            p = expr.bit_length() - 1
            if p not in quotient:
                quotient[p] = (expr, 1 << dimension)
                variable ^= 1 << dimension
                dimension += 1
                break
            basis_expr, basis_var = quotient[p]
            expr ^= basis_expr
            variable ^= basis_var
        coords.append((variable, val))
    if dimension > 15:
        return dimension, []
    matches = []
    for bits in range(1 << dimension):
        payload = bytearray()
        for lane in range(4):
            native = 0
            for j in range(32):
                variable, val = coords[32 * lane + j]
                native |= (val ^ ((bits & variable).bit_count() & 1)) << j
            native ^= native >> 11
            native ^= (native << 7) & 0x9D2C5680
            native ^= (native << 15) & 0xEFC60000
            native ^= native >> 18
            payload.extend(native.to_bytes(4, "little"))
        key = bytes(x ^ y for x, y in zip(payload, mask))
        if hashlib.sha256(key).hexdigest() == digest:
            matches.append((key.hex().upper(), payload.hex().upper(), bits))
    return dimension, matches


def synthetic_positive():
    # Three omitted initial-state bits; no historical K04 material in the control.
    state = random.Random(410037).getrandbits(19968)
    absent = []
    for at in range(951, 955):
        for expr in mt.get(states, at):
            index = expr.bit_length() - 1
            if index not in absent:
                absent.append(index)
            if len(absent) == 3:
                break
        if len(absent) == 3:
            break
    assert len(absent) == 3
    held = mt.Basis()
    for j in range(19968):
        if j not in absent:
            held.insert(1 << j, (state >> j) & 1)
    payload = bytearray()
    for at in range(951, 955):
        native = sum((((expr & state).bit_count() & 1) << j)
                     for j, expr in enumerate(mt.get(states, at)))
        native ^= native >> 11
        native ^= (native << 7) & 0x9D2C5680
        native ^= (native << 15) & 0xEFC60000
        native ^= native >> 18
        payload.extend(native.to_bytes(4, "little"))
    key = bytes(x ^ y for x, y in zip(payload, mask))
    dimension, matches = coupon_keys(held, hashlib.sha256(key).hexdigest())
    assert dimension == 3 and len(matches) == 1 and matches[0][0] == key.hex().upper()
    print("synthetic withheld-3-bit coupon recovery: PASS")


def original():
    raw = (SRC / "evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
    _, record_size, count = struct.unpack_from("<HHI", raw, 8)
    assert record_size == 24
    node50, node49 = {}, {}
    for i in range(count):
        record = raw[16 + i * 24:16 + (i + 1) * 24]
        _, node, event, latch, seq, ctrl, _, crc = struct.unpack("<IHBBI4sII", record)
        if zlib.crc32(record[:20]) != crc:
            continue
        value = int.from_bytes(ctrl, "little")
        if node == 50:
            node50[seq] = value
        if node == 49 and event == 82 and seq in range(300, 304):
            node49[seq] = value
    assert set(range(46, 65)).issubset(node50) and set(range(300, 304)) == set(node49)
    receipts_raw = (SRC / "evidence/maintenance/seal-receipts.jsonl").read_bytes()
    assert hashlib.sha256(receipts_raw).hexdigest() == "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
    rev1 = [json.loads(line) for line in receipts_raw.splitlines()
            if b'"permit":"PTW-417"' in line or b'"permit": "PTW-417"' in line]
    rev1 = [r for r in rev1 if r["revision"] == 1]
    assert len(rev1) == 5
    counts = {"seals": 0, "recorder": 0, "win_latch": 0, "tested_portfolios": 0, "complete_candidates": 0}
    winners = []
    for bay_order in itertools.permutations("ABCD"):
        for a_order in itertools.permutations([r for r in rev1 if r["bay"] == "A"]):
            order = [r for bay in bay_order for r in
                     (a_order if bay == "A" else [next(z for z in rev1 if z["bay"] == bay)])]
            head = clone(source)
            try:
                for i, row in enumerate(order):
                    add_word(head, -919 + i, int.from_bytes(bytes.fromhex(row["serial"][3:]), "little"))
            except (AssertionError, ValueError):
                continue
            counts["seals"] += 1
            for start in range(46, 61):
                mid = clone(head)
                try:
                    for j in range(5):
                        add_word(mid, -465 + j, node50[start + j])
                except (AssertionError, ValueError):
                    continue
                counts["recorder"] += 1
                for at in (-297, -296, -295, -294):
                    final = clone(mid)
                    try:
                        for j in range(4):
                            add_word(final, at + j, node49[300 + j])
                    except (AssertionError, ValueError):
                        continue
                    counts["win_latch"] += 1
                    dimension, hits = coupon_keys(final, target_digest)
                    if dimension <= 15:
                        counts["tested_portfolios"] += 1
                        counts["complete_candidates"] += 1 << dimension
                        winners.extend((bay_order, a_order, start, at, hit) for hit in hits)
    assert counts == {"seals": 48, "recorder": 720, "win_latch": 1980,
                      "tested_portfolios": 420, "complete_candidates": 3360}, counts
    assert not winners, winners
    print("original-source model counts:", counts)
    print("original unmodified K04 SHA256 hits: 0/3360")
    print("K04 component: unresolved; model placements unverified")


if __name__ == "__main__":
    synthetic_positive()
    original()
