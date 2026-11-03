"""H-17 source-only seq53 heldout contradiction of the proposed 4..11 MT chronology.

SFT from repository root:
    python agents/agent20/k04_seq53_heldout_fullwidth_falsifier_sft.py

Original source parser modules are reused read-only. Selected K04 job row129,
mask, SHA target, K08 nonce and candidate are never accessed here.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
sys.path.insert(0, str(ROOT / "agents" / "agent2"))
from k04_p951_symbolic_basis import source, get, untemper, Basis
from k04_node50_full_syndrome_gap_sft import recorder_controls


def predicted_native(source_basis, bits):
    value = mask = 0
    for bit, expression in enumerate(bits):
        fixed = source_basis.predict(expression)
        if fixed is not None:
            value |= fixed << bit
            mask |= 1 << bit
    return value, mask


def insert_control(base, vectors, stage, printed):
    native = untemper(printed)
    for bit, expression in enumerate(get(vectors, stage)):
        base.insert(expression, (native >> bit) & 1)


def main():
    printer, vectors = source(ROOT / "resources")
    original = recorder_controls()
    assert printer.rank == 15365
    assert original[53] == 0xF7E4B4E8
    assert untemper(original[53]) == 0x3346A145

    # The published 56-control history assigns seq52=-481, seq54=-459.
    # A 4..11 output increment per *single* original sequence interval
    # forces the intervening seq53 to exactly -470 (both gaps 11).
    prior, later = -481, -459
    permissible = [stage for stage in range(prior + 4, prior + 12)
                   if 4 <= later - stage <= 11]
    assert permissible == [-470], permissible

    predicted, mask = predicted_native(printer, get(vectors, -470))
    actual = untemper(original[53])
    mismatch = (predicted ^ actual) & mask
    assert (predicted, mask, mismatch) == (
        0x080C1C00, 0x09CC1C00, 0x09481C00)
    assert mask.bit_count() == 9 and mismatch.bit_count() == 7

    # Genuine original source-positive: BOTH already assigned flanking
    # whole recorder words jointly fit the untouched printer source.
    with_flanks = Basis()
    with_flanks.rows = dict(printer.rows)
    with_flanks.rank = printer.rank
    insert_control(with_flanks, vectors, prior, original[52])
    insert_control(with_flanks, vectors, later, original[54])
    assert with_flanks.rank == 15427
    assert predicted_native(with_flanks, get(vectors, -470)) == (
        predicted, mask)

    # A fabricated donor satisfying all 9 original-source-fixed bits
    # survives the identical comparison, and flipping one such bit fails.
    control = (actual & ~mask) | (predicted & mask)
    assert ((control ^ predicted) & mask) == 0
    assert ((control ^ (1 << 10) ^ predicted) & mask) != 0
    print("ORIGINAL spool SHA-256 and recorder CRC/SHA-256: PASS")
    print("original printer rank:", printer.rank,
          "joint flanking source rank:", with_flanks.rank)
    print("source-selected original seq52=-481 seq54=-459")
    print("bounded 4..11 original seq53 stage set:", permissible)
    print("seq53 actual native CONTROL:", f"{actual:08X}")
    print("source native predicted fixed mask:", f"{mask:08X}")
    print("source native fixed bits:", mask.bit_count())
    print("original mismatch mask:", f"{mismatch:08X}",
          "mismatch bits:", mismatch.bit_count())
    print("source-consistent synthetic exact masked-word positive: PASS")
    print("single constrained-bit synthetic falsifier: PASS")
    print("global all-record 4..11 shared-MT chronology: FALSIFIED")
    print("56-control truncated alternative, target K04 and K08: UNRESOLVED")


if __name__ == "__main__":
    main()
