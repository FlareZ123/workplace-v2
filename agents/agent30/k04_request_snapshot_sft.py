"""H-17 K04: read-only same-job REQUESTED buffers as xoroshiro state snapshots.

Run from repository root: python agents/agent30/k04_request_snapshot_sft.py
No third-party dependencies. Original files and official verifier are unchanged.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[2] / "resources"
MASK64 = (1 << 64) - 1
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def rol(x: int, n: int) -> int:
    return ((x << n) | (x >> (64 - n))) & MASK64


def step(a: int, b: int, variant: str) -> tuple[int, int, int]:
    if variant == "plusplus":
        out = (rol((a + b) & MASK64, 17) + a) & MASK64
        rot_a, shift_t, rot_t = 49, 21, 28
    else:
        out = (a + b) & MASK64
        rot_a, shift_t, rot_t = 24, 16, 37
    t = a ^ b
    return out, (rol(a, rot_a) ^ t ^ (t << shift_t)) & MASK64, rol(t, rot_t)


def decode(block: bytes, view: int) -> tuple[int, int]:
    endian = "little" if view & 1 else "big"
    words = [int.from_bytes(block[i:i + 8], endian) for i in (0, 8)]
    return tuple(words[::-1] if view & 2 else words)


def encode(words: tuple[int, int], view: int) -> bytes:
    endian = "little" if view & 1 else "big"
    return b"".join(w.to_bytes(8, endian) for w in (words[::-1] if view & 2 else words))


def advance(source: tuple[int, int], variant: str):
    a, b = source
    for _ in range(2):
        _, a, b = step(a, b, variant)
    middle_state = a, b
    outputs = []
    for _ in range(2):
        y, a, b = step(a, b, variant)
        outputs.append(y)
    return middle_state, tuple(outputs), (a, b)


def original_requests() -> tuple[bytes, bytes]:
    log = (E / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(log).hexdigest() == SPOOL_SHA
    rows = []
    for line in log.decode("ascii").splitlines():
        if "JOB=PS-261003-0417 " in line and "CLASS=RECOVER" in line:
            rows.append(dict(t.split("=", 1) for t in line.split()[1:]))
    assert [(r["ATTEMPT"], r["STATE"]) for r in rows] == [
        ("1", "REQUESTED"), ("2", "ACK"), ("3", "REQUESTED")]
    # Never decode selected ACK2 payload. Its copied bytes do not enter the model.
    first = bytes.fromhex(rows[0]["PAYLOAD"])
    third = bytes.fromhex(rows[2]["PAYLOAD"])
    assert first.hex().upper() == "CD3E4F216ADB2FB180DA2AA90B33F7A4"
    assert third.hex().upper() == "44D53DFC29D7943A95D89371DA58EC64"
    return first, third


def main() -> None:
    first, third = original_requests()
    route = json.loads((E / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((E / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    assert len(mask) == 16 and len(target) == 64

    planted = 0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA
    for variant in ("plus", "plusplus"):
        mid, middle_outputs, end = advance(planted, variant)
        a, b = planted
        sequence = []
        for index in range(4):
            o, a, b = step(a, b, variant)
            sequence.append(o)
            if index == 1:
                assert (a, b) == mid
        assert (a, b) == end
        assert tuple(sequence[2:]) == middle_outputs
        for view in range(4):
            assert decode(encode(planted, view), view) == planted
            assert decode(encode(end, view), view) == end
            assert len(encode(mid, view)) == len(encode(middle_outputs, view)) == 16
    print("SYNTHETIC_FOUR_STEP_STATE_AND_OUTPUT_CONTROLS=PASS")

    source_matches = 0
    hits = []
    count = 0
    for variant in ("plus", "plusplus"):
        for view in range(4):
            mid, outs, predicted_third = advance(decode(first, view), variant)
            match = predicted_third == decode(third, view)
            source_matches += match
            for role, words in (("state", mid), ("outputs", outs)):
                coupon = encode(words, view)
                component = bytes(x ^ y for x, y in zip(coupon, mask))
                count += 1
                if hashlib.sha256(component).hexdigest() == target:
                    hits.append((variant, view, role, coupon.hex().upper(), component.hex().upper()))
            print(f"ORIGINAL_SOURCE variant={variant} view={view} third_state_match={match}")
    print(f"ORIGINAL_STATE_MATCHES={source_matches} COMPLETE_K04_CANDIDATES={count} ORIGINAL_K04_PASSES={len(hits)}")
    for hit in hits:
        print("ORIGINAL_K04_PASS", hit)
    assert count == 16
    assert source_matches == 0
    assert not hits


if __name__ == "__main__":
    main()
