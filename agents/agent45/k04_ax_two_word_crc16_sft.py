"""K04: two-native-MT-word CRC16 checkpoint emitter, source-only SFT.

Run: python agents/agent45/k04_ax_two_word_crc16_sft.py resources
Requires numpy; reads immutable original records and the established Agent45
p951 closure. Omits selected printer row129; no slot target or mask is loaded.

Publisher notes: CRC16 over eight bytes in two 32-bit words, fixed lag1..32,
native/tempered, endian/word orientations, CCITT and ARC, init0 or FFFF.
Each original transfer's first 8 checkpoint samples are training; last 8
are held out. A transferred sample constrains an original source phase only
when both contributing MT words are fully source-observed.
"""
from pathlib import Path
import binascii
import hashlib
import json
import random
import re
import sys
import numpy as np
from k04_p951_seed_residue_inverse_sft import STARTS, close, untemper

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
SPOOL_HASH = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
AX_HASH = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
STAGE_MIN, STAGE_MAX = -1100, 3999
FULL = 0xffffffff
OFFSET = 2000


def crc_table(polynomial, reflected=False):
    out = []
    for n in range(256):
        code = n if reflected else n << 8
        for _ in range(8):
            if reflected:
                code = (code >> 1) ^ (polynomial if code & 1 else 0)
            else:
                code = ((code << 1) ^ (polynomial if code & 0x8000 else 0)) & 65535
        out.append(code & 65535)
    return np.array(out, dtype=np.uint16)


CCITT_TABLE = crc_table(0x1021)
ARC_TABLE = crc_table(0xA001, True)


def temper32(x):
    x = x.copy()
    x ^= x >> 11
    x ^= (x << 7) & np.uint32(0x9d2c5680)
    x ^= (x << 15) & np.uint32(0xefc60000)
    x ^= x >> 18
    return x


def crc_pair_outputs(words, lag, reverse_words, big_endian, family, initial):
    left, right = words[:-lag], words[lag:]
    if reverse_words:
        left, right = right, left
    table = CCITT_TABLE if family == "ccitt" else ARC_TABLE
    code = np.full(len(left), initial, dtype=np.uint16)
    for word in (left, right):
        byte_positions = range(3, -1, -1) if big_endian else range(4)
        for index in byte_positions:
            byte = ((word >> (8 * index)) & 255).astype(np.uint8)
            if family == "ccitt":
                code = ((code << 8) ^ table[((code >> 8) ^ byte) & 255]).astype(np.uint16)
            else:
                code = ((code >> 8) ^ table[(code ^ byte) & 255]).astype(np.uint16)
    return code


def sources():
    spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    audit = (ROOT / "evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_HASH
    assert hashlib.sha256(audit).hexdigest() == AX_HASH
    packets = [
        bytes.fromhex(x.decode("ascii"))
        for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)
    ]
    assert len(packets) == len(STARTS) == 133 and STARTS[129] == 951
    rows = [json.loads(line) for line in audit.decode("utf-8").splitlines()]
    original = {}
    for transfer in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
        parts = sorted(
            (r for r in rows if r["kind"] == "CHUNK" and r["transfer"] == transfer),
            key=lambda r: (r["seq"], r["attempt"])
        )
        assert len(parts) == 16
        assert [(p["seq"], p["attempt"]) for p in parts] == [
            (i, a) for i in range(8) for a in (1, 2)
        ]
        original[transfer] = np.array([
            [int.from_bytes(bytes.fromhex(p["checkpoint"]), endian) for p in parts]
            for endian in ("big", "little")
        ], dtype=np.uint16)
    return packets, original


def independent_crc(left, right, family, initial, big_endian, reverse):
    a, b = (right, left) if reverse else (left, right)
    payload = int(a).to_bytes(4, "big" if big_endian else "little")
    payload += int(b).to_bytes(4, "big" if big_endian else "little")
    if family == "ccitt":
        return binascii.crc_hqx(payload, initial)
    crc = initial
    for byte in payload:
        crc ^= byte
        for _ in range(8):
            crc = ((crc >> 1) ^ (0xa001 if crc & 1 else 0)) & 65535
    return crc


def geometry(full, lag):
    pair_known = full[:-lag] & full[lag:]
    by_stride = {}
    for stride in range(1, 9):
        stop = min(OFFSET + STAGE_MAX + 1, len(pair_known) - 15 * stride)
        stages = np.arange(OFFSET + STAGE_MIN, stop, dtype=np.int32)
        positions = stages[:, None] + stride * np.arange(16, dtype=np.int32)[None, :]
        train_count = pair_known[positions[:, :8]].sum(axis=1)
        eligible = np.flatnonzero(train_count >= 1)
        selected = positions[eligible]
        by_stride[stride] = (selected, stages[eligible] - OFFSET,
                             train_count[eligible],
                             pair_known[selected[:, 8:]].sum(axis=1))
    return by_stride, pair_known


def authentic_old_positive(native, full, original):
    native = temper32(native)
    index = OFFSET - 157 + np.arange(16)
    known = np.flatnonzero(full[index])
    assert len(known) == 5
    expected = ((native[index[known]] >> 16) & 65535).astype(np.uint16)
    assert np.array_equal(expected, original["AX-7778"][1, known])
    assert np.count_nonzero(expected != original["AX-7778"][0, known]) >= 1
    print("Existing original AX-7778 direct high16 control: 5/5 source-full words PASS")


def synthetic_controls():
    checks = 0
    for seed in (20261103, 1947, 8675309):
        rng = random.Random(seed)
        draw = [rng.getrandbits(32) for _ in range(967)]
        packets = [
            b"".join(draw[i].to_bytes(4, "little") for i in range(s, s + 4))
            for s in STARTS
        ]
        values, masks, origin = close(packets)
        assert origin == OFFSET
        native = np.array(values, dtype=np.uint32)
        full = np.array(masks, dtype=np.uint32) == FULL
        for word_type in ("native", "tempered"):
            v = native if word_type == "native" else temper32(native)
            actual = [untemper(x) for x in draw] if word_type == "native" else draw
            for family in ("ccitt", "arc"):
                for initial in (0, 65535):
                    for big_endian in (False, True):
                        for reverse in (False, True):
                            stage, lag, stride = 3, 1, 1
                            test = np.array([
                                independent_crc(
                                    actual[stage + k * stride],
                                    actual[stage + k * stride + lag],
                                    family, initial, big_endian, reverse
                                ) for k in range(16)
                            ], dtype=np.uint16)
                            pred = crc_pair_outputs(
                                v, lag, reverse, big_endian, family, initial
                            )
                            ix = OFFSET + stage + stride * np.arange(16)
                            known = full[ix] & full[ix + lag]
                            assert int(known[:8].sum()) >= 3
                            assert int(known[8:].sum()) >= 3
                            assert np.array_equal(pred[ix][known], test[known])
                            victim = int(np.flatnonzero(known[8:])[0] + 8)
                            altered = test.copy()
                            altered[victim] ^= 1
                            assert pred[ix[victim]] != altered[victim]
                            checks += 1
    assert checks == 96
    print("96 genuine seeded full-spool paired-CRC positives PASS; "
          "96 corrupted heldout samples detected")


def scan(native, full, originals):
    forms = {"native": native, "tempered": temper32(native)}
    checked = train_hits = qualified_heldout = heldout_hits = 0
    examples = []
    for lag in range(1, 33):
        layouts, both_full = geometry(full, lag)
        number = sum(len(v[0]) for v in layouts.values())
        checked += number * 2 * 2 * 2 * 2 * 2 * 4 * 2
        for word_type, words in forms.items():
            for reverse in (False, True):
                for big_endian in (False, True):
                    for family in ("ccitt", "arc"):
                        for initial in (0, 65535):
                            predictions = crc_pair_outputs(
                                words, lag, reverse, big_endian, family, initial
                            )
                            for stride, (ix, starts, train, hold) in layouts.items():
                                if len(ix) == 0:
                                    continue
                                values = predictions[ix]
                                known = both_full[ix]
                                for name, observed in originals.items():
                                    for endian in range(2):
                                        target = observed[endian]
                                        compatible = (
                                            (values[:, :8] == target[:8]) | ~known[:, :8]
                                        ).all(axis=1)
                                        survived = np.flatnonzero(compatible)
                                        train_hits += len(survived)
                                        if not len(survived):
                                            continue
                                        heldout = survived[hold[survived] >= 3]
                                        qualified_heldout += len(heldout)
                                        if not len(heldout):
                                            continue
                                        complete = (
                                            (values[heldout, 8:] == target[8:]) |
                                            ~known[heldout, 8:]
                                        ).all(axis=1)
                                        for item in np.flatnonzero(complete):
                                            i = int(heldout[item])
                                            examples.append((name, endian, word_type,
                                                             family, initial, reverse,
                                                             big_endian, lag, stride,
                                                             int(starts[i])))
                                        heldout_hits += int(complete.sum())
    assert checked == 89598208, checked
    assert train_hits == 430, train_hits
    assert qualified_heldout == 52, qualified_heldout
    assert heldout_hits == 0 and not examples
    print(json.dumps({
        "original_qualifying_assignments": checked,
        "one_or_more_full_first_half_checkpoint_train_hits": train_hits,
        "training_hits_with_at_least_three_full_heldout_words": qualified_heldout,
        "heldout_full_matches": heldout_hits,
        "result": "NO_MATCH_IN_DEFINED_TWO_WORD_CRC16_CLASS",
        "authentic_selected_K04_bits": 0
    }, indent=2))


def main():
    packets, originals = sources()
    values, masks, origin = close(packets)
    assert origin == OFFSET
    native = np.array(values, dtype=np.uint32)
    full = np.array(masks, dtype=np.uint32) == FULL
    authentic_old_positive(native, full, originals)
    synthetic_controls()
    scan(native, full, originals)


if __name__ == "__main__":
    main()
