#!/usr/bin/env python3
"""Source-pinned K04 LABEL→RECOVER pair-stage screen.

Usage:
    python k04_label_recover_pair_sft.py /path/to/h17-archive-dump.zip

This tests whether the two note-aligned LABEL→RECOVER control pairs expose a
shared bytewise copy-stage that predicts PS-0417. The note-to-spool alignment
is an inferred locator, not a source-authenticated foreign key.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import re
import sys
import zipfile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"

def parse_rows(blob: bytes):
    rows = {}
    for line in blob.decode("ascii").splitlines():
        m = re.fullmatch(
            r"(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) "
            r"PAYLOAD=([A-F0-9]{32}) DEST=(\w+)", line)
        if not m:
            continue
        utc, job, attempt, state, klass, payload, dest = m.groups()
        rows[(job[-4:], attempt, state, klass)] = {
            "utc": utc, "job": job, "attempt": int(attempt),
            "state": state, "klass": klass,
            "payload": bytes.fromhex(payload), "dest": dest}
    return rows

def row(rows, suffix, attempt, state, klass, dest):
    x = rows[(suffix, str(attempt), state, klass)]
    assert x["dest"] == dest, (suffix, x["dest"], dest)
    return x

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def common_perm_affine(L1, R1, L2, R2, mode):
    """Find p,c with R[j]=L[p[j]] XOR/+/- c[j] in both control pairs."""
    options = []
    for j in range(16):
        here = []
        for i in range(16):
            if mode == "xor":
                c1, c2 = L1[i] ^ R1[j], L2[i] ^ R2[j]
            elif mode == "add":
                c1, c2 = (R1[j] - L1[i]) & 255, (R2[j] - L2[i]) & 255
            elif mode == "sub":
                c1, c2 = (L1[i] - R1[j]) & 255, (L2[i] - R2[j]) & 255
            else:
                raise ValueError(mode)
            if c1 == c2:
                here.append((i, c1))
        options.append(here)
    solutions = []
    def visit(j, used, perm, constants):
        if j == 16:
            solutions.append((tuple(perm), bytes(constants)))
            return
        for i, c in options[j]:
            if i not in used:
                visit(j + 1, used | {i}, perm + [i], constants + [c])
    visit(0, set(), [], [])
    return [len(x) for x in options], solutions

def bit_permute_byte(value, permutation):
    out = 0
    for out_bit, in_bit in enumerate(permutation):
        out |= ((value >> in_bit) & 1) << out_bit
    return out

def main(path):
    with zipfile.ZipFile(path) as z:
        spool = z.read("evidence/print/spool-reconstruction.log")
        notes = z.read("evidence/crew/noticeboard-and-desk-notes.txt")
        routing = json.loads(z.read("evidence/recovery-routing.json"))
        acceptance = json.loads(z.read("acceptance.json"))
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(notes).hexdigest() == NOTES_SHA
    note_text = notes.decode("utf-8")
    assert "N22 / Simon" in note_text and "fax machine" in note_text
    assert "N23 / Emily" in note_text and "wording in my margin" in note_text

    rows = parse_rows(spool)
    p317 = row(rows, "0317", 1, "ACK", "LABEL", "store")["payload"]
    r318 = row(rows, "0318", 1, "ACK", "RECOVER", "store")["payload"]
    p322 = row(rows, "0322", 1, "ACK", "LABEL", "bench")["payload"]
    r323 = row(rows, "0323", 1, "ACK", "RECOVER", "store")["payload"]
    p417 = row(rows, "0417", 1, "ACK", "LABEL", "bench")["payload"]
    r417 = row(rows, "0417", 2, "ACK", "RECOVER", "bench")["payload"]

    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"].lower()
    d1, d2, dt = xor(p317, r318), xor(p322, r323), xor(p417, r417)
    print("SOURCE_SHA", SPOOL_SHA)
    print("NOTE_SHA", NOTES_SHA)
    print("CONTROL_DESTS", "store->store", "bench->store", "TARGET_DEST", "bench->bench")
    print("XOR_DELTAS", d1.hex().upper(), d2.hex().upper(), dt.hex().upper())
    print("CONTROL_DELTAS_EQUAL", d1 == d2)

    for mode in ("xor", "add", "sub"):
        counts, solutions = common_perm_affine(p317, r318, p322, r323, mode)
        print("COMMON_BYTE_PERM_AFFINE", mode, "per_output_counts", counts,
              "complete_solutions", len(solutions))
        for perm, constants in solutions:
            predicted = bytes(
                (p417[perm[j]] ^ constants[j]) if mode == "xor"
                else ((p417[perm[j]] + constants[j]) & 255) if mode == "add"
                else ((p417[perm[j]] - constants[j]) & 255)
                for j in range(16))
            print("PREDICTED_TARGET", mode, predicted.hex().upper(),
                  "matches_ACK2", predicted == r417)

    bit_hits = []
    for permutation in itertools.permutations(range(8)):
        q1 = bytes(bit_permute_byte(x, permutation) for x in p317)
        q2 = bytes(bit_permute_byte(x, permutation) for x in p322)
        if xor(q1, r318) == xor(q2, r323):
            bit_hits.append((permutation, xor(q1, r318)))
    print("COMMON_PER_BYTE_BIT_PERMUTATION_PLUS_FIXED_XOR",
          "permutations_tested", 40320, "hits", len(bit_hits))

    for name, coupon in (
        ("target_RECOVER", r417), ("target_LABEL", p417),
        ("target_LABEL_XOR_RECOVER", dt),
        ("control1_LABEL_XOR_RECOVER", d1),
        ("control2_LABEL_XOR_RECOVER", d2)):
        digest = hashlib.sha256(xor(coupon, mask)).hexdigest()
        print("K04_COMMITMENT_CHECK", name, digest, "HIT", digest == target)

    print("LIMIT shared byte permutation with fixed per-position XOR/add/sub "
          "constants and shared per-byte bit permutation plus fixed XOR only; "
          "note-to-spool sequence is inferred, controls have different DEST "
          "transitions; no arbitrary fax codec or other transform is excluded.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
