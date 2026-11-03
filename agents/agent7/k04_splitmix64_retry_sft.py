"""Read-only K04 SplitMix64 selected-retry inverse and original source holdout.

Uses only Python 3 standard library. Run from the GitHub working tree:
    python agents/agent7/k04_splitmix64_retry_sft.py
The original source, route, acceptance and candidate are never modified.
"""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources/evidence/print/spool-reconstruction.log"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
GOLDEN = 0x9E3779B97F4A7C15
BITS = (1 << 64) - 1


def unshift(value: int, shift: int) -> int:
    width = shift
    while width < 64:
        value ^= value >> width
        width <<= 1
    return value & BITS


def forward(value: int, mode: str) -> int:
    if mode == "stafford13":
        value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & BITS
        value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & BITS
        return (value ^ (value >> 31)) & BITS
    value = ((value ^ (value >> 33)) * 0xFF51AFD7ED558CCD) & BITS
    value = ((value ^ (value >> 33)) * 0xC4CEB9FE1A85EC53) & BITS
    return (value ^ (value >> 33)) & BITS


def inverse(value: int, mode: str) -> int:
    if mode == "stafford13":
        value = unshift(value, 31)
        value = value * pow(0x94D049BB133111EB, -1, 1 << 64) & BITS
        value = unshift(value, 27)
        value = value * pow(0xBF58476D1CE4E5B9, -1, 1 << 64) & BITS
        return unshift(value, 30)
    value = unshift(value, 33)
    value = value * pow(0xC4CEB9FE1A85EC53, -1, 1 << 64) & BITS
    value = unshift(value, 33)
    value = value * pow(0xFF51AFD7ED558CCD, -1, 1 << 64) & BITS
    return unshift(value, 33)


def decode(packet: bytes, byteorder: str, reverse: bool) -> tuple[int, int]:
    assert len(packet) == 16
    pair = [int.from_bytes(packet[p:p + 8], byteorder) for p in (0, 8)]
    return tuple(pair[::-1] if reverse else pair)


def encode(pair: tuple[int, int], byteorder: str, reverse: bool) -> bytes:
    return b"".join(value.to_bytes(8, byteorder) for value in (pair[::-1] if reverse else pair))


def check(first: bytes, third: bytes, mode: str, byteorder: str, reverse: bool):
    initial = [inverse(value, mode) for value in decode(first, byteorder, reverse)]
    final = [inverse(value, mode) for value in decode(third, byteorder, reverse)]
    gamma = (initial[1] - initial[0]) & BITS
    compatible = bool(gamma & 1) and ((final[1] - final[0]) & BITS) == gamma
    middle = encode(
        tuple(forward((initial[0] + gamma * index) & BITS, mode) for index in (2, 3)),
        byteorder, reverse
    )
    component = bytes(a ^ b for a, b in zip(middle, MASK))
    hit = hashlib.sha256(component).hexdigest() == TARGET
    return compatible, gamma == GOLDEN and compatible, middle, hit


def main() -> None:
    source = SOURCE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA
    regex = re.compile(
        r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) "
        r"CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)$"
    )
    rows = [match.groups() for line in source.decode().splitlines()
            if (match := regex.match(line))]
    assert len(rows) == 133
    assert all(row[3] == "ACK" for row in rows[:128])
    selected = [row for row in rows if row[1] == "PS-261003-0417" and row[4] == "RECOVER"]
    assert [(row[2], row[3]) for row in selected] == [
        ("1", "REQUESTED"), ("2", "ACK"), ("3", "REQUESTED")
    ]
    a, _, b = [bytes.fromhex(row[5]) for row in selected]
    assert a.hex().upper() == "CD3E4F216ADB2FB180DA2AA90B33F7A4"
    assert b.hex().upper() == "44D53DFC29D7943A95D89371DA58EC64"

    positive_count = 0
    rows_examined = 0
    compatible_count = 0
    target_hits = 0
    for mode in ("stafford13", "murmur64"):
        for byteorder in ("little", "big"):
            for reverse in (False, True):
                for seed in (0, 1, 0x9876543210ABCDEF):
                    for gamma in (GOLDEN, 0x1111222233334445):
                        samples = tuple(forward((seed + gamma * i) & BITS, mode)
                                        for i in range(1, 7))
                        one = encode(samples[:2], byteorder, reverse)
                        three = encode(samples[4:6], byteorder, reverse)
                        good, fixed, middle, _ = check(one, three, mode, byteorder, reverse)
                        assert good and fixed == (gamma == GOLDEN)
                        assert middle == encode(samples[2:4], byteorder, reverse)
                        positive_count += 1

                fixed_packet_count = 0
                for record in rows[:128]:
                    words = decode(bytes.fromhex(record[5]), byteorder, reverse)
                    raw = [inverse(word, mode) for word in words]
                    fixed_packet_count += ((raw[1] - raw[0]) & BITS) == GOLDEN
                    rows_examined += 1
                compatible, fixed, middle, hit = check(a, b, mode, byteorder, reverse)
                compatible_count += compatible
                target_hits += hit
                print(
                    "mode=", mode, "byteorder=", byteorder, "reverse=", reverse,
                    "fixed_gamma_intact_rows=", fixed_packet_count,
                    "same_job_compatible=", compatible, "fixed_gamma=", fixed,
                    "hypothetical_middle=", middle.hex().upper(),
                    "original_K04_hit=", hit
                )
                assert fixed_packet_count == 0 and not compatible and not hit
    assert positive_count == 48
    assert rows_examined == 1024 and compatible_count == 0 and target_hits == 0
    print("SUMMARY:", positive_count, "seeded positives PASS;",
          rows_examined, "intact fixed-gamma packet checks 0;",
          "8 source-bracketed stage models 0;",
          "8 complete hypothetical K04 candidates 0.")


if __name__ == "__main__":
    main()
