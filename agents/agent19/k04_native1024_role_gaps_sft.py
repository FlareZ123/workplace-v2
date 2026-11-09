"""H-17: source-only 1024-bit native printer issuer, role-dependent skip schedules.

Run: python agents/agent19/k04_native1024_role_gaps_sft.py resources
Reuses published full-state inverse SFTs in the same agent directory.
No target commitment or disputed ACK2 is loaded.
"""
from __future__ import annotations

import hashlib
import itertools
import random
import re
import sys
from pathlib import Path

import k04_xorshift1024_star_source_inverse_sft as xs
import k04_xoroshiro1024_source_inverse_sft as xr

CLASSES = ("LABEL", "STORES", "RECOVER")
DESTS = ("store", "bench", "desk")
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def read_roles(root: Path):
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = re.findall(
        rb"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) "
        rb"CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)", raw
    )
    assert len(rows) == 133
    assert [int(v[0]) for v in rows[:128]] == list(range(300, 428))
    return ([r[3].decode() for r in rows[:128]],
            [r[5].decode() for r in rows[:128]])


def positions(classes, dests, class_cost, dest_cost):
    stages, current = [], 0
    for role, dest in zip(classes[:24], dests[:24]):
        stages.extend((current, current + 1))
        current += 2 + class_cost[role] + dest_cost[dest]
    return tuple(stages)


def schedules(classes, dests):
    seen = set()
    counts = {}
    for mode in ("class", "dest", "add01"):
        total = 0
        values = range(9) if mode != "add01" else range(2)
        repeats = 3 if mode != "add01" else 6
        for cost in itertools.product(values, repeat=repeats):
            cc, dc = dict.fromkeys(CLASSES, 0), dict.fromkeys(DESTS, 0)
            if mode == "class":
                cc = dict(zip(CLASSES, cost))
            elif mode == "dest":
                dc = dict(zip(DESTS, cost))
            else:
                cc, dc = dict(zip(CLASSES, cost[:3])), dict(zip(DESTS, cost[3:]))
            stages = positions(classes, dests, cc, dc)
            if stages in seen:
                continue
            seen.add(stages)
            total += 1
            yield mode, cost, stages
        counts[mode] = total
        print("SCHEDULE", mode, total, flush=True)
    assert counts == {"class": 729, "dest": 720, "add01": 36}


def main():
    root = (Path(sys.argv[1]) if len(sys.argv) > 1
            else Path(__file__).resolve().parents[2] / "resources")
    classes, dests = read_roles(root)
    layouts = list(schedules(classes, dests))
    assert len(layouts) == 1485
    source_xs = xs.source_words(root)
    source_xr = xr.original_views(root)
    assert len(source_xs) == len(source_xr) == 4

    planted = [random.Random(20261109 + i).getrandbits(64) for i in range(16)]
    for family, variant, multiplier in (
        ("xorshift1024", "M8", 1181783497276652981),
        ("xorshift1024", "phi", 0x9e3779b97f4a7c13),
        ("xoroshiro1024", "star", None),
        ("xoroshiro1024", "starstar", None),
    ):
        for select in (555, 1000, -1):
            stages = list(layouts[select][2])
            if family == "xorshift1024":
                synthetic = xs.emit(planted, stages, multiplier)
                recovered, bad, rank = xs.recover(synthetic, stages, multiplier)
            else:
                synthetic = xr.emit(planted, stages, variant)
                recovered, bad, rank = xr.invert(synthetic, stages, variant)
            assert bad is None and rank == 1024 and recovered == planted

        count = 0
        for _, _, stage_tuple in layouts:
            stages = list(stage_tuple)
            for view in (source_xs if family == "xorshift1024" else source_xr):
                if family == "xorshift1024":
                    _, bad, _ = xs.recover(view, stages, multiplier)
                else:
                    _, bad, _ = xr.invert(view, stages, variant)
                assert bad is not None, (
                    f"unexpected real source-compatible {family}/{variant} {stages}"
                )
                count += 1
        assert count == 5940
        print("MODEL", family, variant,
              "original_contradictions", count,
              "synthetic_1024bit_inverse_positives", 3,
              "original_selected_K04", "UNRECOVERED", flush=True)


if __name__ == "__main__":
    main()
