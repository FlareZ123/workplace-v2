"""Original-source SFT: K04 selected K02 + signed PTW417 strided MT producer.
Run from the repo: python agents/agent12/h17_k04_k02_ptw_strided_source_sft.py
Read-only original records; K04 copied ACK and the original K04 SHA are not model inputs.
"""
from __future__ import annotations
import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
from k04_p951_symbolic_basis import source, ORIGIN, MAG, untemper

SOURCE_SHA = {
    "telemetry": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
    "seals": "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
}
K02_ORIGINAL = "E1A5E474BAD7E853A2E8C71D3317D507"
K03_ORIGINAL = "D7DAD6BC9714519B7DAD0AD4BE8E87FD"
MASK_ORIGINAL = "8556C8CB6140A7F9A5123AC7571BEE1C"
TARGET_ORIGINAL = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

class Basis:
    def __init__(self, original=None):
        self.rows = {} if original is None else original.rows.copy()
        self.pivots = sum(1 << p for p in self.rows)
        self.rank = len(self.rows)
    def insert(self, v, b):
        while v:
            p = v.bit_length() - 1
            old = self.rows.get(p)
            if old is None:
                self.rows[p] = (v, b)
                self.pivots |= 1 << p
                self.rank += 1
                return
            v ^= old[0]
            b ^= old[1]
        assert not b, "source equation contradiction"
    def reduce(self, v):
        b = 0
        seen = v & self.pivots
        while seen:
            p = seen.bit_length() - 1
            x, val = self.rows[p]
            v ^= x
            b ^= val
            seen = v & self.pivots
        return v, b

def source_blocks(root):
    tele = (root / "evidence/telemetry/freeze-export.jsonl").read_bytes()
    seals = (root / "evidence/maintenance/seal-receipts.jsonl").read_bytes()
    assert hashlib.sha256(tele).hexdigest() == SOURCE_SHA["telemetry"]
    assert hashlib.sha256(seals).hexdigest() == SOURCE_SHA["seals"]
    start = datetime(2026, 10, 3, 21, 13, 40, tzinfo=timezone.utc)
    end = datetime(2026, 10, 3, 21, 13, 48, tzinfo=timezone.utc)
    pick = {}
    for line in tele.splitlines():
        row = json.loads(line)
        if (row.get("tag"), row.get("field"), row.get("quality"), row.get("state")) != ("LT-204", "DIAG_WORD", "GOOD", "HOLD"):
            continue
        if not start <= datetime.fromisoformat(row["ts"]) < end:
            continue
        seq = row["seq"]
        if 0 <= seq < 8 and (seq not in pick or row["revision"] > pick[seq]["revision"]):
            pick[seq] = row
    k02 = b"".join(int(pick[seq]["value"]).to_bytes(2, "big") for seq in range(8))
    assert k02.hex().upper() == K02_ORIGINAL
    pick_seals = {}
    for line in seals.splitlines():
        row = json.loads(line)
        if (row.get("permit"), row.get("state"), row.get("fitment"), row.get("signed")) != ("PTW-417", "CLOSED", "AS_LEFT", True):
            continue
        bay = row["bay"]
        if bay not in pick_seals or row["revision"] > pick_seals[bay]["revision"]:
            pick_seals[bay] = row
    k03 = b"".join(bytes.fromhex(pick_seals[bay]["serial"].split("-")[1]) for bay in "BDAC")
    assert k03.hex().upper() == K03_ORIGINAL
    routing = json.loads((root / "evidence/recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((root / "acceptance.json").read_text(encoding="utf-8"))
    assert routing["K04"]["masked_component"] == MASK_ORIGINAL
    assert acceptance["slot_sha256"]["K04"] == TARGET_ORIGINAL
    assert hashlib.sha256(k02).digest()[:16].hex() == "0d7e3ab56fb75da3eb0e2e06786d239e"
    return k02, k03

def output(data, order, endian, unt):
    pieces = [data[i:i + 4] for i in range(0, 16, 4)]
    if order:
        pieces.reverse()
    return [untemper(int.from_bytes(p, endian)) if unt else int.from_bytes(p, endian) for p in pieces]

def build_projector(base, s, stages, target):
    donor, checks = {}, []
    for n, pos in enumerate(stages):
        for bit, vec in enumerate(s[pos - ORIGIN]):
            i = 32 * n + bit
            r, e = base.reduce(vec)
            expr = (1 << i) ^ (e << 128)
            while r:
                pivot = r.bit_length() - 1
                if pivot not in donor:
                    donor[pivot] = (r, expr)
                    break
                x, y = donor[pivot]
                r ^= x
                expr ^= y
            if not r:
                checks.append(expr)
    free, outputs = {}, []
    for vec in target:
        r, e = base.reduce(vec)
        expr = e << 128
        free_mask = 0
        while r:
            pivot = r.bit_length() - 1
            if pivot not in donor:
                break
            x, y = donor[pivot]
            r ^= x
            expr ^= y
        while r:
            pivot = r.bit_length() - 1
            if pivot not in free:
                j = len(free)
                free[pivot] = (r, 1 << j)
                free_mask ^= 1 << j
                break
            x, y = free[pivot]
            r ^= x
            free_mask ^= y
        outputs.append((expr & ((1 << 128) - 1), (expr >> 128) & 1, free_mask))
    constant = sum(value << j for j, (_, value, _) in enumerate(outputs))
    donor_out = [sum(1 << j for j, (coeff, _, _) in enumerate(outputs) if coeff >> i & 1) for i in range(128)]
    free_out = [sum(1 << j for j, (_, _, coeff) in enumerate(outputs) if coeff >> i & 1) for i in range(len(free))]
    return checks, constant, donor_out, free_out

def projector_value(raw, constant, terms):
    out = constant
    while raw:
        x = raw & -raw
        out ^= terms[x.bit_length() - 1]
        raw ^= x
    return out

def printer_output(native):
    result = bytearray()
    for lane in range(4):
        x = (native >> (32 * lane)) & 0xffffffff
        x ^= x >> 11
        x ^= (x << 7) & 0x9d2c5680
        x ^= (x << 15) & 0xefc60000
        x ^= x >> 18
        result.extend((x & 0xffffffff).to_bytes(4, "little"))
    return bytes(result)

def main(root):
    t0 = time.monotonic()
    k02, k03 = source_blocks(root)
    prior, states = source(root)
    base = Basis(prior)
    assert base.rank == 15365
    while len(states) <= 1408 - ORIGIN:
        i = len(states)
        t = i - 624
        states.append([states[t+397][j] ^ (states[t][31] if j == 30 else (states[t+1][j+1] if j < 30 else 0)) ^ (states[t+1][0] if MAG >> j & 1 else 0) for j in range(32)])
    target = [v for p in range(951, 955) for v in states[p - ORIGIN]]
    words = [k03[i:i+4] for i in range(0, 16, 4)]
    choices = [(int.from_bytes(w, "big"), int.from_bytes(w, "little"),
                untemper(int.from_bytes(w, "big")), untemper(int.from_bytes(w, "little"))) for w in words]
    corpus = [sum(choices[order[i]][modes[i]] << (32*i) for i in range(4))
              for order in itertools.permutations(range(4))
              for modes in itertools.product(range(4), repeat=4)]
    assert len(corpus) == 6144

    assignments = matched_source = tested_full = nmodels = positives = 0
    component_values = set()
    coupon_natives = set()
    for k02_stage in (1178, 1405):
        geometry = Basis(base)
        for pos in range(k02_stage, k02_stage + 4):
            for v in states[pos - ORIGIN]:
                geometry.insert(v, 0)
        target_reduced = [geometry.reduce(v)[0] for v in target]
        possible = []
        for stride in range(2, 7):
            for first in range(-1000, 952):
                stages = [first + j * stride for j in range(4)]
                donor = Basis()
                for pos in stages:
                    for v in states[pos - ORIGIN]:
                        r = geometry.reduce(v)[0]
                        if r:
                            donor.insert(r, 0)
                rank_before = donor.rank
                for v in target_reduced:
                    if v:
                        donor.insert(v, 0)
                q = donor.rank - rank_before
                if q <= 16:
                    possible.append((stride, first, stages, q))
        assert len(possible) == 80
        print("phase", k02_stage, "target-reaching geometry", len(possible), flush=True)
        for order, endian, untemp in itertools.product((0, 1), ("little", "big"), (0, 1)):
            donor_basis = Basis(base)
            for i, word in enumerate(output(k02, order, endian, untemp)):
                for bit, vec in enumerate(states[k02_stage+i-ORIGIN]):
                    donor_basis.insert(vec, (word >> bit) & 1)
            for stride, first, stages, q in possible:
                constraints, constant, columns, free = build_projector(donor_basis, states, stages, target)
                assert len(free) == q
                nmodels += 1
                fake = sum(donor_basis.reduce(vec)[1] << (32*n+j)
                           for n, pos in enumerate(stages) for j, vec in enumerate(states[pos-ORIGIN]))
                assert all(((c & fake).bit_count() ^ (c >> 128)) & 1 == 0 for c in constraints)
                expected = sum(donor_basis.reduce(vec)[1] << j for j, vec in enumerate(target))
                predicted = projector_value(fake, constant, columns)
                assert expected in {predicted ^ sum(free[i] for i in range(q) if x >> i & 1) for x in range(1 << q)}
                positives += 1
                for raw in corpus:
                    assignments += 1
                    if any(((c & raw).bit_count() ^ (c >> 128)) & 1 for c in constraints):
                        continue
                    matched_source += 1
                    native_base = projector_value(raw, constant, columns)
                    for subset in range(1 << q):
                        native = native_base
                        for j, term in enumerate(free):
                            if subset >> j & 1:
                                native ^= term
                        coupon_natives.add(native)
                        component = bytes(a ^ b for a,b in zip(printer_output(native), bytes.fromhex(MASK_ORIGINAL)))
                        component_values.add(component)
                        tested_full += 1
                        assert hashlib.sha256(component).hexdigest() != TARGET_ORIGINAL, "original K04 recovery match"
    assert (nmodels, assignments, matched_source, tested_full, len(component_values)) == (1280, 7864320, 184448, 590848, 1408)
    print("models", nmodels, "source_assignments", assignments, "source_compatible", matched_source,
          "full_original_K04_checks", tested_full, "distinct_components", len(component_values),
          "synthetic_complete_positive", positives, "ORIGINAL_K04_HITS 0")
    extra = 0
    for native in coupon_natives:
        original = printer_output(native)
        for reverse_words, reverse_word_bytes, reverse_bits in itertools.product((False,True), repeat=3):
            parts = [original[i:i+4] for i in range(0,16,4)]
            if reverse_words:
                parts.reverse()
            if reverse_word_bytes:
                parts = [x[::-1] for x in parts]
            payload = b"".join(parts)
            if reverse_bits:
                payload = bytes(int(f"{x:08b}"[::-1], 2) for x in payload)
            for use_mask in (False,True):
                candidate = bytes(a ^ b for a,b in zip(payload, bytes.fromhex(MASK_ORIGINAL))) if use_mask else payload
                assert hashlib.sha256(candidate).hexdigest() != TARGET_ORIGINAL
                extra += 1
    assert extra == 22528
    print("alternate_serializer_checks", extra, "ORIGINAL_K04_HITS 0",
          "elapsed_seconds", round(time.monotonic() - t0, 2))

if __name__ == "__main__":
    import os
    root = Path(os.environ.get("H17_RESOURCE_ROOT", str(Path(__file__).resolve().parents[2] / "resources")))
    main(root)
