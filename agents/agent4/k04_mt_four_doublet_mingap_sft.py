"""H-17: source-only MT doublet obstruction for seven draws between spool packets.

Usage: python agents/agent4/k04_mt_four_doublet_mingap_sft.py [spool.log]
Standard library only; source read-only; selected row 129 is never decoded.
"""
import hashlib
from pathlib import Path
import re
import sys

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TARGET_ROW = 129
MASK = 0xFFFFFFFF


def untemper(value):
    def undo_right(y, offset):
        original = y
        for _ in range(5):
            y = original ^ (y >> offset)
        return y & MASK

    def undo_left(y, offset, mask):
        original = y
        for _ in range(5):
            y = original ^ ((y << offset) & mask)
        return y & MASK

    value = undo_right(value, 18)
    value = undo_left(value, 15, 0xEFC60000)
    value = undo_left(value, 7, 0x9D2C5680)
    return undo_right(value, 11)


def temper(value):
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    return (value ^ (value >> 18)) & MASK


def twist_pair(before, now):
    joint = (before & 0x80000000) | (now & 0x7FFFFFFF)
    return (joint >> 1) ^ (0x9908B0DF if now & 1 else 0)


def load_original(path):
    content = path.read_bytes()
    assert hashlib.sha256(content).hexdigest() == SOURCE_SHA
    rows = [line for line in content.decode("ascii").splitlines() if line and not line.startswith("#")]
    assert len(rows) == 133
    assert all(marker in rows[TARGET_ROW] for marker in (
        "JOB=PS-261003-0417", "ATTEMPT=2", "STATE=ACK", "CLASS=RECOVER"))
    words = []
    for index, row in enumerate(rows):
        if index == TARGET_ROW:
            words.append(None)
            continue
        payload = re.search(r"\bPAYLOAD=([0-9A-F]{32})\b", row)
        assert payload is not None, index
        blob = bytes.fromhex(payload.group(1))
        words.append(tuple(untemper(int.from_bytes(blob[4*j:4*j+4], "little")) for j in range(4)))
    return words


def check_frozen_core(words):
    # (first source row, middle row, final row, right-input lane, middle lane, final lane)
    # Each first lane is independently corroborated by the following lane.
    four_doublets = (
        (11, 65, 95, 1, 0, 2),
        (12, 66, 96, 1, 1, 2),
        (32, 84, 115, 1, 2, 0),
        (42, 95, 126, 1, 1, 2),
    )
    stage_differences = []
    for r, k, l, p, i, q in four_doublets:
        for delta in (0, 1):
            pred = words[k][i+delta] ^ twist_pair(words[r][p+delta-1], words[r][p+delta])
            assert pred == words[l][q+delta], (r, k, l, delta)
        stage_differences.append((396+p-i, 623+p-q))
    assert stage_differences == [(397, 622), (396, 622), (395, 624), (396, 622)]
    # Exact stage-value algebra, with S_j the start of historical row j:
    #   S42-S11 = (S95-S11) - (S95-S42) = 622-396 = 226.
    #   (S32-S12)+(S66-S65)+(S126-S115) = (S42-S11)-1-2 = 223.
    observed_total = stage_differences[0][1] - stage_differences[3][0] - 1 - 2
    n_intervals = (32-12) + (66-65) + (126-115)
    min_seven = n_intervals * 7
    assert (observed_total, n_intervals, min_seven) == (223, 32, 224)
    return observed_total, n_intervals, min_seven


def main():
    spool = (Path(sys.argv[1]) if len(sys.argv)>1 else
             Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log")
    for number in (0, 1, 0x12345678, 0xFFFFFFFF):
        assert untemper(temper(number)) == number
    source = load_original(spool)
    observed, gaps, floor = check_frozen_core(source)
    print(f"SOURCE PASS sha256={SOURCE_SHA} selected_row={TARGET_ROW} withheld=True")
    print("DOUBLETS PASS 4 independent source triples x 2 adjacent complete 32-bit matches")
    print(f"STAGE OBSTRUCTION observed_sum={observed} gaps={gaps} if_min7={floor} deficit={floor-observed}")
    print("RESULT no uniform >=7-word-per-ordinary-job producer fits all four doublets; no K04 candidate generated")


if __name__ == "__main__":
    main()
