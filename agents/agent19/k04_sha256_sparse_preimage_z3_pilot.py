"""H-17 K04 SHA256 sparse-component inversion: constrained Z3 feasibility pilot.

Scope: test whether an exact QF_BV SHA256 circuit can recover known synthetic
one-/two-byte preimages faster than exhaustive enumeration. The original K04
selected SHA digest is untouched and unused unless an independently calibrated
solver proves effective. This is a generator-independent different algorithm
for the same finite damaged-copy family.

Run on checkout with Python 3 and z3-solver: python agents/agent19/k04_sha256_sparse_preimage_z3_pilot.py
"""
import hashlib
import sys
import time
from pathlib import Path
from z3 import BitVec, BitVecVal, Concat, LShR, RotateRight, SolverFor, simplify, sat

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    "resources/evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "resources/evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "resources/acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
COPIED = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
BASE = bytes(a ^ b for a, b in zip(COPIED, MASK))
IV = (
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
    0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19
)
K = (
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2
)

def rotr(v, n):
    return RotateRight(v, n)

def sigma0(x):
    return rotr(x, 7) ^ rotr(x, 18) ^ LShR(x, 3)

def sigma1(x):
    return rotr(x, 17) ^ rotr(x, 19) ^ LShR(x, 10)

def big0(x):
    return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22)

def big1(x):
    return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25)

def symbolic_sha256(message_bytes):
    assert len(message_bytes) == 16
    w = [Concat(*message_bytes[i:i + 4]) for i in range(0, 16, 4)]
    w.extend(BitVecVal(0x80000000 if i == 4 else (128 if i == 15 else 0), 32)
             for i in range(4, 16))
    for i in range(16, 64):
        w.append(w[i - 16] + sigma0(w[i - 15]) + w[i - 7] + sigma1(w[i - 2]))
    a, b, c, d, e, f, g, h = [BitVecVal(x, 32) for x in IV]
    for i in range(64):
        t1 = h + big1(e) + ((e & f) ^ (~e & g)) + BitVecVal(K[i], 32) + w[i]
        t2 = big0(a) + ((a & b) ^ (a & c) ^ (b & c))
        a, b, c, d, e, f, g, h = (t1 + t2, a, b, c, d + t1, e, f, g)
    return tuple(v + BitVecVal(c, 32) for v, c in zip((a, b, c, d, e, f, g, h), IV))

def source_pin():
    for relative, expected in SOURCES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected

def solve_positions(positions, planted):
    unknown = {p: BitVec("unknown_byte_%d" % p, 8) for p in positions}
    msg = [unknown.get(i, BitVecVal(BASE[i], 8)) for i in range(16)]
    target = hashlib.sha256(planted).digest()
    exprs = symbolic_sha256(msg)
    solver = SolverFor("QF_BV")
    solver.set(timeout=60000)
    for i in range(8):
        solver.add(exprs[i] == int.from_bytes(target[i * 4:i * 4 + 4], "big"))
    started = time.perf_counter()
    outcome = solver.check()
    elapsed = time.perf_counter() - started
    print("Z3 sparse positions=%s, result=%s elapsed=%.3fs" %
          (positions, outcome, elapsed), flush=True)
    if outcome == sat:
        model = solver.model()
        recovered = bytearray(BASE)
        for p, var in unknown.items():
            recovered[p] = model.eval(var).as_long()
        print("Recovered complete synthetic component:", bytes(recovered).hex().upper(), flush=True)
        assert bytes(recovered) == planted, "incorrect 128-bit synthetic recovery"
        return True
    return False

def main():
    source_pin()
    literal = [BitVecVal(v, 8) for v in BASE]
    fully = symbolic_sha256(literal)
    grounded = b"".join(simplify(word).as_long().to_bytes(4, "big") for word in fully)
    assert grounded == hashlib.sha256(BASE).digest()
    print("Symbolic SHA256 grounded 16-byte digest equals hashlib, original SHA source pins PASS", flush=True)

    synthetic1 = bytearray(BASE)
    synthetic1[0] = 0x17
    one = solve_positions((0,), bytes(synthetic1))
    synthetic2 = bytearray(BASE)
    synthetic2[0], synthetic2[1] = 0x17, 0xC2
    two = solve_positions((0, 1), bytes(synthetic2)) if one else False
    print("CONCLUSION one-byte=%s two-byte=%s; original K04 target was not queried" %
          (one, two), flush=True)
    return 0 if one else 3

if __name__ == "__main__":
    sys.exit(main())
