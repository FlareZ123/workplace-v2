"""K04: fit reversible GF(2^32) four-word late-stage generator from future packets.

Fit arbitrary four coefficients (and optional constant) to the 12
intact 32-bit words in source packet indices 130,131,132. Test remaining
future words as full source holdouts; then invert across four missing
words at index129 and four known words at index128. Original evidence
and acceptance are read-only; the selected copied packet is excluded.
"""
import hashlib
import itertools
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def field(poly):
    def mul(a, b):
        answer = 0
        for _ in range(32):
            if b & 1:
                answer ^= a
            b >>= 1
            a <<= 1
            if a >> 32:
                a = (a & 0xffffffff) ^ poly
        return answer

    def inv(x):
        assert x != 0
        power = (1 << 32) - 2
        answer = 1
        while power:
            if power & 1:
                answer = mul(answer, x)
            x = mul(x, x)
            power >>= 1
        return answer
    return mul, inv


def solve(matrix, outputs, mul, inv):
    n = len(outputs)
    m = [list(row) + [outputs[i]] for i, row in enumerate(matrix)]
    assert all(len(r) == n + 1 for r in m)
    for col in range(n):
        pivot = next((i for i in range(col, n) if m[i][col]), None)
        if pivot is None:
            return None
        m[pivot], m[col] = m[col], m[pivot]
        scale = inv(m[col][col])
        m[col] = [mul(scale, x) for x in m[col]]
        for i in range(n):
            if i != col and m[i][col]:
                factor = m[i][col]
                m[i] = [x ^ mul(factor, y)
                        for x, y in zip(m[i], m[col])]
    return [m[i][-1] for i in range(n)]


def reconstruct(post_words, mul, inv, affine):
    assert len(post_words) == 12
    n = 5 if affine else 4
    matrix = [post_words[i-4:i] + ([1] if affine else [])
              for i in range(4, 4+n)]
    coeff = solve(matrix, post_words[4:4+n], mul, inv)
    if coeff is None or coeff[0] == 0:
        return None
    a, constant = coeff[:4], coeff[4] if affine else 0
    holdout = []
    for i in range(4+n, 12):
        pred = constant
        for j in range(4):
            pred ^= mul(a[j], post_words[i-4+j])
        holdout.append(pred == post_words[i])
    sequence = dict(enumerate(post_words))
    inverse_first = inv(a[0])
    for t in range(3, -5, -1):
        answer = sequence[t] ^ constant
        for j in range(1, 4):
            answer ^= mul(a[j], sequence[t-4+j])
        sequence[t-4] = mul(answer, inverse_first)
    return coeff, holdout, [sequence[i] for i in range(-4, 0)], [
        sequence[i] for i in range(-8, -4)
    ]


def pack(words):
    return b"".join(x.to_bytes(4, "big") for x in words)


def packet_view(packet, reverse_words, reverse_word_bytes, reflect_bits):
    words = [packet[i:i+4] for i in range(0, 16, 4)]
    if reverse_words:
        words.reverse()
    if reverse_word_bytes:
        words = [w[::-1] for w in words]
    bs = b"".join(words)
    if reflect_bits:
        bs = bytes(int(f"{b:08b}"[::-1], 2) for b in bs)
    return [int.from_bytes(bs[i:i+4], "big") for i in range(0, 16, 4)]


def inverse_packet(words, reverse_words, reverse_word_bytes, reflect_bits):
    bs = pack(words)
    if reflect_bits:
        bs = bytes(int(f"{b:08b}"[::-1], 2) for b in bs)
    segments = [bs[i:i+4] for i in range(0, 16, 4)]
    if reverse_word_bytes:
        segments = [w[::-1] for w in segments]
    if reverse_words:
        segments.reverse()
    return b"".join(segments)


def source():
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    lines = [x for x in raw.decode("ascii").splitlines() if "PAYLOAD=" in x]
    assert len(lines) == 133
    assert lines[129].startswith(
        "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER "
    )
    values = {}
    for i in (128, 130, 131, 132):
        m = re.search(r"PAYLOAD=([0-9A-F]{32})(?:\s|$)", lines[i])
        assert m is not None
        values[i] = bytes.fromhex(m.group(1))
    return values


def synthetic_positive():
    random_source = random.Random(0x20261103)
    out = []
    for poly in (0x8d, 0x04c11db7):
        mul, inv = field(poly)
        for affine in (False, True):
            for _ in range(100):
                coefficients = [random_source.getrandbits(32)
                                for _ in range(4)]
                coefficients[0] |= 1
                constant = random_source.getrandbits(32) if affine else 0
                words = [random_source.getrandbits(32) for _ in range(4)]
                for _ in range(16):
                    current = constant
                    for j in range(4):
                        current ^= mul(coefficients[j], words[-4+j])
                    words.append(current)
                result = reconstruct(words[8:20], mul, inv, affine)
                if result is None:
                    continue
                recovered, heldout, target, pre = result
                assert all(heldout), (poly, affine)
                assert target == words[4:8] and pre == words[0:4]
                out.append([hex(poly), affine, True])
                break
            else:
                raise AssertionError("Synthetic source could not be recovered")
    return out


def main():
    values = source()
    routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    original_target = acceptance["slot_sha256"]["K04"]
    results = []
    for poly in (0x8d, 0x04c11db7):
        mul, inv = field(poly)
        for flags in itertools.product((False, True), repeat=3):
            post = []
            for i in (130, 131, 132):
                post.extend(packet_view(values[i], *flags))
            for affine in (False, True):
                model = reconstruct(post, mul, inv, affine)
                assert model is not None
                coeff, heldout, selected_words, previous_words = model
                selected_packet = inverse_packet(selected_words, *flags)
                prior_packet = inverse_packet(previous_words, *flags)
                k04 = bytes(a ^ b for a, b in zip(selected_packet, mask))
                results.append({
                    "poly": hex(poly), "serializer": list(flags),
                    "affine": affine, "source_heldout_successes": sum(heldout),
                    "source_heldout_tests": len(heldout),
                    "previous_18_01_packet_matches": prior_packet == values[128],
                    "complete_predicted_K04": k04.hex().upper(),
                    "original_K04_SHA_match": hashlib.sha256(k04).hexdigest()
                                              == original_target,
                })
    assert len(results) == 32
    assert all(r["source_heldout_successes"] == 0 for r in results)
    assert all(not r["previous_18_01_packet_matches"] for r in results)
    assert all(not r["original_K04_SHA_match"] for r in results)
    assert len(set(r["complete_predicted_K04"] for r in results)) == 32
    print(json.dumps({
        "source_sha256": PIN,
        "disputed_selected_payload_read": False,
        "models": len(results),
        "source_post_holdout_matches": sum(r["source_heldout_successes"]
                                          for r in results),
        "source_pre_holdout_matches": sum(r["previous_18_01_packet_matches"]
                                         for r in results),
        "distinct_complete_K04_candidates": 32,
        "authentic_K04_matches": 0,
        "synthetic_positive": synthetic_positive(),
        "one_example": results[0],
        "result": "NO_MATCH_POSTTARGET_STAGE_INCONSISTENT",
    }, indent=2))


if __name__ == "__main__":
    main()
