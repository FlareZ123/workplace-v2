"""Cross-domain K05/K06/K07 selected-vs-alternative role transform holdout.
Read-only, source-derived, standard library. Optional resources-directory arg.
"""
import hashlib
import json
import re
import struct
import sys
import zlib
from pathlib import Path

E = (Path(sys.argv[1]) if len(sys.argv) > 1
     else Path(__file__).resolve().parents[2] / "resources") / "evidence"
raw = (E / "recorder/trip-recorder.raw").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
rec = {}
for i in range(struct.unpack_from("<I", raw, 12)[0]):
    item = raw[16+i*24:16+(i+1)*24]
    _, node, event, latch, seq = struct.unpack_from("<I H B B I", item)
    good = zlib.crc32(item[:20]) == struct.unpack_from("<I", item, 20)[0]
    if node == 49 and event == 82 and good and (200 <= seq <= 203 or 300 <= seq <= 303):
        rec[seq // 100, latch] = item[12:16]
assert len(rec) == 8
K05 = (b"".join(rec[2, i] for i in range(4)),
       b"".join(rec[3, i] for i in range(4)))

pages = dict(((r, s), bytes.fromhex(h)) for r, s, h in re.findall(
    r"DOCUMENT RC-17 / REV ([^ /\n]+) / SECTION ([^\n]+)\n.*?Footer control strip: ([0-9A-F]{8})",
    (E / "procedures/RC-17-scans.txt").read_text(), re.S))
order = ("DRAIN", "ISOLATE", "PURGE", "VERIFY")
K06 = (b"".join(pages["B", x] for x in order),
       b"".join(pages["C", x] for x in order))

lines = [json.loads(x) for x in (E / "transfers/transfer-audit.jsonl").read_text().splitlines()]
def transfer(t):
    values = []
    for seq in range(8):
        matching = [r for r in lines if r["kind"] == "CHUNK" and r["transfer"] == t and r["seq"] == seq]
        x = max(matching, key=lambda r: r["attempt"])
        assert x["attempt"] == 2
        values.append(bytes.fromhex(x["checkpoint"]))
    return b"".join(values)
K07 = transfer("AX-7778"), transfer("AX-7782")
assert K05[1].hex().upper() == "FF8B78200A56E8586DCDA00EF01E4572"
assert K06[1].hex().upper() == "5DBF40EE52FAAED9A536D3326CF0D95A"
assert hashlib.sha256(K07[1]).digest()[:16].hex().upper() == "93495F5E425AB8E592123DABAEB68545"

spool = (E / "print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
printrows = []
for line in spool.decode().splitlines():
    if "PAYLOAD=" in line:
        row = dict(part.split("=", 1) for part in line.split()[1:])
        row["timestamp"] = line.split()[0]
        printrows.append(row)
def packet(job, cls, state, attempt, time):
    vals = [bytes.fromhex(r["PAYLOAD"]) for r in printrows if
            r["JOB"] == "PS-261003-" + job and r["CLASS"] == cls and
            r["STATE"] == state and r["ATTEMPT"] == attempt and
            r["timestamp"].split("T")[1].startswith(time)]
    assert len(vals) == 1
    return vals[0]
other = {
    "0417 same-class requested-to-ACK-copied": (
        packet("0417", "RECOVER", "REQUESTED", "1", "18:01"),
        packet("0417", "RECOVER", "ACK", "2", "18:02")),
    "0420 different-class ACK-to-ACK": (
        packet("0420", "STORES", "ACK", "1", "17:00"),
        packet("0420", "RECOVER", "ACK", "2", "18:25"))}
assert other["0417 same-class requested-to-ACK-copied"][1].hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"

def rol(x, n):
    return ((x << n) | (x >> (32-n))) & 0xffffffff if n else x

def fit(a, b, kind, r=0):
    if kind == "xor":
        return lambda x: bytes(v ^ u ^ w for v, u, w in zip(x, a, b))
    if kind == "add8":
        return lambda x: bytes((v + w - u) & 255 for v, u, w in zip(x, a, b))
    if kind.startswith("add128"):
        order = "big" if kind.endswith("be") else "little"
        delta = (int.from_bytes(b, order)-int.from_bytes(a, order))%(1<<128)
        return lambda x: ((int.from_bytes(x, order)+delta)%(1<<128)).to_bytes(16, order)
    order = "big" if kind.endswith("be") else "little"
    wa = [int.from_bytes(a[i:i+4],order) for i in range(0,16,4)]
    wb = [int.from_bytes(b[i:i+4],order) for i in range(0,16,4)]
    pad = [rol(v, r)^w for v,w in zip(wa,wb)]
    def apply(x):
        wx=[int.from_bytes(x[i:i+4],order) for i in range(0,16,4)]
        return b"".join((rol(v,r)^p).to_bytes(4,order) for v,p in zip(wx,pad))
    return apply

models = [("xor",0),("add8",0),("add128be",0),("add128le",0)]
models += [(f"rol32-{endian}",r) for endian in ("be","le") for r in range(32)]
transitions = {"K05 prior-to-selected":K05,"K06 withdrawn-to-authorized":K06,
               "K07 drill-to-committed":K07}
out = {}
for name, (src, selected) in transitions.items():
    matches=[]
    max_correct=0
    for kind,r in models:
        predictor=fit(src,selected,kind,r)
        for held_name,(held_src,held_selected) in transitions.items():
            if held_name == name: continue
            actual = predictor(held_src)
            max_correct=max(max_correct,sum(a==b for a,b in zip(actual,held_selected)))
            if actual == held_selected:
                matches.append((kind,r,held_name))
    out[name] = {"models":len(models),"exact_other_selected":matches,
                 "maximum_bytes_correct_of_16":max_correct}

# Independently generated synthetic holdout, with fixed hidden four-word pad.
a=bytes.fromhex("731462BCA19E5754FA10504B09037A5C")
x=bytes.fromhex("40A7629A3C2255263DC1871B6EBD6504")
pad=(0x131D1701,0xA536F09A,0x48381E6B,0x0F121A3D)
def independent_transform(source):
    words=[int.from_bytes(source[i:i+4],"little") for i in range(0,16,4)]
    return b"".join((rol(v,7)^p).to_bytes(4,"little") for v,p in zip(words,pad))
b=independent_transform(a)
y=independent_transform(x)
assert a != b and x != y and fit(a,b,"rol32-le",7)(x) == y
print(json.dumps({"original_transitions":{k:[a.hex(),b.hex()] for k,(a,b) in transitions.items()},
                  "printer_controls":{k:[a.hex(),b.hex()] for k,(a,b) in other.items()},
                  "heldout_results":out,"synthetic_nontrivial_rol_positive":True},indent=2))
