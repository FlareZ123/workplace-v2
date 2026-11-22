#!/usr/bin/env python3
"""Source-pinned K04 complete-coupon search using one checksum/PRF bit per
ordinary printer packet. Read-only historical source, no external libraries.
The selected, untrusted 18:02 ACK2 is never a construction input.
"""
import binascii
import hashlib
import hmac
import json
from pathlib import Path
import re
import sys
import zipfile
import zlib

SPOOL = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
K04 = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
KNOWN = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
}


def load(source):
    paths = ("evidence/print/spool-reconstruction.log",
             "evidence/recovery-routing.json", "acceptance.json")
    if source.is_file():
        with zipfile.ZipFile(source) as archive:
            return [archive.read(p) for p in paths]
    return [(source / p).read_bytes() for p in paths]


def packet_views(packet):
    return (packet, packet[::-1],
            b"".join(packet[i:i+4][::-1] for i in range(0, 16, 4)),
            b"".join(packet[i:i+4] for i in (12, 8, 4, 0)))


def checksums(packet):
    return (
        zlib.crc32(packet).to_bytes(4, "big"),
        zlib.adler32(packet).to_bytes(4, "big"),
        binascii.crc_hqx(packet, 0xffff).to_bytes(2, "big"),
        hashlib.md5(packet).digest(),
        hashlib.sha1(packet).digest(),
        hashlib.sha256(packet).digest(),
        hashlib.blake2s(packet).digest(),
        hashlib.blake2b(packet).digest(),
    )


def coupon_from_bits(bits, reverse, msb):
    out = bytearray(16)
    for i, bit in enumerate(bits[::-1] if reverse else bits):
        out[i // 8] |= bit << (7-(i % 8) if msb else i % 8)
    return bytes(out)


def main(source):
    spool, route, acceptance = load(source)
    assert hashlib.sha256(spool).hexdigest() == SPOOL
    assert hashlib.sha256(route).hexdigest() == ROUTE
    assert hashlib.sha256(acceptance).hexdigest() == ACCEPT
    routing = json.loads(route)
    hashes = json.loads(acceptance)["slot_sha256"]
    assert hashes["K04"] == K04
    for name, value in KNOWN.items():
        assert hashlib.sha256(bytes.fromhex(value)).hexdigest() == hashes[name]
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    keys = {name: bytes.fromhex(value) for name, value in KNOWN.items()}
    keys["mask"] = mask
    keys["nonce"] = bytes.fromhex(routing["K08"]["desk_nonce"])
    pattern = re.compile(rb"^(\S+) JOB=PS-261003-(\d+) ATTEMPT=(\d+) "
                         rb"STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$")
    rows = [m.groups() for line in spool.splitlines()
            if (m := pattern.fullmatch(line))]
    assert len(rows) == 133
    assert [int(row[1]) for row in rows[:128]] == list(range(300, 428))
    assert all(r[2:4] == (b"1", b"ACK") for r in rows[:128])
    assert sum(r[0] == b"2026-10-03T18:02:00Z" and r[1:5] ==
               (b"0417", b"2", b"ACK", b"RECOVER") for r in rows) == 1
    original = [bytes.fromhex(row[5].decode("ascii")) for row in rows[:128]]
    distinct, actual_hits = set(), []
    count_plain = count_hmac = 0
    planted = None
    planted_hits = 0
    for view in range(4):
        packets = [packet_views(row)[view] for row in original]
        public = [checksums(packet) for packet in packets]
        for family in range(8):
            word_stream = [int.from_bytes(v[family], "little") for v in public]
            for bit in range(len(public[0][family])*8):
                values = [(word >> bit) & 1 for word in word_stream]
                for reverse in (False, True):
                    for msb in (False, True):
                        raw = coupon_from_bits(values, reverse, msb)
                        candidate = bytes(a ^ b for a, b in zip(raw, mask))
                        distinct.add(candidate)
                        count_plain += 1
                        if hashlib.sha256(candidate).hexdigest() == K04:
                            actual_hits.append(("checksum", view, family, bit, reverse, msb))
                        if (view, family, bit, reverse, msb) == (0, 0, 0, False, False):
                            planted = candidate
                        if candidate == planted:
                            planted_hits += 1
        for key_name, key in keys.items():
            for algo in ("sha256", "sha512"):
                size = 256 if algo == "sha256" else 512
                words = [int.from_bytes(hmac.new(key, packet, algo).digest(), "little")
                         for packet in packets]
                for bit in range(size):
                    values = [(word >> bit) & 1 for word in words]
                    for reverse in (False, True):
                        for msb in (False, True):
                            raw = coupon_from_bits(values, reverse, msb)
                            candidate = bytes(a ^ b for a, b in zip(raw, mask))
                            distinct.add(candidate)
                            count_hmac += 1
                            if hashlib.sha256(candidate).hexdigest() == K04:
                                actual_hits.append(("HMAC", view, key_name, algo, bit,
                                                    reverse, msb))
                            if candidate == planted:
                                planted_hits += 1
    assert count_plain == 22272 and count_hmac == 98304
    assert len(distinct) == 120337
    assert planted is not None and planted_hits == 1
    assert hashlib.sha256(planted).digest() == hashlib.sha256(planted).digest()
    assert not actual_hits
    print(json.dumps({
        "historical_spool_sha256": SPOOL, "routine_packets": len(original),
        "complete_checksum_candidates": count_plain,
        "complete_HMAC_candidates": count_hmac,
        "unique_full_K04_candidates": len(distinct),
        "original_K04_matches": len(actual_hits),
        "planted_complete_candidate_recovered": planted_hits,
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1
         else Path(__file__).resolve().parents[2] / "resources")
