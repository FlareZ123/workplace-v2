"""All-six example MT19937 printer chronologies: complete alternate coupon stage SFT.

Uses six previously published source-compatible but historically speculative
p950..955 printer start-index fixtures. The 18:02 copied ACK2 payload is
excluded before building source equations.

Usage from workplace-v2 root:
    python agents/agent44/k04_six_stage_sft.py
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path
import k04_p951_hidden_stage_coupon_sft as original

# Exact model starts from workplace-v1/agents/agent5/k04_crosssource_six_vectors.json
# p951 is also separately pinned by the original Agent44 single-geometry SFT.
GEOMETRIES = {"950":[0,7,15,22,30,37,45,53,63,71,79,87,94,107,115,121,127,136,142,148,154,164,170,176,182,192,199,205,211,218,224,230,237,243,250,257,265,271,283,293,300,306,313,323,334,341,347,353,359,365,371,377,383,394,401,407,416,423,429,437,446,453,459,469,476,484,490,502,510,517,527,533,539,555,562,568,576,583,589,597,604,610,617,624,632,638,644,650,658,665,671,677,685,692,700,709,716,728,735,742,748,755,770,776,782,788,795,801,809,820,827,833,840,846,853,861,870,876,884,890,898,904,911,917,923,929,935,941,946,950,954,958,962],"952":[0,7,15,22,30,43,49,55,64,73,81,89,96,109,117,123,129,137,143,149,156,162,168,179,185,191,197,203,209,215,224,230,237,243,250,263,271,278,285,294,302,308,315,325,336,343,349,355,361,367,373,379,385,394,401,407,416,423,429,435,441,448,460,471,478,486,492,504,512,519,525,531,537,543,560,566,572,580,588,595,602,608,617,624,632,638,644,650,658,664,671,679,686,693,702,711,718,730,737,744,756,762,768,774,780,786,793,803,811,818,825,831,840,846,853,861,870,876,882,890,897,906,912,918,925,931,937,943,948,952,956,960,964],"953":[0,7,15,22,30,37,43,57,66,74,82,90,97,110,118,124,130,136,142,148,156,166,172,179,187,193,199,205,211,218,224,230,237,243,250,256,262,268,287,296,303,309,316,326,337,344,350,356,362,368,374,380,386,394,401,407,416,423,429,437,444,450,462,472,479,487,493,505,513,520,528,535,548,557,564,570,576,582,590,597,604,610,617,624,632,638,644,650,660,669,675,681,688,695,703,712,719,731,738,745,751,766,772,778,784,790,797,806,813,820,827,833,840,846,853,861,870,883,889,896,902,908,914,920,926,932,938,944,949,953,957,961,965],"954":[0,7,17,23,31,37,47,57,67,75,83,91,98,111,119,125,131,137,143,149,155,164,170,176,182,189,196,204,211,218,224,230,238,245,251,269,275,281,287,297,304,310,317,327,338,345,352,358,364,370,376,382,388,394,402,409,417,424,430,437,448,457,463,473,480,488,494,506,514,521,529,536,550,556,562,568,574,581,590,596,604,610,617,624,633,639,645,651,661,667,675,681,689,696,704,713,720,732,739,746,752,758,768,774,782,788,795,809,815,821,827,833,839,846,853,862,871,877,883,889,898,908,915,921,927,933,939,945,950,954,958,962,966],"955":[0,7,14,22,30,46,52,58,68,76,84,92,99,112,120,126,132,138,144,150,156,162,168,174,180,189,199,205,211,218,224,230,237,243,250,256,262,272,288,298,305,311,318,328,339,346,352,358,364,370,376,382,388,394,401,407,416,423,430,437,451,458,464,474,481,489,495,507,515,522,530,542,548,554,560,566,572,579,585,591,604,610,617,624,632,638,644,650,658,664,673,682,690,697,705,714,721,733,740,747,753,759,765,771,777,786,793,802,808,816,822,833,839,846,853,861,870,881,891,897,903,909,916,922,928,934,940,946,951,955,959,963,967]}
GEOMETRIES = {int(k): v for k, v in GEOMETRIES.items()}
GEOMETRIES[951] = list(original.STARTS)


def build_source_basis(expressions, rows, starts):
    basis = {}
    for r, row in enumerate(rows):
        for j, word in enumerate(row):
            for bit, expr in enumerate(expressions[starts[r] + j]):
                residual = original.reduce_row(
                    (expr << 1) | ((word >> bit) & 1), basis
                )
                assert residual != 1, ("source contradiction", r, j, bit)
                if residual > 1:
                    basis[residual.bit_length() - 1] = residual
    return basis


def main():
    root = Path(__file__).resolve().parents[2]
    source = root / "resources/evidence/print/spool-reconstruction.log"
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == original.SOURCE_SHA
    lines = [line for line in raw.decode("ascii").splitlines()
             if line.startswith("2026-")]
    assert len(lines) == 133
    rows = [
        [original.untemper(word) for word in struct.unpack(
            "<4I", bytes.fromhex(
                re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1)
            )
        )]
        for line in lines
    ]
    rows[129] = []
    routing = json.loads(
        (root / "resources/evidence/recovery-routing.json").read_text()
    )
    acceptance = json.loads(
        (root / "resources/acceptance.json").read_text()
    )
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    expected = {
        950: (15366, 244, 67, 378),
        951: (15365, 253, 73, 399),
        952: (15367, 264, 84, 432),
        953: (15368, 263, 64, 391),
        954: (15365, 252, 65, 382),
        955: (15369, 263, 72, 407),
    }

    unique = set()
    hits = []
    assignments = 0
    invariant = None
    for p in sorted(GEOMETRIES):
        starts = GEOMETRIES[p]
        assert len(starts) == 133 and starts[129] == p
        expressions = original.state_expressions(starts[-1] + 3)
        basis = build_source_basis(expressions, rows, starts)
        values = original.source_fixed_words(expressions, basis)

        # The same four unprinted bytes are independently fixed by each
        # source-compatible geometry at its different absolute index p-254.
        hidden = list(original.coupons_for_stage(values, p - 254))
        assert len(hidden) == 1
        assert hidden[0].hex().upper() == "C9304FE833674EFD67B213839E4BA01D"
        invariant = invariant or hidden[0]
        assert hidden[0] == invariant
        printed = struct.unpack("<4I", hidden[0])
        assert [word >> 30 for word in printed[:3]] == [3, 3, 2]
        assert printed[3] >> 29 == 0
        assert "DEST=bench" in lines[93] and "CLASS=LABEL" in lines[94]

        full = one = count = 0
        for stage in range(starts[-1] + 1):
            coupons = list(original.coupons_for_stage(values, stage) or ())
            if not coupons:
                continue
            if len(coupons) == 1:
                full += 1
            else:
                assert len(coupons) == 2
                one += 1
            for coupon in coupons:
                component = bytes(a ^ b for a, b in zip(coupon, mask))
                unique.add(component)
                count += 1
                if hashlib.sha256(component).hexdigest() == target:
                    hits.append((p, stage, coupon.hex().upper()))
        assert (len(basis), full, one, count) == expected[p]
        assignments += count
        print("GEOMETRY", p, "SOURCE_RANK", len(basis),
              "FULL_WINDOWS", full, "ONE_BIT_WINDOWS", one,
              "COMPLETE_CANDIDATES", count)

    assert assignments == 2389
    assert len(unique) == 945
    assert len(hits) == 0
    planted = sorted(unique)[500]
    synthetic_digest = hashlib.sha256(planted).hexdigest()
    assert sum(hashlib.sha256(value).hexdigest() == synthetic_digest
               for value in unique) == 1
    print("MODEL_INVARIANT_UNPRINTED_BUFFER", invariant.hex().upper())
    print("TOTAL_SOURCE_CANDIDATE_ASSIGNMENTS", assignments)
    print("UNIQUE_SOURCE_COMPONENT_CANDIDATES", len(unique))
    print("ORIGINAL_K04_COMMITMENT_HITS", len(hits))
    print("PLANTED_COMPLETE_COMPONENT_POSITIVE", "PASS")


if __name__ == "__main__":
    main()
