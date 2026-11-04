"""Read-only H-17 conditional CPython binary-seed B construction test.

Ten source-evidenced hash/KDF architectures expand record identities or whole
surviving member contents to hypothetical 2357..2428-byte printer seed B.
The five original-source B-word gates are from Agent15's published conditional
p951/CPython model; they are NOT authenticated actual seed or K04 coupon bits.
Selected ESC-N ACK2 copy and all original commitments are excluded.
"""
import hashlib
import hmac
import itertools
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", str(Path(__file__).resolve().parents[2] / "resources/evidence")))
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
LENGTHS = range(2357, 2429)
K22 = bytes.fromhex("FD6A4CF7")
K23 = bytes.fromhex("06EDCDAD")
K590 = {bytes.fromhex(v) for v in ("6425CF5B","E425CF5B")}
K601 = bytes.fromhex("49342EC0")
K602 = {bytes.fromhex(v) for v in ("64589C88","E4589C88")}


def source_inputs():
    spool = (ROOT / "print/spool-reconstruction.log").read_bytes()
    routing = (ROOT / "recovery-routing.json").read_bytes()
    notes = (ROOT / "crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(routing).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(notes).hexdigest() == NOTES_SHA
    sheet = json.loads(routing)
    mask = bytes.fromhex(sheet["K04"]["masked_component"])
    nonce = bytes.fromhex(sheet["K08"]["desk_nonce"])
    job = "PS-261003-0417"
    lane = "ESC-N"
    tickets = ("ST-094","ST-081","ST-106","ST-099","ST-112")
    labels = {
        "IR-261003-H17","H17-IR-261003","H17","IR-261003","REC8/1","K04",
        job,"PS-261003-0420","PS-261003-0448",lane,"RECOVER","ACK",
        "ATTEMPT=2","H17-POL-17/A3","FA-17","L-29/N","L-29/S",
        "2026-10-03","20261003","2026-10-03T18:02:00Z",
        "PS-261003-0417/2","PS-261003-0417:ACK:RECOVER",
        "PS-261003-0417/ACK/RECOVER/2","PS-261003-0417/RECOVER",
        "|".join(tickets),",".join(tickets)," ".join(tickets),
        "|".join(t[3:] for t in tickets),",".join(t[3:] for t in tickets),
        "|".join((lane,job,"ACK","RECOVER","2")),
        "/".join((lane,job,"ACK","RECOVER","2")),
        "H17-POL-17/A3|FA-17|L-29/N",
        "H17-POL-17/A3/FA-17/L-29/N",
        "H17-IR-261003|ESC-N|PS-261003-0417",
        "IR-261003-H17/ESC-N/PS-261003-0417",
    }
    for a,b in itertools.product(
         (job,lane,"H17","IR-261003-H17","RECOVER","L-29/N","FA-17"),
         (job,lane,"H17","IR-261003-H17","RECOVER","L-29/N","FA-17","2","2026-10-03")):
        if a != b:
            for delimiter in ("/",":","|","_","-"," ",chr(10)):
                labels.add(a+delimiter+b)
    samples = {}
    for label in labels:
        for form,variant in (("raw",label),("upper",label.upper()),("lower",label.lower())):
            samples[f"label:{form}:{label}"] = variant.encode()
    sample_files = {
        "route-mask-hex":sheet["K04"]["masked_component"].encode(),
        "route-mask-bytes":mask,
        "desk-nonce-hex":sheet["K08"]["desk_nonce"].encode(),
        "desk-nonce-bytes":nonce,
        "recovery-routing.json":routing,
        "crew-notes":notes,
        "spool-selected-row-omitted":b"\n".join(line for line in spool.splitlines()
            if b"JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" not in line),
    }
    for f in ROOT.rglob("*"):
        if f.is_file() and f.relative_to(ROOT).as_posix() != "print/spool-reconstruction.log":
            sample_files["member:" + f.relative_to(ROOT).as_posix()] = f.read_bytes()
    samples.update(sample_files)
    return sorted(set(samples.values())),mask,nonce,len(labels),len(samples)


def hkdf(ikm,salt,info,length):
    prk = hmac.digest(salt,ikm,"sha256")
    blocks = []
    previous = b""
    for counter in range(1,(length+31)//32+1):
        previous = hmac.digest(prk,previous+info+bytes((counter,)),"sha256")
        blocks.append(previous)
    return b"".join(blocks)[:length]


def counter_digest(message,algo,initial,length):
    chunks = []
    size = 0
    while size < length:
        item = hashlib.new(algo,message+initial.to_bytes(4,"big")).digest()
        chunks.append(item)
        size += len(item)
        initial += 1
    return b"".join(chunks)[:length]


def emit(message,mask,nonce):
    length = max(LENGTHS)
    yield "SHAKE128",hashlib.shake_128(message).digest(length)
    yield "SHAKE256",hashlib.shake_256(message).digest(length)
    for algo in ("sha256","sha512"):
        for counter in (0,1):
            yield f"{algo}-counter{counter}",counter_digest(message,algo,counter,length)
    for salt,info,name in (
        (b"",b"","plain"),(mask,b"","mask-salt"),
        (nonce,b"RECOVER","nonce-salt"),(mask,b"ESC-N","mask-route")):
        yield f"HKDF-SHA256:{name}",hkdf(message,salt,info,length)


def source_words(seed):
    n = len(seed)
    return {22:seed[n-28:n-24],23:seed[n-32:n-28],
            590:seed[n-2300:n-2296],601:seed[n-2344:n-2340],
            602:seed[n-2348:n-2344]}


def run():
    sources,mask,nonce,label_count,variant_count = source_inputs()
    # In every actual producer, plant a genuine generated B, recover its
    # five source-gate bytes, then reject a flipped first-gate byte.
    for producer,stream in emit(b"PS-261003-0417|ESC-N|synthetic",mask,nonce):
        for n in (606,616,623):
            for leading in (0,3):
                length = 4*n-64-leading
                planted = stream[:length]
                reference = source_words(planted)
                assert len(reference)==5 and all(len(v)==4 for v in reference.values())
                altered = bytearray(planted)
                altered[length-27] ^= 1
                assert source_words(altered)[22] != reference[22]
                assert all(source_words(planted)[i] == v for i,v in reference.items())
    print("PLANTED PASS: all ten producers, 3 seed lengths, both boundary offsets, altered-byte negatives")
    checked = 0
    hit22 = 0
    hit23 = 0
    hit5 = 0
    for source in sources:
        for name,stream in emit(source,mask,nonce):
            for length in LENGTHS:
                w = source_words(stream[:length])
                checked += 1
                if w[22] != K22:
                    continue
                hit22 += 1
                print("K22_MATCH",name,length,hashlib.sha256(source).hexdigest()[:16])
                if w[23] == K23:
                    hit23 += 1
                    if w[590] in K590 and w[601] == K601 and w[602] in K602:
                        hit5 += 1
    print(f"LABELS={label_count} INPUT_VARIANTS={variant_count} DISTINCT_SOURCES={len(sources)}")
    print(f"PRODUCERS=10 LENGTHS=72 COMPLETE_B_ASSIGNMENTS={checked} "
          f"K22_MATCHES={hit22} K22_K23_MATCHES={hit23} ALL_FIVE_MATCHES={hit5}")
    assert checked == len(sources)*10*len(LENGTHS)
    assert (hit22,hit23,hit5)==(0,0,0)


if __name__ == "__main__":
    run()
