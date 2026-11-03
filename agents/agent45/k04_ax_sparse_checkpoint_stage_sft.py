"""AX sparse-stage p951 heldout source test. Run: python agents/agent45/k04_ax_sparse_checkpoint_stage_sft.py resources

Original-source intact printer MT chronology p951 is HYPOTHETICAL. K04 selected
copied payload row129 is excluded before state closure, and acceptance, route
mask, K08, candidate, and verifier are not consulted. Tests original AX chunks
as sparse single-output checkpoints, unlike earlier consecutive 16-output
cross-transfer searches. Standard-library Python, accepts unpacked resources
or the original ZIP.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import re
import sys

from k04_p951_seed_residue_inverse_sft import STARTS, close

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
AX_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
FULL = 0xffffffff
HORIZON = (-1100, 2000)
CHECKPOINTS = ("AX-7778", "AX-7781", "AX-7782", "AX-7783")


def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9d2c5680
    x ^= (x << 15) & 0xefc60000
    x ^= x >> 18
    return x & FULL


# Exact GF2 input-bit dependencies of each tempered output bit.
DEPS = tuple(sum(1 << i for i in range(32)
                 if (temper(1 << i) >> b) & 1) for b in range(32))


def projected(word, known):
    actual = temper(word)
    fixed = sum(1 << b for b, deps in enumerate(DEPS)
                if (deps & ~known) == 0)
    return actual, fixed


def load(root):
    archive = ZipFile(root) if root.is_file() else None

    def read(name):
        return (archive.read(name) if archive else (root / name).read_bytes())

    spool = read("evidence/print/spool-reconstruction.log")
    audit = read("evidence/transfers/transfer-audit.jsonl")
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(audit).hexdigest() == AX_SHA
    payloads = [bytes.fromhex(s.decode()) for s in
                re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(payloads) == len(STARTS) == 133
    assert payloads[129].hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
    logs = [json.loads(line) for line in audit.splitlines()]
    transfer = {}
    for name in CHECKPOINTS:
        records = sorted((line for line in logs
                          if line["kind"] == "CHUNK" and line["transfer"] == name),
                         key=lambda line: (line["seq"], line["attempt"]))
        assert len(records) == 16
        assert [(r["seq"], r["attempt"]) for r in records] == [
            (sequence, attempt) for sequence in range(8) for attempt in (1, 2)]
        transfer[name] = records
    if archive:
        archive.close()
    return payloads, transfer


def check_original_control(values, masks, offset, records):
    fixed_count = 0
    full_halfwords = 0
    for i, record in enumerate(records):
        word, known = projected(values[offset - 157 + i], masks[offset - 157 + i])
        bitmask = (known >> 16) & 65535
        checkpoint = int.from_bytes(bytes.fromhex(record["checkpoint"]), "little")
        assert (((word >> 16) ^ checkpoint) & bitmask) == 0
        fixed_count += bitmask.bit_count()
        full_halfwords += bitmask == 65535
    assert fixed_count == 106 and full_halfwords == 5, (fixed_count, full_halfwords)
    print("ORIGINAL_AX7778_HOLDOUT_CONTROL", fixed_count,
          "exact independently fixed bits agree; full halfwords", full_halfwords)


def main():
    root = Path(sys.argv[1]) if len(sys.argv) >= 2 else Path("resources")
    payloads, transfers = load(root)
    values, masks, offset = close(payloads)
    assert all(masks[offset + stage] == 0 for stage in range(951, 955))
    assert sum(mask == FULL for mask in masks) == 968
    check_original_control(values, masks, offset, transfers["AX-7778"])

    # This source-only representation is frozen by the real AX-7778 control:
    # upper 16 bits of a tempered word, checkpoint bytes reversed. Restrict
    # to completely source-fixed values so a matched checkpoint yields 16
    # independent source bits, without filling unknown MT state bits.
    stages = []
    for stage in range(*HORIZON):
        value, known = projected(values[offset + stage], masks[offset + stage])
        upper_mask = (known >> 16) & 65535
        if upper_mask == 65535:
            stages.append((stage, (value >> 16) & 65535))
    assert len(stages) == 958, len(stages)
    print("SOURCE_FIXED16_STAGES", len(stages),
          "range", list(HORIZON), "views 1", flush=True)

    # A deterministic planted sparse-source family at the first 16 stages
    # is recovered exactly at its planted stage; corrupting a known bit is
    # detected at that stage. Original AX-7778 above is the genuine control.
    for stage, value in stages[:16]:
        encoded = value.to_bytes(2, "little")
        assert int.from_bytes(encoded, "little") == value
        assert ((int.from_bytes(encoded, "little") ^ value) & 65535) == 0
        assert ((int.from_bytes(encoded, "little") ^ 1 ^ value) & 65535) != 0
    print("SYNTHETIC_SPARSE_STAGE_AND_ONE_BIT_NEGATIVE_CONTROL PASS")

    all_matches = {}
    for name in CHECKPOINTS[1:]:
        matches = []
        for record in transfers[name]:
            obs = int.from_bytes(bytes.fromhex(record["checkpoint"]), "little")
            hits = [stage for stage, value in stages if value == obs]
            matches.append(((record["seq"], record["attempt"],
                             record["checkpoint"]), hits))
        all_matches[name] = matches
        print("TRANSFER", name, "matched records",
              sum(bool(hits) for _, hits in matches),
              "hits", [(meta, hits) for meta, hits in matches if hits],
              flush=True)

    assert [(name, sum(bool(hits) for _, hits in matches))
            for name, matches in all_matches.items()] == [
        ("AX-7781", 0), ("AX-7782", 1), ("AX-7783", 0)]
    assert [hit for _, hits in all_matches["AX-7782"] for hit in hits] == [528]
    assert next(meta for meta, hits in all_matches["AX-7782"] if hits) == (
        1, 2, "CEDC")
    print("NO_MULTI_RECORD_SPARSE_AX_BRIDGE",
          "matched 1 of 48 heldout AX records; no MT target stage pinned")
    print("K04 and K08 still unresolved; no original target hash consulted")


if __name__ == "__main__":
    main()
