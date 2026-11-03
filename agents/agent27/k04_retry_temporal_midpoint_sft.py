"""Agent27 SFT: K04 retry clock midpoint from 18:01 and 18:03 REQUESTED buffers.
Original evidence and verifier read-only. Python 3 standard library.
"""
import hashlib
import itertools
import pathlib
import re
import sys

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
BEFORE = bytes.fromhex("CD3E4F216ADB2FB180DA2AA90B33F7A4")
AFTER = bytes.fromhex("44D53DFC29D7943A95D89371DA58EC64")
COPIED = "A9A9DC5731A5E2AE879C47215C2559D5"
ROW = re.compile(r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)$")


def lane_choices(a, b, width, endian, arc):
    base = 1 << (8 * width)
    output = []
    for p in range(0, 16, width):
        x = int.from_bytes(a[p:p+width], endian)
        y = int.from_bytes(b[p:p+width], endian)
        if arc == "integer":
            v = x + y
            low, high = v // 2, (v + 1) // 2
        elif arc == "forward":
            d = (y - x) % base
            low, high = x + d // 2, x + (d + 1) // 2
        else:
            d = (x - y) % base
            low, high = y + d // 2, y + (d + 1) // 2
        output.append(tuple(dict.fromkeys(
            (z % base).to_bytes(width, endian) for z in (low, high))))
    return output


def enumerate_width(a, b, width):
    for endian in ("little", "big"):
        for arc in ("integer", "forward", "reverse"):
            for segments in itertools.product(*lane_choices(a,b,width,endian,arc)):
                yield (width,endian,arc), b"".join(segments)


def enumerate_all(a, b):
    for width in (1,2,4,8,16):
        yield from enumerate_width(a,b,width)


def main():
    src = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else
        "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(src).hexdigest() == SPOOL_SHA
    rows = [ROW.fullmatch(s) for s in src.decode().splitlines()
        if s and not s.startswith("#")]
    assert len(rows) == 133 and all(rows)
    expected = [
        ("2026-10-03T18:01:00Z","PS-261003-0417","1","REQUESTED","RECOVER",BEFORE.hex().upper()),
        ("2026-10-03T18:02:00Z","PS-261003-0417","2","ACK","RECOVER",COPIED),
        ("2026-10-03T18:03:00Z","PS-261003-0417","3","REQUESTED","RECOVER",AFTER.hex().upper()),
    ]
    assert [r.groups()[:6] for r in rows[128:131]] == expected

    count, original_hits = 0, []
    distinct = set()
    for model, raw in enumerate_all(BEFORE,AFTER):
        count += 1
        distinct.add(raw)
        component = bytes(x^y for x,y in zip(raw,MASK))
        if hashlib.sha256(component).digest()==TARGET or hashlib.sha256(raw).digest()==TARGET:
            original_hits.append((model,raw.hex()))
    assert count == 12807 and len(distinct)==6647 and not original_hits

    planted = b"".join(x[-1] for x in lane_choices(BEFORE,AFTER,4,"big","forward"))
    assert planted.hex().upper()=="0909C68FCA5961F68B595F0D72C67204"
    positive = hashlib.sha256(bytes(x^y for x,y in zip(planted,MASK))).digest()
    n_positive = sum(hashlib.sha256(bytes(x^y for x,y in zip(c,MASK))).digest()==positive
        for _,c in enumerate_all(BEFORE,AFTER))
    assert n_positive == 2

    routine = [bytes.fromhex(r.group(6)) for r in rows[:128]]
    holdout = {}
    for width in (1,2,4,8,16):
        found = 0
        for i in range(1,127):
            if any(c==routine[i] for _,c in
                enumerate_width(routine[i-1],routine[i+1],width)):
                found += 1
        holdout[width]=found
    assert not any(holdout.values())
    print("source_sha256=PASS event=0417 REQUESTED 18:01/18:03 midpoint 18:02")
    print("candidate_assignments",count,"distinct_raw_coupons",len(distinct),
        "full_sha256_checks",2*count,"original_hits",len(original_hits))
    print("planted_midpoint",planted.hex().upper(),"planted_hits",n_positive)
    print("heldout_126_routine_triples",holdout)


if __name__=="__main__":
    main()
