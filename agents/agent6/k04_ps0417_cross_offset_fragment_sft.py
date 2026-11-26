#!/usr/bin/env python3
"""Bounded cross-offset reassembly screen for the four PS-0417 source rows.

Exploratory only. Never prints source payloads, the route mask, or candidate
component bytes. The four-fragment search is implemented in the adjacent C++.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROW_RE = re.compile(
    r"^\S+ JOB=(?P<job>\S+) ATTEMPT=(?P<attempt>\d+) "
    r"STATE=(?P<state>\S+) CLASS=(?P<class>\S+) "
    r"PAYLOAD=(?P<payload>[0-9A-F]{32}) DEST=(?P<dest>\S+)$"
)
EXPECTED = [(1, "ACK", "LABEL"), (1, "REQUESTED", "RECOVER"),
            (2, "ACK", "RECOVER"), (3, "REQUESTED", "RECOVER")]


def load(root: Path):
    spool = (root / "evidence/print/spool-reconstruction.log").read_text(encoding="ascii")
    rows = []
    for line in spool.splitlines():
        m = ROW_RE.match(line)
        if m and m.group("job") == "PS-261003-0417":
            rows.append({
                "attempt": int(m.group("attempt")),
                "state": m.group("state"),
                "class": m.group("class"),
                "dest": m.group("dest"),
                "payload": bytes.fromhex(m.group("payload")),
            })
    observed = [(r["attempt"], r["state"], r["class"]) for r in rows]
    if observed != EXPECTED or any(r["dest"] != "bench" for r in rows):
        raise RuntimeError("PS-0417 source-row selector changed; refusing to run")
    route = json.loads((root / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "acceptance.json").read_text())
    return rows, bytes.fromhex(route["K04"]["masked_component"]), bytes.fromhex(acceptance["slot_sha256"]["K04"])


def compositions(total: int, n: int):
    for cuts in itertools.combinations(range(1, total), n - 1):
        prev = 0
        lengths = []
        for c in cuts + (total,):
            lengths.append(c - prev)
            prev = c
        yield tuple(lengths)


def candidate(rows, lengths, choices):
    return b"".join(rows[row]["payload"][off:off + length]
                   for length, (row, off) in zip(lengths, choices))


def run_small(rows, mask, target):
    totals = {}
    for n, planted_lengths, planted_choices in (
        (2, (7, 9), ((1, 2), (3, 5))),
        (3, (5, 6, 5), ((0, 1), (1, 4), (3, 8))),
    ):
        planted = candidate(rows, planted_lengths, planted_choices)
        planted_component = bytes(a ^ b for a, b in zip(planted, mask))
        synthetic_target = hashlib.sha256(planted_component).digest()
        original_hits = synthetic_hits = checked = 0
        for lengths in compositions(16, n):
            options = [[(r, off) for r in range(4) for off in range(17 - length)]
                       for length in lengths]
            for choices in itertools.product(*options):
                payload = candidate(rows, lengths, choices)
                component = bytes(a ^ b for a, b in zip(payload, mask))
                digest = hashlib.sha256(component).digest()
                original_hits += digest == target
                synthetic_hits += digest == synthetic_target
                checked += 1
        if synthetic_hits != 1 or original_hits != 0:
            raise RuntimeError(f"control/target assertion failed for {n}-fragment domain")
        totals[n] = {"candidate_constructions": checked,
                     "synthetic_positive_control_hits": synthetic_hits,
                     "original_commitment_hits": original_hits}
    print(json.dumps({"scope": "2- and 3-fragment contiguous reassembly; arbitrary offsets and split lengths; four source rows; repetition allowed",
                      "results": totals}, indent=2))


def run_shard(rows, mask, target, threads: int, shard: int, shards: int, executable: Path | None):
    cpp = Path(__file__).with_suffix(".cpp")
    with tempfile.TemporaryDirectory(prefix="h17-k04-fragments-") as td:
        td = Path(td)
        input_path = td / "input.bin"
        input_path.write_bytes(b"".join(r["payload"] for r in rows) + mask + target)
        if executable is None:
            compiler = shutil.which("g++")
            if not compiler:
                raise RuntimeError("g++ is required for the 4-fragment exhaustive search")
            exe = td / "search"
            subprocess.run([compiler, "-O3", "-march=native", "-fopenmp",
                            str(cpp), "-lcrypto", "-o", str(exe)], check=True)
        else:
            exe = executable.resolve()
        subprocess.run([str(exe), str(input_path), str(threads), str(shard), str(shards)], check=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--resource-root", type=Path, default=Path("resources"))
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--shard", type=int)
    p.add_argument("--shards", type=int, default=4)
    p.add_argument("--small-only", action="store_true")
    p.add_argument("--exe", type=Path, help="optional precompiled C++ search executable")
    a = p.parse_args()
    rows, mask, target = load(a.resource_root)
    if a.small_only:
        run_small(rows, mask, target)
        return
    if a.shard is None:
        p.error("--shard is required unless --small-only is used")
    run_shard(rows, mask, target, a.threads, a.shard, a.shards, a.exe)


if __name__ == "__main__":
    main()
