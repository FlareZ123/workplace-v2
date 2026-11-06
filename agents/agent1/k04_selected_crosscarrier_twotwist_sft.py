"""K04 original-source selected-control two-twist MT19937 bridge SFT.

Run from repository root: python agents/agent1/k04_selected_crosscarrier_twotwist_sft.py
Reads immutable resources; excludes disputed printer ACK2 and all acceptance targets.
"""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import random
import re
import struct
import zlib

ROOT = Path(__file__).resolve().parents[2] / "resources" / "evidence"
STAGES = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
MASK = 0xBFFFFFFF

def untemper(y):
    x = y ^ (y >> 18)
    x = y ^ (x >> 18)
    z = x
    for _ in range(2):
        z = x ^ ((z << 15) & 0xEFC60000)
    x = z
    for _ in range(6):
        z = x ^ ((z << 7) & 0x9D2C5680)
    x = z
    for _ in range(4):
        z = x ^ (z >> 11)
    return z & 0xFFFFFFFF

def mix(x):
    return ((x & 0x7FFFFFFF) >> 1) ^ (0x9908B0DF if x & 1 else 0)

def four(buf, order):
    assert len(buf) == 16
    return [untemper(int.from_bytes(buf[i:i+4], order)) for i in range(0,16,4)]

def candidates():
    groups = {}
    rc = (ROOT / "procedures/RC-17-scans.txt").read_text()
    strips = {}
    for rev, sec, hexword in re.findall(
        r"DOCUMENT RC-17 / REV (B|C|D-draft) / SECTION (\w+).*?Footer control strip: ([0-9A-F]{8})", rc, re.S
    ):
        strips[rev, sec] = hexword
    for rev in ("B", "C", "D-draft"):
        groups["RC17_" + rev] = bytes.fromhex("".join(
            strips[rev, sec] for sec in ("DRAIN", "ISOLATE", "PURGE", "VERIFY")
        ))
    raw = (ROOT / "recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
    valid = []
    for i in range(88):
        r = raw[16 + i*24:16 + (i+1)*24]
        if zlib.crc32(r[:20]) & 0xFFFFFFFF != struct.unpack_from("<I", r, 20)[0]:
            continue
        _, node, event, latch, seq, word, _, _ = struct.unpack("<IHBBI4sII", r)
        valid.append((node, event, latch, seq, word))
    top = {}
    for node, event, latch, seq, word in valid:
        k = (node, event, latch)
        if k not in top or top[k][0] < seq:
            top[k] = (seq, word)
    for node, event in {(n,e) for n,e,_,_,_ in valid}:
        if all((node,event,i) in top for i in range(4)):
            groups[f"TRP2_node{node}_event{event}_top4"] = b"".join(
                top[node,event,i][1] for i in range(4)
            )
    for first in (200,300,900,990):
        by_seq = {seq:word for node,event,_,seq,word in valid
                  if node == 49 and event == 82 and first <= seq < first+4}
        if len(by_seq) == 4:
            groups[f"TRP2_node49_{first}"] = b"".join(
                by_seq[first+i] for i in range(4)
            )
    chains = defaultdict(dict)
    for line in (ROOT / "transfers/transfer-audit.jsonl").read_text().splitlines():
        o = json.loads(line)
        if o.get("kind") != "CHUNK":
            continue
        key,seq,attempt = o["transfer"],o["seq"],o["attempt"]
        if seq not in chains[key] or chains[key][seq][0] < attempt:
            chains[key][seq] = (attempt,o["checkpoint"])
    for key,chain in chains.items():
        if all(i in chain for i in range(8)):
            groups["AX_" + key] = bytes.fromhex("".join(chain[i][1] for i in range(8)))
    assert len(groups) == 11 and all(len(x) == 16 for x in groups.values())
    return groups

def main():
    raw = (ROOT / "print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    rows = [x for x in raw.decode().splitlines() if "PAYLOAD=" in x]
    assert len(rows) == len(STAGES) == 133
    native = {}
    for i,line in enumerate(rows):
        if i == 129:
            assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line
            continue
        packet = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line)[1])
        for j,v in enumerate(four(packet,"little")):
            native[STAGES[i]+j] = v
    predictions = []
    for t in sorted(native):
        if all(t+k+d in native for k in range(2) for d in (0,227,396)):
            p = tuple((native[t+k+396] ^ mix(native[t+k]) ^ mix(native[t+k+227])) & MASK
                      for k in range(2))
            observations = tuple(native.get(t+850+k) for k in range(2))
            predictions.append((t,p,observations))
    assert len(predictions) == 36
    actual = [(t,p,d) for t,p,d in predictions if all(x is not None for x in d)]
    assert len(actual) == 6 and all(all(((x^y)&MASK)==0 for x,y in zip(p,d))
                                    for t,p,d in actual)
    seeded_rng = random.Random(0xC0FFEE)
    seeded = [untemper(seeded_rng.getrandbits(32)) for _ in range(2200)]
    for t,_,_ in predictions:
        for k in range(2):
            predicted = (seeded[t+k+396] ^ mix(seeded[t+k]) ^ mix(seeded[t+k+227])) & MASK
            assert ((seeded[t+850+k] ^ predicted) & MASK) == 0
    groups = candidates()
    ranking = []
    for key,buf in sorted(groups.items()):
        for order in ("little","big"):
            donor = four(buf,order)
            best = max((sum(31-((donor[off+k]^pred[k]) & MASK).bit_count()
                              for k in range(2)), t, off)
                       for t,pred,_ in predictions for off in range(3))
            ranking.append((key,order,best[0],best[1],best[2]))
    observed_max = max(x[2] for x in ranking)
    assert observed_max == 44 and not any(x[2] == 62 for x in ranking)
    print("ORIGINAL_PREDICTION_SITES",len(predictions))
    print("ORIGINAL_HELDOUT_TWO_WORD_CONTROLS",len(actual),"PASS")
    print("SEEDED_TWO_WORD_POSITIVES",len(predictions),"PASS")
    print("CANDIDATE_GROUPS",len(groups),"ORIENTATIONS",len(ranking))
    print("OBSERVED_MAX_MATCH_BITS",observed_max,"OF_62")
    for key,order,bits,t,off in sorted(ranking,key=lambda x:-x[2]):
        print("GROUP",key,order,"BITS",bits,"AT",t,off)
    rng = random.Random(0xA911C7)
    maxima = []
    for _ in range(1000):
        best = 0
        for _group in groups:
            for _order in range(2):
                donor = [rng.getrandbits(32) for _ in range(4)]
                for _,pred,_ in predictions:
                    for off in range(3):
                        bits = sum(31-((donor[off+k]^pred[k]) & MASK).bit_count()
                                   for k in range(2))
                        best = max(best,bits)
        maxima.append(best)
    assert (min(maxima),sorted(maxima)[500],max(maxima),sum(v>=44 for v in maxima)) == (41,44,50,794)
    print("NULL_SETS",len(maxima),"NULL_MAX_RANGE",min(maxima),max(maxima))
    print("NULL_MEDIAN",sorted(maxima)[500],"NULL_TAIL_GE_OBS",sum(v>=44 for v in maxima))
    print("K04_AUTHENTICATED_COUPON_BITS",0,"K08_VERBATIM_WORDS",0)

if __name__ == "__main__":
    main()
