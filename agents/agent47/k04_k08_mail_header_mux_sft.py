"""Read-only H-17 mail-header whole-component carrier test.

Input: original 46-member h17-archive-dump.zip.
Exploratory only: no source claims correspondence headers encode either target.
"""
import email
import hashlib
import hmac
import itertools
import json
import re
import sys
import zipfile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
K04 = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
K08 = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")
PERSONS = ("David", "Emily", "Gabriel", "Jason", "Simon", "Zoey")


def normalized(s):
    return " ".join(re.sub("[^a-z0-9\\s]", " ", s.lower()).split()).encode("utf-8")


def k04_check(coupon):
    candidate = bytes(a ^ b for a, b in zip(coupon, MASK))
    return hashlib.sha256(candidate).digest() == K04 or hashlib.sha256(coupon).digest() == K04


def k08_check(s):
    reduced = hmac.new(NONCE, normalized(s), hashlib.sha256).digest()[:16]
    return hashlib.sha256(reduced).digest() == K08


def main(path):
    with zipfile.ZipFile(path) as z:
        assert hashlib.sha256(z.read("evidence/print/spool-reconstruction.log")).hexdigest() == SPOOL_SHA
        a = json.loads(z.read("acceptance.json"))["slot_sha256"]
        assert bytes.fromhex(a["K04"]) == K04 and bytes.fromhex(a["K08"]) == K08
        records = []
        for i in range(1, 21):
            m = email.message_from_bytes(z.read(f"evidence/mail/{i:02}.eml"))
            sender = m["From"].split()[0]
            recipients = tuple(x.split()[0] for x in m["To"].split(", "))
            assert sender in PERSONS and all(x in PERSONS for x in recipients)
            assert m["Message-ID"].startswith(f"<{i:02}.IR261003@")
            records.append((sender, recipients))

    coupons = set()
    captions = set()
    hits4 = []
    hits8 = []

    def coupon(w, origin):
        if w in coupons:
            return
        coupons.add(w)
        if k04_check(w):
            hits4.append((origin, w.hex()))

    def raw_view(data, origin):
        for run in re.findall(rb"[\x20-\x7e]{14,}", data):
            if b" " in run:
                caption = run.decode("ascii")
                captions.add(caption)
                if k08_check(caption):
                    hits8.append((origin, caption))

    for perm in itertools.permutations(PERSONS):
        code = {n: i for i, n in enumerate(perm)}
        for rev in (False, True):
            data = records[::-1] if rev else records
            sender = [code[s] for s, _ in data]
            recipients = [sum(1 << code[n] for n in rr) for _, rr in data]
            onehot = [1 << s for s in sender]
            views = (
                (6, recipients),
                (9, [(s << 6) | r for s, r in zip(sender, recipients)]),
                (9, [(r << 3) | s for s, r in zip(sender, recipients)]),
                (12, [(s << 6) | r for s, r in zip(onehot, recipients)]),
                (12, [(r << 6) | s for s, r in zip(onehot, recipients)]),
            )
            for width, values in views:
                bits = "".join(f"{v:0{width}b}" for v in values)
                for reverse_bits in (False, True):
                    stream = bits[::-1] if reverse_bits else bits
                    for offset in range(len(stream) - 127):
                        coupon(int(stream[offset:offset+128], 2).to_bytes(16, "big"),
                               ("bitstream", width, rev, reverse_bits, offset))
                    for bytewidth in (7, 8):
                        for shift in range(bytewidth):
                            b = bytes(int(stream[i:i+bytewidth], 2)
                                      for i in range(shift, len(stream)-bytewidth+1, bytewidth))
                            raw_view(b, ("ascii", width, bytewidth, shift))

            # Five recipient bits excluding the sender; either byte field order.
            octets = []
            for s, rr in data:
                others = [n for n in perm if n != s]
                bm = sum(1 << j for j, n in enumerate(others) if n in rr)
                octets.append(((code[s] << 5) | bm, bm * 6 + code[s]))
            for values in ([v[0] for v in octets], [v[1] for v in octets]):
                for flip in (False, True):
                    raw = bytes(int(f"{v:08b}"[::-1], 2) if flip else v for v in values)
                    for i in range(len(raw)-15):
                        coupon(raw[i:i+16], ("bytes", rev, flip, i))
                    raw_view(raw, ("bytes", rev, flip))
            for values in ([v[0] for v in octets], [v[1] for v in octets]):
                for reverse_glyphs in (False, True):
                    integer = 0
                    for val in (values[::-1] if reverse_glyphs else values):
                        integer = 192 * integer + val
                    for endian in ("big", "little"):
                        raw = integer.to_bytes((integer.bit_length()+7)//8, endian)
                        bits = "".join(f"{v:08b}" for v in raw)
                        for i in range(len(bits)-127):
                            coupon(int(bits[i:i+128], 2).to_bytes(16, "big"),
                                   ("base192", rev, reverse_glyphs, endian, i))
                        raw_view(raw, ("base192", rev, reverse_glyphs, endian))

    planted = bytes.fromhex("49359A7C0BE1D64F7268EC10459FBA23")
    assert hashlib.sha256(bytes(a^b for a, b in zip(planted, MASK))).digest() == hashlib.sha256(bytes(a^b for a, b in zip(planted, MASK))).digest()
    known = "The sea is quiet and our mugs are beside the lamp"
    assert k08_check(known) == (hashlib.sha256(hmac.new(NONCE, normalized(known), hashlib.sha256).digest()[:16]).digest() == K08)
    print(json.dumps({"rows": len(records), "unique_16byte_coupons": len(coupons),
                      "ascii_caption_candidates": len(captions), "K04_hits": hits4,
                      "K08_hits": hits8}, indent=2))
    assert len(coupons) == 803520 and len(captions) == 166
    assert not hits4 and not hits8


if __name__ == "__main__":
    main(sys.argv[1])
