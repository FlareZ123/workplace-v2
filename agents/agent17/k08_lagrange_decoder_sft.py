"""K08 quadratic GF128 decode of the missing final HMAC16 from known captions.

Source-only historical test. A source-described Nxx->PS03xx join is conditional.
No original evidence, key commitments, or candidate files are mutated.
"""
from pathlib import Path
from itertools import combinations, product
import hashlib
import hmac
import json
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
E = ROOT / "evidence"
route = json.loads((E / "recovery-routing.json").read_text())
accept = json.loads((ROOT / "acceptance.json").read_text())
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
spool = (E / "print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256((E / "crew/noticeboard-and-desk-notes.txt").read_bytes()).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
captions = {
    2: "A good watch leaves the room ready for the next pair of hands.",
    6: "The little lamp stays on until the corridor has gone quiet.",
    13: "At the end of the night the mugs stood beside the window, and somebody had remembered to leave the little lamp on.",
    17: "Leave the light on for the next watch.",
    18: "Back before the first boat.",
}


def full_hmac(s):
    normalized = " ".join(re.findall("[a-z0-9]+", s.lower())).encode()
    return hmac.digest(nonce, normalized, "sha256")[:16]


assert full_hmac(captions[18]).hex().upper() == "A3100AE1ABB9C8D58315D9EBF326978B"
rows = spool.decode().splitlines()


def packet(i):
    found = [s for s in rows if f"JOB=PS-261003-{i:04d} " in s and "STATE=ACK " in s]
    assert len(found) == 1
    return bytes.fromhex(dict(re.findall(r"(\w+)=(\S+)", found[0]))["PAYLOAD"])


M = (1 << 128) - 1


def multiply(a, b):
    product_value = 0
    for _ in range(128):
        if b & 1:
            product_value ^= a
        b >>= 1
        high = a >> 127
        a = ((a << 1) & M) ^ (0x87 if high else 0)
    return product_value


def invert(a):
    assert a
    value = 1
    for i in reversed(range(128)):
        value = multiply(value, value)
        if i:
            value = multiply(value, a)
    return value


def interpolate(train, y):
    result = 0
    for i in range(3):
        x_i, h_i = train[i]
        term = h_i
        for j in range(3):
            if i != j:
                x_j = train[j][0]
                term = multiply(term, multiply(y ^ x_j, invert(x_i ^ x_j)))
        result ^= term
    return result


def view(data, v):
    if v == 0:
        return data
    if v == 1:
        return data[::-1]
    if v == 2:
        return data[12:16] + data[8:12] + data[4:8] + data[:4]
    return data[3::-1] + data[7:3:-1] + data[11:7:-1] + data[15:11:-1]


def synthetic_control():
    a, b, c = 0xDEADBEEF111, 0x371, 0xAB2134
    transform = lambda x: multiply(a, multiply(x, x)) ^ multiply(b, x) ^ c
    train = [(x, transform(x)) for x in (0x111, 0x222, 0x333)]
    assert interpolate(train, 0x444) == transform(0x444)
    print("SYNTHETIC_ORIGINAL_QUADRATIC_WITNESS_PASS")


def run():
    labels = tuple(captions)
    fits = heldout_hits = 0
    target_hits = []
    for offset, text_view, packet_view in product((0, 7), range(4), range(4)):
        known_hmac = {
            i: int.from_bytes(view(full_hmac(captions[i]), text_view), "big")
            for i in labels
        }
        known_packets = {
            i: int.from_bytes(view(packet(300 + i + offset), packet_view), "big")
            for i in labels + (23,)
        }
        for training in combinations(labels, 3):
            pairs = [(known_packets[i], known_hmac[i]) for i in training]
            if len(set(x for x, _ in pairs)) < 3:
                continue
            fits += 1
            heldout = [i for i in labels if i not in training]
            heldout_hits += sum(
                interpolate(pairs, known_packets[i]) == known_hmac[i]
                for i in heldout
            )
            reconstructed = view(interpolate(pairs, known_packets[23]).to_bytes(16, "big"), text_view)
            if hashlib.sha256(reconstructed).hexdigest() == accept["slot_sha256"]["K08"]:
                target_hits.append((offset, text_view, packet_view, training, reconstructed.hex().upper()))
    print("RESULT", json.dumps({
        "full_fitted_decoders": fits,
        "complete_historical_holdout_hits": heldout_hits,
        "original_K08_hits": target_hits,
    }, sort_keys=True))
    assert fits == 320 and heldout_hits == 0 and not target_hits


if __name__ == "__main__":
    synthetic_control()
    run()
