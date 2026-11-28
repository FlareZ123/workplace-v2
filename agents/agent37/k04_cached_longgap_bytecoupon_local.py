#!/usr/bin/env python3
"""Local-only K04 original commitment reducer for cached firstpacket states.

Checks every 16-byte serialized coupon from a cached full xoroshiro128++
state in 0..65535 whole-packet skip positions and 0..15 extra byte slips.
The original K04 commitment is evaluated BEFORE any REQUESTED3 holdout;
later replay counts are separate and never filter true commitment hits.

Crucially, this is a cheap full-output reducer, NOT a second SAT inversion.
Only read specifically named non-PDF original ZIP members; all source
bytes, state models and verified component bytes remain private.
"""
from __future__ import annotations
import argparse, hashlib, json, os, random, stat, sys, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import stream
from agents.agent7.k04_xoropp_byte_slip_reducer import escrow_hits

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
P12 = (0,1,2,3,22,23,24,25,45,46,47,48)
M64 = (1 << 64) - 1


def serialized(state, endian, order, gap_limit):
    ys = stream(*state, 2 * (gap_limit + 4))
    if order == "ba":
        ys = [ys[i+1] if i%2==0 else ys[i-1] for i in range(len(ys))]
    return b"".join(x.to_bytes(8, endian) for x in ys)


def reduce_state(state, mask, target, endian, order, maxgap):
    if len(mask) != 16 or len(target) != 64:
        raise ValueError("Malformed source-independent component test")
    data = serialized(state, endian, order, maxgap)
    hits = []
    checked = 0
    for gap in range(maxgap+1):
        start = 16*(gap+1)
        for slip in range(16):
            coupon = data[start+slip:start+slip+16]
            if len(coupon) != 16:
                raise AssertionError("Partial coupon outside hypothesized stream")
            part = bytes(x^y for x,y in zip(coupon,mask))
            checked += 1
            if hashlib.sha256(part).hexdigest() == target:
                hits.append(part)
    return checked, hits


def source_inputs(path):
    with zipfile.ZipFile(path) as z:
        def pinned(name, digest):
            if name.lower().endswith(".pdf"):
                raise RuntimeError("Restricted PDF forbidden")
            raw = z.read(name)
            if hashlib.sha256(raw).hexdigest()!=digest:
                raise RuntimeError("Original source SHA256 mismatch")
            return raw
        spool = pinned("evidence/print/spool-reconstruction.log", SPOOL_SHA)
        route = pinned("evidence/recovery-routing.json", ROUTE_SHA)
        checks = pinned("acceptance.json", ACCEPT_SHA)
    rows = spool.decode().splitlines()
    def requested(attempt):
        found = [row for row in rows
            if "JOB=PS-261003-0417 " in row
            and f"ATTEMPT={attempt} " in row
            and "STATE=REQUESTED " in row
            and "CLASS=RECOVER " in row]
        if len(found) != 1:
            raise ValueError("Nonunique intact requested original")
        import re
        m = re.search(r"\bPAYLOAD=([0-9A-F]{32})\b", found[0])
        if m is None:
            raise ValueError("No intact packet")
        return bytes.fromhex(m.group(1))
    first, later = requested(1), requested(3)
    mask = bytes.fromhex(json.loads(route)["K04"]["masked_component"])
    target = json.loads(checks)["slot_sha256"]["K04"]
    return first, later, mask, target


def read_private_receipt(path, first, endian, order):
    path = path.expanduser()
    if path.is_symlink() or path.parent.is_symlink():
        raise PermissionError("Private receipt path cannot be a symlink")
    if not path.is_file() or stat.S_IMODE(path.stat().st_mode)&0o077:
        raise PermissionError("Private receipt must be chmod 0600")
    if stat.S_IMODE(path.parent.stat().st_mode)&0o077:
        raise PermissionError("Private state directory must be chmod 0700")
    with path.open(encoding="ascii") as f:
        data = json.load(f)
    meta = data["meta"]
    source = meta.get("source_sha256", meta.get("spool_sha256"))
    firsthash = meta.get("first_sha256", meta.get("firstpacket_sha256"))
    view = meta.get("serializer", meta.get("view"))
    if source != SPOOL_SHA or firsthash != hashlib.sha256(first).hexdigest():
        raise ValueError("Cached state source/firstpacket checksum mismatch")
    if view != endian+"/"+order:
        raise ValueError("Cached state serializer mismatch")
    if not 0<=data["parent"]<4096 or len(data["children"])!=16:
        raise ValueError("Invalid complete parent receipt")
    if sorted(c["child"] for c in data["children"])!=list(range(16)):
        raise ValueError("Duplicate or missing P16 child")
    obs = [int.from_bytes(first[i:i+8], endian) for i in (0,8)]
    if order=="ba": obs.reverse()
    states=set()
    for c in data["children"]:
        terminal = c.get("terminal", c.get("status"))
        if terminal not in ("unknown","unsat"):
            raise ValueError("Invalid model terminal")
        sub = c["child"]
        if not 0<=sub<16: raise ValueError("Invalid P16 child")
        for pair in c["states"]:
            a,b=pair
            if not(type(a)==type(b)==int and 0<=a<=M64 and 0<=b<=M64):
                raise ValueError("Malformed cached generator state")
            if stream(a,b,2)!=obs:
                raise ValueError("Cached state fails exact firstpacket replay")
            p12=sum(((a>>pos)&1)<<j for j,pos in enumerate(P12))
            p16=sum(((a>>pos)&1)<<j for j,pos in enumerate((4,5,6,7)))
            if (p12,p16)!=(data["parent"],sub):
                raise ValueError("Cached state belongs to another exact cube")
            states.add((a,b))
    if bool(data["sealed"]) != all(c.get("terminal",c.get("status"))=="unsat" for c in data["children"]):
        raise ValueError("Receipt sealed flag contradicts child disposition")
    return states,bool(data["sealed"])


def synthetic():
    r=random.Random(104408)
    a,b=r.getrandbits(64),r.getrandbits(64)
    mask=r.randbytes(16)
    gap,slip=65000,15
    data=serialized((a,b),"little","ab",65535)
    pos=16*(gap+1)+slip
    truth=bytes(x^y for x,y in zip(data[pos:pos+16],mask))
    target=hashlib.sha256(truth).hexdigest()
    checked,hits=reduce_state((a,b),mask,target,"little","ab",65535)
    assert hits==[truth] and checked==1048576
    false=hashlib.sha256(b"poisoned synthetic commitment").hexdigest()
    _,poisoned=reduce_state((a,b),mask,false,"little","ab",3)
    assert not poisoned
    print(json.dumps({
        "synthetic_only":True,"complete_target_hit":True,
        "planted_gap":65000,"planted_byte_slip":15,
        "original_values_read":False,"full_candidates":checked,
        "negative_poison_control":True,
    },sort_keys=True))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--synthetic",action="store_true")
    p.add_argument("--zip",type=Path)
    p.add_argument("--receipt",type=Path)
    p.add_argument("--escrow",type=Path)
    p.add_argument("--endian",choices=("little","big"),default="little")
    p.add_argument("--order",choices=("ab","ba"),default="ab")
    p.add_argument("--max-gap",type=int,default=65535)
    a=p.parse_args()
    if a.synthetic: return synthetic()
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        p.error("Original source processing prohibited in public CI")
    if a.zip is None or a.receipt is None or a.escrow is None:
        p.error("Original ZIP, private state receipt and escrow are required")
    if not 0<=a.max_gap<=65535: p.error("Bounded 16-bit gap domain required")
    escrow=a.escrow.expanduser().resolve()
    if escrow.parent != a.receipt.parent.resolve():
        p.error("Hit escrow must stay in private receipt directory")
    first, later, mask, target=source_inputs(a.zip)
    states,sealed=read_private_receipt(a.receipt,first,a.endian,a.order)
    total=0;matches=0
    for state in states:
        checked,hits=reduce_state(state,mask,target,a.endian,a.order,a.max_gap)
        total+=checked;matches+=len(hits)
        if hits: escrow_hits(escrow,hits)
    print(json.dumps({
        "local_private_original":True,
        "receipt_sealed":sealed,"source_states":len(states),
        "complete_coupon_SHA_checks":total,"original_commitment_hits":matches,
        "max_whole_packet_gaps":a.max_gap,"byte_slips":16,
        "unresolved_state_search_remains":not sealed,
        "source_or_candidate_values_exposed":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
