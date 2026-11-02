"""Source-pinned K04 donor test: node50 CRC-valid recorder quartets.

One signed original 16-byte source group supplies three hypothetical future
native MT donor outputs; one of 69 contiguous node50 recorder control-word
quartets supplies four others. Exact original K04 SHA256 decides candidates.
This is a speculative future emission model, not historical authentication.

Run: python agents/agent39/k04_p951_node50_future_donor_sft.py
"""
import hashlib
import importlib.util
import itertools
import json
import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "coupon", ROOT / "agents/agent39/k04_p951_seven_donor_affine_sft.py"
)
coupon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coupon)
REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"


def recorder_quartets():
    source = ROOT / "resources/evidence/recorder/trip-recorder.raw"
    blob = source.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == REC_SHA
    assert blob[:8] == b"TRP2DUMP"
    version, record_size, count = struct.unpack_from("<HHI", blob, 8)
    assert (version, record_size, count) == (2, 24, 88)
    controls = {}
    for n in range(count):
        rec = blob[16 + 24*n:16 + 24*(n+1)]
        assert len(rec) == 24
        if (zlib.crc32(rec[:20]) & 0xffffffff) != struct.unpack_from("<I", rec, 20)[0]:
            continue
        _, node, _, _, seq = struct.unpack_from("<I H B B I", rec)
        if node == 50:
            assert seq not in controls
            controls[seq] = rec[12:16]
    assert sorted(controls) == list(range(72))
    blocks = [
        (start, [controls[start+k] for k in range(4)])
        for start in range(69)
    ]
    assert len(blocks) == 69
    return blocks


def check_historical(coupon_map):
    originals = coupon.preserved_groups()
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    accept = json.loads((ROOT / "resources/acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = bytes.fromhex(accept["slot_sha256"]["K04"])
    found = []
    tested = 0
    blocks = recorder_quartets()
    for family, source in originals.items():
        for take in ("first", "last"):
            for little, retemper, reverse in itertools.product((False, True), repeat=3):
                left = coupon.interpretation(source, little, retemper, reverse, take)
                for seq, recorded in blocks:
                    for right_little, right_tempered, right_reverse in itertools.product((False,True), repeat=3):
                        ordered = recorded[::-1] if right_reverse else recorded
                        right = [
                            (coupon.prior.untemper(value) if right_tempered else value)
                            for value in (
                                int.from_bytes(word, "little" if right_little else "big")
                                for word in ordered
                            )
                        ]
                        native = coupon.select_native(coupon_map, left + right)
                        for output_little in (False, True):
                            payload = b"".join(
                                coupon.temper(x).to_bytes(
                                    4, "little" if output_little else "big"
                                ) for x in native
                            )
                            component = bytes(a ^ b for a,b in zip(payload,mask))
                            tested += 1
                            if hashlib.sha256(component).digest() == target:
                                found.append((family,take,little,retemper,reverse,
                                              seq,right_little,right_tempered,
                                              right_reverse,output_little,
                                              component.hex().upper()))
    assert tested == 105984, tested
    assert found == [], found
    print("Six signed source blocks and 69 CRC-valid node50 quartets:",tested)
    print("Original K04 SHA256 complete-candidate matches:",len(found))


def main():
    expressions = coupon.express()
    coupon.positive_controls(expressions)
    spool = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == coupon.SOURCE_SHA
    fields = re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)
    assert len(fields) == len(coupon.prior.STARTS) == 133
    assert coupon.prior.STARTS[129] == 951
    packets = [
        b"" if i == 129 else bytes.fromhex(value.decode())
        for i,value in enumerate(fields)
    ]
    coupon_map = coupon.make_coupon_map(expressions, packets)
    check_historical(coupon_map)
    print("No independently authenticated K04 selected payload bits.")


if __name__ == "__main__":
    main()
