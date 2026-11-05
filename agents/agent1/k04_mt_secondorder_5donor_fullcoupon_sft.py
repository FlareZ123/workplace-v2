"""H-17 K04 source-pinned MT two-twist five-donor full-coupon SFT.

Run as a Python module/file inside workplace-v2. Read-only: never loads selected
ACK2 bytes, never alters acceptance, resource evidence or canonical candidate.
Depends on the previously committed Agent22 original-source helpers.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import random
import re
import struct
import sys
import zlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "resources" / "evidence"
sys.path.insert(0, str(ROOT / "agents" / "agent22"))
import k04_future_donor_source_syndrome_sft as prior

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
RECORDER_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
ORIGINAL_K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
ORIGINAL_MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TWIST_MAGIC = 0x9908B0DF
BIT30 = 0x40000000


def lmix(x: int) -> int:
    return ((x & 0x7FFFFFFF) >> 1) ^ (TWIST_MAGIC if x & 1 else 0)


def temper(x: int) -> int:
    y = x ^ (x >> 11)
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & 0xFFFFFFFF


def all_original_16byte_carriers() -> dict[bytes, str]:
    """Rebuild the same 532 independently retained source windows as Agent22."""
    carrier: dict[bytes, str] = {}

    def add(label: str, b: bytes) -> None:
        if len(b) == 16:
            carrier.setdefault(b, label)

    for root, _, files in os.walk(ROOT / "resources"):
        for name in files:
            path = Path(root) / name
            relative = path.relative_to(ROOT / "resources").as_posix()
            if relative in ("acceptance.json", "verify.py", "candidate.template.json"):
                continue
            raw = path.read_bytes()
            if relative == "evidence/print/spool-reconstruction.log":
                raw = b"\n".join(
                    line for line in raw.splitlines()
                    if not (b"JOB=PS-261003-0417" in line and b"ATTEMPT=2 STATE=ACK" in line)
                )
            for match in re.finditer(rb"(?<![0-9A-Fa-f])([0-9A-Fa-f]{32})(?![0-9A-Fa-f])", raw):
                add("HEX32:" + relative + ":" + str(match.start()), bytes.fromhex(match[1].decode()))

    raw = (E / "recorder" / "trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == RECORDER_SHA
    records = []
    controls = []
    for i in range(88):
        rec = raw[16 + i * 24:16 + (i + 1) * 24]
        _, node, ev, latch, seq, word, aux, crc = struct.unpack("<IHBBI4sII", rec)
        controls.append(word)
        records.append((node, ev, latch, seq, word))
    for i in range(85):
        add("TRP2:physical:" + str(i), b"".join(controls[i:i + 4]))
    ordered = sorted(records, key=lambda x: (x[0], x[1], x[3], x[2]))
    for i in range(85):
        add("TRP2:sorted:" + str(i), b"".join(x[4] for x in ordered[i:i + 4]))
    for node, ev in sorted({x[:2] for x in records}):
        cohort = sorted((x for x in records if x[:2] == (node, ev)), key=lambda x: x[3])
        for i in range(len(cohort) - 3):
            add(f"TRP2:node{node}:event{ev}:{i}", b"".join(x[4] for x in cohort[i:i + 4]))

    text = (E / "procedures" / "RC-17-scans.txt").read_text()
    foot = []
    for page in text.split("\f"):
        match = re.search(r"Footer control strip:\s*([0-9A-F]{8})", page)
        if match:
            revision = re.search(r"DOCUMENT RC-17 / REV ([^/]+) / SECTION ([^\n]+)", page)
            foot.append((revision[1].strip(), revision[2].strip(), bytes.fromhex(match[1])))
    for i in range(len(foot) - 3):
        add("RC17:scan:" + str(i), b"".join(x[2] for x in foot[i:i + 4]))
    for rev in sorted({x[0] for x in foot}):
        parts = {section: b for r, section, b in foot if r == rev}
        if len(parts) == 4:
            add("RC17:" + rev + ":service", b"".join(parts[k] for k in ("DRAIN", "ISOLATE", "PURGE", "VERIFY")))
            add("RC17:" + rev + ":alpha", b"".join(parts[k] for k in sorted(parts)))

    telemetry = [json.loads(line) for line in (E / "telemetry" / "freeze-export.jsonl").read_text().splitlines()]
    cohorts = {
        "ALL": [x for x in telemetry if x.get("field") == "DIAG_WORD"],
        "LT204": [x for x in telemetry if x.get("tag") == "LT-204" and x.get("field") == "DIAG_WORD"],
        "GOODHOLD": [x for x in telemetry if x.get("tag") == "LT-204" and x.get("field") == "DIAG_WORD" and x.get("quality") == "GOOD" and x.get("state") == "HOLD"]
    }
    for key, cohort in cohorts.items():
        for order, rows in (
            ("source", cohort),
            ("seq", sorted(cohort, key=lambda x: (x["seq"], x["revision"]))),
            ("time", sorted(cohort, key=lambda x: x["ts"]))
        ):
            words = [int(x["value"]).to_bytes(2, "big") for x in rows if isinstance(x.get("value"), int) and 0 <= x["value"] <= 65535]
            for i in range(len(words) - 7):
                add(f"TELEMETRY:{key}:{order}:{i}", b"".join(words[i:i + 8]))

    seals = [json.loads(line) for line in (E / "maintenance" / "seal-receipts.jsonl").read_text().splitlines()]
    source = [(x["permit"], x["bay"], x["serial"].split("-")[-1]) for x in seals]
    for i in range(len(source) - 3):
        add("SEAL:source:" + str(i), b"".join(bytes.fromhex(x[2]) for x in source[i:i + 4]))
    for permit in sorted({x[0] for x in source}):
        vals = sorted((x for x in source if x[0] == permit), key=lambda x: x[1])
        for i in range(len(vals) - 3):
            add(f"SEAL:{permit}:{i}", b"".join(bytes.fromhex(x[2]) for x in vals[i:i + 4]))

    accepted = {
        "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
        "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
        "K03": "1384AF96E25D6ADA666209CB55E062FA",
        "K05": "FF8B78200A56E8586DCDA00EF01E4572",
        "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
        "K07": "93495F5E425AB8E592123DABAEB68545"
    }
    for k, value in accepted.items():
        add("DERIVED:" + k, bytes.fromhex(value))
    for name, b in prior.groups().items():
        add("SELECTED:" + name, b)

    assert len(carrier) == 532, len(carrier)
    return carrier


def fourword_views(carriers: dict[bytes, str]) -> dict[tuple[int, int, int, int], str]:
    results = {}
    for blob, source in carriers.items():
        for little, untempered, reverse in itertools.product((False, True), repeat=3):
            value = tuple(prior.decode(blob, little, untempered, reverse, "all"))
            results.setdefault(value, source)
    assert len(results) == 4256, len(results)
    return results


def gap_field_views() -> dict[int, str]:
    gap = {}
    raw = (E / "recorder" / "trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == RECORDER_SHA
    for i in range(88):
        record = raw[16 + i * 24:16 + (i + 1) * 24]
        if zlib.crc32(record[:20]) != struct.unpack_from("<I", record, 20)[0]:
            continue
        _, node, event, latch, seq = struct.unpack_from("<IHBBI", record)
        word = record[12:16]
        for endian, is_native in itertools.product(("little", "big"), (False, True)):
            value = int.from_bytes(word, endian)
            gap.setdefault(prior.untemper(value) if is_native else value, f"TRP2:{node}:{event}:{seq}:{latch}:{endian}:{is_native}")
    text = (E / "procedures" / "RC-17-scans.txt").read_text()
    for i, hexword in enumerate(re.findall(r"Footer control strip:\s*([0-9A-F]{8})", text)):
        word = bytes.fromhex(hexword)
        for endian, is_native in itertools.product(("little", "big"), (False, True)):
            value = int.from_bytes(word, endian)
            gap.setdefault(prior.untemper(value) if is_native else value, f"RC17:{i}:{endian}:{is_native}")
    for name, blob in prior.groups().items():
        for little, is_native, reverse in itertools.product((False, True), repeat=3):
            for word in prior.decode(blob, little, is_native, reverse, "all"):
                gap.setdefault(word, "SELECTED:" + name)
    assert len(gap) == 448, len(gap)
    return gap


def original_test() -> None:
    spool = (E / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    routing = json.loads((E / "recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources" / "acceptance.json").read_text())
    assert bytes.fromhex(routing["K04"]["masked_component"]) == ORIGINAL_MASK
    assert acceptance["slot_sha256"]["K04"] == ORIGINAL_K04_SHA
    copied_0417 = [line for line in spool.decode().splitlines() if "JOB=PS-261003-0417" in line and "ATTEMPT=2 STATE=ACK" in line]
    assert len(copied_0417) == 1
    # Never decode the disputed selected line.
    rows = [x for x in spool.decode().splitlines() if "PAYLOAD=" in x]
    assert len(rows) == 133
    def output(row: int, lane: int) -> int:
        field = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", rows[row])[1])
        return prior.untemper(int.from_bytes(field[lane * 4:lane * 4 + 4], "little"))
    # Provenance: hypothetical chronology assigns row73=>x556, row104=>x782.
    assert "JOB=PS-261003-0373 " in rows[73]
    assert "JOB=PS-261003-0404 " in rows[104]
    early = tuple(output(73, i) for i in (0, 1, 2))
    middle = tuple(output(104, i) for i in (0, 1, 2, 3))
    future = fourword_views(all_original_16byte_carriers())
    gap = gap_field_views()
    target = bytes.fromhex(ORIGINAL_K04_SHA)
    checks, matches = 0, []
    gap_mix = {x: lmix(x) for x in gap}

    for donor, name in future.items():
        base0 = donor[0] ^ lmix(middle[0])
        base_later = tuple(
            donor[i + 1] ^ lmix(early[i]) ^ lmix(middle[i + 1])
            for i in range(3)
        )
        suffixes = []
        for bits in range(8):
            words = tuple(x ^ (BIT30 if bits & (1 << i) else 0) for i, x in enumerate(base_later))
            raw = b"".join(temper(x).to_bytes(4, "little") for x in words)
            suffixes.append(bytes(a ^ b for a, b in zip(raw, ORIGINAL_MASK[4:])))
        for x555, mix in gap_mix.items():
            for high in (0, BIT30):
                raw = temper(base0 ^ mix ^ high).to_bytes(4, "little")
                head = bytes(a ^ b for a, b in zip(raw, ORIGINAL_MASK[:4]))
                for tail in suffixes:
                    checks += 1
                    component = head + tail
                    if hashlib.sha256(component).digest() == target:
                        matches.append((name, gap[x555], component.hex().upper()))
    assert checks == 4256 * 448 * 16
    print("ORIGINAL_COMPLETE_K04_CANDIDATES", checks, "HITS", len(matches))
    assert not matches, matches


def true_seeded_controls() -> None:
    for seed in (0, 7, 1983, 20261003, 0xDEADBEEF):
        rng = random.Random(seed)
        native = [prior.untemper(rng.getrandbits(32)) for _ in range(1409)]
        base = [
            native[1405 + i] ^ lmix(native[555 + i]) ^ lmix(native[782 + i])
            for i in range(4)
        ]
        reconstructed = [
            tuple(word ^ (BIT30 if flags & (1 << i) else 0) for i, word in enumerate(base))
            for flags in range(16)
        ]
        assert reconstructed.count(tuple(native[951:955])) == 1
    print("TRUE_SEEDED_FULLCOUPON_CONTROLS", 5, "PASS")


if __name__ == "__main__":
    true_seeded_controls()
    original_test()
