"""H-17 K04 whole-source carrier byte-pad reconstruction, read-only SFT.

Run in a checkout with the original h17-archive-dump.zip path as argument.
Uses the original K04 SHA256 target and fixed mask without mutating them.
"""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ZIP_SHA = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
COPIED = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def plusbyte(a, b, sign):
    return bytes((x + sign * y) & 255 for x, y in zip(a, b))


def fixed_carriers(source):
    with zipfile.ZipFile(source) as z:
        files = {x.filename: z.read(x) for x in z.infolist() if not x.is_dir()}
    assert len(files) == 46
    spool = files["evidence/print/spool-reconstruction.log"]
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    marker = b"2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD="
    assert spool.count(marker) == 1
    assert bytes.fromhex(spool.split(marker, 1)[1][:32].decode("ascii")) == COPIED
    assert json.loads(files["acceptance.json"])["slot_sha256"]["K04"].lower() == TARGET.hex()
    assert bytes.fromhex(json.loads(files["evidence/recovery-routing.json"])["K04"]["masked_component"]) == MASK
    values = set()
    n_raw = n_hex = 0
    for data in files.values():
        for offset in range(max(0, len(data) - 15)):
            values.add(data[offset:offset + 16])
            n_raw += 1
        for match in re.finditer(rb"[0-9A-Fa-f]{32,}", data):
            group = match.group()
            for offset in range(len(group) - 31):
                values.add(bytes.fromhex(group[offset:offset + 32].decode("ascii")))
                n_hex += 1
    assert (n_raw, n_hex, len(values)) == (117583, 892, 67470)
    return values


def candidates(donor):
    """Yield 32 (family, fully reduced 16-byte candidate) pairs."""
    source_component = xor(COPIED, MASK)
    yield "xor-pad component", xor(source_component, donor)
    yield "xor-pad mask", xor(COPIED, donor)
    yield "plus-byte physical", xor(plusbyte(COPIED, donor, 1), MASK)
    yield "minus-byte physical", xor(plusbyte(COPIED, donor, -1), MASK)
    yield "plus-byte component", plusbyte(source_component, donor, 1)
    yield "minus-byte component", plusbyte(source_component, donor, -1)
    for phase, base in (("physical", COPIED), ("component", source_component)):
        for sign, verb in ((1, "plus"), (-1, "minus")):
            for endian in ("big", "little"):
                n = (int.from_bytes(base, endian) + sign * int.from_bytes(donor, endian)) & ((1 << 128) - 1)
                result = n.to_bytes(16, endian)
                yield f"{verb}-128 {endian} {phase}", xor(result, MASK) if phase == "physical" else result
            for endian in ("big", "little"):
                words = []
                for k in range(0, 16, 4):
                    n = (int.from_bytes(base[k:k+4], endian) + sign * int.from_bytes(donor[k:k+4], endian)) & 0xffffffff
                    words.append(n.to_bytes(4, endian))
                result = b"".join(words)
                yield f"{verb}-word32 {endian} {phase}", xor(result, MASK) if phase == "physical" else result
    for name in ("sha256_first16", "sha256_last16", "sha512_first16", "sha512_last16", "blake2s16"):
        if name == "blake2s16":
            pad = hashlib.blake2s(donor, digest_size=16).digest()
        else:
            method, edge = name.split("_")
            full = hashlib.new(method, donor).digest()
            pad = full[:16] if edge == "first16" else full[-16:]
        yield f"xor-hashpad {name}", xor(source_component, pad)
        yield f"plus-hashpad {name}", plusbyte(source_component, pad, 1)


def run(zip_path):
    assert hashlib.sha256(zip_path.read_bytes()).hexdigest() == ZIP_SHA
    values = fixed_carriers(zip_path)
    prior_mask = {xor(COPIED, x) for x in values}
    prior_direct = {xor(MASK, x) for x in values}
    all_generated = set()
    per_family = {}
    target_hits = []
    positive_donor = bytes.fromhex("FBBBC54356483F5864BB3F06794518A5")
    assert positive_donor in values
    synthetic_hash = hashlib.sha256(xor(xor(COPIED, MASK), positive_donor)).digest()
    positives = 0
    assignments = 0
    for donor in values:
        for family, candidate in candidates(donor):
            assignments += 1
            per_family[family] = per_family.get(family, 0) + 1
            all_generated.add(candidate)
            digest = hashlib.sha256(candidate).digest()
            if digest == TARGET:
                target_hits.append({"family": family, "donor": donor.hex().upper(),
                                    "component": candidate.hex().upper()})
            if family == "xor-pad component" and digest == synthetic_hash:
                positives += 1
                assert donor == positive_donor
    assert len(per_family) == 32 and assignments == 2159040
    assert len(all_generated) == 1943265
    assert not target_hits and positives == 1
    print(json.dumps({
        "original_zip_sha256": ZIP_SHA,
        "carrier_values": len(values),
        "operations": len(per_family),
        "complete_assignments": assignments,
        "distinct_full_k04_components": len(all_generated),
        "distinct_new_beyond_two_prior_carrier_stages": len(all_generated - (prior_mask | prior_direct)),
        "original_k04_matches": target_hits,
        "synthetic_planted_full_component_hits": positives,
    }, indent=2))


if __name__ == "__main__":
    run(Path(sys.argv[1]))
