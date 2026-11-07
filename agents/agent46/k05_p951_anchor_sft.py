"""Bounded cross-archive scan of accepted K05 against the p951 printer MT basis."""
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent49"))
from k04_p951_symbolic_basis import ORIGIN, LAST, get, source, temper

EXPECTED_K05 = "FF8B78200A56E8586DCDA00EF01E4572"


def predictions(basis, symbolic, transform):
    out = {}
    eligible = 0
    full = 0
    for stage in range(ORIGIN, LAST + 1):
        mask = value = 0
        for bit, equation in enumerate(transform(get(symbolic, stage))):
            predicted = basis.predict(equation)
            if predicted is not None:
                mask |= 1 << bit
                value |= predicted << bit
        if mask.bit_count() >= 24:
            out[stage] = (mask, value)
            eligible += 1
            full += mask == 0xFFFFFFFF
    return out, eligible, full


def main():
    candidate = json.loads((ROOT / "candidate.json").read_text(encoding="utf-8"))
    k05_hex = candidate["K05"]
    assert k05_hex == EXPECTED_K05, k05_hex
    k05 = bytes.fromhex(k05_hex)
    assert len(k05) == 16

    basis, symbolic = source(ROOT)
    assert basis.rank == 15365, basis.rank

    views = {
        "native": lambda word: word,
        "tempered": temper,
    }
    stage_maps = {}
    stage_counts = {}
    for view, transform in views.items():
        stage_maps[view], eligible, full = predictions(basis, symbolic, transform)
        stage_counts[view] = {"eligible": eligible, "fully_fixed": full}
        assert eligible == 1117 and full == 991

    individual = []
    block = []
    for view, stage_map in stage_maps.items():
        for endian in ("little", "big"):
            words = [
                int.from_bytes(k05[i:i + 4], endian)
                for i in range(0, 16, 4)
            ]
            for lane, word in enumerate(words):
                for stage, (mask, predicted) in stage_map.items():
                    if mask.bit_count() >= 24 and ((word ^ predicted) & mask) == 0:
                        individual.append((view, endian, lane, stage, mask.bit_count()))

            for permutation in itertools.permutations(range(4)):
                for start in range(ORIGIN, LAST - 2):
                    matches = []
                    for offset, lane in enumerate(permutation):
                        mask, predicted = stage_map.get(start + offset, (0, 0))
                        if mask.bit_count() < 24 or ((words[lane] ^ predicted) & mask) != 0:
                            break
                        matches.append(mask.bit_count())
                    else:
                        block.append((view, endian, permutation, start, min(matches)))

    assert individual == [], individual
    assert block == [], block
    print(json.dumps({
        "candidate": "K05",
        "component_hex": k05_hex,
        "source_rank": basis.rank,
        "stage_counts": stage_counts,
        "individual_word_matches": len(individual),
        "consecutive_four_word_matches": len(block),
        "views": ["native", "tempered"],
        "byte_orders": ["little", "big"],
        "minimum_fixed_bits_per_word": 24,
        "within_block_permutations": 24,
        "selected_K04_row129_remains_withheld": True,
    }, indent=2))


if __name__ == "__main__":
    main()
