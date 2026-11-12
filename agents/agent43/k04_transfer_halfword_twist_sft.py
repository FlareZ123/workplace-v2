"""Source-pinned K04 transfer-halfword extension of the p951 MT predecessor test.

Run from the repository root:
    python agents/agent43/k04_transfer_halfword_twist_sft.py

The selected printer row 129 is omitted before its payload is parsed. The
script does not read the K04 route mask, K04 commitment, candidate, or verifier.
All conclusions are conditional on the existing hypothetical p951 MT19937
printer-stage vector and its 227-step predecessor identity.
"""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TRANSFER_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
MAG = 0x9908B0DF
LOW31 = 0xBFFFFFFF
MASK32 = 0xFFFFFFFF

# Hypothetical p951 packet starts from the existing source-only MT basis.
STARTS = [
    0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,
    154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,
    272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,
    401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,
    531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,
    658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,
    788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,
    912,918,924,930,936,942,947,951,955,959,963
]
SELECTED_ROW = 129

sys.path.insert(0, str(ROOT))
_p951_spec = importlib.util.spec_from_file_location(
    "p951_source", ROOT / "agents" / "agent49" / "k04_p951_symbolic_basis.py"
)
p951 = importlib.util.module_from_spec(_p951_spec)
_p951_spec.loader.exec_module(p951)


def untemper(value):
    x = value & MASK32
    for shift, left, mask in (
        (18, False, MASK32),
        (15, True, 0xEFC60000),
        (7, True, 0x9D2C5680),
        (11, False, MASK32),
    ):
        y = x
        for _ in range(6):
            y = x ^ (((y << shift) & mask) if left else (y >> shift))
        x = y & MASK32
    return x


def temper(value):
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    value ^= value >> 18
    return value & MASK32


def printer_words():
    raw = (EVIDENCE / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    words = {}
    packet_row = 0
    for line in raw.decode("ascii").splitlines():
        if "PAYLOAD=" not in line:
            continue
        if packet_row != SELECTED_ROW:
            match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
            assert match is not None, packet_row
            payload = bytes.fromhex(match.group(1))
            words[packet_row] = [
                untemper(int.from_bytes(payload[4*j:4*j+4], "little"))
                for j in range(4)
            ]
        # The selected row is skipped before its PAYLOAD field is parsed.
        packet_row += 1
    assert packet_row == 133
    assert len(words) == 132 and SELECTED_ROW not in words
    return words


def checkpoint_streams():
    raw = (EVIDENCE / "transfers" / "transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TRANSFER_SHA
    rows = [json.loads(line) for line in raw.splitlines()]
    chunks = [row for row in rows if row["kind"] == "CHUNK"]
    assert len(chunks) == 64
    streams = {}
    selected = {}
    for transfer in sorted({row["transfer"] for row in chunks}):
        items = sorted(
            (row for row in chunks if row["transfer"] == transfer),
            key=lambda row: (row["seq"], row["attempt"]),
        )
        assert len(items) == 16
        assert [(row["seq"], row["attempt"]) for row in items] == [
            (seq, attempt) for seq in range(8) for attempt in (1, 2)
        ]
        # The existing AX-7778 bridge treats each 2-byte checkpoint as a
        # little-endian halfword; preserve that interpretation here.
        streams[transfer] = [
            int.from_bytes(bytes.fromhex(row["checkpoint"]), "little")
            for row in items
        ]
        by_seq = defaultdict(list)
        for row in items:
            by_seq[row["seq"]].append(row)
        chosen = [max(by_seq[seq], key=lambda row: row["attempt"])
                  for seq in range(8)]
        selected[transfer] = [
            int.from_bytes(bytes.fromhex(row["checkpoint"]), "little")
            for row in chosen
        ]
    assert set(streams) == {"AX-7778", "AX-7781", "AX-7782", "AX-7783"}
    return streams, selected


def predecessor_high16_pairs(words):
    # The 227-step packet-start pairs already used by the p951 predecessor
    # fingerprint. Do not infer or search arbitrary row-pair distances here.
    pairs = [
        (a, b)
        for a in range(len(STARTS))
        for b in range(a + 1, len(STARTS))
        if STARTS[b] - STARTS[a] == 227
    ]
    assert len(pairs) == 12
    allowed = {}
    for a, b in pairs:
        lane_sets = []
        for lane in range(4):
            difference = (words[a][lane] ^ words[b][lane]) & LOW31
            parity = difference >> 31
            lower = (
                ((difference ^ (MAG if parity else 0)) & 0x3FFFFFFF) << 1
            ) | parity
            # The predecessor's unknown MSB yields exactly two possible
            # tempered high-halfword values.
            lane_sets.append({
                temper(lower) >> 16,
                temper(lower | 0x80000000) >> 16,
            })
        allowed[(a, b)] = lane_sets
    return pairs, allowed


def scan_windows(streams, allowed):
    full, partial = [], []
    for transfer, values in streams.items():
        for start in range(len(values) - 3):
            window = values[start:start+4]
            for pair, lane_sets in allowed.items():
                matches = [window[i] in lane_sets[i] for i in range(4)]
                count = sum(matches)
                record = (
                    transfer, start, pair,
                    [f"{value:04X}" for value in window],
                )
                if count == 4:
                    full.append(record)
                elif count >= 2:
                    partial.append((record, count, matches))
    return full, partial



def direct_post_target_sequence():
    """Test AX-7782 as 16 consecutive CPython getrandbits(16) outputs after the spool."""
    basis, symbolic = p951.source(ROOT)
    assert basis.rank == 15365
    assert p951.ORIGIN == -1100 and p951.LAST == 1040

    audit = [
        json.loads(line)
        for line in (EVIDENCE / "transfers" / "transfer-audit.jsonl").read_text().splitlines()
    ]
    commit = next(
        row for row in audit
        if row["kind"] == "COMMIT" and row["transfer"] == "AX-7782"
        and row.get("dry_run") is False
    )
    receipt = datetime.fromisoformat(commit["receipt_utc"].replace("Z", "+00:00"))
    items = sorted(
        (row for row in audit if row["kind"] == "CHUNK" and row["transfer"] == "AX-7782"),
        key=lambda row: (row["seq"], row["attempt"]),
    )
    assert len(items) == 16
    values = [
        int.from_bytes(bytes.fromhex(row["checkpoint"]), "little")
        for row in items
    ]

    packet_lines = [
        line for line in (EVIDENCE / "print" / "spool-reconstruction.log").read_text().splitlines()
        if "PAYLOAD=" in line
    ]
    last_packet_time = datetime.fromisoformat(
        packet_lines[-1].split()[0].replace("Z", "+00:00")
    )
    assert receipt > last_packet_time
    # Row 132 starts at 963 and contains four words; the first possible
    # post-spool output is 967. Search every 16-word placement still inside
    # the existing p951 model's declared range.
    first_start = 967
    last_start = p951.LAST - len(values) + 1
    assert first_start == 967 and last_start == 1025

    def reduce_source(value, rhs=0):
        remainder = 0
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis.rows:
                vector, bit = basis.rows[pivot]
                value ^= vector
                rhs ^= bit
            else:
                remainder |= 1 << pivot
                value ^= 1 << pivot
        return remainder, rhs

    consistent_alignments = []
    encodings = (
        ("tempered", "low", 0),
        ("tempered", "high", 16),
        ("native", "low", 0),
        ("native", "high", 16),
    )
    for kind, half, bitbase in encodings:
        stage_map = {}
        for stage in range(first_start, last_start + len(values)):
            word = p951.temper(p951.get(symbolic, stage)) if kind == "tempered" else p951.get(symbolic, stage)
            stage_map[stage] = [
                reduce_source(word[bitbase + bit]) for bit in range(16)
            ]
        for start in range(first_start, last_start + 1):
            small = {}
            consistent = True
            for index, value in enumerate(values):
                for bit in range(16):
                    residual, offset = stage_map[start + index][bit]
                    rhs = ((value >> bit) & 1) ^ offset
                    while residual:
                        pivot = residual.bit_length() - 1
                        if pivot not in small:
                            small[pivot] = (residual, rhs)
                            break
                        vector, known = small[pivot]
                        residual ^= vector
                        rhs ^= known
                    if not residual and rhs:
                        consistent = False
                        break
                if not consistent:
                    break
            if consistent:
                consistent_alignments.append((kind, half, start))

    assert len(consistent_alignments) == 0, consistent_alignments
    return {
        "transfer_receipt_utc": commit["receipt_utc"],
        "last_spool_packet_utc": packet_lines[-1].split()[0],
        "checkpoint_order": "seq ascending, attempt ascending",
        "checkpoint_count": len(values),
        "post_target_encoding_start_pairs_tested": len(encodings) * (last_start - first_start + 1),
        "encodings": ["tempered-low16", "tempered-high16", "native-low16", "native-high16"],
        "consistent_alignments": consistent_alignments,
    }


def main():
    words = printer_words()
    streams, selected = checkpoint_streams()
    pairs, allowed = predecessor_high16_pairs(words)
    full, partial = scan_windows(streams, allowed)
    selected_full, selected_partial = scan_windows(selected, allowed)

    expected = [
        ("AX-7778", 11, (34, 64), ["35AE", "78FE", "42DD", "FD35"])
    ]
    assert full == expected, full
    assert partial == [], partial
    assert selected_full == [], selected_full
    assert selected_partial == [], selected_partial
    direct_sequence = direct_post_target_sequence()

    # Positive control: the known AX-7778 group is found exactly.
    control = [0x35AE, 0x78FE, 0x42DD, 0xFD35]
    assert all(control[i] in allowed[(34, 64)][i] for i in range(4))
    # Negative control: mutate one bit of one checkpoint.
    mutated = control.copy()
    mutated[2] ^= 1
    assert not all(mutated[i] in allowed[(34, 64)][i] for i in range(4))

    print(json.dumps({
        "p951_227_packet_pairs": len(pairs),
        "transfers": sorted(streams),
        "all_attempt_windows_tested": sum(len(v)-3 for v in streams.values()),
        "all_attempt_full_matches": full,
        "all_attempt_partial_matches_ge_2": len(partial),
        "highest_attempt_windows_tested": sum(len(v)-3 for v in selected.values()),
        "highest_attempt_full_matches": selected_full,
        "highest_attempt_partial_matches_ge_2": len(selected_partial),
        "direct_post_target_sequence": direct_sequence,
        "AX_7782_highest_attempt_chain": [
            f"{value:04X}" for value in selected["AX-7782"]
        ],
        "positive_control": "PASS",
        "one_bit_negative_control": "PASS",
        "new_K04_bits_recovered": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
