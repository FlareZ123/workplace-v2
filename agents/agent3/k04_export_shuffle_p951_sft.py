"""SFT: test export-order Fisher-Yates side channel against original p951 printer closure.

Run from repo: python agents/agent3/k04_export_shuffle_p951_sft.py resources
Selected spool row129, copied ACK, K04/K08 checks are excluded. This is a
conditional MT19937 stage experiment, not historical printer authentication.
"""
import hashlib
import importlib.util
import itertools
import json
import random
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("source_mt", ROOT / "agent49/k04_p951_symbolic_basis.py")
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
ORIGIN, LAST = mt.ORIGIN, mt.LAST
PIN = {
 "evidence/recorder/trip-recorder.raw": "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
 "evidence/transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
 "evidence/telemetry/freeze-export.jsonl": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
}

def read(root, name):
    raw = (root / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN[name]
    return raw

def source_top8(root):
    basis, words = mt.source(root)
    values, masks = [], []
    for word in words:
        value = mask = 0
        for j, bit in enumerate(mt.temper(word)[24:32]):
            predicted = basis.predict(bit)
            if predicted is not None:
                value |= predicted << j
                mask |= 1 << j
        values.append(value)
        masks.append(mask)
    return values, masks

def decisions(observed, original):
    assert len(set(observed)) == len(observed) == len(original)
    label = {item: i for i, item in enumerate(original)}
    final = [label[item] for item in observed]
    work = list(range(len(original)))
    out = []
    for i in range(len(original) - 1, 0, -1):
        j = work.index(final[i])
        out.append((i, j))
        work[i], work[j] = work[j], work[i]
    assert work == final
    return out

def starts(draws, values, masks, rejected):
    # Exact existential rejection branching, no limit on rejected draws.
    # The LAST+1 boundary is deliberately unconstrained.
    n = len(values)
    possible = bytearray([1]) * (n+1)
    for i, j in reversed(draws):
        k = (i+1).bit_length()
        shift = 8-k
        if i not in rejected:
            reject = bytearray(n)
            for at in range(n):
                value = values[at] >> shift
                mask = masks[at] >> shift
                reject[at] = any(((value ^ x) & mask) == 0 for x in range(i+1, 1<<k))
            rejected[i] = reject
        reject = rejected[i]
        updated = bytearray(n+1)
        updated[n] = 1
        for at in range(n-1, -1, -1):
            value = values[at] >> shift
            mask = masks[at] >> shift
            accepts = ((value ^ j) & mask) == 0
            updated[at] = (accepts and possible[at+1]) or (reject[at] and updated[at+1])
        possible = updated
    return [at+ORIGIN for at in range(n) if possible[at]]

def recorder_orders(root):
    raw = read(root, "evidence/recorder/trip-recorder.raw")
    observed = []
    for i in range(88):
        _, node, event, latch, seq = struct.unpack_from("<IHBBI", raw, 16+24*i)
        observed.append((node, seq))
    ordinary = sorted((x for x in observed if x[0] == 50), key=lambda x:x[1])
    groups = [sorted(x for x in observed if x[0] == 49 and lo <= x[1] < lo+4)
              for lo in (200,300,900,990)]
    assert len(ordinary) == 72 and all(len(g) == 4 for g in groups)
    for order in itertools.permutations(range(4)):
        special = sum((groups[i] for i in order), [])
        yield observed, ordinary + special
        yield observed, special + ordinary

def transfer_orders(root):
    rows = [json.loads(line) for line in read(root,"evidence/transfers/transfer-audit.jsonl").splitlines()]
    def key(r): return r["transfer"],r["kind"],r.get("seq"),r.get("attempt")
    observed = [key(x) for x in rows]
    groups = {t:[x for x in rows if x["transfer"]==t] for t in sorted({x["transfer"] for x in rows})}
    for group_order in itertools.permutations(groups):
        for seq_first in (True,False):
            for receipt_last in (True,False):
                original = []
                for t in group_order:
                    chunks = [x for x in groups[t] if x["kind"] == "CHUNK"]
                    chunks.sort(key=(lambda x:(x["seq"],x["attempt"])) if seq_first
                                else (lambda x:(x["attempt"],x["seq"])))
                    receipt = [x for x in groups[t] if x["kind"] != "CHUNK"]
                    original.extend(chunks+receipt if receipt_last else receipt+chunks)
                yield observed, [key(x) for x in original]

def telemetry_orders(root):
    rows = [json.loads(line) for line in read(root,"evidence/telemetry/freeze-export.jsonl").splitlines()]
    def key(r): return r["tag"],r["field"],r["seq"],r["revision"]
    observed = [key(x) for x in rows]
    diag = sorted((x for x in rows if x["field"]=="DIAG_WORD"),key=lambda x:(x["seq"],x["revision"]))
    pv = [x for x in rows if x["field"]=="PV"]
    seq = sorted(pv,key=lambda x:(x["seq"],x["tag"]))
    tag = sorted(pv,key=lambda x:(x["tag"],x["seq"]))
    variants = [
      sorted(rows,key=lambda x:(x["seq"],x["revision"],x["tag"])),
      sorted(rows,key=lambda x:(x["ts"],x["tag"],x["seq"],x["revision"])),
      diag+seq,seq+diag,diag+tag,tag+diag,
      sorted(rows,key=lambda x:(x["tag"],x["field"],x["seq"],x["revision"])),
    ]
    for original in variants: yield observed, [key(x) for x in original]

def positive_control():
    seed, burn, n = 382, 150, 145
    r = random.Random(seed)
    for _ in range(burn): r.getrandbits(32)
    observed = list(range(n))
    r.shuffle(observed)
    reference = random.Random(seed)
    values = [reference.getrandbits(32)>>24 for _ in range(500)]
    possible = starts(decisions(observed,list(range(n))),values,[255]*500,{})
    assert burn+ORIGIN in possible
    print("CONTROL: planted 145-row Python shuffle, exact start at array position 150 recovered")

def main(root):
    positive_control()
    values,masks = source_top8(root)
    print("SOURCE: original 132 intact printer rows, rank15365, target row129 withheld")
    for label, layouts in (("RECORDER",recorder_orders),("TRANSFER",transfer_orders),("TELEMETRY",telemetry_orders)):
        hits = []
        count = 0
        rejection_cache = {}
        for observed,original in layouts(root):
            found = starts(decisions(observed,original),values,masks,rejection_cache)
            count += 1
            if found: hits.append(found)
        bounded = sum(sum(at<=1033 for at in found) for found in hits)
        print(label,"layouts",count,"positive_layouts",len(hits),"starts",sum(map(len,hits)),
              "starts<=1033",bounded)
        if hits: print("  surviving starts (first 3 layouts)",hits[:3])
    print("No nonboundary shuffle-origin witness for the proposed shared printer MT stage.")

if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources")
