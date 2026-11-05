"""Original H17 K04 complete bit-unaligned original carrier search.

Run: python agents/agent3/k04_sourcewide_unaligned_carrier_sft.py
Read-only: source, route, acceptance and canonical key are never modified.
"""
from pathlib import Path
import hashlib
import re
import time

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
P = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
M = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
H = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
REVERSE = bytes(int(f"{x:08b}"[::-1], 2) for x in range(256))
LIMIT = (1 << 128) - 1

def source_streams():
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        yield str(path.relative_to(EVIDENCE)), raw
        for found in re.finditer(rb"(?<![0-9a-fA-F])[0-9a-fA-F]{16,}(?![0-9a-fA-F])", raw):
            if len(found.group()) % 2 == 0:
                yield f"{path.relative_to(EVIDENCE)}:hex:{found.start()}", bytes.fromhex(found.group().decode("ascii"))

def windows(raw):
    for bytepos in range(len(raw)-16):
        number = int.from_bytes(raw[bytepos:bytepos+17], "big")
        for shift in range(1, 8):
            yield bytepos, shift, ((number >> (8-shift)) & LIMIT).to_bytes(16, "big")

def make_hash(payload, mask):
    return hashlib.sha256(bytes(x ^ y for x,y in zip(payload,mask))).digest()

def main():
    assert hashlib.sha256((EVIDENCE/"print"/"spool-reconstruction.log").read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    sources = list(source_streams())
    assert len(sources) == 189 and sum(len(v) for _, v in sources) == 114964
    assert make_hash(P, M) != H

    synthetic = b"\xA6" + bytes.fromhex("00112233445566778899AABBCCDDEEFF") + b"\x5A"
    planted_coupon = list(windows(synthetic))[6][2]
    planted_target = make_hash(planted_coupon, M)
    planted_hits = sum(
        make_hash(coupon, M) == planted_target
        for source_view in (synthetic, synthetic.translate(REVERSE))
        for _,_,window in windows(source_view)
        for coupon in (window,window.translate(REVERSE))
    )
    assert planted_hits == 1, planted_hits
    print("SYNTHETIC_COMPLETE_COUPON_POSITIVE", planted_hits, flush=True)

    original_hits = []
    num_windows = num_hashes = 0
    started = time.monotonic()
    for name, source in sources:
        if len(source) < 17:
            continue
        for source_bit_order, byte_view in ((0, source), (1, source.translate(REVERSE))):
            for bytepos, shift, window in windows(byte_view):
                for output_bit_order, value in ((0,window),(1,window.translate(REVERSE))):
                    component = bytes(x ^ y for x,y in zip(value,M))
                    if hashlib.sha256(component).digest() == H:
                        original_hits.append((name,bytepos,shift,source_bit_order,output_bit_order,"coupon",value.hex().upper()))
                    component = bytes(x ^ y for x,y in zip(P,value))
                    if hashlib.sha256(component).digest() == H:
                        original_hits.append((name,bytepos,shift,source_bit_order,output_bit_order,"mask",value.hex().upper()))
                    num_hashes += 2
                num_windows += 1
    assert num_windows == 1567160 and num_hashes == 6268640, (num_windows,num_hashes)
    assert not original_hits, original_hits
    print("SOURCE_STREAMS",len(sources),"BIT_UNALIGNED_WINDOWS",num_windows,"COMPLETE_K04_SHA256",num_hashes,"ORIGINAL_MATCHES",len(original_hits),"SECONDS",round(time.monotonic()-started,2))

if __name__ == "__main__":
    main()
