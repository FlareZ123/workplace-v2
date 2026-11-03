"""H-17 K04 source-only calibration of compact, complete-ACK producers.

This deliberately withholds the disputed 18:02 ACK2 coupon and the K04
target commitment. Models must predict intact chronological printer records.
The official evidence is never changed.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import zipfile
from pathlib import Path

PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SELECT_JOB = "PS-261003-0417"
SELECT_DATE = "2026-10-03T18:02:00Z"


def load_spool() -> list[dict[str, str]]:
    path = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    records = []
    for line in raw.decode("utf-8").splitlines():
        if not line.startswith("2026-"):
            continue
        parts = line.split()
        row = {"TS": parts[0]}
        row.update(item.split("=", 1) for item in parts[1:])
        assert len(bytes.fromhex(row["PAYLOAD"])) == 16
        records.append(row)
    assert sum(is_selected(r) for r in records) == 1
    return records


def is_selected(r: dict[str, str]) -> bool:
    return (r["JOB"] == SELECT_JOB and r["TS"] == SELECT_DATE
            and r["ATTEMPT"] == "2" and r["STATE"] == "ACK"
            and r["CLASS"] == "RECOVER")


def metadata_test(rows: list[dict[str, str]]) -> dict:
    templates = [
        "{J}", "{J}|{A}", "{J}|{C}|{D}", "{J}|{A}|{C}|{D}",
        "{T}", "{T}|{J}", "{T}|{J}|{A}", "{T}|{C}|{D}",
        "{J}|{T}|{A}|{C}|{D}", "{T}|{J}|{A}|{S}|{C}|{D}",
        "JOB={J} ATTEMPT={A} STATE={S} CLASS={C} DEST={D}",
        "{T} JOB={J} ATTEMPT={A} CLASS={C} DEST={D}",
        "{T} JOB={J} ATTEMPT={A} STATE={S} CLASS={C} DEST={D}",
    ]
    formats = [fmt + end for fmt in templates for end in ("", "\n", "\r\n")]
    formats += [fmt.replace("|", " ") for fmt in formats if "|" in fmt]

    def encoded(r: dict[str, str], template: str) -> bytes:
        fields = dict(J=r["JOB"], A=r["ATTEMPT"], C=r["CLASS"],
                      D=r["DEST"], T=r["TS"], S=r["STATE"])
        return template.format(**fields).encode("ascii")

    def digests(raw: bytes) -> dict[str, bytes]:
        return {
            "md5": hashlib.md5(raw).digest(),
            "sha256first": hashlib.sha256(raw).digest()[:16],
            "sha256last": hashlib.sha256(raw).digest()[16:],
            "sha1first": hashlib.sha1(raw).digest()[:16],
            "blake2s": hashlib.blake2s(raw, digest_size=16).digest(),
            "blake2b": hashlib.blake2b(raw, digest_size=16).digest(),
        }

    ordinary = [r for r in rows if r["STATE"] == "ACK" and not is_selected(r)]
    groups = {
        "all_ACK": ordinary,
        "RECOVER_ACK": [r for r in ordinary if r["CLASS"] == "RECOVER"],
        "RECOVER_ACK_bench": [r for r in ordinary if r["CLASS"] == "RECOVER" and r["DEST"] == "bench"],
        "all_ACK_bench": [r for r in ordinary if r["DEST"] == "bench"],
    }
    outcomes = {}
    for name, sample in groups.items():
        best = 0
        full = 0
        for template in formats:
            digest_rows = [digests(encoded(r, template)) for r in sample]
            for method in digest_rows[0]:
                key = int(sample[0]["PAYLOAD"], 16) ^ int.from_bytes(digest_rows[0][method], "big")
                matched = 0
                for r, d in zip(sample, digest_rows):
                    if (int(r["PAYLOAD"], 16) ^ int.from_bytes(d[method], "big")) != key:
                        break
                    matched += 1
                best = max(best, matched)
                full += matched == len(sample)
        outcomes[name] = {"controls": len(sample), "models": len(formats) * 6,
                          "best_consecutive_fit": best, "complete_fits": full}

    # Positive: model key inferred on one synthetic payload predicts another.
    test = groups["RECOVER_ACK_bench"][:2]
    key = int("B60A939C1F57D24E0F628A3778D4B5C2", 16)
    f0, f1 = [int.from_bytes(digests(encoded(r, formats[0]))["md5"], "big") for r in test]
    synthetic0, synthetic1 = f0 ^ key, f1 ^ key
    recovered_key = synthetic0 ^ f0
    assert recovered_key == key and (f1 ^ recovered_key) == synthetic1
    return outcomes


def predictor(values: list[int], width: int, lag: int) -> dict:
    """Discover an arbitrary time-invariant GF(2)-affine word transition.

    A dependent feature vector requiring a different output disproves
    the whole class; this fits any linear bit-mixing matrix at that width.
    """
    dimension = width * lag + 1
    basis: dict[int, tuple[int, int]] = {}
    for index in range(lag, len(values)):
        feature = 1 << (width * lag)
        for t in range(lag):
            feature |= values[index - t - 1] << (t * width)
        outcome = values[index]
        while feature:
            pivot = feature.bit_length() - 1
            if pivot in basis:
                bfeature, bout = basis[pivot]
                feature ^= bfeature
                outcome ^= bout
            else:
                basis[pivot] = (feature, outcome)
                break
        if not feature and outcome:
            return {"dimension": dimension, "rank": len(basis),
                    "first_contradiction_output": index}
    return {"dimension": dimension, "rank": len(basis),
            "first_contradiction_output": None}


def linear_test(rows: list[dict[str, str]]) -> dict:
    # Only the 128 intact chronological ACKs before the incident retries.
    pre = [bytes.fromhex(r["PAYLOAD"]) for r in rows
           if r["STATE"] == "ACK" and r["TS"] < "2026-10-03T18:01:00"]
    assert len(pre) == 128
    outcome = {}
    for bits in (32, 64):
        size = bits // 8
        permutations = list(itertools.permutations(range(16 // size)))
        for lag in ((1, 2, 4) if bits == 32 else (1, 2)):
            fits = []
            for order in permutations:
                words = [int.from_bytes(packet[k * size:(k + 1) * size], "little")
                         for packet in pre for k in order]
                fits.append(predictor(words, bits, lag))
            failures = [x for x in fits if x["first_contradiction_output"] is not None]
            outcome[f"GF2_{bits}bit_lag{lag}"] = {
                "lane_orders": len(permutations),
                "contradictory_lane_orders": len(failures),
                "earliest_contradiction_output":
                    min((x["first_contradiction_output"] for x in failures), default=None),
                "latest_contradiction_output":
                    max((x["first_contradiction_output"] for x in failures), default=None),
            }

    # 128 packets offer just 127 consecutive input/output pairs, fewer
    # than the 129 independent affine input features of a 128-bit map.
    outcome["GF2_128bit_lag1"] = {
        "observed_pairs": 127, "feature_dimension": 129, "determined": False
    }

    def step(s: int) -> int:
        x = s ^ ((s << 13) & 0xFFFFFFFF)
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        return x ^ 0xC0FFEE33

    state = 0x619C731B
    planted = [state]
    for _ in range(150):
        state = step(state)
        planted.append(state)
    control = predictor(planted, 32, 1)
    assert control["first_contradiction_output"] is None and control["rank"] >= 32
    outcome["positive_control"] = "PASS"
    return outcome


def main() -> None:
    rows = load_spool()
    result = {"input_sha256": PIN, "selected_excluded": True,
              "metadata_digest_xor": metadata_test(rows),
              "affine_recurrence": linear_test(rows)}
    assert all(x["complete_fits"] == 0 for x in result["metadata_digest_xor"].values())
    assert all(x["contradictory_lane_orders"] == x["lane_orders"]
               for x in result["affine_recurrence"].values() if "lane_orders" in x)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
