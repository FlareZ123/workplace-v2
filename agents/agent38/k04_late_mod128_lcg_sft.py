"""Single-file K04 late-event LCG source-to-target holdout diagnostic.

Hypothesis only: one 128-bit modular affine state advances exactly once
per chronological late Z-format spool event, across three different printer
accounts. The disputed 18:02 coupon is never parsed or hashed. All original
checks use intact 18:01, 18:03, 18:24, and 18:25 printer records.

The actual hypothesis has no contemporaneous producer testimony, no proof
of shared state across accounts, and no independently verified K04 coupon.
A source holdout failure is a scoped falsification, not key recovery.
"""

from pathlib import Path
import hashlib
import re

MODULUS = 1 << 128
SOURCE = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def successors(a: int, b: int, first: int) -> tuple[int, ...]:
    states = [first]
    for _ in range(4):
        states.append((a * states[-1] + b) % MODULUS)
    return tuple(states)


def possible_chains(first: int, third: int, fourth: int, fifth: int) -> tuple[int, list[tuple[int, int, int]]]:
    # Fit every full-width affine multiplier from the LAST three observed
    # events, then test a two-step prediction crossing the missing event.
    difference = (fourth - third) % MODULUS
    next_difference = (fifth - fourth) % MODULUS
    assert difference != 0
    family_size = difference & -difference
    if next_difference % family_size:
        return 0, []
    quotient = MODULUS // family_size
    multiplier_base = ((next_difference // family_size) * pow(difference // family_size, -1, quotient)) % quotient
    assert family_size <= 16, "Only the frozen small source family is admissible"
    exact = []
    for index in range(family_size):
        multiplier = multiplier_base + index * quotient
        increment = (fourth - multiplier * third) % MODULUS
        hidden_second = (multiplier * first + increment) % MODULUS
        predicted_third = (multiplier * hidden_second + increment) % MODULUS
        if predicted_third == third:
            exact.append((multiplier, increment, hidden_second))
    return family_size, exact


def source_rows() -> dict[int, bytes]:
    source = SOURCE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA256
    retained = {}
    for line in source.decode("ascii").splitlines():
        if not line.startswith("2026-10-03T18:"):
            continue
        if line.startswith("2026-10-03T18:02:"):
            continue
        minute = int(line[14:16])
        if minute not in (1, 3, 24, 25):
            continue
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert match is not None
        retained[minute] = bytes.fromhex(match.group(1))
    assert set(retained) == {1, 3, 24, 25}
    return retained


def main() -> None:
    print("Hypothesis: one exact +1 modular-LCG step per late event (three printer accounts)")
    print("Source SHA256:", SOURCE_SHA256)
    print("Held out 18:02 ACK2 entirely; no route mask or acceptance hashes read")

    for multiplier, increment, first in ((3, 1, 0), (2, 1, 0)):
        x0, x1, x2, x3, x4 = successors(multiplier, increment, first)
        count, candidate_chains = possible_chains(x0, x2, x3, x4)
        assert count in (1, 4)
        assert (multiplier, increment, x1) in candidate_chains
        print("Synthetic positive a=", multiplier, ": PASS", sep="")

    retained = source_rows()
    for endian, expected_family in (("big", 2), ("little", 1)):
        x0, x2, x3, x4 = (int.from_bytes(retained[minute], endian) for minute in (1, 3, 24, 25))
        family, matching = possible_chains(x0, x2, x3, x4)
        assert family == expected_family
        print(f"Original {endian}: admissible later multipliers={family}; "
              f"exact 18:01 -> [18:02] -> 18:03 full-block predictions={len(matching)}")
        assert not matching, "Unexpected matching source holdout; authenticate producer before target check"

    print("STOP: both original source holdouts failed, selected K04 bits gained=0/128")


if __name__ == "__main__":
    main()
