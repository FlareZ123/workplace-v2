"""H-17 K04 Philox4x32-10 source-calibrated emitter trial.

Usage: python agents/agent16/k04_philox_source_keys_sft.py <repository-root>
All input records and original verifier/commitments are read-only.
The original source does not attest a Philox printer generator.
"""
import hashlib
import json
import re
import struct
import sys
from datetime import datetime
from pathlib import Path

MASK32 = (1 << 32) - 1
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ACK2 = "A9A9DC5731A5E2AE879C47215C2559D5"
K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"


def philox(counter, key):
    """Official Random123 Philox4x32-10, 4 x u32 counter, 2 x u32 key."""
    c0, c1, c2, c3 = counter
    k0, k1 = key
    for _ in range(10):
        a = 0xD2511F53 * c0
        b = 0xCD9E8D57 * c2
        c0, c1, c2, c3 = (
            ((b >> 32) ^ c1 ^ k0) & MASK32, b & MASK32,
            ((a >> 32) ^ c3 ^ k1) & MASK32, a & MASK32,
        )
        k0 = (k0 + 0x9E3779B9) & MASK32
        k1 = (k1 + 0xBB67AE85) & MASK32
    return c0, c1, c2, c3


def serialize(words):
    return tuple(struct.pack(endian, *sequence)
                 for sequence in (words, words[::-1])
                 for endian in ("<4I", ">4I"))


def counter(row, index, form):
    clock = row["datetime"]
    epoch = int(clock.timestamp())
    minute = clock.hour * 60 + clock.minute
    job = row["job"]
    attempt = row["attempt"]
    klass = {"LABEL": 1, "STORES": 2, "RECOVER": 3}[row["class"]]
    dest = {"store": 1, "bench": 2, "desk": 3}[row["dest"]]
    choices = (
        (index, 0, 0, 0), (index + 1, 0, 0, 0),
        (job, 0, 0, 0), (epoch, 0, 0, 0),
        (minute, 0, 0, 0), (job, attempt, klass, dest),
        (index, job, attempt, 0), (epoch, job, attempt, klass),
    )
    return tuple(x & MASK32 for x in choices[form])


def originals(root):
    # Two published Random123 known-answer vectors.
    assert serialize(philox((0, 0, 0, 0), (0, 0)))[0].hex() == (
        "d5e827668dc569e14cac57bcd8db009b"
    )
    assert serialize(philox((1, 0, 0, 0), (0, 0)))[0].hex() == (
        "a4cce4f8db00b25ceb74a5b167ff7e09"
    )
    source = (root / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SPOOL_SHA
    route = json.loads((root / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "resources/acceptance.json").read_text())
    candidate = json.loads((root / "candidate.json").read_text())
    assert acceptance["slot_sha256"]["K04"] == K04_SHA
    assert route["K04"]["masked_component"] == "8556C8CB6140A7F9A5123AC7571BEE1C"
    rows = []
    pat = re.compile(
        r"(?P<when>\S+) JOB=PS-261003-(?P<job>\d+) "
        r"ATTEMPT=(?P<attempt>\d+) STATE=(?P<state>\S+) "
        r"CLASS=(?P<class>\S+) PAYLOAD=(?P<payload>[0-9A-F]{32}) "
        r"DEST=(?P<dest>\S+)"
    )
    for line in source.decode().splitlines():
        m = pat.fullmatch(line)
        if m is None:
            continue
        row = m.groupdict()
        row["datetime"] = datetime.fromisoformat(row["when"])
        row["job"] = int(row["job"])
        row["attempt"] = int(row["attempt"])
        row["payload"] = bytes.fromhex(row["payload"])
        rows.append(row)
    assert len(rows) == 133
    selections = [
        (i, r) for i, r in enumerate(rows)
        if r["job"] == 417 and r["attempt"] == 2
        and r["state"] == "ACK" and r["class"] == "RECOVER"
    ]
    assert len(selections) == 1
    index, selected = selections[0]
    assert index == 129 and selected["payload"].hex().upper() == ACK2
    accepted = ("K01", "K02", "K03", "K05", "K06", "K07")
    assert all(hashlib.sha256(bytes.fromhex(candidate[k])).hexdigest()
               == acceptance["slot_sha256"][k] for k in accepted)
    source16 = [bytes.fromhex(candidate[k]) for k in accepted]
    source16 += [
        bytes.fromhex(route["K04"]["masked_component"]),
        bytes.fromhex(route["K08"]["desk_nonce"]),
    ]
    keys = []
    for data in source16:
        left, right = data[:8], data[8:]
        for octets in (
            left, right, bytes(a ^ b for a, b in zip(left, right)),
            hashlib.sha256(data).digest()[:8],
        ):
            keys += [struct.unpack("<2I", octets), struct.unpack(">2I", octets)]
    assert len(keys) == len(set(keys)) == 64
    return rows, index, selected, keys, bytes.fromhex(route["K04"]["masked_component"])


def main(root):
    rows, selected_index, selected, keys, mask = originals(root)
    source_positions = (0, 3, 43, 84, 127)
    target = bytes.fromhex(K04_SHA)
    source_hits = []
    selected_hits = []
    # Candidate generator geometry is selected without consulting ACK2's content.
    for key_index, key in enumerate(keys):
        for form in range(8):
            for layout in range(4):
                for idx in source_positions:
                    value = serialize(philox(counter(rows[idx], idx, form), key))[layout]
                    if value == rows[idx]["payload"]:
                        source_hits.append((key_index, form, layout, idx))
                payload = serialize(philox(counter(selected, selected_index, form), key))[layout]
                component = bytes(a ^ b for a, b in zip(payload, mask))
                if hashlib.sha256(component).digest() == target:
                    selected_hits.append((key_index, form, layout, component.hex().upper()))
    # Synthetic full-packet source calibration and exact real-path commitment control.
    key_index, form, layout = 5, 6, 3
    source_witness = tuple(
        serialize(philox(counter(rows[i], i, form), keys[key_index]))[layout]
        for i in source_positions
    )
    payload_witness = serialize(
        philox(counter(selected, selected_index, form), keys[key_index])
    )[layout]
    synthetic_digest = hashlib.sha256(
        bytes(a ^ b for a, b in zip(payload_witness, mask))
    ).digest()
    synthetic_source_hits = 0
    synthetic_target_hits = 0
    for key in keys:
        for f in range(8):
            for v in range(4):
                if tuple(serialize(philox(counter(rows[i], i, f), key))[v]
                         for i in source_positions) == source_witness:
                    synthetic_source_hits += 1
                payload = serialize(philox(counter(selected, selected_index, f), key))[v]
                if hashlib.sha256(bytes(a ^ b for a, b in zip(payload, mask))).digest() == synthetic_digest:
                    synthetic_target_hits += 1
    print(f"source_records={len(rows)} selected_index={selected_index}")
    print(f"keys={len(keys)} forms=8 serializers=4 conditions={len(keys)*8*4}")
    print(f"five_original_controls={source_positions}")
    print(f"source_hits={len(source_hits)} original_K04_hits={len(selected_hits)}")
    print(f"synthetic_source_hits={synthetic_source_hits} synthetic_target_hits={synthetic_target_hits}")
    assert not source_hits and not selected_hits
    assert synthetic_source_hits == synthetic_target_hits == 1
    print("PASS BOUNDED NO_MATCH: authentic K04 still unresolved")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("."))
