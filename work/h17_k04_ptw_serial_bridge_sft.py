#!/usr/bin/env python3
"""Bounded PTW-seal / printer-stream cross-source tests for K04.

Run from the repository root. This falsifies three source-motivated hypotheses;
it does not alter canonical candidates.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt  # noqa: E402


def load_records():
    records = []
    path = ROOT / "resources/evidence/maintenance/seal-receipts.jsonl"
    for line in path.read_text().splitlines():
        d = json.loads(line)
        if d.get("state") == "CLOSED" and d.get("fitment") == "AS_LEFT" and d.get("signed"):
            records.append({
                "permit": int(d["permit"].split("-")[1]),
                "bay": d["bay"],
                "revision": int(d["revision"]),
                "serial": d["serial"][3:].upper(),
            })
    return records


def selected_ptw417(records):
    latest = {}
    for d in records:
        if d["permit"] == 417:
            old = latest.get(d["bay"])
            if old is None or d["revision"] > old["revision"]:
                latest[d["bay"]] = d
    # The K03 source rule uses the signed closeout witness walk B,D,A,C.
    return [latest[b]["serial"] for b in ("B", "D", "A", "C")]


def all_raw_four_serials(records, target_hash):
    serials = sorted({d["serial"] for d in records})
    checked = 0
    for perm in itertools.permutations(serials, 4):
        words = [bytes.fromhex(x) for x in perm]
        for flips in range(16):
            candidate = b"".join(words[j][::-1] if (flips >> j) & 1 else words[j] for j in range(4))
            checked += 1
            if hashlib.sha256(candidate).hexdigest() == target_hash:
                return {"hit": True, "candidate": candidate.hex().upper(),
                        "serials": perm, "byte_flips": flips, "checked": checked}
    return {"hit": False, "distinct_serials": len(serials), "checked": checked}


def add_gap_block(basis, symbolic, serials, start, endian):
    for offset, serial in enumerate(serials):
        native = mt.untemper(int.from_bytes(bytes.fromhex(serial), endian))
        for bit, form in enumerate(mt.get(symbolic, start + offset)):
            basis.insert(form, (native >> bit) & 1)


def predict_k04(basis, symbolic, mask):
    payload = bytearray()
    for stage in range(951, 955):
        stateword = 0
        for bit, form in enumerate(mt.get(symbolic, stage)):
            value = basis.predict(form)
            if value is None:
                return None
            stateword |= value << bit
        value = stateword
        value ^= value >> 11
        value ^= (value << 7) & 0x9D2C5680
        value ^= (value << 15) & 0xEFC60000
        value ^= value >> 18
        payload.extend((value & 0xFFFFFFFF).to_bytes(4, "little"))
    component = bytes(a ^ b for a, b in zip(payload, mask))
    return payload.hex().upper(), component.hex().upper(), hashlib.sha256(component).hexdigest()


def gap_bridge(records, target_hash, mask):
    base, symbolic = mt.source(ROOT)
    latest = {}
    for d in records:
        if 390 <= d["permit"] <= 416:
            old = latest.get(d["permit"])
            if old is None or d["revision"] > old["revision"]:
                latest[d["permit"]] = d
    windows = []
    for start in range(390, 414):
        numbers = list(range(start, start + 4))
        if all(n in latest for n in numbers):
            windows.append((f"PTW{start}-{start+3}", [latest[n]["serial"] for n in numbers]))
    windows.append(("PTW417-BDAC", selected_ptw417(records)))
    checked = conflicts = full = 0
    for (name_a, block_a), (name_b, block_b) in itertools.permutations(windows, 2):
        for endian_a, endian_b in itertools.product(("big", "little"), repeat=2):
            checked += 1
            basis = mt.Basis()
            basis.rows = dict(base.rows)
            basis.rank = base.rank
            try:
                add_gap_block(basis, symbolic, block_a, 328, endian_a)
                add_gap_block(basis, symbolic, block_b, 724, endian_b)
            except AssertionError:
                conflicts += 1
                continue
            result = predict_k04(basis, symbolic, mask)
            if result is None:
                continue
            full += 1
            if result[2] == target_hash:
                return {
                    "hit": True, "first_block": name_a, "second_block": name_b,
                    "first_endian": endian_a, "second_endian": endian_b,
                    "payload": result[0], "component": result[1], "sha256": result[2],
                    "base_rank": base.rank, "final_rank": basis.rank,
                    "pairs_checked": checked, "source_conflicts": conflicts,
                }
    return {
        "hit": False, "window_count": len(windows), "pairs_checked": checked,
        "source_conflicts": conflicts, "fully_predicted": full,
        "base_rank": base.rank, "rank_after_two_blocks": base.rank + 256,
    }


def cpython_payload(seed, mode):
    r = random.Random(seed)
    if mode == "randbytes":
        return r.randbytes(16)
    if mode == "get128be":
        return r.getrandbits(128).to_bytes(16, "big")
    if mode == "get128le":
        return r.getrandbits(128).to_bytes(16, "little")
    if mode == "4x32be":
        return b"".join(r.getrandbits(32).to_bytes(4, "big") for _ in range(4))
    if mode == "4x32le":
        return b"".join(r.getrandbits(32).to_bytes(4, "little") for _ in range(4))
    raise ValueError(mode)


def cpp_mt_words(seed, n=4):
    seed &= 0xFFFFFFFF
    state = [0] * 624
    state[0] = seed
    for i in range(1, 624):
        state[i] = (1812433253 * (state[i - 1] ^ (state[i - 1] >> 30)) + i) & 0xFFFFFFFF
    index = 624
    output = []
    for _ in range(n):
        if index >= 624:
            for k in range(624):
                y = (state[k] & 0x80000000) | (state[(k + 1) % 624] & 0x7FFFFFFF)
                state[k] = state[(k + 397) % 624] ^ (y >> 1) ^ (0x9908B0DF if y & 1 else 0)
            index = 0
        y = state[index]
        index += 1
        y ^= y >> 11
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y << 15) & 0xEFC60000
        y ^= y >> 18
        output.append(y & 0xFFFFFFFF)
    return output


def java_nextbytes(seed, n=16):
    mask = (1 << 48) - 1
    state = (seed ^ 0x5DEECE66D) & mask
    output = bytearray()
    while len(output) < n:
        state = (state * 0x5DEECE66D + 0xB) & mask
        value = state >> 16
        for _ in range(min(4, n - len(output))):
            output.append(value & 0xFF)
            value >>= 8
    return bytes(output)


def xorshift_words(seed, n=4):
    x = seed & 0xFFFFFFFF or 0x6D2B79F5
    output = []
    for _ in range(n):
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        x &= 0xFFFFFFFF
        output.append(x)
    return output


def splitmix_words(seed, n=2):
    x = seed & 0xFFFFFFFFFFFFFFFF
    output = []
    for _ in range(n):
        x = (x + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = x
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        output.append((z ^ (z >> 31)) & 0xFFFFFFFFFFFFFFFF)
    return output


def seed_payloads(seed):
    out = {f"cpy_{mode}": cpython_payload(seed, mode)
           for mode in ("randbytes", "get128be", "get128le", "4x32be", "4x32le")}
    for endian in ("big", "little"):
        out[f"cpp_mt_{endian}"] = b"".join(x.to_bytes(4, endian) for x in cpp_mt_words(seed))
        out[f"xorshift_{endian}"] = b"".join(x.to_bytes(4, endian) for x in xorshift_words(seed))
        out[f"splitmix_{endian}"] = b"".join(x.to_bytes(8, endian) for x in splitmix_words(seed))
    out["java_nextbytes"] = java_nextbytes(seed)
    return out


def same_suffix_seed_controls(records):
    by_permit = {}
    for d in records:
        if 390 <= d["permit"] <= 416:
            old = by_permit.get(d["permit"])
            if old is None or d["revision"] > old["revision"]:
                by_permit[d["permit"]] = d
    spool = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_text().splitlines()
    by_job = {}
    for line in spool:
        m = re.search(r"JOB=PS-\d{6}-(\d{4}).*?PAYLOAD=([0-9A-F]{32})", line)
        if m:
            by_job[int(m.group(1))] = bytes.fromhex(m.group(2))
    checked = matches = 0
    for permit, record in sorted(by_permit.items()):
        payload = by_job.get(permit)
        if payload is None:
            continue
        seed = int(record["serial"], 16)
        for generated in seed_payloads(seed).values():
            checked += 1
            if generated == payload:
                matches += 1
    return {"permit_job_pairs": len(by_permit), "candidate_views": checked, "matches": matches}


def main():
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    target_hash = acceptance["slot_sha256"]["K04"]
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    records = load_records()
    summary = {
        "raw_four_serial_coupon": all_raw_four_serials(records, target_hash),
        "ptw_serials_as_p951_gap_blocks": gap_bridge(records, target_hash, mask),
        "same_suffix_ptw_serial_seed_controls": same_suffix_seed_controls(records),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
