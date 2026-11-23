"""K04 all42-source compatible 98-word CPython seeds: exact residue completion.

The first complete 624-offset × n1..623 inverse finds n=98 possible only at
29 output offsets. Reconstruct all 98 *actual* CPython init_by_array key words
when the source-derived key-term intersections uniquely determine them.
Only complete exact source-matching seeds produce a selected 16-byte coupon;
a partial seed is never padded or guessed. Original selected ACK2 is never read.

Run: python agents/agent50/k04_all42_n98_seed_completion_sft.py
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from k04_all42_cpython_shortseed_sft import (
    ROOT, STAGES, SOURCE_SHA, U, projected_initial_state, planted,
    term_domains, consistent
)

SEED_WORDS = 98


def key_residue_domains(terms: list[tuple[int,set[int]]], n: int):
    words: dict[int, set[int]] = {}
    for j, allowed in terms:
        residue = j % n
        candidates = {(t - residue) & U for t in allowed}
        if residue in words:
            words[residue].intersection_update(candidates)
        else:
            words[residue] = candidates
    return words


def source_packets():
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)$",
        raw, re.M,
    )
    assert len(rows) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    return [None if i == 129 else bytes.fromhex(row[5].decode())
            for i,row in enumerate(rows)]


def maybe_full_seed(offset: int, domains: dict[int,set[int]],
                    packets: list[bytes | None]):
    # Enumerate only if all seed words are constrained and total exact
    # combinations are <= 4096. No arbitrary default for absent residues.
    if len(domains) != SEED_WORDS:
        return []
    total = 1
    for vals in domains.values():
        total *= len(vals)
        if total > 4096:
            return []
    allwords = [sorted(domains[i]) for i in range(SEED_WORDS)]
    matched: list[dict] = []
    for wordtuple in itertools.product(*allwords):
        seed = sum(v << (i*32) for i,v in enumerate(wordtuple))
        rng = random.Random(seed)
        emitted = [rng.getrandbits(32) for _ in range(offset + STAGES[-1] + 4)]
        expected = [None if r ==129 else b"".join(
            emitted[offset+start+j].to_bytes(4, "little") for j in range(4))
            for r,start in enumerate(STAGES)]
        if any(a is not None and a != b for a,b in zip(packets,expected)):
            continue
        raw_coupon = b"".join(emitted[offset+STAGES[129]+j].to_bytes(4, "little")
                              for j in range(4))
        route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
        acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
        component = bytes(x^y for x,y in zip(
            raw_coupon, bytes.fromhex(route["K04"]["masked_component"])))
        matched.append({
            "source_matched": True,
            "original_K04_SHA_PASS":
                hashlib.sha256(component).hexdigest() ==
                acceptance["slot_sha256"]["K04"],
            "coupon": raw_coupon.hex().upper(),
            "component": component.hex().upper(),
            "output_offset":offset,
        })
    return matched


def main():
    positive = 0
    for offset in (0, 7, 586):
        seed = sum(((0x12345678 ^ i*0x10101) & U) << (32*i)
                   for i in range(SEED_WORDS))
        state, packet = planted(seed, offset)
        projected = projected_initial_state(offset, packet)
        assert all(value == (mask & full)
                   for (mask, value), full in zip(projected, state))
        rows = term_domains(projected, 0)
        allowed = key_residue_domains(rows, SEED_WORDS)
        assert all(((seed >> (r*32)) & U) in v for r,v in allowed.items())
        assert consistent(rows, SEED_WORDS)
        positive += 1
    assert positive == 3
    print("PLANTED_N98_KEY_DOMAIN_POSITIVES", positive, "PASS", flush=True)
    original = source_packets()
    survivors = []
    recovered = []
    for offset in range(624):
        states = projected_initial_state(offset, original)
        if (states[0][1] ^ 0x80000000) & states[0][0]:
            continue
        terms = term_domains(states, 0)
        if not consistent(terms, SEED_WORDS):
            continue
        domains = key_residue_domains(terms, SEED_WORDS)
        assert all(domains.values())
        known = sum(len(vals)==1 for vals in domains.values())
        absent = SEED_WORDS-len(domains)
        ambiguous = sum(len(vals)>1 for vals in domains.values())
        if len(survivors) < 32:
            print("SOURCE_N98", offset,
                  "KEY_RESIDUES_PRESENT",len(domains),
                  "UNIQUE_WORDS",known,
                  "UNSEEN_WORDS",absent,
                  "AMBIGUOUS_WORDS",ambiguous, flush=True)
        survivors.append((offset,known,absent,ambiguous))
        recovered.extend(maybe_full_seed(offset, domains, original))
    assert len(survivors)==29, len(survivors)
    print("RESULT",json.dumps({
        "selected_ACK2_payload_decoded":False,
        "source_sha256":SOURCE_SHA,
        "seed_words":SEED_WORDS,
        "tested_offsets":624,
        "necessary_compatible_offsets":len(survivors),
        "max_unique_seed_words":max(known for _,known,_,_ in survivors),
        "min_unseen_seed_words":min(absent for _,_,absent,_ in survivors),
        "min_ambiguous_seed_words":min(amb for _,_,_,amb in survivors),
        "complete_source_seed_candidates":len(recovered),
        "complete_original_K04_passes":sum(x["original_K04_SHA_PASS"] for x in recovered),
        "all_complete_source_candidates":recovered,
    },sort_keys=True),flush=True)


if __name__ == "__main__":
    main()
