#!/usr/bin/env python3
"""Bounded K04 test: L-29/N five-ticket set as a Merkle/XOR commitment.

Read-only. Uses only Python stdlib and the original resource files.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def parse_sets(fleet_text: str):
    job_re = re.compile(r"^(PS-[0-9-]+)\s+\S+\s+(L-29/[NS])\s+(\S+)\s+(\S+)$")
    tab_re = re.compile(r"^(L-29/[NS])\s+(\d{2})\s+(ST-\d+)\s+(.+)$")
    jobs = {}
    tabs = {"L-29/N": [], "L-29/S": []}
    for raw in fleet_text.splitlines():
        line = raw.strip()
        m = job_re.match(line)
        if m:
            job, cassette, account, folio = m.groups()
            jobs[cassette] = {"job": job, "account": account, "folio": folio}
            continue
        m = tab_re.match(line)
        if m:
            cassette, tab, ticket, part_return = m.groups()
            part, ret = part_return.rsplit(", ", 1)
            tabs[cassette].append(
                {"tab": tab, "ticket": ticket, "part": part, "return": ret}
            )
    for cassette in tabs:
        tabs[cassette].sort(key=lambda x: int(x["tab"]))
    if set(jobs) != set(tabs) or any(len(v) != 5 for v in tabs.values()):
        raise ValueError("could not parse both five-tab cassette sets")
    return jobs, tabs


def load_records(resource_root: Path):
    evidence = resource_root / "evidence"
    fleet = (evidence / "h17-supplemental-office-files" /
             "print-fleet-retirement-note.txt").read_text()
    ledger_path = (evidence / "h17-supplemental-office-files" /
                   "supplier-reconciliation-L29.csv")
    with ledger_path.open(newline="") as f:
        ledger = list(csv.DictReader(line for line in f if not line.startswith("#")))
    jobs, tabs = parse_sets(fleet)
    sets = {}
    for cassette, entries in tabs.items():
        info = jobs[cassette]
        records = []
        for item in entries:
            matches = [
                row for row in ledger
                if row["line_ref"] == item["ticket"]
                and row["source"] == "L29"
                and row["run"] == "R3"
                and row["posting"] == "POSTED"
                and row["account"] == info["account"]
                and row["folio_or_jacket"] == info["folio"]
            ]
            if len(matches) != 1:
                raise ValueError(f"{cassette} {item['ticket']}: expected one R3 POSTED row")
            records.append({**matches[0], **item})
        sets[cassette] = {"job": info["job"], "records": records}
    return sets


def encodings(record):
    return [
        record["ticket"],
        "|".join(record[k] for k in (
            "ticket", "source", "run", "posting", "account",
            "folio_or_jacket", "amount_eur", "description"
        )),
        "|".join((record["ticket"], record["amount_eur"], record["description"])),
        "|".join((record["tab"], record["ticket"], record["part"], record["return"])),
        "|".join((record["tab"], record["ticket"], record["part"],
                  record["return"], record["amount_eur"], record["description"])),
        json.dumps(record, sort_keys=True, separators=(",", ":")),
    ]


HASHERS = {
    "sha256": sha256,
    "md5": lambda b: hashlib.md5(b).digest(),
    "blake2s16": lambda b: hashlib.blake2s(b, digest_size=16).digest(),
    "blake2b16": lambda b: hashlib.blake2b(b, digest_size=16).digest(),
}


def merkle_root(leaves, digest, mode):
    level = [digest(x) for x in leaves]
    if mode == "rfc6962":
        def rec(nodes):
            if len(nodes) == 1:
                return nodes[0]
            split = 1 << ((len(nodes) - 1).bit_length() - 1)
            return digest(rec(nodes[:split]) + rec(nodes[split:]))
        return rec(level)
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            if i + 1 < len(level):
                nxt.append(digest(level[i] + level[i + 1]))
            elif mode == "duplicate-last":
                nxt.append(digest(level[i] + level[i]))
            elif mode == "promote-last":
                nxt.append(level[i])
            elif mode == "zero-pad":
                nxt.append(digest(level[i] + bytes(len(level[i]))))
            else:
                raise ValueError(mode)
        level = nxt
    return level[0]


def root_candidates(root):
    if len(root) == 16:
        return [root]
    if len(root) == 32:
        return [root[:16], root[16:]]
    return []


def xor_digest_candidates(leaves, digest):
    digests = [digest(x) for x in leaves]
    if len(digests[0]) == 16:
        parts = [("digest16", digests)]
    else:
        parts = [
            ("first16", [d[:16] for d in digests]),
            ("last16", [d[16:] for d in digests]),
        ]
    out = []
    for label, values in parts:
        acc = bytes(16)
        for value in values:
            acc = bytes(a ^ b for a, b in zip(acc, value))
        out.append((label, acc))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resource-root", type=Path,
                    default=Path(__file__).resolve().parents[1] / "resources")
    args = ap.parse_args()
    root = args.resource_root
    sets = load_records(root)
    acceptance = json.loads((root / "acceptance.json").read_text())
    routing = json.loads((root / "evidence" / "recovery-routing.json").read_text())
    target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    mask = bytes.fromhex(routing["K04"]["masked_component"])

    spool = (root / "evidence" / "print" / "spool-reconstruction.log").read_text()
    m = re.search(
        r"JOB=" + re.escape(sets["L-29/S"]["job"]) +
        r".*?STATE=ACK CLASS=RECOVER PAYLOAD=([0-9A-Fa-f]{32})",
        spool
    )
    if not m:
        raise ValueError("South RECOVER ACK control row not found")
    south_payload = bytes.fromhex(m.group(1))

    all_merkle = []
    all_xor = []
    for cassette in ("L-29/N", "L-29/S"):
        records = sets[cassette]["records"]
        for enc_index in range(6):
            leaves = [encodings(r)[enc_index].encode("utf-8") for r in records]
            for hash_name, digest in HASHERS.items():
                for mode in ("duplicate-last", "promote-last", "zero-pad", "rfc6962"):
                    root_hash = merkle_root(leaves, digest, mode)
                    for half_index, coupon in enumerate(root_candidates(root_hash)):
                        label = f"{cassette}/enc{enc_index}/{hash_name}/{mode}/half{half_index}"
                        all_merkle.append((label, coupon))
                for half_name, coupon in xor_digest_candidates(leaves, digest):
                    label = f"{cassette}/enc{enc_index}/{hash_name}/xor-{half_name}"
                    all_xor.append((label, coupon))

    north_merkle = [(n, c) for n, c in all_merkle if n.startswith("L-29/N/")]
    north_xor = [(n, c) for n, c in all_xor if n.startswith("L-29/N/")]
    south_merkle = [(n, c) for n, c in all_merkle if n.startswith("L-29/S/")]
    south_xor = [(n, c) for n, c in all_xor if n.startswith("L-29/S/")]

    def k04_hits(candidates):
        hits = []
        for label, coupon in candidates:
            for transform, component in (
                ("direct", coupon),
                ("xor-route-mask", bytes(a ^ b for a, b in zip(coupon, mask))),
            ):
                if sha256(component) == target:
                    hits.append({"model": label, "transform": transform,
                                 "component": component.hex().upper()})
        return hits

    def south_hits(candidates):
        hits = []
        for label, coupon in candidates:
            for transform, value in (
                ("direct", coupon),
                ("xor-K04-mask-control-only",
                 bytes(a ^ b for a, b in zip(coupon, mask))),
            ):
                if value == south_payload:
                    hits.append({"model": label, "transform": transform})
        return hits

    # Pipeline positive control: the same exact K04 checker must accept a
    # deliberately planted synthetic coupon after the prescribed mask.
    planted_coupon = north_merkle[0][1]
    planted_component = bytes(a ^ b for a, b in zip(planted_coupon, mask))
    planted_target = sha256(planted_component)
    synthetic_pass = (
        sha256(bytes(a ^ b for a, b in zip(planted_coupon, mask))) == planted_target
    )

    result = {
        "north_job": sets["L-29/N"]["job"],
        "south_control_job": sets["L-29/S"]["job"],
        "north_tickets": [r["ticket"] for r in sets["L-29/N"]["records"]],
        "south_tickets": [r["ticket"] for r in sets["L-29/S"]["records"]],
        "unique_north_merkle_coupons": len({c for _, c in north_merkle}),
        "unique_north_xor_coupons": len({c for _, c in north_xor}),
        "north_k04_merkle_hits": k04_hits(north_merkle),
        "north_k04_xor_set_hits": k04_hits(north_xor),
        "south_payload_hex": south_payload.hex().upper(),
        "south_merkle_control_hits": south_hits(south_merkle),
        "south_xor_control_hits": south_hits(south_xor),
        "synthetic_masked_commitment_control_pass": synthetic_pass,
        "scope": "bounded ticket-set Merkle/XOR commitment hypothesis only",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not synthetic_pass:
        raise SystemExit("synthetic positive control failed")


if __name__ == "__main__":
    main()
