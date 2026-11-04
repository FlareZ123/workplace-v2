"""K04: original-source p951 CPython UTF-8 string-seed discriminator.

Run: python agents/agent15/k04_p951_utf8_seed_gate_sft.py
No selected copied ACK, K04/K08 digest, route mask, or verifier is used.
The source-based first-cycle CPython model is hypothetical, not attested.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / "resources/evidence/print/spool-reconstruction.log"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
U = 0xFFFFFFFF
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
BASE = [19650218]
for i in range(1, 624):
    BASE.append((1812433253*(BASE[-1] ^ (BASE[-1] >> 30)) + i) & U)


def mix(x: int, m: int) -> int:
    return (x ^ (x >> 30)) * m & U


def key_term(i: int, a: int, b: int, c: int) -> int:
    earlier = ((b + i - 1) & U) ^ mix(a, 1566083941)
    later = ((c + i) & U) ^ mix(b, 1566083941)
    return (later - (BASE[i] ^ mix(earlier, 1664525))) & U


def untemper(x: int) -> int:
    for shift, left, mask in ((18, False, U), (15, True, 0xEFC60000),
                               (7, True, 0x9D2C5680), (11, False, U)):
        y = x
        for _ in range(6):
            y = x ^ (((y << shift) & mask) if left else y >> shift)
        x = y & U
    return x


def twist(x: int) -> int:
    return ((x >> 1) ^ (0x9908B0DF if x & 1 else 0)) & U


def inverse_twist(x: int) -> int:
    return (((x ^ (0x9908B0DF if x >> 31 else 0)) << 1) | (x >> 31)) & U


def source_key_term() -> tuple[list[int], list[int]]:
    raw = SPOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    tokens = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(tokens) == len(STARTS) == 133
    assert STARTS[129] == 951
    size, origin = 6000, 2000
    values, masks = [0]*size, [0]*size

    def add(pos: int, value: int, mask: int) -> int:
        if not 0 <= pos < size:
            return 0
        assert ((values[pos] ^ value) & masks[pos] & mask) == 0
        fresh = mask & ~masks[pos]
        values[pos] = (values[pos] & ~fresh) | (value & fresh)
        masks[pos] |= fresh
        return fresh.bit_count()

    for row, (token, start) in enumerate(zip(tokens, STARTS)):
        if row == 129:
            continue  # Do not even decode the disputed selected buffer.
        packet = bytes.fromhex(token.decode("ascii"))
        for lane in range(4):
            add(origin + start + lane,
                untemper(int.from_bytes(packet[4*lane:4*lane+4], "little")), U)

    for iteration in range(30):
        added = 0
        for t in range(size-624):
            value = (values[t] & 0x80000000) | (values[t+1] & 0x7FFFFFFF)
            mask = (masks[t] & 0x80000000) | (masks[t+1] & 0x7FFFFFFF)
            if masks[t+397] == masks[t+624] == U:
                inverted = inverse_twist(values[t+397] ^ values[t+624])
                added += add(t, inverted, 0x80000000)
                added += add(t+1, inverted, 0x7FFFFFFF)
            if mask == U:
                if masks[t+397] == U:
                    added += add(t+624, values[t+397] ^ twist(value), U)
                if masks[t+624] == U:
                    added += add(t+397, values[t+624] ^ twist(value), U)
        if not added:
            break
    else:
        raise AssertionError("masked original-source recurrence did not converge")

    indices = [origin-624+j for j in (21,22,23)]
    missing = [U ^ masks[i] for i in indices]
    assert [x.bit_count() for x in missing] == [0,0,1], [
        hex(x) for x in missing
    ]
    a, b, c = [values[i] for i in indices]
    terms = sorted({key_term(23,a,b,c), key_term(23,a,b,c | missing[2])})
    return terms, [masks[i] for i in indices]


def synthetic_seed_controls() -> None:
    for n in (249,606,623):
        text = "A" * (4*n-64)
        data = text.encode("utf-8")
        numeric = int.from_bytes(data + hashlib.sha512(data).digest(), "big")
        true_word = (numeric >> (32*22)) & U
        state = random.Random(text).getstate()[1][:624]
        observed = key_term(23,*state[21:24])
        assert true_word == 0x41414141
        assert observed == (true_word+22) & U, (n,observed)
    print("3/3 actual CPython string-seed positive controls PASS",flush=True)


def main() -> None:
    synthetic_seed_controls()
    terms, masks = source_key_term()
    assert terms == [0x7D6A4D0D,0xFD6A4D0D], [f"{x:08X}" for x in terms]
    possible_little_endian_words = [
        ((term-22)&U).to_bytes(4,"little") for term in terms
    ]
    assert all(word[0] == 0xF7 for word in possible_little_endian_words)
    print(json.dumps({
        "source_key_term_T22": [f"{x:08X}" for x in terms],
        "native_state_masks_S21_S22_S23": [f"{x:08X}" for x in masks],
        "possible_seed_word_22_little_endian": [
            x.hex().upper() for x in possible_little_endian_words
        ],
        "utf8_text_seed_possible": False,
        "model": "original p951 chronology; CPython first-cycle init_by_array",
        "scope": "UTF-8 text seed with key-word lengths 364..623",
        "authenticated_k04_bits": 0
    },indent=2))


if __name__ == "__main__":
    main()
