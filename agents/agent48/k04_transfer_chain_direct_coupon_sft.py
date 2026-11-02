"""K04 direct native transfer-checkpoint chain copy hypothesis.

All 4 transfer IDs, both source-observed attempts at every seq0..7,
normal/reversed sequence and normal/swapped checkpoint byte order.
4*2**8*2*2=4,096 full opaque coupon candidates. Original SHA commitment,
not a verifier mutation. Distinct from symbolic MT donor reconstructions.
"""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/transfers/transfer-audit.jsonl").read_bytes()
assert hashlib.sha256(raw).hexdigest() == (
    "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
)
rows = [json.loads(line) for line in raw.splitlines()]
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
accept = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target = bytes.fromhex(accept["slot_sha256"]["K04"])
assert len(mask) == len(target) // 2 == 16

def digest(packet):
    return hashlib.sha256(bytes(x ^ y for x,y in zip(packet,mask))).digest()

def candidates():
    for transfer in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
        by_seq = []
        for seq in range(8):
            chunks = sorted((r for r in rows if
                             r["kind"] == "CHUNK" and
                             r["transfer"] == transfer and
                             r["seq"] == seq), key=lambda r:r["attempt"])
            assert [r["attempt"] for r in chunks] == [1,2]
            by_seq.append(tuple(bytes.fromhex(r["checkpoint"]) for r in chunks))
        for bits in itertools.product((0,1),repeat=8):
            fragments = [by_seq[seq][bits[seq]] for seq in range(8)]
            for reverse in (False,True):
                chosen = fragments[::-1] if reverse else fragments
                for swap in (False,True):
                    packet = b"".join(x[::-1] if swap else x for x in chosen)
                    yield (transfer,bits,reverse,swap,packet)

def main():
    planted = next((c for c in candidates()
                   if c[0]=="AX-7781" and c[2] and c[3]),None)
    assert planted
    synth = digest(planted[4])
    original = positive = searched = 0
    for transfer,bits,rev,swap,packet in candidates():
        result = digest(packet)
        original += result == target
        positive += result == synth
        searched += 1
    assert searched == 4096 and original == 0 and positive >= 1
    print("4,096 full source transfer-chain coupon candidates")
    print("original K04 acceptance matches:", original)
    print("synthetic transfer-chain positive:", positive)

if __name__ == "__main__":
    main()
