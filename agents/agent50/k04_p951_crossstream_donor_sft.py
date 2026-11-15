#!/usr/bin/env python3
"""Bounded cross-stream donor tests for the conditional p951 K04 model.

Run from the workplace-v2 repository root:
    python agents/agent50/k04_p951_crossstream_donor_sft.py

The p951 model itself remains conditional / not source-attested. This script
only tests whether retained source vectors can supply its two proposed
four-word gap blocks (stages 328..331 and 724..727).
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
import struct
import sys
import zlib
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "resources"
EVIDENCE = RES / "evidence"
sys.path.insert(0, str(ROOT / "work"))
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt  # noqa: E402


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def temper_int(x: int) -> int:
    y = x
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & 0xFFFFFFFF


class SmallBasis:
    def __init__(self):
        self.rows = {}

    def insert(self, value: int, rhs: int) -> bool:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = (value, rhs)
                return True
            row, bit = self.rows[pivot]
            value ^= row
            rhs ^= bit
        return rhs == 0

    def predict(self, value: int):
        rhs = 0
        while value:
            pivot = value.bit_length() - 1
            if pivot not in self.rows:
                return None
            row, bit = self.rows[pivot]
            value ^= row
            rhs ^= bit
        return rhs


def build_candidate_blocks():
    blocks = {}

    # K01: four WN-14 signed groups in A,B,C,D order.
    group_bytes = {}
    for message_id in ("03", "06", "14"):
        text = (EVIDENCE / "mail" / f"{message_id}.eml").read_text(errors="replace")
        for group, value in re.findall(
            r"WN-14\s*/\s*group\s+([A-D])\s*/\s*([0-9A-F]{8})", text
        ):
            group_bytes[group] = bytes.fromhex(value)
    assert set(group_bytes) == {"A", "B", "C", "D"}
    blocks["K01_WN14_signed"] = b"".join(group_bytes[g] for g in "ABCD")

    # K02: the eight GOOD/HOLD LT-204 DIAG_WORD values in the routed UTC window.
    diag = {}
    for obj in read_jsonl(EVIDENCE / "telemetry" / "freeze-export.jsonl"):
        if not (
            obj.get("tag") == "LT-204"
            and obj.get("field") == "DIAG_WORD"
            and obj.get("quality") == "GOOD"
            and obj.get("state") == "HOLD"
        ):
            continue
        ts = parse_dt(obj["ts"])
        if not (
            datetime(2026, 10, 3, 21, 13, 40, tzinfo=timezone.utc)
            <= ts
            < datetime(2026, 10, 3, 21, 13, 48, tzinfo=timezone.utc)
        ):
            continue
        seq = obj["seq"]
        if seq not in diag or obj["revision"] > diag[seq]["revision"]:
            diag[seq] = obj
    assert set(diag) == set(range(8))
    k02 = b"".join(diag[i]["value"].to_bytes(2, "big") for i in range(8))
    blocks["K02_DIAG_WORD_preimage"] = k02

    # K03: highest signed CLOSED/AS_LEFT PTW-417 serial per bay, B,D,A,C.
    seals = {}
    for obj in read_jsonl(EVIDENCE / "maintenance" / "seal-receipts.jsonl"):
        if not (
            obj.get("permit") == "PTW-417"
            and obj.get("state") == "CLOSED"
            and obj.get("fitment") == "AS_LEFT"
            and obj.get("signed")
        ):
            continue
        bay = obj["bay"]
        if bay not in seals or obj["revision"] > seals[bay]["revision"]:
            seals[bay] = obj
    assert set(seals) == {"A", "B", "C", "D"}
    serials = [seals[b]["serial"] for b in ("B", "D", "A", "C")]
    blocks["K03_serial_raw"] = b"".join(bytes.fromhex(s[3:]) for s in serials)
    # Deliberately weak candidate: first 16 bytes of the ASCII preimage.
    blocks["K03_serial_ascii_prefix"] = "|".join(serials).encode()[:16]

    # Parse the 24-byte recorder records.
    rawrec = (EVIDENCE / "recorder" / "trip-recorder.raw").read_bytes()
    assert (len(rawrec) - 16) % 24 == 0
    recorder = []
    for i in range((len(rawrec) - 16) // 24):
        raw = rawrec[16 + i * 24 : 16 + (i + 1) * 24]
        ts, node, event, latch, seq, control, aux, stored_crc = struct.unpack("<IHBBI4sII", raw)
        calculated_crc = zlib.crc32(raw[:20]) & 0xFFFFFFFF
        recorder.append(
            {
                "i": i,
                "raw": raw,
                "ts": ts,
                "node": node,
                "event": event,
                "latch": latch,
                "seq": seq,
                "control": control,
                "aux": aux,
                "stored_crc": stored_crc,
                "calculated_crc": calculated_crc,
            }
        )
    by_seq = {r["seq"]: r for r in recorder}

    # K05: TRP2 node-31/event-82 control words, seq 300..303.
    k05_seqs = (300, 301, 302, 303)
    blocks["K05_TRP2_control"] = b"".join(by_seq[s]["control"] for s in k05_seqs)

    # K06: RC-17 Rev-C footer strips in the routed service order.
    rc17 = (EVIDENCE / "procedures" / "RC-17-scans.txt").read_text(errors="replace")
    strips = {}
    for match in re.finditer(
        r"DOCUMENT RC-17\s*/\s*REV C\s*/\s*SECTION\s+(\w+).*?Footer control strip:\s*([0-9A-F]{8})",
        rc17,
        re.S,
    ):
        strips[match.group(1)] = bytes.fromhex(match.group(2))
    assert set(strips) >= {"DRAIN", "ISOLATE", "PURGE", "VERIFY"}
    blocks["K06_RC17_service"] = b"".join(
        strips[name] for name in ("DRAIN", "ISOLATE", "PURGE", "VERIFY")
    )

    # K07: latest AX-7782 checkpoint per sequence, 0..7.
    transfer_rows = read_jsonl(EVIDENCE / "transfers" / "transfer-audit.jsonl")
    transfers = defaultdict(dict)
    for obj in transfer_rows:
        if obj.get("kind") != "CHUNK":
            continue
        transfer = obj["transfer"]
        seq = obj["seq"]
        if seq not in transfers[transfer] or obj["attempt"] > transfers[transfer][seq]["attempt"]:
            transfers[transfer][seq] = obj
    assert set(transfers["AX-7782"]) == set(range(8))
    k07 = b"".join(bytes.fromhex(transfers["AX-7782"][i]["checkpoint"]) for i in range(8))
    blocks["K07_AX7782_preimage"] = k07

    route = json.loads((EVIDENCE / "recovery-routing.json").read_text())
    acceptance = json.loads((RES / "acceptance.json").read_text())
    blocks["K04_mask"] = bytes.fromhex(route["K04"]["masked_component"])
    blocks["K08_nonce"] = bytes.fromhex(route["K08"]["desk_nonce"])

    # Whole 16-byte control-word windows from the four retained recorder groups.
    recorder_groups = {
        "predecessor": (200, 201, 202, 203),
        "K05": (300, 301, 302, 303),
        "bad_tail": (900, 901, 902, 903),
        "latest_tail": (990, 991, 992, 993),
    }
    for label, seqs in recorder_groups.items():
        rows = [by_seq[s] for s in seqs]
        blocks[f"TRP2_{label}"] = b"".join(r["control"] for r in rows)

        stored = b"".join(r["stored_crc"].to_bytes(4, "little") for r in rows)
        calculated = b"".join(r["calculated_crc"].to_bytes(4, "little") for r in rows)
        syndrome = b"".join(
            (r["stored_crc"] ^ r["calculated_crc"]).to_bytes(4, "little") for r in rows
        )
        blocks[f"{label}_crc_stored"] = stored
        blocks[f"{label}_crc_calc"] = calculated
        blocks[f"{label}_crc_syndrome"] = syndrome
        blocks[f"{label}_aux"] = b"".join(r["aux"].to_bytes(4, "little") for r in rows)
        blocks[f"{label}_seq"] = b"".join(r["seq"].to_bytes(4, "little") for r in rows)
        blocks[f"{label}_timestamp"] = b"".join(r["ts"].to_bytes(4, "little") for r in rows)

    # Other complete transfer checkpoint vectors, latest attempt per seq.
    for transfer, seq_rows in sorted(transfers.items()):
        if set(seq_rows) == set(range(8)):
            blocks[f"{transfer}_latest_vector"] = b"".join(
                bytes.fromhex(seq_rows[i]["checkpoint"]) for i in range(8)
            )

    assert all(len(value) == 16 for value in blocks.values()), {
        k: len(v) for k, v in blocks.items() if len(v) != 16
    }
    return blocks, k02, k07, route, acceptance


def reduce_source_form(value: int, rhs: int, source_basis):
    remainder = 0
    while value:
        pivot = value.bit_length() - 1
        if pivot in source_basis.rows:
            row, bit = source_basis.rows[pivot]
            value ^= row
            rhs ^= bit
        else:
            bit = 1 << pivot
            remainder |= bit
            value ^= bit
    return remainder, rhs


def donor_forms(block: bytes, start: int, endian: str, transform: str, sym, source_basis):
    forms = []
    for lane in range(4):
        word = int.from_bytes(block[lane * 4 : lane * 4 + 4], endian)
        raw = mt.untemper(word) if transform == "untemper" else word
        for bit, equation in enumerate(mt.get(sym, start + lane)):
            remainder, offset = reduce_source_form(equation, 0, source_basis)
            forms.append((remainder, ((raw >> bit) & 1) ^ offset))
    return forms


def reconstruct_target(forms_a, forms_b, target_forms, mask):
    basis = SmallBasis()
    for vector, rhs in forms_a + forms_b:
        if not basis.insert(vector, rhs):
            return None
    raw_bits = []
    for vector, offset in target_forms:
        prediction = basis.predict(vector)
        if prediction is None:
            return None
        raw_bits.append(offset ^ prediction)
    words = []
    for lane in range(4):
        raw = sum(raw_bits[lane * 32 + bit] << bit for bit in range(32))
        words.append(temper_int(raw))
    payload = b"".join(word.to_bytes(4, "little") for word in words)
    component = bytes(a ^ b for a, b in zip(payload, mask))
    return payload, component, hashlib.sha256(component).hexdigest()


def halfword_reconstruction(
    values_a,
    values_b,
    stages,
    target_forms,
    mask,
    source_basis,
    sym,
    endian_a,
    endian_b,
    kind_a,
    kind_b,
    half_a_first,
    half_a_second,
    reverse_a,
    reverse_b,
    swap_a,
    swap_b,
):
    a = [int.from_bytes(values_a[i : i + 2], endian_a) for i in range(0, 16, 2)]
    b = [int.from_bytes(values_b[i : i + 2], endian_b) for i in range(0, 16, 2)]
    if reverse_a:
        a.reverse()
    if reverse_b:
        b.reverse()
    if swap_a:
        a = a[4:] + a[:4]
    if swap_b:
        b = b[4:] + b[:4]

    basis = SmallBasis()
    for index, stage in enumerate(stages):
        half_a = half_a_first if index < 4 else half_a_second
        half_b = "high" if half_a == "low" else "low"
        for values, kind, half in ((a, kind_a, half_a), (b, kind_b, half_b)):
            equations = mt.temper(mt.get(sym, stage)) if kind == "tempered" else mt.get(sym, stage)
            bit_indices = range(16) if half == "low" else range(16, 32)
            for value_bit, output_bit in enumerate(bit_indices):
                remainder, offset = reduce_source_form(
                    equations[output_bit], 0, source_basis
                )
                if not basis.insert(remainder, ((values[index] >> value_bit) & 1) ^ offset):
                    return None

    raw_bits = []
    for vector, offset in target_forms:
        prediction = basis.predict(vector)
        if prediction is None:
            return None
        raw_bits.append(offset ^ prediction)
    words = []
    for lane in range(4):
        raw = sum(raw_bits[lane * 32 + bit] << bit for bit in range(32))
        words.append(temper_int(raw))
    payload = b"".join(word.to_bytes(4, "little") for word in words)
    component = bytes(a ^ b for a, b in zip(payload, mask))
    return payload, component, hashlib.sha256(component).hexdigest()


def main():
    blocks, k02, k07, route, acceptance = build_candidate_blocks()
    source_basis, sym = mt.source(ROOT)
    assert source_basis.rank == 15365
    assert mt.STARTS[129] == 951

    mask = bytes.fromhex(route["K04"]["masked_component"])
    target_hash = acceptance["slot_sha256"]["K04"]

    target_forms = []
    for stage in range(951, 955):
        for equation in mt.get(sym, stage):
            target_forms.append(reduce_source_form(equation, 0, source_basis))
    assert len(target_forms) == 128

    variants = []
    for name, block in blocks.items():
        for endian in ("little", "big"):
            for transform in ("untemper", "raw"):
                variants.append((f"{name}|{endian}|{transform}", block, endian, transform))
    assert len(variants) == 160

    pre_328 = {}
    pre_724 = {}
    for name, block, endian, transform in variants:
        pre_328[name] = donor_forms(block, 328, endian, transform, sym, source_basis)
        pre_724[name] = donor_forms(block, 724, endian, transform, sym, source_basis)

    complete_pairs = 0
    hits = []
    for left in variants:
        for right in variants:
            result = reconstruct_target(
                pre_328[left[0]], pre_724[right[0]], target_forms, mask
            )
            if result is None:
                continue
            complete_pairs += 1
            if result[2] == target_hash:
                hits.append((left[0], right[0], result[0].hex(), result[1].hex()))
    assert complete_pairs == 21504, complete_pairs
    assert not hits, hits

    # Halfword hypothesis: K02 and K07 each provide one 16-bit half of the
    # eight missing 32-bit outputs, in checkpoint/diagnostic sequence order.
    stages = (328, 329, 330, 331, 724, 725, 726, 727)
    halfword_complete = 0
    halfword_hits = []
    for params in itertools.product(
        ("big", "little"),
        ("big", "little"),
        ("tempered", "raw"),
        ("tempered", "raw"),
        ("low", "high"),
        ("low", "high"),
        (False, True),
        (False, True),
        (False, True),
        (False, True),
    ):
        (
            endian_a,
            endian_b,
            kind_a,
            kind_b,
            half_a_first,
            half_a_second,
            reverse_a,
            reverse_b,
            swap_a,
            swap_b,
        ) = params
        result = halfword_reconstruction(
            k02,
            k07,
            stages,
            target_forms,
            mask,
            source_basis,
            sym,
            endian_a,
            endian_b,
            kind_a,
            kind_b,
            half_a_first,
            half_a_second,
            reverse_a,
            reverse_b,
            swap_a,
            swap_b,
        )
        if result is None:
            continue
        halfword_complete += 1
        if result[2] == target_hash:
            halfword_hits.append((params, result[0].hex(), result[1].hex()))
    assert halfword_complete == 512, halfword_complete
    assert not halfword_hits, halfword_hits

    print(
        json.dumps(
            {
                "source_rank": source_basis.rank,
                "candidate_blocks": len(blocks),
                "variants": len(variants),
                "ordered_donor_pairs": len(variants) ** 2,
                "complete_donor_pairs": complete_pairs,
                "K04_donor_hits": len(hits),
                "halfword_mappings": 1024,
                "complete_halfword_mappings": halfword_complete,
                "K04_halfword_hits": len(halfword_hits),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
