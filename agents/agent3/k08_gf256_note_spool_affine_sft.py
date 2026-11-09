"""K08 source-only GF(256) byte-affine note-to-spool transport experiment.

Calibrate P[j] = a[j]*H[j] XOR b[j] independently in each byte lane
from two complete older Emily notes. Test three untouched complete notes
and infer a hypothetical PS-0323 K08 component. The Nxx-to-job index
association is conditional, not historically authenticated.
"""
import hashlib
import hmac
import itertools
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
NOTES = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
assert hashlib.sha256(NOTES.read_bytes()).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
IDS = (2, 6, 13, 17, 18)
texts = {
    int(n): body.split(": ", 1)[-1]
    for n, body in re.findall(
        r"^N(\d\d) / Emily \[censored\]\n([^\n]+)", NOTES.read_text(), re.M
    )
}
packets = {
    int(n): bytes.fromhex(value)
    for n, value in re.findall(
        r"JOB=PS-261003-(\d+) ATTEMPT=1 STATE=ACK CLASS=\w+ PAYLOAD=([0-9A-F]{32})",
        SPOOL.read_text(),
    )
    if 300 <= int(n) <= 427
}
assert len(packets) == 128
h = {
    n: hmac.digest(
        NONCE,
        " ".join(re.findall("[a-z0-9]+", texts[n].lower())).encode(),
        "sha256",
    )[:16]
    for n in IDS
}
p = {n: packets[300+n] for n in IDS+(23,)}
assert h[18].hex().upper() == "A3100AE1ABB9C8D58315D9EBF326978B"


def multiply(a, b, reduction):
    value = 0
    while b:
        if b & 1:
            value ^= a
        a = ((a << 1) ^ (reduction if a & 128 else 0)) & 255
        b >>= 1
    return value


def inverse(x, reduction):
    assert x
    output, power, base = 1, 254, x
    while power:
        if power & 1:
            output = multiply(output, base, reduction)
        base = multiply(base, base, reduction)
        power >>= 1
    return output


def view(raw, variant):
    words = [raw[i:i+4] for i in range(0, 16, 4)]
    if variant & 1:
        words = [w[::-1] for w in words]
    if variant & 2:
        words = words[::-1]
    return b"".join(words)


def fit(ha, hb, pa, pb, reduction):
    if any(x == y or a == b for x, y, a, b in zip(ha, hb, pa, pb)):
        return None
    slopes = tuple(
        multiply(a ^ b, inverse(x ^ y, reduction), reduction)
        for x, y, a, b in zip(ha, hb, pa, pb)
    )
    offsets = tuple(a ^ multiply(c, x, reduction) for a, c, x in zip(pa, slopes, ha))
    return slopes, offsets


def encode(value, model, reduction):
    slopes, offsets = model
    return bytes(
        multiply(slopes[i], value[i], reduction) ^ offsets[i] for i in range(16)
    )


def decode(value, model, reduction):
    slopes, offsets = model
    return bytes(
        multiply(value[i] ^ offsets[i], inverse(slopes[i], reduction), reduction)
        for i in range(16)
    )


def positive(reduction):
    original = (
        tuple((i*17+1) % 255+1 for i in range(16)),
        tuple((i*23+47) % 256 for i in range(16)),
    )
    packets = {n: encode(view(h[n], 1), original, reduction) for n in IDS}
    inferred = fit(view(h[17], 1), view(h[18], 1), packets[17], packets[18], reduction)
    assert inferred == original
    assert all(encode(view(h[n], 1), inferred, reduction) == packets[n] for n in IDS)
    final = hmac.digest(NONCE, b"synthetic late watch keeper caption", "sha256")[:16]
    cipher = encode(view(final, 1), inferred, reduction)
    assert view(decode(cipher, inferred, reduction), 1) == final


def main():
    models = skipped = heldouts = 0
    matches = []
    for reduction in (0x1b, 0x1d, 0x2d, 0x87):
        assert all(
            multiply(x, inverse(x, reduction), reduction) == 1
            for x in range(1, 256)
        )
        positive(reduction)
        for hv, pv in itertools.product(range(4), repeat=2):
            for a, b in itertools.combinations(IDS, 2):
                model = fit(
                    view(h[a], hv), view(h[b], hv),
                    view(p[a], pv), view(p[b], pv), reduction,
                )
                if model is None:
                    skipped += 1
                    continue
                models += 1
                heldouts += sum(
                    encode(view(h[k], hv), model, reduction) == view(p[k], pv)
                    for k in IDS if k not in (a, b)
                )
                candidate = view(decode(view(p[23], pv), model, reduction), hv)
                if hashlib.sha256(candidate).hexdigest() == TARGET:
                    matches.append((reduction, hv, pv, a, b, candidate.hex()))
    assert (models, skipped, heldouts, matches) == (576, 64, 0, [])
    print("ORIGINAL complete models", models, "singular fits", skipped,
          "single whole historical heldout matches", heldouts, "K08 hits", len(matches))
    print("PLANTED full selected-output controls: 4/4 PASS")


if __name__ == "__main__":
    main()
