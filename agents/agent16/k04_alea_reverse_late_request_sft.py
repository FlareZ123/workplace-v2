"""Bounded reverse-Alea test: can late PS-0417 REQUESTED3 recover prior ACK2?

Reads only the retained source export and the unchanged route/acceptance files.
The selected ACK2 payload is not decoded or used. Candidate bytes are never
printed or written. Run from the repository root, or set H17_SOURCE_ROOT.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
from pathlib import Path

A = 2_091_639
Q = 1 << 32
MASK32 = Q - 1
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPTANCE_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"


def forward(words: list[int], carry: int, count: int) -> tuple[list[int], int]:
    out = list(words)
    for _ in range(count):
        n = A * out[-3] + carry
        out.append(n & MASK32)
        carry = n >> 32
    return out, carry


def reverse_previous_packet(current: tuple[int, int, int, int]):
    """Invert one four-word Alea/MWC3 block, returning prior packet and carry.

    For y[t+3] = (A*y[t] + c[t]) mod 2^32, the carry c[t] is uniquely
    recoverable and must be < A. Each earlier word/carry pair then follows
    by exact quotient/remainder inversion. The final forward check guards the
    inverse derivation and implementation.
    """
    y0, y1, y2, y3 = current
    c_t = (y3 - A * y0) % Q
    if c_t >= A:
        return None

    y_minus1, c_tm1 = divmod(c_t * Q + y2, A)
    y_minus2, c_tm2 = divmod(c_tm1 * Q + y1, A)
    y_minus3, c_tm3 = divmod(c_tm2 * Q + y0, A)
    y_minus4, _ = divmod(c_tm3 * Q + y_minus1, A)
    previous = [y_minus4, y_minus3, y_minus2, y_minus1]
    if any(not 0 <= word < Q for word in previous):
        return None

    check, _ = forward(previous, c_tm3, 4)
    if check[4:8] != [y0, y1, y2, y3]:
        return None
    return previous, c_tm3


def serialize(
    words: tuple[int, ...] | list[int], order: tuple[int, ...], flip: int
) -> bytes:
    chunks = [b""] * 4
    for j, index in enumerate(order):
        chunks[index] = words[j].to_bytes(
            4, "little" if flip & (1 << index) else "big"
        )
    return b"".join(chunks)


def late_request_views(packet: bytes):
    """Yield the 384 permutation/per-word-endian interpretations."""
    assert len(packet) == 16
    for order in itertools.permutations(range(4)):
        for flip in range(16):
            words = tuple(
                int.from_bytes(
                    packet[4 * index : 4 * index + 4],
                    "little" if flip & (1 << index) else "big",
                )
                for index in order
            )
            yield order, flip, words


def read_sources(root: Path):
    spool_path = root / "evidence/print/spool-reconstruction.log"
    spool = spool_path.read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA

    selected_ack2 = None
    late_request3 = None
    row_count = 0
    selected_marker = (
        b"JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER "
    )
    request3_re = re.compile(
        rb"JOB=PS-261003-0417 ATTEMPT=3 STATE=REQUESTED CLASS=RECOVER "
        rb"PAYLOAD=([A-F0-9]{32}) DEST=bench"
    )
    for line in spool.splitlines():
        if b" PAYLOAD=" not in line:
            continue
        row_count += 1
        if selected_marker in line:
            # Identify the selected row by metadata only. Do not parse its
            # payload field or feed it to the candidate path.
            assert selected_ack2 is None
            selected_ack2 = True
            continue
        match = request3_re.search(line)
        if match:
            assert late_request3 is None
            late_request3 = bytes.fromhex(match.group(1).decode("ascii"))

    assert row_count == 133 and selected_ack2 and late_request3 is not None

    route_raw = (root / "evidence/recovery-routing.json").read_bytes()
    acceptance_raw = (root / "acceptance.json").read_bytes()
    assert hashlib.sha256(route_raw).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(acceptance_raw).hexdigest() == ACCEPTANCE_SHA
    route = json.loads(route_raw)
    acceptance = json.loads(acceptance_raw)
    mask = bytes.fromhex(route["K04"]["masked_component"])
    commitment = acceptance["slot_sha256"]["K04"]
    assert len(mask) == 16 and len(commitment) == 64
    return late_request3, mask, commitment


def synthetic_positive_control():
    initial = [0x10203040, 0x50607080, 0x90A0B0C0]
    initial_carry = 123456
    stream, _ = forward(initial, initial_carry, 9)
    first_packet = stream[:4]
    second_packet = stream[4:8]
    third_packet = stream[8:12]

    reversed_once = reverse_previous_packet(tuple(third_packet))
    assert reversed_once is not None and reversed_once[0] == second_packet
    reversed_twice = reverse_previous_packet(tuple(reversed_once[0]))
    assert reversed_twice is not None and reversed_twice[0] == first_packet

    synthetic_mask = bytes(range(16))
    target = hashlib.sha256(
        bytes(
            a ^ b
            for a, b in zip(
                b"".join(word.to_bytes(4, "little") for word in first_packet),
                synthetic_mask,
            )
        )
    ).hexdigest()
    recovered_payload = b"".join(
        word.to_bytes(4, "little") for word in reversed_twice[0]
    )
    recovered_component = bytes(
        a ^ b for a, b in zip(recovered_payload, synthetic_mask)
    )
    assert hashlib.sha256(recovered_component).hexdigest() == target

def main():
    root_value = os.environ.get("H17_SOURCE_ROOT")
    root = Path(root_value) if root_value else Path(__file__).resolve().parents[2] / "resources"
    synthetic_positive_control()
    late_packet, mask, commitment = read_sources(root)

    one_back_views = 0
    one_back_packets = set()
    one_back_hits = 0
    two_back_views = 0
    two_back_packets = set()
    two_back_hits = 0
    for order, flip, words in late_request_views(late_packet):
        first = reverse_previous_packet(words)
        if first is None:
            continue
        one_back_views += 1
        one_back_packet = serialize(first[0], order, flip)
        assert len(one_back_packet) == 16
        one_back_packets.add(one_back_packet)
        one_component = bytes(a ^ b for a, b in zip(one_back_packet, mask))
        if hashlib.sha256(one_component).hexdigest() == commitment:
            one_back_hits += 1

        # One additional inverse step is the specific missing-attempt-2
        # alternative: REQUESTED2 body followed by a separate ACK2 event.
        second = reverse_previous_packet(tuple(first[0]))
        if second is None:
            continue
        two_back_views += 1
        two_back_packet = serialize(second[0], order, flip)
        assert len(two_back_packet) == 16
        two_back_packets.add(two_back_packet)
        two_component = bytes(a ^ b for a, b in zip(two_back_packet, mask))
        if hashlib.sha256(two_component).hexdigest() == commitment:
            two_back_hits += 1

    assert one_back_views == 8, one_back_views
    assert len(one_back_packets) == 8, len(one_back_packets)
    assert one_back_hits == 0, one_back_hits
    assert two_back_views == 8, two_back_views
    assert len(two_back_packets) == 8, len(two_back_packets)
    assert two_back_hits == 0, two_back_hits
    print("synthetic_reverse_and_commitment_control=PASS")
    print("late_REQUESTED3_serializer_views=384")
    print("one_packet_back_valid_views=8 distinct_packets=8 K04_hits=0")
    print("two_packets_back_valid_views=8 distinct_packets=8 K04_hits=0")
    print("selected_ACK2_payload_decoded=False")
    print("historical_Alea_producer_or_ACK2_binding=NOT_ESTABLISHED")


if __name__ == "__main__":
    main()
