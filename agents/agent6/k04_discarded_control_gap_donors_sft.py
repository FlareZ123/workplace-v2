"""K04 complete two-gap donor test using original nonselected discarded records.

Increment relative to the existing 186 whole-source-carrier gap test:
CRC-rejected TRP2 node49 event82 seq900..903 (both source orders)
and withdrawn/unissued RC-17 rev B/D footer quartets. The true selected
ACK2 copied buffer is never admitted as a source donor.
"""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent12"))
import k04_future_quartet_sourcecarriers_sft as prior

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
PROC_SHA = "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d"
K04_HASH = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"


def original_extra(read):
    raw = read("evidence/recorder/trip-recorder.raw")
    assert hashlib.sha256(raw).hexdigest() == REC_SHA
    assert raw[:8] == b"TRP2DUMP"
    _, size, count = struct.unpack_from("<HHI", raw, 8)
    assert size == 24 and count == 88
    bad = []
    for i in range(count):
        packet = raw[16 + 24*i:16 + 24*(i+1)]
        crc = zlib.crc32(packet[:20])
        actual = int.from_bytes(packet[20:24], "little")
        if crc == actual:
            continue
        _, node, event, latch, seq = struct.unpack_from("<IHBBI", packet)
        assert (node, event, seq - 900, actual ^ crc) == (49, 82, latch, 0x100)
        bad.append((seq, latch, i, packet[12:16]))
    assert sorted(x[0] for x in bad) == [900, 901, 902, 903]
    assert sorted(x[1] for x in bad) == [0, 1, 2, 3]
    source = {
        "CRC-invalid seq900..903": b"".join(x[3] for x in sorted(bad)),
        "CRC-invalid raw-file order": b"".join(x[3] for x in sorted(bad, key=lambda x: x[2])),
    }

    raw = read("evidence/procedures/RC-17-scans.txt")
    assert hashlib.sha256(raw).hexdigest() == PROC_SHA
    for revision in ("B", "D-draft"):
        groups = {}
        for page in raw.decode("utf-8").split("\f"):
            header = re.search(r"DOCUMENT RC-17 / REV (.*?) / SECTION (DRAIN|ISOLATE|PURGE|VERIFY)", page)
            strip = re.search(r"Footer control strip: ([A-F0-9]{8})", page)
            if header and header.group(1) == revision:
                assert strip is not None
                groups[header.group(2)] = bytes.fromhex(strip.group(1))
        assert len(groups) == 4
        source["RC17 " + revision + " four-page controls"] = b"".join(
            groups[section] for section in ("DRAIN", "ISOLATE", "PURGE", "VERIFY")
        )
    assert len(source) == 4 and len(set(source.values())) == 4
    return source


def make_candidate(anchor, gap_a, gap_b, mask):
    native = []
    preceding = anchor
    for a, b in zip(gap_a, gap_b):
        native.append(b ^ prior.twist(preceding, a))
        preceding = a
    return bytes(x ^ y for x, y in zip(prior.encode(native), mask))


def seeded_whole_coupon_positive():
    rng = __import__("random").Random(20261111)
    words = [prior.untemper(rng.getrandbits(32)) for _ in range(955)]
    actual = prior.encode(words[951:955])
    assert actual == prior.encode([
        words[724 + j] ^ prior.twist(words[327] if j == 0 else words[327 + j],
                                    words[328 + j])
        for j in range(4)
    ])


def main():
    with prior.DirectoryReader(ROOT / "resources") as record:
        old = prior.source_carriers(record)
        assert len(old) == 186
        new = original_extra(record.read)
        spool = record.read("evidence/print/spool-reconstruction.log")
        assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
        row43 = [row for row in spool.splitlines()
                 if b"JOB=PS-261003-0343 " in row]
        assert len(row43) == 1
        packet = bytes.fromhex(re.search(rb"PAYLOAD=([A-F0-9]{32})", row43[0]).group(1).decode())
        anchor = prior.untemper(int.from_bytes(packet[12:16], "little"))
        assert anchor == 0x59E4D0B9
        route = json.loads(record.read("evidence/recovery-routing.json"))
        mask = bytes.fromhex(route["K04"]["masked_component"])
        target = json.loads((ROOT/"resources/acceptance.json").read_text())["slot_sha256"]["K04"]
        assert target == K04_HASH

    seeded_whole_coupon_positive()
    assert not any(blob in old for blob in new.values())
    all_sources = dict(old)
    for label, blob in new.items():
        all_sources[blob] = label
    assert len(all_sources) == 190

    old_view = [(name, words) for blob, name in old.items() for words in prior.layouts(blob)]
    new_view = [(name, words) for name, blob in new.items() for words in prior.layouts(blob)]
    assert len(old_view) == 1488 and len(new_view) == 32

    planted = make_candidate(anchor, new_view[0][1], old_view[0][1], mask)
    planted_hash = hashlib.sha256(planted).digest()
    expected_hash = bytes.fromhex(target)
    tested = authentic = planted_found = 0
    match = []
    for a_name, a_words in new_view:
        for b_name, b_words in old_view + new_view:
            if a_name == b_name:
                continue
            for x, y, names in ((a_words, b_words, (a_name, b_name)),
                                (b_words, a_words, (b_name, a_name))):
                candidate = make_candidate(anchor, x, y, mask)
                result = hashlib.sha256(candidate).digest()
                tested += 1
                if result == planted_hash:
                    planted_found += 1
                if result == expected_hash:
                    authentic += 1
                    match.append((names, candidate.hex().upper()))
    assert tested == 96768  # source/view order assignments with self-pair removal
    assert planted_found >= 1
    print("K04_DISCARDED_SOURCE_GAP_CANDIDATES",
          "original_carriers", len(old),
          "new_carriers", len(new),
          "full_components_checked", tested,
          "original_hits", authentic,
          "planted_full_positive", planted_found,
          "genuine_mt19937_control", "PASS")
    for names, component in match:
        print("ORIGINAL_K04_COMPONENT", names, component)


if __name__ == "__main__":
    main()
