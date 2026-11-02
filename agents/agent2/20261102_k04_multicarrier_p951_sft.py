"""H-17 K04 conditional p951 MT19937 cross-carrier witness reproducer.

Original source only. Printer ACK row129 and every K04/K08 commitment,
route XOR mask and verifier are excluded. The p951 chronology is a
preexisting speculative shared-printer/recorder index fixture.
Usage: python agents/agent2/20261102_k04_multicarrier_p951_sft.py resources
"""
import hashlib
import json
import re
import struct
import sys
import zlib
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
MASK = 0xffffffff
MAG = 0x9908b0df

def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9d2c5680
    x ^= (x << 15) & 0xefc60000
    return (x ^ (x >> 18)) & MASK

def untemper(x):
    for shift, left, filt in ((18,False,MASK),(15,True,0xefc60000),
                              (7,True,0x9d2c5680),(11,False,MASK)):
        y = x
        for _ in range(6):
            y = x ^ (((y << shift) & filt) if left else (y >> shift))
        x = y & MASK
    return x

def twist(x):
    return ((x >> 1) ^ (MAG if x & 1 else 0)) & MASK

def inverse_twist(x):
    low = x >> 31
    return (((x ^ (MAG if low else 0)) << 1) | low) & MASK

def source_closure(root):
    data = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == SPOOL_SHA
    payloads = [bytes.fromhex(x) for x in
                re.findall(rb"PAYLOAD=([A-F0-9]{32})", data)]
    assert len(payloads) == 133 and len(STARTS) == 133 and STARTS[129] == 951
    offset, count = 2000, 6000
    word, known = [0] * count, [0] * count
    learned = 0
    def add(at, value, mask):
        nonlocal learned
        if at < 0 or at >= count:
            return
        assert ((word[at] ^ value) & known[at] & mask) == 0
        new = mask & ~known[at]
        if new:
            word[at] = (word[at] & ~new) | (value & new)
            known[at] |= new
            learned += new.bit_count()

    for row, (data, at) in enumerate(zip(payloads, STARTS)):
        if row == 129:
            continue
        for lane in range(4):
            value = untemper(int.from_bytes(data[lane*4:lane*4+4], "little"))
            add(offset + at + lane, value, MASK)

    assert learned == 528 * 32
    for repeat in range(30):
        before = learned
        for t in range(count - 624):
            mask = (known[t] & 0x80000000) | (known[t+1] & 0x7fffffff)
            value = (word[t] & 0x80000000) | (word[t+1] & 0x7fffffff)
            if known[t+397] == MASK and known[t+624] == MASK:
                inverse = inverse_twist(word[t+397] ^ word[t+624])
                add(t, inverse, 0x80000000)
                add(t+1, inverse, 0x7fffffff)
            if mask == MASK:
                if known[t+397] == MASK:
                    add(t+624, word[t+397] ^ twist(value), MASK)
                if known[t+624] == MASK:
                    add(t+397, word[t+624] ^ twist(value), MASK)
        if learned == before:
            break
    assert all(known[offset + STARTS[129] + lane] == 0 for lane in range(4))
    print("SOURCE closure full",sum(x == MASK for x in known),
          "partial",sum(0 < x < MASK for x in known),
          "known bits",learned,"iterations",repeat+1)
    return word, known, offset

def source_controls(root):
    raw = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == REC_SHA
    out = []
    for i in range(88):
        at = 16 + 24 * i
        ts,node,event,latch,seq,value,aux,crc = struct.unpack_from(
            "<IHBBI4sII", raw, at)
        good = zlib.crc32(raw[at:at+20]) == crc
        out.append((f"TRP2 r{i} seq{seq} node{node} event{event} CRC={good}",value))
    procedure = (root / "evidence/procedures/RC-17-scans.txt").read_text()
    pages = re.finditer(
        r"DOCUMENT RC-17 / ([^\n]+)[\s\S]*?Footer control strip: ([0-9A-F]{8})",
        procedure)
    for i, match in enumerate(pages):
        out.append((f"RC-17 {i} {match[1]}",bytes.fromhex(match[2])))
    lines = (root / "evidence/maintenance/seal-receipts.jsonl").read_text().splitlines()
    for i, line in enumerate(lines):
        entry = json.loads(line)
        out.append((f"SEAL r{i} {entry['permit']} bay{entry.get('bay','')}",
                    bytes.fromhex(entry["serial"].split("-")[1])))
    for i, source in enumerate(("049AAB2E","1CDE7A82","CD7C6023","4303C91A")):
        out.append((f"WN14 ink{i}",bytes.fromhex(source)))
    assert len(out) == 148
    return out

def main(root):
    for sample in (0,1,0xdeadbeef,0x12345678,MASK):
        assert untemper(temper(sample)) == sample
        assert inverse_twist(twist(sample)) == sample
    word, known, offset = source_closure(root)
    observations = source_controls(root)
    result = {}
    for order in ("little", "big"):
        matches = []
        for label, raw in observations:
            x = untemper(int.from_bytes(raw,order))
            for pos, mask in enumerate(known):
                bits = mask.bit_count()
                if bits >= 30 and ((word[pos] ^ x) & mask) == 0:
                    matches.append((label,pos-offset,bits,raw.hex().upper()))
        result[order] = matches
    assert len(result["little"]) == 20 and not result["big"]
    NEW = {
        "TRP2 r3 seq24":(-683,32,"09CAAF96"),
        "TRP2 r9 seq7":(-810,32,"326F907A"),
        "TRP2 r11 seq12":(-775,32,"D95DE699"),
        "TRP2 r24 seq13":(-769,32,"EA04CEF9"),
        "TRP2 r44 seq41":(-568,32,"6A03B41F"),
        "TRP2 r54 seq25":(-677,32,"686932D1"),
        "TRP2 r39 seq45":(-540,31,"4BC25CCB"),
        "TRP2 r41 seq901":(-320,31,"BA194782"),
        "SEAL r21 PTW-405":(-964,32,"F6E935B9"),
        "SEAL r22 PTW-412":(-944,31,"5AD7D397"),
        "SEAL r24 PTW-414":(-937,31,"645EB28C"),
    }
    for label, want in NEW.items():
        hits = [(at,bits,raw) for name,at,bits,raw in result["little"]
                if name.startswith(label)]
        assert hits == [want], (label,hits)
        print("NEW",label,"at",want[0],"known",want[1],"source",want[2])
    print("TOTAL low31/full32 matches",len(result["little"]),
          "opposite-endian matches",len(result["big"]))
    print("SELECTED K04 raw word masks",
          [hex(known[offset+STARTS[129]+k]) for k in range(4)])
    print("No new verified REC8 component. Model is conditional.")

if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1
         else Path(__file__).resolve().parents[2] / "resources")
