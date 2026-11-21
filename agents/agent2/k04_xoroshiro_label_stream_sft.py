"""Target-blind K04 constructor: same-job LABEL ACK -> RECOVER packet stream.

Hypothesis: the four chronological PS-0417 packets are four consecutive
16-byte outputs from one xoroshiro128++ stream:
  0 LABEL/ACK attempt 1 (known)
  1 RECOVER/REQUESTED attempt 1 (known)
  2 RECOVER/ACK attempt 2 (withheld; proposed coupon)
  3 RECOVER/REQUESTED attempt 3 (known)

Each packet contains two consecutive native 64-bit outputs. The selected ACK2
payload is deliberately not read or used as a solver constraint. The model is
source-motivated but unverified; only the untouched K04 commitment can promote
a unique complete 16-byte middle packet to a candidate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path

os.environ["BTORMODELGEN"] = "1"
os.environ["BTORINCREMENTAL"] = "1"

import pyboolector

ROOT = Path(__file__).resolve().parents[2]
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK64 = (1 << 64) - 1
KNOWN_POSITIONS = (0, 1, 2, 3, 6, 7)
PLANTED_STATE = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)


def rol(x: int, n: int) -> int:
    return ((x << n) | (x >> (64 - n))) & MASK64


def stream(state: tuple[int, int], count: int = 8) -> list[int]:
    a, b = state
    result = []
    for _ in range(count):
        result.append((rol((a + b) & MASK64, 17) + a) & MASK64)
        t = a ^ b
        a = (rol(a, 49) ^ t ^ (t << 21)) & MASK64
        b = rol(t, 28)
    return result


def decode_packet(payload: bytes, view: int) -> tuple[int, int]:
    if len(payload) != 16 or view not in range(4):
        raise ValueError("invalid packet or serializer view")
    parts = [payload[:8], payload[8:]]
    if view & 2:
        parts.reverse()
    endian = "little" if view & 1 else "big"
    return tuple(int.from_bytes(part, endian) for part in parts)


def encode_packet(words: tuple[int, int], view: int) -> bytes:
    if view not in range(4):
        raise ValueError("invalid serializer view")
    ordered = list(words[::-1] if view & 2 else words)
    endian = "little" if view & 1 else "big"
    return b"".join(word.to_bytes(8, endian) for word in ordered)


def solve_unique(known: dict[int, int]) -> dict:
    if set(known) != set(KNOWN_POSITIONS):
        raise ValueError(f"expected known output positions {KNOWN_POSITIONS}")

    bt = pyboolector.Boolector()
    initial_a = bt.Var(bt.BitVecSort(64), "initial_s0")
    first_output = known[0]
    # Invert y0 = rotl(s0+s1,17)+s0 to eliminate s1 exactly.
    initial_b = (
        bt.Ror(bt.Const(first_output, 64) - initial_a, 17) - initial_a
    )

    a, b = initial_a, initial_b
    outputs = []
    for _ in range(8):
        outputs.append(bt.Rol(a + b, 17) + a)
        t = a ^ b
        a, b = bt.Rol(a, 49) ^ t ^ (t << 21), bt.Rol(t, 28)

    for position, expected in known.items():
        bt.Assert(outputs[position] == bt.Const(expected, 64))

    started = time.monotonic()
    status = bt.Sat()
    elapsed = round(time.monotonic() - started, 3)
    if status == bt.UNSAT:
        return {"status": "UNSAT", "solve_seconds": elapsed}
    if status != bt.SAT:
        return {"status": "UNKNOWN", "solve_seconds": elapsed, "solver_code": int(status)}

    state = (
        int(initial_a.assignment, 2),
        int(initial_b.assignment, 2),
    )
    generated = stream(state)
    if any(generated[i] != known[i] for i in KNOWN_POSITIONS):
        raise AssertionError("Boolector model failed native replay")
    middle = (generated[4], generated[5])

    # Block the entire predicted 128-bit middle packet, not merely the state.
    bt.Assert(
        (outputs[4] != bt.Const(middle[0], 64))
        | (outputs[5] != bt.Const(middle[1], 64))
    )
    started = time.monotonic()
    alternate_status = bt.Sat()
    alternate_elapsed = round(time.monotonic() - started, 3)
    if alternate_status == bt.UNSAT:
        unique = True
        alternative = None
    elif alternate_status == bt.SAT:
        unique = False
        alternative = (
            int(outputs[4].assignment, 2),
            int(outputs[5].assignment, 2),
        )
    else:
        unique = None
        alternative = None

    return {
        "status": "SAT",
        "unique_middle": unique,
        "middle_words": middle,
        "alternative_middle": alternative,
        "solve_seconds": elapsed,
        "uniqueness_seconds": alternate_elapsed,
    }


def extract_line(lines: list[str], prefix: str) -> str:
    matches = [line for line in lines if line.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(f"expected one source row for {prefix!r}, found {len(matches)}")
    return matches[0]


def metadata(line: str) -> dict[str, str]:
    result = {}
    for token in line.split()[1:]:
        if "=" not in token or token.startswith("PAYLOAD="):
            continue
        key, value = token.split("=", 1)
        result[key] = value
    return result


def payload(line: str) -> bytes:
    match = re.search(r"\bPAYLOAD=([0-9A-F]{32})\b", line)
    if not match:
        raise ValueError("required intact source payload is absent")
    return bytes.fromhex(match.group(1))


def source_packets() -> tuple[bytes, bytes, bytes, dict]:
    path = ROOT / "resources/evidence/print/spool-reconstruction.log"
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SPOOL_SHA256:
        raise ValueError(f"original spool SHA256 mismatch: {digest}")
    lines = raw.decode("ascii").splitlines()

    label = extract_line(lines, "2026-10-03T16:45:00+00:00 ")
    request1 = extract_line(lines, "2026-10-03T18:01:00Z ")
    ack2 = extract_line(lines, "2026-10-03T18:02:00Z ")
    request3 = extract_line(lines, "2026-10-03T18:03:00Z ")

    expected = (
        (label, {"JOB": "PS-261003-0417", "ATTEMPT": "1", "STATE": "ACK",
                 "CLASS": "LABEL", "DEST": "bench"}),
        (request1, {"JOB": "PS-261003-0417", "ATTEMPT": "1", "STATE": "REQUESTED",
                    "CLASS": "RECOVER", "DEST": "bench"}),
        (ack2, {"JOB": "PS-261003-0417", "ATTEMPT": "2", "STATE": "ACK",
                "CLASS": "RECOVER", "DEST": "bench"}),
        (request3, {"JOB": "PS-261003-0417", "ATTEMPT": "3", "STATE": "REQUESTED",
                    "CLASS": "RECOVER", "DEST": "bench"}),
    )
    for line, required in expected:
        fields = metadata(line)  # PAYLOAD is explicitly excluded.
        if any(fields.get(key) != value for key, value in required.items()):
            raise ValueError(f"PS-0417 event metadata mismatch: {required}")

    # The ACK2 line is checked for identity/status only. Its PAYLOAD field is
    # never extracted, parsed, or passed to the solver.
    return payload(label), payload(request1), payload(request3), {
        "spool_sha256": digest,
        "label_ack1_timestamp": "2026-10-03T16:45:00+00:00",
        "recover_request1_timestamp": "2026-10-03T18:01:00Z",
        "recover_ack2_timestamp": "2026-10-03T18:02:00Z",
        "recover_request3_timestamp": "2026-10-03T18:03:00Z",
        "selected_ack2_payload_used": False,
    }


def load_k04() -> tuple[bytes, str]:
    route = json.loads(
        (ROOT / "resources/evidence/recovery-routing.json").read_text()
    )
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    commitment = acceptance["slot_sha256"]["K04"]
    if len(mask) != 16:
        raise ValueError("K04 route mask is not 16 bytes")
    return mask, commitment


def positive_control(view: int) -> dict:
    outputs = stream(PLANTED_STATE)
    known = {position: outputs[position] for position in KNOWN_POSITIONS}
    result = solve_unique(known)
    if result["status"] != "SAT" or result["unique_middle"] is not True:
        raise AssertionError(f"planted source-stream control did not solve uniquely: {result}")
    if result["middle_words"] != (outputs[4], outputs[5]):
        raise AssertionError("planted middle packet was not recovered exactly")
    return {
        "status": "PASS",
        "view": view,
        "known_output_positions": list(KNOWN_POSITIONS),
        "unique_middle": True,
        "planted_middle": [f"{x:016X}" for x in result["middle_words"]],
        "solve_seconds": result["solve_seconds"],
        "uniqueness_seconds": result["uniqueness_seconds"],
    }


def run_source(view: int) -> dict:
    label, request1, request3, source_meta = source_packets()
    known = {}
    for packet_index, packet in ((0, label), (1, request1), (3, request3)):
        first, second = decode_packet(packet, view)
        known[packet_index * 2] = first
        known[packet_index * 2 + 1] = second

    result = solve_unique(known)
    output = {
        "model": "same-job LABEL_ACK1 -> RECOVER_REQUEST1 -> RECOVER_ACK2 -> RECOVER_REQUEST3 xoroshiro128++ stream",
        "view": view,
        "known_output_positions": list(KNOWN_POSITIONS),
        "source": source_meta,
        "solver_status": result["status"],
        "solve_seconds": result.get("solve_seconds"),
    }
    if result["status"] != "SAT":
        if result["status"] == "UNKNOWN":
            output["solver_code"] = result.get("solver_code")
        return output

    output["unique_middle"] = result["unique_middle"]
    output["uniqueness_seconds"] = result["uniqueness_seconds"]
    if result["unique_middle"] is not True:
        output["disposition"] = "NON_UNIQUE_OR_UNKNOWN_MIDDLE"
        return output

    coupon = encode_packet(result["middle_words"], view)
    mask, commitment = load_k04()
    component = bytes(a ^ b for a, b in zip(coupon, mask))
    digest = hashlib.sha256(component).hexdigest()
    output["predicted_coupon_sha256"] = hashlib.sha256(coupon).hexdigest()
    output["predicted_component_sha256"] = digest
    output["K04_commitment_match"] = digest == commitment
    if digest == commitment:
        output["disposition"] = "COMPLETE_K04_CANDIDATE"
        output["coupon"] = coupon.hex().upper()
        output["component"] = component.hex().upper()
    else:
        output["disposition"] = "UNIQUE_COMPLETE_OUTPUT_HASH_MISS"
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--view", type=int, choices=range(4), required=True)
    parser.add_argument("--control-only", action="store_true")
    parser.add_argument("--result-path", type=Path)
    args = parser.parse_args()

    if args.control_only:
        result = {"positive_control": positive_control(args.view)}
    else:
        result = run_source(args.view)

    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.result_path:
        args.result_path.write_text(rendered + "\n")
    print(rendered, flush=True)


if __name__ == "__main__":
    main()
