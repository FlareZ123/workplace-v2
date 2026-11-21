"""H-17 K04 exact xoroshiro64* / xoroshiro64** 32-bit output-state inversion.

Read-only original-source test. Selected attempt-2 payload is withheld from all
generator fits. Each of the two alternative 64-bit-state generators is inverted
from two observed 32-bit outputs. The two remaining words of the same source
REQUESTED packet must match exactly before any missing-packet construction.
The first/third attempts are each used as a separate possible stream anchor.

Reference algorithm: Apache Commons RNG XoRoShiRo64StarStar.java and
XoRoShiRo64Star.java, corresponding to Blackman/Vigna xoroshiro64.
This is NOT the 128-bit-state xoroshiro128++ first-pair search.
"""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
M32 = (1 << 32) - 1
MULTIPLIER = 0x9E3779BB
INV_MULTIPLIER = pow(MULTIPLIER, -1, 1 << 32)
INV_FIVE = pow(5, -1, 1 << 32)
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def rol(value: int, n: int) -> int:
    return ((value << n) | (value >> (32 - n))) & M32


def ror(value: int, n: int) -> int:
    return ((value >> n) | (value << (32 - n))) & M32


def next_word(state: tuple[int, int], starstar: bool) -> tuple[int, tuple[int, int]]:
    a, b = state
    x = a * MULTIPLIER & M32
    output = (rol(x, 5) * 5) & M32 if starstar else x
    t = a ^ b
    return output, ((rol(a, 26) ^ t ^ (t << 9)) & M32, rol(t, 13))


def invert_two_outputs(y0: int, y1: int, starstar: bool) -> tuple[int, int]:
    def undo_output(y: int) -> int:
        return (
            (ror(y * INV_FIVE & M32, 5) * INV_MULTIPLIER) & M32
            if starstar else (y * INV_MULTIPLIER) & M32
        )

    a0, a1 = undo_output(y0), undo_output(y1)
    # a1 = rol(a0, 26) XOR t XOR (t << 9), t = a0 XOR b0.
    t = a1 ^ rol(a0, 26)
    t ^= (t << 9) & M32
    t ^= (t << 18) & M32
    return a0, a0 ^ t


def previous_state(state: tuple[int, int]) -> tuple[int, int]:
    a1, b1 = state
    t = ror(b1, 13)
    a0 = ror((a1 ^ t ^ (t << 9)) & M32, 26)
    return a0, a0 ^ t


def stream(state: tuple[int, int], n: int, starstar: bool) -> tuple[list[int], tuple[int, int]]:
    words = []
    for _ in range(n):
        y, state = next_word(state, starstar)
        words.append(y)
    return words, state


def decode_packet(packet: bytes, endian: str) -> tuple[int, ...]:
    return tuple(int.from_bytes(packet[i:i + 4], endian) for i in range(0, 16, 4))


def encode_coupon(outputs: list[int], endian: str, order: tuple[int, ...]) -> bytes:
    # order maps physical word indices into the generator's output order.
    physical = [outputs[order.index(i)] for i in range(4)]
    return b"".join(word.to_bytes(4, endian) for word in physical)


def original_source() -> tuple[dict[str, bytes], bytes, str]:
    path = ROOT / "evidence/print/spool-reconstruction.log"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    packets: dict[str, bytes] = {}
    for line in raw.decode("ascii").splitlines():
        if not line.startswith("2026-10-03T18:0"):
            continue
        fields = dict(x.split("=", 1) for x in line.split()[1:])
        if fields["JOB"] != "PS-261003-0417" or fields["ATTEMPT"] == "2":
            continue  # selected ACK2 is excluded before its payload is decoded
        if fields["STATE"] == "REQUESTED" and fields["ATTEMPT"] in ("1", "3"):
            packets[fields["ATTEMPT"]] = bytes.fromhex(fields["PAYLOAD"])
    assert sorted(packets) == ["1", "3"]
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    return packets, bytes.fromhex(route["K04"]["masked_component"]), acceptance["slot_sha256"]["K04"]


def main() -> None:
    # Synthetic positive: recover the entire 64-bit state from two words,
    # re-predict source words 2..3, and both a missing middle packet and later
    # independent four-word holdout. Check a complete masked coupon hash.
    mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
    for variant in (False, True):
        initial = (0x12345678, 0x9ABCDEF1)
        outputs, _ = stream(initial, 12, variant)
        recovered = invert_two_outputs(*outputs[:2], variant)
        assert recovered == initial
        whole, final_state = stream(recovered, 12, variant)
        assert whole == outputs
        for _ in range(12):
            final_state = previous_state(final_state)
        assert final_state == initial
        control_coupon = encode_coupon(outputs[4:8], "little", (0, 1, 2, 3))
        planted = bytes(a ^ b for a, b in zip(control_coupon, mask))
        assert hashlib.sha256(planted).digest() == hashlib.sha256(
            bytes(a ^ b for a, b in zip(
                encode_coupon(whole[4:8], "little", (0, 1, 2, 3)), mask
            ))
        ).digest()
    print("PLANTED_PASS: xoroshiro64* and ** inverse, 4-word source, middle hash, later holdout")

    packets, source_mask, target_sha = original_source()
    source_pass = 0
    target_hits = 0
    model_checks = 0
    for variant in (False, True):
        for endian in ("big", "little"):
            for order in itertools.permutations(range(4)):
                for attempt in ("1", "3"):
                    model_checks += 1
                    observed = decode_packet(packets[attempt], endian)
                    arranged = [observed[i] for i in order]
                    state = invert_two_outputs(*arranged[:2], variant)
                    reproduced, _ = stream(state, 4, variant)
                    if reproduced != arranged:
                        continue
                    source_pass += 1
                    if attempt == "1":
                        predicted, _ = stream(state, 8, variant)
                        middle = predicted[4:8]
                    else:
                        for _ in range(4):
                            state = previous_state(state)
                        middle, _ = stream(state, 4, variant)
                    coupon = encode_coupon(middle, endian, order)
                    component = bytes(a ^ b for a, b in zip(coupon, source_mask))
                    hit = hashlib.sha256(component).hexdigest() == target_sha
                    target_hits += int(hit)
                    if hit:
                        print(f"K04_ORIGINAL_HIT component={component.hex().upper()}")
    assert model_checks == 192
    assert source_pass == 0 and target_hits == 0
    print("ORIGINAL_DONE: source_fits=0/192; K04_commitment_hits=0; no 16-byte recovery")


if __name__ == "__main__":
    main()
