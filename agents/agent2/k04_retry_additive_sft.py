"""Read-only K04 modular-additive retry producer test, 19,440,000 complete candidates.

Input: original evidence/print/spool-reconstruction.log. No evidence mutation.
The hypothetical addition producer is NOT historically authenticated.
"""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SOURCES = (
    ("2026-10-03T16:45:00+00:00", "1", "ACK", "LABEL", "E1E60D5F6B6DD2225FA6D5A2A63AD932"),
    ("2026-10-03T18:01:00Z", "1", "REQUESTED", "RECOVER", "CD3E4F216ADB2FB180DA2AA90B33F7A4"),
    ("2026-10-03T18:02:00Z", "2", "ACK", "RECOVER", "A9A9DC5731A5E2AE879C47215C2559D5"),
    ("2026-10-03T18:03:00Z", "3", "REQUESTED", "RECOVER", "44D53DFC29D7943A95D89371DA58EC64"),
)
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")


def run(spool_path):
    source = Path(spool_path).read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA, "Source SHA mismatch"
    lines = source.decode("ascii").splitlines()
    donors = []
    for timestamp, attempt, state, kind, payload in SOURCES:
        expected = (f"{timestamp} JOB=PS-261003-0417 ATTEMPT={attempt} "
                    f"STATE={state} CLASS={kind} PAYLOAD={payload} ")
        assert sum(line.startswith(expected) for line in lines) == 1, expected
        donors.append(bytes.fromhex(payload))
    choices = []
    for lane in range(4):
        words = [int.from_bytes(d[4 * lane:4 * lane + 4], "little") for d in donors]
        variants = []
        for subset in range(1, 16):
            total = sum(word for idx, word in enumerate(words) if subset & (1 << idx)) & 0xFFFFFFFF
            variants.extend((total.to_bytes(4, "little"), total.to_bytes(4, "big")))
        assert len(variants) == 30
        choices.append(variants)

    plant_order = (2, 0, 3, 1)
    plant_picks = (5, 12, 21, 26)
    plant = b"".join(choices[plant_order[lane]][plant_picks[plant_order[lane]]] for lane in range(4))
    plant_slot = bytes(x ^ y for x, y in zip(plant, MASK))
    plant_digest = hashlib.sha256(plant_slot).digest()

    checked = original_hits = control_hits = 0
    started = time.monotonic()
    for order in itertools.permutations(range(4)):
        lane_options = [
            [bytes(v ^ MASK[4 * pos + j] for j, v in enumerate(word))
             for word in choices[order[pos]]]
            for pos in range(4)
        ]
        for a in lane_options[0]:
            for b in lane_options[1]:
                first8 = a + b
                for c in lane_options[2]:
                    first12 = first8 + c
                    for d in lane_options[3]:
                        candidate = first12 + d
                        digest = hashlib.sha256(candidate).digest()
                        checked += 1
                        if digest == TARGET:
                            original_hits += 1
                            print("K04_ORIGINAL_PASS", candidate.hex().upper(), flush=True)
                        if digest == plant_digest:
                            control_hits += 1
    assert checked == 19_440_000 and control_hits == 1
    result = dict(model="same-job modular retry-sum by 32-bit lane, endian/order",
                  spool_sha256=SOURCE_SHA, assignments=checked,
                  original_hits=original_hits, planted_positive_hits=control_hits,
                  seconds=round(time.monotonic() - started, 3))
    print(json.dumps(result, indent=2))
    return original_hits


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python k04_retry_additive_sft.py PATH_TO_ORIGINAL_SPOOL")
    raise SystemExit(2 if run(sys.argv[1]) else 0)
