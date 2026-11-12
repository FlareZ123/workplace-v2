"""Test source-derived 16-byte donor blocks against the unique p951 gap pair.

Run from the repository root:
    python agents/agent43/k04_unique_gap_source_block_pair_sft.py

The p951 source builder withholds the selected printer row before parsing its
payload. This script never reads that payload, the K04 mask, or the K04
commitment until all source-block candidate payloads have been generated.
"""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import itertools
import json
import re
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "resources" / "evidence"
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    "p951_basis", ROOT / "agents" / "agent49" / "k04_p951_symbolic_basis.py"
)
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)

# This is the unique pair identified by Agent 50's source-only gap-pair SFT.
GAP_STARTS = (328, 724)
TARGET_START = 951
BAY_ORDER = ("B", "D", "A", "C")


def read_blocks():
    route = json.loads((E / "recovery-routing.json").read_text())
    blocks = {}

    # K01: four WN-14 ink groups in letter order, recovered across mail.
    groups = {}
    for path in sorted((E / "mail").glob("*.eml")):
        text = path.read_text(errors="replace")
        for match in re.finditer(
            r"WN-14\s*/\s*group\s+([A-D])\s*/\s*([0-9A-F]{8})", text
        ):
            groups[match.group(1)] = match.group(2)
    assert set(groups) == set("ABCD")
    blocks["K01_WN14_ABCD"] = b"".join(bytes.fromhex(groups[k]) for k in "ABCD")

    # K02: the eight selected LT-204 DIAG_WORD values, unsigned 16-bit big-endian.
    k02 = route["K02"]
    start = datetime.fromisoformat(k02["start_utc"])
    end = datetime.fromisoformat(k02["end_utc_exclusive"])
    samples = {}
    for line in (E / "telemetry" / "freeze-export.jsonl").read_text().splitlines():
        row = json.loads(line)
        ts = datetime.fromisoformat(row["ts"])
        if (row.get("tag") == "LT-204" and row.get("field") == "DIAG_WORD"
                and row.get("quality") == "GOOD" and row.get("state") == "HOLD"
                and start <= ts < end):
            seq = row["seq"]
            if seq not in samples or row["revision"] > samples[seq]["revision"]:
                samples[seq] = row
    assert set(samples) == set(range(8))
    blocks["K02_LT204_SEQ0_7"] = b"".join(
        int(samples[i]["value"]).to_bytes(2, "big") for i in range(8)
    )

    # K03: four selected PTW-417 as-left serial suffix words in closeout order.
    seals = [
        json.loads(line)
        for line in (E / "maintenance" / "seal-receipts.jsonl").read_text().splitlines()
    ]
    selected = {}
    for row in seals:
        if (row.get("permit") == "PTW-417" and row.get("state") == "CLOSED"
                and row.get("fitment") == "AS_LEFT" and row.get("signed")):
            bay = row["bay"]
            old = selected.get(bay)
            if old is None or row["revision"] > old["revision"] or (
                row["revision"] == old["revision"] and "asset" in row
            ):
                selected[bay] = row
    assert all(selected[bay]["revision"] == 2 for bay in BAY_ORDER)
    blocks["K03_PTW417_BDAC"] = b"".join(
        bytes.fromhex(selected[bay]["serial"].split("-")[-1]) for bay in BAY_ORDER
    )

    # K05: four CRC-valid node49/event82 control words, greatest seq per latch.
    raw = (E / "recorder" / "trip-recorder.raw").read_bytes()
    magic, version, record_size, count = struct.unpack_from("<8sHHI", raw, 0)
    assert (magic, version, record_size) == (b"TRP2DUMP", 2, 24)
    k05 = route["K05"]
    start = datetime.fromisoformat(k05["start_utc"])
    end = datetime.fromisoformat(k05["end_utc_exclusive"])
    controls = {}
    for i in range(count):
        rec = raw[16 + i*24:16 + (i+1)*24]
        utc, node, event, latch, seq, control, aux, crc = struct.unpack(
            "<I H B B I 4s I I", rec
        )
        if zlib.crc32(rec[:20]) & 0xffffffff != crc:
            continue
        ts = datetime.fromtimestamp(utc, timezone.utc)
        if node == k05["node"] and event == k05["event"] and start <= ts < end:
            old = controls.get(latch)
            if old is None or seq > old[0]:
                controls[latch] = (seq, control)
    assert set(controls) == set(range(4))
    blocks["K05_TRP2_LATCH0123"] = b"".join(controls[i][1] for i in range(4))

    # K06: all RC-17 revision blocks in the service_order recorded in archive-labels.ini.
    ini = (E / "archive-labels.ini").read_text()
    order_match = re.search(r"(?im)^\\s*service_order\\s*=\\s*([A-Z, \\t]+)$", ini)
    assert order_match is not None
    service_order = tuple(part.strip().upper() for part in order_match.group(1).split(","))
    assert len(service_order) == 4
    rc = (E / "procedures" / "RC-17-scans.txt").read_text()
    strips = {}
    pattern = (
        r"DOCUMENT RC-17 / REV (B|C|D-draft) / SECTION "
        r"(DRAIN|ISOLATE|PURGE|VERIFY).*?Footer control strip: ([0-9A-F]{8})"
    )
    for match in re.finditer(pattern, rc, re.S):
        strips[(match.group(1), match.group(2))] = match.group(3)
    for revision in ("B", "C", "D-draft"):
        assert all((revision, section) in strips for section in service_order)
        blocks[f"RC17_{revision}_SERVICE"] = b"".join(
            bytes.fromhex(strips[(revision, section)]) for section in service_order
        )

    # K07: committed AX-7782 chain, greatest attempt per chunk sequence.
    audit = [
        json.loads(line)
        for line in (E / "transfers" / "transfer-audit.jsonl").read_text().splitlines()
    ]
    commit = next(
        row for row in audit
        if row["kind"] == "COMMIT" and row.get("dry_run") is False
    )
    transfer = commit["transfer"]
    chunks = [row for row in audit if row["kind"] == "CHUNK" and row["transfer"] == transfer]
    checkpoints = []
    for seq in range(8):
        choices = [row for row in chunks if row["seq"] == seq]
        chosen = max(choices, key=lambda row: row["attempt"])
        checkpoints.append(bytes.fromhex(chosen["checkpoint"]))
    blocks["K07_AX7782_SEQ0_7"] = b"".join(checkpoints)

    # Additional PTW-417 revision-history blocks. Revision 2 duplicates K03;
    # revisions 1, 3 and 4 are retained as source-derived controls.
    for revision in (1, 3, 4):
        by_bay = {}
        for row in seals:
            if row.get("permit") == "PTW-417" and row.get("revision") == revision:
                if revision == 1 and "asset" not in row:
                    continue
                by_bay[row["bay"]] = row
        assert set(by_bay) == set("ABCD")
        blocks[f"PTW417_REV{revision}_BDAC"] = b"".join(
            bytes.fromhex(by_bay[bay]["serial"].split("-")[-1]) for bay in BAY_ORDER
        )

    # The K03 block and PTW revision 2 are identical; retain only one.
    assert len(blocks) == 11, list(blocks)
    assert len({value for value in blocks.values()}) == 11
    return route, blocks


def reduce_source(rows, value, rhs=0):
    remainder = 0
    while value:
        pivot = value.bit_length() - 1
        if pivot in rows:
            vector, bit = rows[pivot]
            value ^= vector
            rhs ^= bit
        else:
            remainder |= 1 << pivot
            value ^= 1 << pivot
    return remainder, rhs


def insert_small(rows, value, rhs):
    while value:
        pivot = value.bit_length() - 1
        if pivot not in rows:
            rows[pivot] = (value, rhs)
            return True
        vector, bit = rows[pivot]
        value ^= vector
        rhs ^= bit
    return rhs == 0


def reduce_small(rows, value, rhs=0):
    while value:
        pivot = value.bit_length() - 1
        if pivot not in rows:
            return value, rhs
        vector, bit = rows[pivot]
        value ^= vector
        rhs ^= bit
    return 0, rhs


def main():
    route, blocks = read_blocks()
    basis, symbolic = mt.source(ROOT)
    assert basis.rank == 15365

    donor_stages = (
        list(range(GAP_STARTS[0], GAP_STARTS[0] + 4))
        + list(range(GAP_STARTS[1], GAP_STARTS[1] + 4))
    )
    donor_forms = {
        stage: [reduce_source(basis.rows, expr) for expr in mt.get(symbolic, stage)]
        for stage in donor_stages
    }
    target_forms = [
        reduce_source(basis.rows, expr)
        for stage in range(TARGET_START, TARGET_START + 4)
        for expr in mt.temper(mt.get(symbolic, stage))
    ]
    assert len(target_forms) == 128

    interpretations = {}
    for name, block in blocks.items():
        interpretations[name] = {}
        for endian in ("little", "big"):
            for representation in ("tempered", "native"):
                words = []
                for lane in range(4):
                    word = int.from_bytes(block[4*lane:4*lane+4], endian)
                    words.append(mt.untemper(word) if representation == "tempered" else word)
                interpretations[name][(endian, representation)] = words

    complete = 0
    inconsistent = 0
    underdetermined = 0
    candidates = []
    names = list(blocks)
    for name_a, name_b in itertools.combinations(names, 2):
        for endian_a in ("little", "big"):
            for rep_a in ("tempered", "native"):
                for endian_b in ("little", "big"):
                    for rep_b in ("tempered", "native"):
                        for swapped in (False, True):
                            assigned = (
                                (name_b, endian_b, rep_b, name_a, endian_a, rep_a)
                                if swapped else
                                (name_a, endian_a, rep_a, name_b, endian_b, rep_b)
                            )
                            first_name, first_endian, first_rep, second_name, second_endian, second_rep = assigned
                            small = {}
                            valid = True
                            for block_index, (name, endian, rep) in enumerate((
                                (first_name, first_endian, first_rep),
                                (second_name, second_endian, second_rep),
                            )):
                                words = interpretations[name][(endian, rep)]
                                for lane, native in enumerate(words):
                                    stage = donor_stages[block_index*4 + lane]
                                    for bit, (residual, offset) in enumerate(donor_forms[stage]):
                                        if not insert_small(small, residual, ((native >> bit) & 1) ^ offset):
                                            valid = False
                                            break
                                    if not valid:
                                        break
                                if not valid:
                                    break
                            if not valid:
                                inconsistent += 1
                                continue

                            payload = bytearray()
                            fixed = True
                            for lane in range(4):
                                word = 0
                                for bit in range(32):
                                    residual, offset = target_forms[lane*32 + bit]
                                    residual, value = reduce_small(small, residual, offset)
                                    if residual:
                                        fixed = False
                                        break
                                    word |= value << bit
                                if not fixed:
                                    break
                                payload.extend(word.to_bytes(4, "little"))
                            if not fixed:
                                underdetermined += 1
                                continue
                            complete += 1
                            candidates.append((
                                first_name, first_endian, first_rep,
                                second_name, second_endian, second_rep,
                                bytes(payload),
                            ))

    assert complete == 1760, (complete, inconsistent, underdetermined)
    assert inconsistent == 0 and underdetermined == 0

    # Candidate generation is complete before consulting K04's mask/commitment.
    mask = bytes.fromhex(route["K04"]["masked_component"])
    acceptance = json.loads((ROOT / "resources" / "acceptance.json").read_text())
    target_hash = acceptance["slot_sha256"]["K04"]
    hits = []
    for label in candidates:
        payload = label[-1]
        component = bytes(a ^ b for a, b in zip(payload, mask))
        if hashlib.sha256(component).hexdigest() == target_hash:
            hits.append(label[:-1] + (payload.hex().upper(), component.hex().upper()))

    assert hits == [], hits
    print(json.dumps({
        "source_blocks": list(blocks),
        "distinct_blocks": len(blocks),
        "gap_pair": GAP_STARTS,
        "target_payload_stages": [TARGET_START, TARGET_START+1, TARGET_START+2, TARGET_START+3],
        "candidate_models": complete,
        "inconsistent_models": inconsistent,
        "underdetermined_models": underdetermined,
        "K04_commitment_hits": hits,
        "new_K04_bits_recovered": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
