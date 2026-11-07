#!/usr/bin/env python3
"""Source-pinned whole-packet test of independent xorshift128 streams per queue partition."""
from __future__ import annotations
import configparser
import hashlib
import json
import random
import re
from collections import defaultdict
from pathlib import Path

MASK32=(1<<32)-1
SOURCE_SHA256="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TARGET_INDEX=129
LATE_CONTROLS={131,132}


def step(state):
    x,y,z,w=state
    t=(x^((x<<11)&MASK32))&MASK32
    out=(w^(w>>19)^t^(t>>8))&MASK32
    return (y,z,w,out),out


def parse_words(payload,endian,reverse):
    chunks=[payload[i:i+4] for i in range(0,16,4)]
    if reverse: chunks.reverse()
    return [int.from_bytes(x,endian) for x in chunks]


def serialize_words(words,endian,reverse):
    chunks=[x.to_bytes(4,endian) for x in words]
    if reverse: chunks.reverse()
    return b"".join(chunks)


def group_key(record,grouping):
    if grouping=="DEST": return record["dest"]
    if grouping=="CLASS": return record["class"]
    if grouping=="CLASSxDEST": return (record["class"],record["dest"])
    raise ValueError(grouping)


def predict(records,grouping,endian,reverse):
    groups=defaultdict(list)
    for i,r in enumerate(records): groups[group_key(r,grouping)].append((i,r))
    predictions={}
    checked=exact=late_checked=late_exact=0
    for members in groups.values():
        _,first=members[0]
        assert first["payload"] is not None
        state=tuple(parse_words(first["payload"],endian,reverse))
        for i,r in members[1:]:
            words=[]
            for _ in range(4):
                state,out=step(state)
                words.append(out)
            predicted=serialize_words(words,endian,reverse)
            predictions[i]=predicted
            if i==TARGET_INDEX: continue
            assert r["payload"] is not None
            hit=predicted==r["payload"]
            checked+=1
            exact+=int(hit)
            if i in LATE_CONTROLS:
                late_checked+=1
                late_exact+=int(hit)
    return predictions,checked,exact,late_checked,late_exact


def select_target(lines,route_job):
    """Select latest RECOVER ACK from headers only; never read PAYLOAD or DEST."""
    rx=re.compile(r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+)(?=\s|$)")
    candidates=[]
    for i,line in enumerate(lines):
        m=rx.match(line)
        if m is None: continue
        ts,job,attempt,state,cl=m.groups()
        if job==route_job and state=="ACK" and cl=="RECOVER":
            candidates.append((int(attempt),ts,i))
    if not candidates: raise ValueError("no route-selected RECOVER ACK")
    return max(candidates,key=lambda x:(x[0],x[1]))[2]


def load_records(root):
    evidence=root/"resources"/"evidence"
    raw=(evidence/"print"/"spool-reconstruction.log").read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    assert sha==SOURCE_SHA256,(sha,SOURCE_SHA256)
    labels=configparser.ConfigParser()
    labels.read(evidence/"archive-labels.ini",encoding="utf-8")
    route_job=labels["printer_routes_2026-09-01_to_2026-10-03"]["ESC-N"]
    lines=[x for x in raw.decode("ascii").splitlines() if x.startswith("2026-")]
    assert len(lines)==133
    target=select_target(lines,route_job)
    assert target==TARGET_INDEX
    records=[]
    for i,line in enumerate(lines):
        h=re.match(r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+)(?=\s|$)",line)
        assert h is not None
        ts,job,attempt,state,cl=h.groups()
        d=re.search(r"(?:^|\s)DEST=(\S+)(?=\s|$)",line)
        assert d is not None
        payload=None
        if i!=target:
            p=re.search(r"(?:^|\s)PAYLOAD=([0-9A-F]{32})(?=\s|$)",line)
            assert p is not None
            payload=bytes.fromhex(p.group(1))
            assert len(payload)==16
        records.append({"timestamp":ts,"job":job,"attempt":int(attempt),
                        "state":state,"class":cl,"dest":d.group(1),"payload":payload})
    assert (records[129]["job"],records[129]["attempt"],records[129]["state"],
            records[129]["class"],records[129]["dest"])==(
                "PS-261003-0417",2,"ACK","RECOVER","bench")
    assert (records[131]["job"],records[131]["attempt"],records[131]["state"],
            records[131]["class"],records[131]["dest"])==(
                "PS-261003-0448",1,"ACK","RECOVER","desk")
    assert (records[132]["job"],records[132]["attempt"],records[132]["state"],
            records[132]["class"],records[132]["dest"])==(
                "PS-261003-0420",2,"ACK","RECOVER","bench")
    assert records[TARGET_INDEX]["payload"] is None
    return records


def synthetic_control(grouping,endian,reverse):
    rng=random.Random(20261107)
    states={}
    records=[]
    for i in range(133):
        r={"class":("LABEL","STORES","RECOVER")[i%3],
           "dest":("bench","store","desk")[(i//3)%3]}
        key=group_key(r,grouping)
        if key not in states: states[key]=tuple(rng.getrandbits(32) for _ in range(4))
        words=[]
        for _ in range(4):
            states[key],out=step(states[key])
            words.append(out)
        r["payload"]=serialize_words(words,endian,reverse)
        records.append(r)
    predictions,checked,exact,late_checked,late_exact=predict(
        records,grouping,endian,reverse)
    assert predictions[TARGET_INDEX]==records[TARGET_INDEX]["payload"]
    assert exact==checked and late_checked==2 and late_exact==2


def main():
    root=Path(__file__).resolve().parents[2]
    records=load_records(root)
    results=[]
    for grouping in ("DEST","CLASS","CLASSxDEST"):
        for endian in ("little","big"):
            for reverse in (False,True):
                synthetic_control(grouping,endian,reverse)
                _,checked,exact,late_checked,late_exact=predict(
                    records,grouping,endian,reverse)
                results.append({
                    "grouping":grouping,"endian":endian,"reverse_words":reverse,
                    "checked_excluding_target":checked,"exact_matches":exact,
                    "late_controls_checked":late_checked,
                    "late_control_exact_matches":late_exact,
                    "synthetic_positive":"PASS"})
    print(json.dumps({
        "source_sha256":SOURCE_SHA256,"packet_count":len(records),
        "header_only_target_index":TARGET_INDEX,"target_payload_parsed":False,
        "late_control_indices":sorted(LATE_CONTROLS),
        "hypothesis":"independent xorshift128 state per explicit queue partition",
        "partition_maps":["DEST","CLASS","CLASSxDEST"],
        "serializations":["little-endian words","big-endian words"],
        "word_orders":["forward","reversed"],"synthetic_controls":"PASS",
        "original_results":results,"target_commitment_consulted":False},indent=2))


if __name__=="__main__": main()
