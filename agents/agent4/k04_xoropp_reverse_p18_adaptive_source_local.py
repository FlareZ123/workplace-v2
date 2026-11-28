#!/usr/bin/env python3
"""LOCAL ONLY — adaptive exact P16 UNKNOWN -> P18 -> P20 K04 source inversion.

For one retained intact REQUESTED3 two-word later packet, divide a P16
still-UNKNOWN full initial-state region into FOUR exact P18 children
(new state bits 8,9). Only the P18 children still UNKNOWN are divided
into their own FOUR exact P20 grandchildren (bits 10,11). Check complete
SAT states acceptance-FIRST over all 177 legal earlier byte-slip 16-byte
coupons; REQUESTED1 is only optional replay, selected ACK2 withheld.
A remaining P20 UNKNOWN stays unresolved for the P22 utility; no timeout
or unvisited leaf is called excluded.

Synthetic mode reads NO source; original mode enforces no CI, SHA-pinned
non-PDF original text through Agent7, out-of-repo owner-private 0700
parent/0600 ledger and hit escrow, aggregate-only public console.
"""
from __future__ import annotations
import argparse
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import stat
import time

from agents.agent15.k04_laterfirst_p16_p20_source_local import exact_states, P20
from agents.agent7.k04_xoropp_p16_subcube_source_local import read_original, P16
from agents.agent4.k04_xoropp_reverse_p16_source_local import full_coupon_scan_177
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import stream

ROOT = Path(__file__).resolve().parents[2]
P18 = P16 + (8,9)
METHOD = "laterfirst-P16-adaptive-P18-P20-177-byte-v1"
ALLOWED_P16 = {"laterfirst-P16-v1", "laterfirst-P16-144-byte-slip-v2",
               "laterfirst-P16-177-byte-slip-v3"}


def owner_only(path, must_exist=False):
    path = path.expanduser().absolute()
    if path == ROOT or ROOT in path.parents or path.is_symlink():
        raise RuntimeError("Source-private path must be outside repository")
    if not path.parent.is_dir() or path.parent.is_symlink() or (
            stat.S_IMODE(path.parent.stat().st_mode) & 0o077):
        raise RuntimeError("Source-private parent not mode0700")
    if must_exist and not path.is_file():
        raise RuntimeError("Missing source-private ledger")
    if path.exists() and stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise RuntimeError("Source-private file must be mode0600")
    return path


def append(path, value):
    fd = os.open(path, os.O_CREAT | os.O_WRONLY | os.O_APPEND |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "a") as f:
        f.write(json.dumps(value, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def states_with_retry(later, cube, positions, first_ms, retry_ms):
    models, status = exact_states(later, cube, first_ms, positions=positions)
    if status == "unknown" and retry_ms > first_ms:
        additional, status = exact_states(
            later, cube, retry_ms, positions=positions)
        models = list(set(models) | set(additional))
    return models, status


def work_one(job):
    parent, child, first, later, mask, target, endian, order, ms, retry = job
    cube16 = parent | (child << 12)
    sub_status = {"P18_unsat":0, "P18_unknown":0,
                  "P20_unsat":0, "P20_unknown":0}
    discovered = set()
    records = []
    for sub18 in range(4):
        cube18 = cube16 | (sub18 << 16)
        states, terminal = states_with_retry(later, cube18, P18, ms, retry)
        discovered.update(states)
        sub_status["P18_" + terminal] += 1
        branch = {"P18_sub":sub18, "P18_status":terminal, "P20":[]}
        if terminal == "unknown":
            for sub20 in range(4):
                cube20 = cube18 | (sub20 << 18)
                additional, leaf = states_with_retry(
                    later, cube20, P20, ms, retry)
                discovered.update(additional)
                sub_status["P20_" + leaf] += 1
                branch["P20"].append((sub20, leaf))
        records.append(branch)
    checks = hits = earlier = 0
    matches = []
    for state in discovered:
        c, found = full_coupon_scan_177(
            state, mask, target, endian, order, first)
        checks += c["complete_coupons"]
        hits += c["accepts"]
        earlier += c["earlier_replays"]
        matches.extend(found)
    assert checks == 177*len(discovered) and hits == len(matches)
    is_terminal = sub_status["P20_unknown"] == 0
    return {
        "parent": parent, "child": child, "method":METHOD,
        "view": endian+"/"+order, "first_ms":ms, "retry_ms":retry,
        "terminal": "unsat" if is_terminal else "unknown",
        "P18_P20_results":records, "counts":sub_status,
        "states":[[hex(x),hex(y)] for x,y in discovered],
        "full_state_count":len(discovered),
        "full_coupon_checks":checks,"commitment_hits":hits,
        "earlier_replays":earlier
    }, matches


def collect_pending(path, view, start, stop):
    latest = {}
    for line in path.read_text().splitlines():
        row = json.loads(line)
        if row.get("method") not in ALLOWED_P16 or row.get("layout",row.get("view")) != view:
            raise ValueError("Foreign source P16 ledger schema/view")
        parent,child = row["parent"],row["child"]
        if not(0<=parent<4096 and 0<=child<16):
            raise ValueError("Bad P16 partition ID")
        status=row.get("status",row.get("terminal"))
        if status not in ("unsat","unknown"):
            raise ValueError("Bad original P16 terminal")
        latest[(parent,child)] = status
    return sorted(key for key,s in latest.items()
                  if s == "unknown" and start<=key[0]<stop)


def synthetic():
    rng=random.Random(20261128)
    recovered=0
    for _ in range(6):
        state=(rng.getrandbits(64),rng.getrandbits(64))
        later=stream(*state,2)
        cube=sum(((state[0]>>pos)&1)<<j for j,pos in enumerate(P18))
        models,status=states_with_retry(later,cube,P18,350,3000)
        assert state in models and status == "unsat"
        recovered+=1
    print({"synthetic_only": True, "P18_true_full_state_recovered":recovered})


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--synthetic",action="store_true")
    p.add_argument("--P16-ledger",type=Path)
    p.add_argument("--adaptive-ledger",type=Path)
    p.add_argument("--hit-escrow",type=Path)
    p.add_argument("--endian",choices=("big","little"),default="little")
    p.add_argument("--order",choices=("ab","ba"),default="ab")
    p.add_argument("--start-parent",type=int,default=0)
    p.add_argument("--parent-count",type=int,default=128)
    p.add_argument("--first-ms",type=int,default=350)
    p.add_argument("--retry-ms",type=int,default=700)
    p.add_argument("--workers",type=int,default=4)
    a=p.parse_args()
    if a.synthetic:
        return synthetic()
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        p.error("No historical original-source CI")
    if not(0<=a.start_parent<4096 and 1<=a.parent_count<=4096-a.start_parent
           and 100<=a.first_ms<=a.retry_ms<=30000 and 1<=a.workers<=4):
        p.error("Invalid exact bounded interval/solver budget")
    if not all((a.P16_ledger,a.adaptive_ledger,a.hit_escrow)):
        p.error("Three private input/output paths required")
    inp=owner_only(a.P16_ledger,True)
    out=owner_only(a.adaptive_ledger)
    escrow=owner_only(a.hit_escrow)
    if len({inp,out,escrow}) != 3:
        p.error("Private state ledgers must be distinct")
    view=a.endian+"/"+a.order
    pending=collect_pending(inp,view,a.start_parent,a.start_parent+a.parent_count)
    done=set()
    if out.exists():
        for line in out.read_text().splitlines():
            row=json.loads(line)
            if row.get("method") != METHOD or row.get("view") != view:
                raise ValueError("Adaptive ledger method/view changed")
            if row["terminal"]=="unsat":
                done.add((row["parent"],row["child"]))
    first,later,mask,target=read_original(a.endian,a.order)
    tasks=[t for t in pending if t not in done]
    jobs=((parent,child,first,later,mask,target,a.endian,a.order,
           a.first_ms,a.retry_ms) for parent,child in tasks)
    totals={"P16_open_selected":len(pending),
            "P16_previously_deep_closed":len(done & set(pending)),
            "processed":0,"new_exhaustive":0,"still_open":0,
            "P18_unsat":0,"P18_unknown":0,
            "P20_unsat":0,"P20_unknown":0,
            "source_compatible_states":0,
            "full_177_coupon_checks":0,"original_K04_hits":0}
    begun=time.monotonic()
    with mp.Pool(a.workers) as pool:
        for record,matches in pool.imap_unordered(work_one,jobs,chunksize=1):
            for match in matches:
                append(escrow,{"component":match,"method":METHOD})
            append(out,record)
            totals["processed"]+=1
            totals["new_exhaustive"]+=int(record["terminal"]=="unsat")
            totals["still_open"]+=int(record["terminal"]=="unknown")
            for key,value in record["counts"].items():
                totals[key]+=value
            totals["source_compatible_states"]+=record["full_state_count"]
            totals["full_177_coupon_checks"]+=record["full_coupon_checks"]
            totals["original_K04_hits"]+=record["commitment_hits"]
            if totals["processed"]%32==0 or totals["processed"]==len(tasks):
                print("AGGREGATE_ONLY",json.dumps({
                    "view":view, "interval":[a.start_parent,a.start_parent+a.parent_count],
                    "elapsed_s":round(time.monotonic()-begun,2),
                    "totals":totals},sort_keys=True),flush=True)


if __name__=="__main__":
    main()
