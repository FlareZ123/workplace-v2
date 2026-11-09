"""H17 conditional full-coupon predictor from two ORIGINAL native MT gap packets.

An external, authenticated source must give the actual source packet bytes
for native stages 328..331 and 724..727. The historical MT19937/p951
producer mapping is still a hypothesis. No actual missing packet is supplied.

Run this module against the intact repository resources with a separate
trusted data acquisition; do not manufacture candidate donor bytes.
"""
from hashlib import sha256
from pathlib import Path
import re
from typing import NamedTuple

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MAG = 0x9908B0DF
U32 = 0xFFFFFFFF


class Recovery(NamedTuple):
    printed_coupon: bytes
    component: bytes
    accepted: bool


def untemper(x: int) -> int:
    for k, left, mask in (
        (18, False, U32),
        (15, True, 0xEFC60000),
        (7, True, 0x9D2C5680),
        (11, False, U32),
    ):
        original = x
        for _ in range(6):
            x = original ^ (((x << k) & mask) if left else x >> k)
            x &= U32
    return x


def temper(x: int) -> int:
    x ^= x >> 11
    x ^= (x << 7) & 0x9D2C5680
    x ^= (x << 15) & 0xEFC60000
    x ^= x >> 18
    return x & U32


def retained_native_327(root: Path) -> int:
    """Read original intact PS-0343 final little-endian u32 output."""
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert sha256(raw).hexdigest() == SPOOL_SHA256
    lines = [line for line in raw.decode("ascii").splitlines()
             if line.startswith("2026-")]
    assert len(lines) == 133
    line = lines[43]
    assert "JOB=PS-261003-0343" in line
    match = re.search(r"(?:^|\\s)PAYLOAD=([0-9A-F]{32})(?=\\s|$)", line)
    assert match is not None
    packet = bytes.fromhex(match.group(1))
    return untemper(int.from_bytes(packet[12:16], "little"))


def reconstruct(native_327: int, gap_328: bytes, gap_724: bytes,
                mask: bytes = MASK) -> Recovery:
    """Use complete native stages328..331 and724..727 in PRINTED little-endian form.

    Returns the 16B hypothetical coupon, XOR-reduced component and the
    unchanged-original historical K04 acceptance outcome. All three
    returned values remain conditional on the unproven issuer hypothesis.
    """
    assert 0 <= native_327 <= U32
    assert len(gap_328) == len(gap_724) == len(mask) == 16
    a = [native_327] + [
        untemper(int.from_bytes(gap_328[i:i + 4], "little"))
        for i in range(0, 16, 4)
    ]
    b = [
        untemper(int.from_bytes(gap_724[i:i + 4], "little"))
        for i in range(0, 16, 4)
    ]
    predicted = []
    for j in range(4):
        carry = (a[j] & 0x80000000) | (a[j + 1] & 0x7FFFFFFF)
        carry = (carry >> 1) ^ (MAG if a[j + 1] & 1 else 0)
        predicted.append((b[j] ^ carry) & U32)
    coupon = b"".join(temper(w).to_bytes(4, "little") for w in predicted)
    component = bytes(x ^ y for x, y in zip(coupon, mask))
    return Recovery(coupon, component, sha256(component).hexdigest() == TARGET)


def planted_controls() -> None:
    import random
    for seed in (0, 1, 42, 0xDEADBEEF):
        rng = random.Random(seed)
        output = [rng.getrandbits(32).to_bytes(4, "little") for _ in range(1000)]
        generated = reconstruct(
            untemper(int.from_bytes(output[327], "little")),
            b"".join(output[328:332]),
            b"".join(output[724:728]),
        )
        assert generated.printed_coupon == b"".join(output[951:955])
        assert generated.component == bytes(
            a ^ b for a, b in zip(generated.printed_coupon, MASK)
        )


if __name__ == "__main__":
    planted_controls()
    source = Path(__file__).resolve().parents[2] / "resources"
    known = retained_native_327(source)
    assert known == 0x59E4D0B9
    print("4/4 complete genuine MT packet controls PASS")
    print(f"Retained original stage327 native word = {known:08X}")
    print("Awaiting two independently indexed original gap packets")
