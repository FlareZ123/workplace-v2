#!/usr/bin/env python3
"""Solve the corrected CPython/k2496 A7-cut necessary relaxation with cvc5.

This is a bounded seed search, not a claim that CPython was the historical
printer producer. The SMT formula excludes selected PS-0417 ACK2 bytes and
the K04 commitment. Any SAT seed is accepted only if genuine CPython output
reproduces every one of the 132 other complete spool packets; only then is
its withheld row-129 packet checked against the K04 commitment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent27"))
from k04_cpython_a7_cut_smt import forward_sieve, check_forward_real_python
sys.path.insert(0, str(ROOT / "agents/agent1"))
from k04_cpython_k2496_shortforward_source_sft import (
    original_source, synthetic_controls, OFFSET,
)
sys.path.insert(0, str(ROOT / "agents/agent28"))
from k04_cpython_real_output_offset_sft import mt

U = 0xFFFFFFFF
TARGET_ROW = 129
SPOOL = ROOT / "resources/evidence/print/spool-reconstruction.log"
ROUTING = ROOT / "resources/evidence/recovery-routing.json"
ACCEPTANCE = ROOT / "resources/evidence/acceptance.json"
OUTDIR = ROOT / "artifacts/k04-cpython-cvc5"


def source_packets() -> list[bytes]:
    raw = SPOOL.read_bytes()
    packets = [bytes.fromhex(v.decode()) for v in
               re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(packets) == len(mt.STARTS) == 133
    assert mt.STARTS[TARGET_ROW] == 951
    return packets


def with_constraints(smt: str, n: int, blockers: list[list[int]]) -> str:
    extra = [f"(assert (not (= k{n-1} #x00000000)))"]
    for key in blockers:
        terms = [f"(not (= k{j} #x{word:08X}))" for j, word in enumerate(key)]
        extra.append("(assert (or " + " ".join(terms) + "))")
    needle = "(check-sat)"
    assert smt.count(needle) == 1
    return smt.replace(needle, "\n".join(extra) + "\n" + needle, 1)


def parse_word(output: str, name: str) -> int:
    patterns = [
        rf"\({name}\s+#x([0-9a-fA-F]{{8}})\)",
        rf"\({name}\s+#b([01]{{32}})\)",
        rf"\({name}\s+\(_ bv([0-9]+) 32\)\)",
    ]
    for pattern in patterns:
        m = re.search(pattern, output)
        if m:
            return int(m.group(1), 16 if "#x" in pattern else 2 if "#b" in pattern else 10)
    raise ValueError(f"could not parse {name} from cvc5 output: {output[-2000:]}")


def invoke_cvc5(smt: str, timeout_ms: int) -> tuple[str, str]:
    import cvc5

    solver = cvc5.Solver()
    solver.setOption("tlimit-per", str(max(1, timeout_ms)))
    solver.setOption("produce-models", "true")
    solver.setOption("print-success", "true")
    parser = cvc5.InputParser(solver)
    parser.setStringInput(cvc5.InputLanguage.SMT_LIB_2_6, smt, "H17-K04-A7-cut")
    symbols = parser.getSymbolManager()
    output: list[str] = []
    status = "NO_STATUS"
    while True:
        command = parser.nextCommand()
        if command.isNull():
            break
        try:
            result = command.invoke(solver, symbols)
            if result is not None:
                output.append(str(result))
        except Exception as exc:
            output.append(f"COMMAND_ERROR: {type(exc).__name__}: {exc}")
            break
    joined = "".join(output)
    for candidate in ("sat", "unsat", "unknown"):
        if re.search(rf"(?m)^\s*{candidate}\s*$", joined):
            status = candidate.upper()
            break
    version = getattr(cvc5, "__version__", "unknown")
    return status, f"cvc5_version={version}\n{joined}"


def validate_seed(keys: list[int], packets: list[bytes]) -> tuple[int, bytes, list[int]]:
    seed = sum(word << (32 * i) for i, word in enumerate(keys))
    rng = random.Random(seed)
    stop = OFFSET + max(mt.STARTS) + 4
    emitted = [rng.getrandbits(32) for _ in range(stop)]
    predicted = [
        b"".join(emitted[OFFSET + start + lane].to_bytes(4, "little")
                 for lane in range(4))
        for start in mt.STARTS
    ]
    mismatches = [
        row for row, (want, got) in enumerate(zip(packets, predicted))
        if row != TARGET_ROW and want != got
    ]
    return seed, predicted[TARGET_ROW], mismatches


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, choices=(2, 3, 4), required=True)
    ap.add_argument("--stop", type=int, required=True)
    ap.add_argument("--timeout-seconds", type=int, default=3600)
    ap.add_argument("--candidate-limit", type=int, default=8)
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    print(f"MODEL=CPython_integer_seed_n{args.n}_offset{OFFSET}_A7cut_stop{args.stop}")
    print(f"SEED_WORDS={args.n}; RELAXATION_STOP={args.stop}; TARGET_ROW_EXCLUDED={TARGET_ROW}")
    print("RUNNING_GENUINE_CPYTHON_SYNTHETIC_CONTROLS")
    synthetic_controls()
    check_forward_real_python()
    packets = source_packets()
    masks = original_source()
    base = forward_sieve(args.n, args.stop, masks)
    blockers: list[list[int]] = []
    summary = {
        "n": args.n, "stop": args.stop, "offset": OFFSET,
        "target_row_excluded": TARGET_ROW, "controls": 132,
        "status": None, "candidate_count": 0, "result": None,
    }

    for attempt in range(args.candidate_limit):
        remaining = args.timeout_seconds - (time.monotonic() - started)
        if remaining <= 2:
            summary["status"] = "GLOBAL_TIMEOUT"
            break
        smt = with_constraints(base, args.n, blockers)
        smt_path = OUTDIR / f"n{args.n}_stop{args.stop}_attempt{attempt+1}.smt2"
        smt_path.write_text(smt)
        status, output = invoke_cvc5(smt, int(remaining * 1000))
        (OUTDIR / f"n{args.n}_attempt{attempt+1}.txt").write_text(output)
        print(f"ATTEMPT={attempt+1} STATUS={status}")
        print(output[-3000:])
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
            component = bytes(a ^ b for a, b in zip(target_payload, mask))
            digest = hashlib.sha256(component).hexdigest()
            print(f"TARGET_PREDICTED_PAYLOAD={target_payload.hex().upper()}")
            print(f"K04_COMPONENT_SHA256={digest}")
            if digest == acceptance["slot_sha256"]["K04"]:
                print(f"K04_COMPONENT_VERIFIED={component.hex().upper()}")
                summary["result"] = "K04_VERIFIED"
                summary["seed_words"] = [f"{x:08X}" for x in keys]
                summary["target_payload"] = target_payload.hex().upper()
                summary["component"] = component.hex().upper()
                summary["component_sha256"] = digest
            else:
                print("FULL_SOURCE_MATCH_BUT_K04_COMMITMENT_MISMATCH")
                summary["result"] = "FULL_SOURCE_MATCH_COMMITMENT_MISMATCH"
            break

        blockers.append(keys)
        print("RELAXED_CANDIDATE_BLOCKED_AFTER_FULL_SOURCE_MISMATCH")
    else:
        summary["status"] = "CANDIDATE_LIMIT_REACHED"

    summary["elapsed_seconds"] = round(time.monotonic() - started, 3)
    (OUTDIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("SUMMARY=" + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
