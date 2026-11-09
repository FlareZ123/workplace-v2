"""Speculative MT624 whole-source coupling: 112 HST PV + 512 printer words.
Run: python agents/agent8/k04_pv112_mt624_directstate_sft.py
Windows 11 and standard library only. The target coupon is excluded from model inputs.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"


def untemper(value: int) -> int:
    def right(y: int, n: int) -> int:
        x = y
        for _ in range(6):
            x = y ^ (x >> n)
        return x & 0xFFFFFFFF

    def left(y: int, n: int, m: int) -> int:
        x = y
        for _ in range(6):
            x = y ^ ((x << n) & m)
        return x & 0xFFFFFFFF

    return right(left(left(right(value, 18), 15, 0xEFC60000),
                      7, 0x9D2C5680), 11)


def predict(words: list[int], length: int = 1024) -> list[int]:
    assert len(words) == 624
    rng = random.Random(19)
    rng.setstate((3, tuple(untemper(w) for w in words) + (624,), None))
    return [rng.getrandbits(32) for _ in range(length)]


def main() -> None:
    spool_bytes = (EVIDENCE / "print" / "spool-reconstruction.log").read_bytes()
    historian_bytes = (EVIDENCE / "telemetry" / "freeze-export.jsonl").read_bytes()
    assert hashlib.sha256(spool_bytes).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    assert hashlib.sha256(historian_bytes).hexdigest() == "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
    routing = json.loads((EVIDENCE / "recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources" / "acceptance.json").read_text())
    assert routing["K04"]["masked_component"] == "8556C8CB6140A7F9A5123AC7571BEE1C"
    target = acceptance["slot_sha256"]["K04"]
    assert target == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
    mask = bytes.fromhex(routing["K04"]["masked_component"])

    spool_lines = [
        line for line in spool_bytes.decode("ascii").splitlines()
        if "PAYLOAD=" in line
    ]
    assert len(spool_lines) == 133
    payloads = [
        bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1))
        for line in spool_lines
    ]
    assert all("ATTEMPT=1" in line and "STATE=ACK" in line
               for line in spool_lines[:128])
    assert "0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in spool_lines[129]
    assert "0448 ATTEMPT=1 STATE=ACK CLASS=RECOVER" in spool_lines[131]
    assert "0420 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in spool_lines[132]

    rows = [json.loads(line) for line in historian_bytes.splitlines()]
    pv = [row for row in rows if row["field"] == "PV"]
    assert len(pv) == 112
    assert len(payloads[:128]) * 4 + len(pv) == 624

    # Genuine Python MT controls: recover all future outputs starting at
    # four arbitrary native stream phases, including a twist boundary.
    for offset in (0, 17, 611, 1000):
        rng = random.Random(0xAC241)
        stream = [rng.getrandbits(32) for _ in range(offset + 660)]
        assert predict(stream[offset:offset + 624], 36) == stream[offset + 624:offset + 660]

    matches: list[dict[str, object]] = []
    target_matches: list[dict[str, object]] = []
    family_count = 0
    for order in ("seq", "timestamp", "file"):
        ordered = (sorted(pv, key=lambda r: r["seq"]) if order == "seq"
                   else sorted(pv, key=lambda r: (r["ts"], r["seq"]))
                   if order == "timestamp" else pv)
        for representation in ("milli", "float32", "raw-int"):
            pv_words = [
                (int(round(float(r["value"]) * 1000))
                 if representation == "milli"
                 else struct.unpack("<I", struct.pack("<f", float(r["value"])))[0]
                 if representation == "float32"
                 else int(round(float(r["value"]))))
                for r in ordered
            ]
            for endian in ("little", "big"):
                for reverse in (False, True):
                    packet_words = []
                    for packet in payloads[:128]:
                        four = [int.from_bytes(packet[j:j + 4], endian)
                                for j in range(0, 16, 4)]
                        packet_words.extend(four[::-1] if reverse else four)
                    for source_order in ("pv-first", "spool-first"):
                        source = (pv_words + packet_words if source_order == "pv-first"
                                  else packet_words + pv_words)
                        outputs = predict(source)
                        family_count += 1
                        for stage in range(len(outputs) - 3):
                            packet = b"".join(
                                int(w).to_bytes(4, endian)
                                for w in (outputs[stage:stage + 4][::-1]
                                          if reverse else outputs[stage:stage + 4])
                            )
                            descriptor = {"PV_order": order, "representation": representation,
                                          "endian": endian, "word_reverse": reverse,
                                          "source_order": source_order, "stage": stage}
                            if packet in (payloads[131], payloads[132]):
                                matches.append({**descriptor, "late_source_index": 131 if packet == payloads[131] else 132})
                            component = bytes(a ^ b for a, b in zip(packet, mask))
                            if hashlib.sha256(component).hexdigest() == target:
                                target_matches.append({**descriptor, "component": component.hex().upper()})

    assert family_count == 72
    print(json.dumps({
        "historian_PV_words": len(pv),
        "printer_native_words": len(payloads[:128]) * 4,
        "MT_state_words": 624,
        "families": family_count,
        "complete_coupon_windows_per_family": 1021,
        "heldout_actual_whole_late_ACK_matches": matches,
        "original_K04_acceptance_matches": target_matches,
        "synthetic_MT_future_controls": "PASS",
        "selected_ACK2_payload_used_as_input": False,
    }, indent=2))


if __name__ == "__main__":
    main()
