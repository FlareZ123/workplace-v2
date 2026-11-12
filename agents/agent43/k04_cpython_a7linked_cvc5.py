#!/usr/bin/env python3
"""Tighter CPython A7-linked short-forward source inversion.

Unlike the A7-cut relaxation, this model also constrains A7 to the first
seven exact CPython init_by_array updates from integer seed words. It stops
before the 624-word wrap, so it does not inherit the old full-model wrap bug.
Every SAT candidate is checked against all 132 intact packets before K04 is
computed or its commitment is queried.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys, time
from pathlib import Path

from k04_cpython_a7cut_cvc5 import (
    ROOT, TARGET_ROW, ROUTING, ACCEPTANCE, OFFSET,
    source_packets, synthetic_controls, check_forward_real_python,
    original_source, forward_sieve, with_constraints, invoke_cvc5,
    parse_word, validate_seed,
)
sys.path.insert(0, str(ROOT / "agents/agent27"))
from k04_cpython_a7_cut_smt import G, F1

OUTDIR = ROOT / "artifacts/k04-cpython-a7linked"


def link_a7_to_seed(smt: str, n: int) -> str:
    h = lambda x: f"#x{x & 0xFFFFFFFF:08X}"
    lines = [f"(define-fun a0 () (_ BitVec 32) {h(G[0])})"]
    for i in range(1, 8):
        j = (i - 1) % n
        prev = f"a{i-1}"
        mix = f"(bvmul {h(F1)} (bvxor {prev} (bvlshr {prev} {h(30)})))"
        expr = f"(bvadd (bvxor {h(G[i])} {mix}) k{j} {h(j)})"
        lines.append(f"(define-fun a{i}_calc () (_ BitVec 32) {expr})")
        if i < 7:
            lines.append(f"(define-fun a{i} () (_ BitVec 32) a{i}_calc)")
    lines.append("(assert (= a7_calc a7))")
    marker = re.search(r"\(define-fun s7 \(\) \(_ BitVec 32\) #x[0-9A-F]{8}\)", smt)
    assert marker, "could not locate the source-pinned S7 declaration"
    return smt[:marker.end()] + "\n" + "\n".join(lines) + smt[marker.end():]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, choices=(2, 3, 4), required=True)
    ap.add_argument("--stop", type=int, required=True)
    ap.add_argument("--timeout-seconds", type=int, default=3600)
    ap.add_argument("--candidate-limit", type=int, default=8)
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    print(f"MODEL=CPython_integer_seed_n{args.n}_offset{OFFSET}_A7_LINKED_stop{args.stop}")
    print(f"TARGET_ROW_EXCLUDED={TARGET_ROW}; EXACT_FIRST_PASS_ROUNDS=1..7")
    synthetic_controls()
    check_forward_real_python()
    packets = source_packets()
    masks = original_source()
    base = link_a7_to_seed(forward_sieve(args.n, args.stop, masks), args.n)
    blockers = []
    summary = {"n":args.n,"stop":args.stop,"offset":OFFSET,"target_row_excluded":TARGET_ROW,
               "controls":132,"status":None,"candidate_count":0,"result":None}

    for attempt in range(args.candidate_limit):
        remaining = args.timeout_seconds - (time.monotonic() - started)
        if remaining <= 2:
            summary["status"] = "GLOBAL_TIMEOUT"
            break
        smt = with_constraints(base, args.n, blockers)
        (OUTDIR / f"n{args.n}_attempt{attempt+1}.smt2").write_text(smt)
        status, output = invoke_cvc5(smt, int(remaining * 1000))
        (OUTDIR / f"n{args.n}_attempt{attempt+1}.txt").write_text(output)
        print(f"ATTEMPT={attempt+1} STATUS={status}")
        print(output[-2500:])
        summary["status"] = status
        if status != "SAT":
            break

        keys = [parse_word(output, f"k{j}") for j in range(args.n)]
        summary["candidate_count"] += 1
        print("SEED_WORDS=" + ",".join(f"{x:08X}" for x in keys))
        seed, target_payload, mismatches = validate_seed(keys, packets)
        print(f"FULL_132_PACKET_MATCHES={132-len(mismatches)}/132")
        if not mismatches:
            routing = json.loads(ROUTING.read_text())
            acceptance = json.loads(ACCEPTANCE.read_text())
            mask = bytes.fromhex(routing["K04"]["masked_component"])
            component = bytes(a ^ b for a,b in zip(target_payload, mask))
            digest = hashlib.sha256(component).hexdigest()
            print(f"TARGET_PREDICTED_PAYLOAD={target_payload.hex().upper()}")
            print(f"K04_COMPONENT_SHA256={digest}")
            if digest == acceptance["slot_sha256"]["K04"]:
                print(f"K04_COMPONENT_VERIFIED={component.hex().upper()}")
                summary.update(result="K04_VERIFIED",seed_words=[f"{x:08X}" for x in keys],
                               target_payload=target_payload.hex().upper(),
                               component=component.hex().upper(),component_sha256=digest)
            else:
                summary["result"] = "FULL_SOURCE_MATCH_COMMITMENT_MISMATCH"
            break
        blockers.append(keys)
        print("RELAXED_CANDIDATE_BLOCKED_AFTER_FULL_SOURCE_MISMATCH")

    summary["elapsed_seconds"] = round(time.monotonic()-started,3)
    (OUTDIR / f"n{args.n}_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("SUMMARY="+json.dumps(summary,sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
