"""H17 source-calibrated late-printer dual-ACK full coupon issuer."""
import hashlib
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from k04_gf128_label_emitter_sft import mul, power

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")

def spool(path):
    b = Path(path).read_bytes()
    assert hashlib.sha256(b).hexdigest() == SPOOL_SHA
    rx = re.compile(r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([A-F\d]{32}) DEST=(\S+)$")
    rows = []
    for line in b.decode("ascii").splitlines():
        m = rx.fullmatch(line)
        if not m:
            assert line.startswith("#") or not line
            continue
        iso, job, attempt, state, cls, payload, dest = m.groups()
        ts = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        rows.append(dict(iso=iso, job=job, attempt=int(attempt), state=state, cls=cls,
                         payload=bytes.fromhex(payload), dest=dest, ts=int(ts.timestamp())))
    assert len(rows) == 133
    assert [(rows[k]["job"], rows[k]["state"], rows[k]["cls"]) for k in (129, 131, 132)] == [
        ("PS-261003-0417", "ACK", "RECOVER"),
        ("PS-261003-0448", "ACK", "RECOVER"),
        ("PS-261003-0420", "ACK", "RECOVER")]
    return rows

def labels(r):
    a, t, n = r["job"], r["ts"], r["attempt"]
    dest, cls, state, iso = r["dest"], r["cls"], r["state"], r["iso"]
    return [
        str(t), str(t//60), str(t//300), str(int(a[-4:])),
        f"{a}|{n}|{state}|{cls}|{dest}", f"{a}|{cls}|{dest}", f"{a}|{n}|{cls}",
        f"H17|{a}|{iso}", f"{iso}|{a}|{dest}",
        f"{a}/{state}/{n}/{cls}/{iso}", f"{a}:{cls}:{dest}:{iso}", f"ESC|{a}|{cls}|{n}"
    ]

def encode(row, form, method):
    b = labels(row)[form].encode("ascii")
    if method == 0: return int.from_bytes(hashlib.sha256(b).digest()[:16],"big")
    if method == 1: return int.from_bytes(hashlib.blake2b(b,digest_size=16).digest(),"big")
    if method == 2: return int.from_bytes(hashlib.md5(b).digest(),"big")
    if method == 3: return int.from_bytes(b[:16].ljust(16,b"\0"),"big")
    if method == 4: return int.from_bytes(b[-16:].rjust(16,b"\0"),"big")
    if method == 5: return int.from_bytes(hashlib.sha256(b).digest()[-16:],"big")
    raise AssertionError

def layout(packet, mode):
    b = packet if isinstance(packet,bytes) else packet.to_bytes(16,"big")
    if mode & 4: b = bytes(int(f"{x:08b}"[::-1],2) for x in b)
    words = [b[j:j+4] for j in range(0,16,4)]
    if mode & 2: words = [w[::-1] for w in words]
    if mode & 1: words.reverse()
    return b"".join(words)

def run(path):
    rows = spool(path)
    anchors = (131,132)
    held = [j for j,r in enumerate(rows[:128]) if r["state"]=="ACK" and r["cls"]=="RECOVER"]
    assert len(held)==35
    assert layout(layout(rows[131]["payload"],7),7)==rows[131]["payload"]
    tested = target_hits = held_full_matches = best_partial = 0
    counts = Counter()
    for form in range(12):
        for method in range(6):
            x = [encode(rows[j],form,method) for j in anchors]
            if x[0]==x[1]:
                continue
            target_x = encode(rows[129],form,method)
            for serializer in range(8):
                y=[int.from_bytes(layout(rows[j]["payload"],serializer),"big") for j in anchors]
                a = mul(y[0]^y[1],power(x[0]^x[1],(1<<128)-2))
                b = y[0]^mul(a,x[0])
                coupon = layout((mul(a,target_x)^b).to_bytes(16,"big"),serializer)
                component=bytes(z^w for z,w in zip(coupon,MASK))
                target_hits += hashlib.sha256(component).digest()==TARGET
                tested+=1
                matches=0
                partial=0
                for j in held:
                    got=layout((mul(a,encode(rows[j],form,method))^b).to_bytes(16,"big"),serializer)
                    n=sum(z==w for z,w in zip(got,rows[j]["payload"]))
                    matches += n==16
                    partial=max(partial,n)
                held_full_matches += matches
                best_partial=max(best_partial,partial)
                counts[matches]+=1
    assert tested==560 and counts==Counter({0:560}) and target_hits==0
    print("ORIGINAL_LATE_TWO_ACK_MODELS",tested,"INDEPENDENT_OLDER_RECOVER_ACK_HOLDOUTS",len(held),
          "FULL_SOURCE_HOLDOUT_MATCHES",held_full_matches,"MAX_PARTIAL_BYTES",best_partial,"K04_SHA_HITS",target_hits)
    a0=0x76b0f7189bda0a85778ba0946be568a2
    b0=0x139aba9c72719c329472df449d148051
    x=[encode(rows[j],7,0) for j in (131,132,129,127)]
    y=[mul(a0,t)^b0 for t in x]
    a=mul(y[0]^y[1],power(x[0]^x[1],(1<<128)-2))
    b=y[0]^mul(a,x[0])
    assert (a,b)==(a0,b0)
    assert [mul(a,t)^b for t in x]==y
    print("SYNTHETIC_TWO_SOURCE_ANCHORS_SELECTED_AND_HELDOUT_EXACT PASS")

if __name__=="__main__":
    p=sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources/evidence/print/spool-reconstruction.log"
    run(p)
