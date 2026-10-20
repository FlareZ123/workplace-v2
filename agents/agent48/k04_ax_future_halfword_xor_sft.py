"""Read-only original AX transfer halfword versus source-only future-word XOR SFT."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SOURCE = ROOT / "evidence/transfers/transfer-audit.jsonl"
EXPECTED_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
FUTURE_XOR = 0xBD2761F8


def temper(word: int) -> int:
    word ^= word >> 11
    word ^= (word << 7) & 0x9D2C5680
    word ^= (word << 15) & 0xEFC60000
    word ^= word >> 18
    return word & 0xFFFFFFFF


def main() -> None:
    data = SOURCE.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == EXPECTED_SHA, (digest, EXPECTED_SHA)
    rows = [json.loads(line) for line in data.splitlines()]
    by_transfer = defaultdict(list)
    for row in rows:
        if row.get("kind") == "CHUNK":
            by_transfer[row["transfer"]].append(row)
    assert set(by_transfer) == {"AX-7778", "AX-7781", "AX-7782", "AX-7783"}
    assert all(len(group) == 16 for group in by_transfer.values())
    upper16 = temper(FUTURE_XOR) >> 16
    assert all(temper(a ^ b) == (temper(a) ^ temper(b)) for a, b in
               [(0xDEADBEEF, 0xCAFECAFE), (0x12345678, 0x87654321), (0, 0xFFFFFFFF)])
    print(f"Source sha256={digest} future_xor={FUTURE_XOR:08X} tempered_upper16={upper16:04X}")
    total = 0
    hits = []
    for transfer in sorted(by_transfer):
        ordered = sorted(by_transfer[transfer], key=lambda row: (row["seq"], row["attempt"]))
        for endian in ("big", "little"):
            values = [int.from_bytes(bytes.fromhex(row["checkpoint"]), endian) for row in ordered]
            local_hits = []
            for i, left in enumerate(values):
                for j in range(i + 1, len(values)):
                    total += 1
                    if left ^ values[j] == upper16:
                        pair = (ordered[i]["seq"], ordered[i]["attempt"],
                                ordered[j]["seq"], ordered[j]["attempt"])
                        hits.append((transfer, endian, pair))
                        local_hits.append(pair)
            print(f"{transfer}/{endian}: tested=120 matches={len(local_hits)} {local_hits}")
    assert total == 960
    print(f"total={total}, matches={len(hits)}, hit_records={hits}")


if __name__ == "__main__":
    main()
