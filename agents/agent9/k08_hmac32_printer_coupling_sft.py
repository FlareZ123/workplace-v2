"""H-17 original K08 final-caption -> full HMAC32 -> printer seed pilot.

Run from repository root with Python 3. This program never edits evidence or
acceptance files. It reads the existing Agent23 selected-withheld MT projector,
checks a genuine planted source, then enumerates 69,120,000 complete captions.

CRITICAL: The shared HMAC32-seeded CPython printer producer is hypothetical.
Even an exact conditional source fit would require physical-media provenance.
"""
from __future__ import annotations

import hashlib
import hmac
import itertools
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent23"))
from k04_cpython_k2496_sixterm_joint_sft import (
    GROUPS, OFFSET, mt, original_packets, source_domains, source_rows, term,
    term_sets, words,
)

SEA = """
the sea was outside
the sea was still outside
the sea was just outside
the sea was there beyond the window
the sea was still there
the sea waited outside
the sea waited beyond the window
the sea lay beyond the window
the sea lay quiet outside
the sea stayed outside
the water was outside
the water was still outside
the water was just outside
the water was still there
the water waited outside
the water lay beyond the window
the water was at the window
the water moved outside
the sea went on outside
the sea carried on outside
the sea kept its own watch
the sea kept moving beyond the window
the sea waited for morning
the water waited for morning
the sea beyond the window
the water beyond the window
the sea at the window
the water at the window
the water and the window
the sea beyond the glass
the sea was getting light
the water was turning silver
""".strip().splitlines()

NIGHT = """
the night was almost finished
the night was almost over
the night was nearly finished
the night was nearly over
the night was coming to an end
the night was ending
the night was over
the night was almost done
the night had nearly ended
the night had almost gone
the last watch was nearly over
the last watch was nearly done
the long watch had ended
the long watch was nearly finished
the watch had come to an end
the end of the night was near
the end of the night was coming
morning was almost here
morning had nearly come
the first light was nearly here
the corridor had gone quiet
the last cup was empty
the last cup was finished
the little lamp stayed on
the little lamp was still on
""".strip().splitlines()

HUMAN = """
there was room for one another
there was room for each other
there was room at the table
there was room at the table for one another
there was room at the table for everyone
there was always room at the table
the table had room for everyone
the table had room for one more
the table had room for each other
the table made room for one more
the crew made room for one another
the crew made room for each other
the crew made room at the table
the late crew made room for one another
the late crew made room for each other
the voices at the table carried on
the voices at the table went on
the voices at the table were still there
the voices at the table kept us company
the voices at the table had room for another
the voices at the table stayed
the people at the table made room
the people at the table stayed together
the people making room for each other
people were making room for one another
somebody made room at the table
somebody had made room at the table
somebody remembered to make room
somebody had left room for another
someone had made room for another
we made room for each other
we kept a place for one another
we saved a place at the table
we left room for each other
we left room for one another
we left room at the table
one more person could sit down
nobody had to sit alone
nobody had to drink alone
there was room for one more cup
there was room for one more voice
the mugs stood together by the window
the mugs were on the table
the cups were still warm
the voices stayed until morning
the voices stayed around the table
the last cup was shared at the table
the room had space for the next watch
the next watch found room at the table
the last watch left room for the next
""".strip().splitlines()

OPENING = (
    "", "at the end of the night", "after the last cup",
    "after a long watch", "as the night came to an end",
    "as the last watch ended", "by the end of the night",
    "when the night was almost over",
)
JOIN = ("and", "while", "as", "when", "but", "and still")
U = 0xFFFFFFFF
EXPECTED = 69_120_000


def authentic_sources() -> tuple[bytes, bytes, list[list[int]], dict[int, set[int]]]:
    crew = (ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(crew).hexdigest() == (
        "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
    )
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    assert nonce.hex().upper() == "5F933DA6A1BD03C32DA5CBC25344F497"
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    assert target.hex() == "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
    n02 = b"a good watch leaves the room ready for the next pair of hands"
    assert hmac.digest(nonce, n02, "sha256")[:16].hex().upper() == (
        "BF889359B0303F2B2B2FD96AE841210B"
    )
    expressions = words(OFFSET)
    domains, s6, s7 = source_domains(source_rows(original_packets(), expressions))
    sets = term_sets(domains, s6, s7)
    assert {j: len(sets[j]) for j in (4, 18, 29)} == {4: 512, 18: 256, 29: 512}
    assert not any(
        all(v in b"abcdefghijklmnopqrstuvwxyz0123456789 " for v in
            ((t - 17) & U).to_bytes(4, "big"))
        for t in sets[18]
    )
    print("ORIGINAL_SOURCE_AUTHENTICATED selected_row129_withheld=1 "
          "rank=15365 T4=512 T18=256 T29=512 N02_HMAC16=PASS")
    return nonce, target, expressions, sets


def planted_source_control(
    nonce: bytes, expressions: list[list[int]], sets: dict[int, set[int]]
) -> None:
    plant = f"{OPENING[1]} {SEA[0]} and {NIGHT[0]} while {HUMAN[0]}"
    seed = hmac.digest(nonce, plant.encode("ascii"), "sha256")
    rng = random.Random(seed)
    actual_state = rng.getstate()[1][:624]
    draws = [rng.getrandbits(32) for _ in range(OFFSET + 974)]
    packets = [
        b"".join(draws[OFFSET + p + i].to_bytes(4, "little") for i in range(4))
        for p in mt.STARTS
    ]
    planted_domains, s6, s7 = source_domains(source_rows(packets, expressions))
    planted_sets = term_sets(planted_domains, s6, s7)
    for at in (4, 18, 29):
        idx = GROUPS[at]
        assert tuple(actual_state[j] for j in idx) in planted_domains[at]
        authentic_term = term(at, {i: actual_state[i] for i in (at - 2, at - 1, at)})
        assert authentic_term in planted_sets[at]
    assert hashlib.sha256(seed[:16]).digest() == hashlib.sha256(
        hmac.digest(nonce, plant.encode("ascii"), "sha256")[:16]
    ).digest()
    assert len(packets) == 133 and len(seed) == 32
    print("GENUINE_PLANTED_HMAC32_SOURCE_HOLDOUT_PASS "
          "source_rank=15365 selected_row129_withheld=1 "
          "T4_T18_T29_full_generator_witness=PASS")


def original_search(nonce: bytes, target: bytes, sets: dict[int, set[int]]) -> None:
    roles = (SEA, NIGHT, HUMAN)
    permutations = tuple(itertools.permutations(range(3)))
    assert (len(SEA), len(NIGHT), len(HUMAN), len(OPENING), len(JOIN)) == (
        32, 25, 50, 8, 6
    )
    assert 32 * 25 * 50 * 8 * 6 * 6 * 6 == EXPECTED
    candidate_count = 0
    t18_count = t4_count = t29_count = accepted_count = 0
    started = time.perf_counter()
    for pref in OPENING:
        before = candidate_count
        for order in permutations:
            aa, bb, cc = (roles[i] for i in order)
            for a in aa:
                for b in bb:
                    for c in cc:
                        for j0 in JOIN:
                            for j1 in JOIN:
                                sentence = f"{a} {j0} {b} {j1} {c}"
                                if pref:
                                    sentence = pref + " " + sentence
                                full_hmac = hmac.digest(nonce, sentence.encode("ascii"), "sha256")
                                candidate_count += 1
                                if hashlib.sha256(full_hmac[:16]).digest() == target:
                                    accepted_count += 1
                                    print("K08_ORIGINAL_COMMITMENT_HIT", sentence)
                                # CPython version2 32-byte seed is HMAC32 || SHA512(HMAC32).
                                k17 = int.from_bytes(full_hmac[-8:-4], "big")
                                if ((k17 + 17) & U) not in sets[18]:
                                    continue
                                t18_count += 1
                                print("PARTIAL_T18_ONLY", sentence)
                                seed_expanded_sha = hashlib.sha512(full_hmac).digest()
                                k3 = int.from_bytes(seed_expanded_sha[-16:-12], "big")
                                if ((k3 + 3) & U) not in sets[4]:
                                    continue
                                t4_count += 1
                                k4 = int.from_bytes(seed_expanded_sha[-20:-16], "big")
                                if ((k4 + 4) & U) not in sets[29]:
                                    continue
                                t29_count += 1
                                print("FULL_THREE_TERM_SOURCE_HIT", sentence)
        assert candidate_count - before == EXPECTED // len(OPENING)
        print("SOURCE_COUPLED_PROGRESS", "opening=" + repr(pref),
              "checked=" + str(candidate_count),
              "T18=" + str(t18_count), "T4=" + str(t4_count),
              "T29=" + str(t29_count),
              "K08=" + str(accepted_count), flush=True)
    assert candidate_count == EXPECTED
    print("SOURCE_COUPLED_COMPLETE checked=", candidate_count,
          "T18=", t18_count, "T4=", t4_count, "T29=", t29_count,
          "K08_original=", accepted_count,
          "seconds=", round(time.perf_counter() - started, 2))
    if t29_count or accepted_count:
        raise RuntimeError("Source or commitment hit requires independent verification")


def main() -> None:
    nonce, target, expressions, sets = authentic_sources()
    planted_source_control(nonce, expressions, sets)
    original_search(nonce, target, sets)


if __name__ == "__main__":
    main()
