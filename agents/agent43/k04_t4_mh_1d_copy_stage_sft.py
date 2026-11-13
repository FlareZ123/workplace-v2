#!/usr/bin/env python3
"""Bounded K04 candidate: CCITT T.4 Group-3 1D Modified-Huffman line decode."""
import argparse, hashlib, json, random, re
from pathlib import Path
from itertools import product

EOL = "000000000001"
WTERM = """00110101 000111 0111 1000 1011 1100 1110 1111
10011 10100 00111 01000 001000 000011 110100 110101
101010 101011 0100111 0001100 0001000 0010111 0000011 0000100
0101000 0101011 0010011 0100100 0011000 00000010 00000011 00011010
00011011 00010010 00010011 00010100 00010101 00010110 00010111 00101000
00101001 00101010 00101011 00101100 00101101 00000100 00000101 00001010
00001011 01010010 01010011 01010100 01010101 00100100 00100101 01011000
01011001 01011010 01011011 01001010 01001011 00110010 00110011 00110100""".split()
BTERM = """0000110111 010 11 10 011 0011 0010 00011
000101 000100 0000100 0000101 0000111 00000100 00000111 000011000
0000010111 0000011000 0000001000 00001100111 00001101000 00001101100 00000110111 00000101000
00000010111 00000011000 000011001010 000011001011 000011001100 000011001101 000001101000 000001101001
000001101010 000001101011 000011010010 000011010011 000011010100 000011010101 000011010110 000011010111
000001101100 000001101101 000011011010 000011011011 000001010100 000001010101 000001010110 000001010111
000001100100 000001100101 000001010010 000001010011 000000100100 000000110111 000000111000 000000100111
000000101000 000001011000 000001011001 000000101011 000000101100 000000101101 000000110010 000000110011""".split()
assert len(WTERM) == len(BTERM) == 64
W = {code:(n,False) for n,code in enumerate(WTERM)}
B = {code:(n,False) for n,code in enumerate(BTERM)}
W.update({"11011":(64,True), "10010":(128,True)})
B.update({"0000001111":(64,True), "000011001000":(128,True)})

def decode_run(bits, pos, table):
    total = 0
    while True:
        found = None
        for end in range(pos+1, min(len(bits),pos+13)+1):
            entry = table.get(bits[pos:end])
            if entry is not None:
                found = entry, end
                break
        if found is None: return None
        (run, makeup), pos = found
        total += run
        if not makeup: return total, pos

def decode_line(bits):
    pos, color, pixels = 0, 0, []
    while len(pixels) < 128:
        result = decode_run(bits, pos, B if color else W)
        if result is None: return None
        run, pos = result
        if run > 128-len(pixels): return None
        pixels.extend([color]*run)
        color ^= 1
    return (pixels,pos) if len(pixels) == 128 else None

def bits_of(data, lsb):
    return "".join(f"{b:08b}"[::-1] if lsb else f"{b:08b}" for b in data)

def pack_pixels(pixels, black_one, lsb_pack):
    values = [p if black_one else 1-p for p in pixels]
    out = bytearray()
    for i in range(0,128,8):
        group = values[i:i+8]
        if lsb_pack: group.reverse()
        out.append(int("".join(map(str,group)),2))
    return bytes(out)

def frame_variants(payload):
    # TIFF/T.4 framing only: byte order, FillOrder, optional EOL(s), <=7 zero fill/pad bits.
    for revbytes, lsbfill in product((False,True), repeat=2):
        raw = payload[::-1] if revbytes else payload
        bits = bits_of(raw, lsbfill)
        for pre, post in product((False,True), repeat=2):
            for pf in (range(8) if pre else (0,)):
                prefix = ("0"*pf + EOL) if pre else ""
                if not bits.startswith(prefix): continue
                body = bits[len(prefix):]
                for sf in (range(8) if post else (0,)):
                    suffix = ("0"*sf + EOL) if post else ""
                    for pad in range(8):
                        tail = suffix + "0"*pad
                        if tail and not body.endswith(tail): continue
                        encoded = body[:-len(tail)] if tail else body
                        decoded = decode_line(encoded)
                        if decoded is None: continue
                        pixels, used = decoded
                        if used != len(encoded): continue
                        spec = (revbytes,lsbfill,pre,pf,post,sf,pad)
                        for black_one,lsbpack in product((False,True),repeat=2):
                            yield spec+(black_one,lsbpack), pack_pixels(pixels,black_one,lsbpack)

def encode_run(n, terms, m64, m128):
    out = ""
    while n >= 128: out += m128; n -= 128
    while n >= 64: out += m64; n -= 64
    return out + terms[n]

def encode_line(pixels, eol=True):
    bits = EOL if eol else ""
    color, i = 0, 0
    while i < 128:
        j = i
        while j < 128 and pixels[j] == color: j += 1
        run = j-i
        if color == 0: bits += encode_run(run,WTERM,"11011","10010")
        else: bits += encode_run(run,BTERM,"0000001111","000011001000")
        i, color = j, color ^ 1
    bits += "0"*((-len(bits))%8)
    return bytes(int(bits[i:i+8],2) for i in range(0,len(bits),8))

def selftest():
    rng = random.Random(20261113)
    for n in range(256):
        pixels = [rng.randrange(2) for _ in range(128)]
        encoded = encode_line(pixels, eol=(n%2==0))
        bits = bits_of(encoded,False)
        if n%2==0:
            assert bits.startswith(EOL)
            bits = bits[len(EOL):]
        decoded = decode_line(bits)
        assert decoded is not None and decoded[0] == pixels, (n,encoded.hex())
        assert set(bits[decoded[1]:]) <= {"0"} and len(bits[decoded[1]:]) <= 7
    # Independent Pillow/libtiff Group-3 strip fixture: 128 pixels in alternating 8-pixel runs.
    fixture = bytes.fromhex("00198b31662cc598b31662cc50")
    fixture_bits = bits_of(fixture,False)
    assert fixture_bits.startswith(EOL)
    fixture_decoded = decode_line(fixture_bits[len(EOL):])
    assert fixture_decoded is not None
    assert fixture_decoded[0] == ([0]*8+[1]*8)*8
    assert fixture_bits[len(EOL)+fixture_decoded[1]:] == "0000"
    print("synthetic_mh_1d_roundtrips=256 PASS")
    print("independent_Pillow_libtiff_G3_fixture PASS")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--selftest",action="store_true")
    ap.add_argument("--root",type=Path,default=Path("resources"))
    args=ap.parse_args()
    if args.selftest: selftest(); return
    ev=args.root/"evidence"
    files={
        "spool":(ev/"print/spool-reconstruction.log").read_bytes(),
        "note":(ev/"crew/noticeboard-and-desk-notes.txt").read_bytes(),
        "route":(ev/"recovery-routing.json").read_bytes(),
        "acceptance":(args.root/"acceptance.json").read_bytes()
    }
    pins={
        "spool":"7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
        "note":"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
        "route":"f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
        "acceptance":"681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
    }
    for name,raw in files.items(): assert hashlib.sha256(raw).hexdigest()==pins[name],name
    assert b"label printer has spent another morning thinking it is a fax machine" in files["note"]
    route=json.loads(files["route"]); acceptance=json.loads(files["acceptance"])
    mask=bytes.fromhex(route["K04"]["masked_component"])
    target=acceptance["slot_sha256"]["K04"]
    lines=files["spool"].decode("ascii").splitlines()
    selected=[x for x in lines if "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in x]
    assert len(selected)==1
    m=re.search(r"\bPAYLOAD=([0-9A-F]{32})\b",selected[0]); assert m
    payload=bytes.fromhex(m.group(1))
    assert payload.hex()=="a9a9dc5731a5e2ae879c47215c2559d5"
    candidates={}
    framing_count=0
    for spec,coupon in frame_variants(payload):
        framing_count+=1
        candidates.setdefault(coupon,spec)
    hits=[]
    for coupon,spec in candidates.items():
        component=bytes(a^b for a,b in zip(coupon,mask))
        if hashlib.sha256(component).hexdigest()==target:
            hits.append({"spec":spec,"coupon":coupon.hex().upper(),"component":component.hex().upper()})
    print(json.dumps({
        "source_pins":pins,"selected_payload":payload.hex().upper(),
        "valid_framing_assignments":framing_count,
        "unique_complete_128_pixel_candidates":len(candidates),
        "K04_commitment_hits":hits,
        "scope":"one-line 128-pixel T.4 Group-3 1D Modified-Huffman only; no 2D, arbitrary bit edits, or source authentication"
    },indent=2))

if __name__=="__main__": main()
