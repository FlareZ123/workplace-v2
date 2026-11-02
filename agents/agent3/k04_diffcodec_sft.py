"""SFT: read-only differential printer-copy line code hypothesis for K04.

Use original ESC-N selected ACK2, byte/word views, 128-bit rotations, and
reversible NRZI or Gray differential encoding/decoding with independently
resettable block boundaries. The complete derived coupon, XOR the original
route mask, is tested against original K04 SHA256. This is a speculative
candidate construction, NOT source-authenticated print-stage evidence.

Run from repository root: python agents/agent3/k04_diffcodec_sft.py
"""
import hashlib
import itertools
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2] / "resources"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def source_payload():
    data = (R / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == SPOOL_SHA
    rows = [line for line in data.decode("ascii").splitlines()
            if "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER " in line]
    assert len(rows) == 1
    return bytes.fromhex(rows[0].split("PAYLOAD=")[1].split()[0])


def bits_of(data):
    return [(value >> (7 - bit)) & 1 for value in data for bit in range(8)]


def from_bits(bits):
    return bytes(sum(bits[8 * k + bit] << (7 - bit) for bit in range(8))
                 for k in range(16))


def view(data, index):
    if index == 0:
        return data
    if index == 1:
        return data[::-1]
    if index == 2:
        return b"".join(data[i:i + 4][::-1] for i in range(0, 16, 4))
    if index == 3:
        return b"".join(data[i:i + 2][::-1] for i in range(0, 16, 2))
    if index == 4:
        return b"".join(data[i:i + 4] for i in (12, 8, 4, 0))
    if index == 5:
        return bytes(int(f"{x:08b}"[::-1], 2) for x in data)
    if index in range(6, 13):
        return bytes(x ^ (255, 85, 170, 240, 15, 51, 204)[index - 6]
                     for x in data)
    if index == 13:
        return bytes(data[(i % 4) * 4 + i // 4] for i in range(16))
    if index == 14:
        return bytes(data[(i // 4) * 4 + 3 - i % 4] for i in range(16))
    if index == 15:
        return bytes(data[(3 - i // 4) * 4 + i % 4] for i in range(16))
    raise ValueError(index)


def differential(src, block, phase, encode, reverse, polarity):
    data = list(src)
    if reverse:
        data.reverse()
    result = []
    for start in range(0, 128, block):
        prior = phase
        for bit in data[start:start + block]:
            if encode:
                prior ^= bit
                result.append(prior)
            else:
                result.append(bit ^ prior)
                prior = bit
    if reverse:
        result.reverse()
    if polarity:
        result = [1 - x for x in result]
    return result


def main():
    source = source_payload()
    route = json.loads((R / "evidence/recovery-routing.json").read_text())
    target = json.loads((R / "acceptance.json").read_text())["slot_sha256"]["K04"]
    mask = bytes.fromhex(route["K04"]["masked_component"])

    for block in (1, 2, 4, 8, 16, 32, 64, 128):
        for phase in (0, 1):
            synthetic = [((k * 17) >> 2) & 1 for k in range(128)]
            coded = differential(synthetic, block, phase, True, False, False)
            assert differential(coded, block, phase, False, False, False) == synthetic
    print("PASS synthetic reversible line-code control")
    count = 0
    seen = set()
    hits = []
    for orientation in range(16):
        base = bits_of(view(source, orientation))
        for rotation in range(128):
            rotated = base[rotation:] + base[:rotation]
            for block in (1, 2, 4, 8, 16, 32, 64, 128):
                for phase, encode, reverse, polarity in itertools.product((0, 1), repeat=4):
                    packet = from_bits(differential(
                        rotated, block, phase, encode, reverse, polarity))
                    if packet in seen:
                        continue
                    seen.add(packet)
                    count += 1
                    candidate = bytes(a ^ b for a, b in zip(packet, mask))
                    if hashlib.sha256(candidate).hexdigest() == target:
                        hits.append((orientation, rotation, block, phase,
                                     encode, reverse, polarity, candidate.hex().upper()))
    assert len(source) == len(mask) == 16
    assert count == 90572
    assert not hits
    synthetic = bytes(range(16))
    masked = bytes(a ^ b for a, b in zip(synthetic, mask))
    assert bytes(a ^ b for a, b in zip(masked, mask)) == synthetic
    print(f"full unique candidate coupons: {count}; commitment hits: {hits}")
    print("Original selected K04: NO_MATCH; historical codec: UNATTESTED")


if __name__ == "__main__":
    main()
