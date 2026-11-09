"""Test source-only note-role metadata alignment against the proposed Nxx -> PS-03xx join.

Read-only original archive sources; no REC8 target guesses. Run from a complete
workplace-v2 checkout or supply the extracted archive root as first argument.
"""

from collections import Counter
from hashlib import sha256
from itertools import permutations
from pathlib import Path
from random import Random
import json
import re
import sys

CREW_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

# Frozen from explicit note descriptions, without reading printer CLASS/DEST.
# An actual note-to-printer event is NOT confirmed by these genres.
# Other notes, including drafts and N23's missing final margin, abstain.
SOURCE_ROLES = {
    9: ("LABEL", "store", "Caption for the galley board"),
    12: ("LABEL", "bench", "Workshop card"),
    16: ("LABEL", "store", "Canteen notice"),
    17: ("LABEL", "store", "Standby envelope label"),
    18: ("LABEL", "store", "Commissioning envelope label"),
    21: ("STORES", "store", "Freezer door"),
    24: ("LABEL", "store", "Departure board"),
}

# Retrospective five-role expectations from Agent17's earlier offset selection.
# Their printer categories were chosen AFTER seeing the source metadata.
RETROSPECTIVE_ROLES = {
    17: ("LABEL", "store"),
    18: ("RECOVER", "store"),
    20: ("RECOVER", "bench"),
    23: ("RECOVER", "store"),
    24: ("LABEL", "store"),
}

OFFSETS = range(-1, 104)  # N01..N24 maps entirely inside PS-0300..0427.
INDEPENDENT_HOLDOUTS = (9, 12, 16, 21)


def load_original(root: Path) -> dict[int, tuple[str, str]]:
    path = root / "evidence"
    crew = (path / "crew" / "noticeboard-and-desk-notes.txt").read_bytes()
    spool = (path / "print" / "spool-reconstruction.log").read_bytes()
    assert sha256(crew).hexdigest() == CREW_SHA256
    assert sha256(spool).hexdigest() == SPOOL_SHA256
    sections = re.split(r"(?=^N\d\d / )", crew.decode("utf-8"), flags=re.M)
    notes = {int(part[1:3]): part for part in sections if re.match(r"^N\d\d / ", part)}
    assert len(notes) == 24
    for index, (_, _, cue) in SOURCE_ROLES.items():
        assert cue in notes[index], (index, cue)

    records: dict[int, tuple[str, str]] = {}
    for line in spool.decode("utf-8").splitlines():
        if "+00:00" not in line or "JOB=" not in line:
            continue
        fields = dict(re.findall(r"\b([A-Z]+)=([^ ]+)", line))
        job = int(fields["JOB"].rsplit("-", 1)[-1])
        assert 300 <= job <= 427 and job not in records
        assert fields["ATTEMPT"] == "1" and fields["STATE"] == "ACK"
        records[job - 300] = (fields["CLASS"], fields["DEST"])
    assert set(records) == set(range(128))
    return records


def score(roles: dict[int, tuple[str, str]], jobs: dict[int, tuple[str, str]], offset: int) -> int:
    return sum(jobs[index + offset] == role for index, role in roles.items())


def rank(roles: dict[int, tuple[str, str]], jobs: dict[int, tuple[str, str]]) -> dict:
    totals = {offset: score(roles, jobs, offset) for offset in OFFSETS}
    observed = totals[0]
    best = max(totals.values())
    return {
        "offset0_score": observed,
        "offset0_rank_including_ties": sum(v >= observed for v in totals.values()),
        "best_score": best,
        "best_offsets": [o for o, v in totals.items() if v == best],
    }


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
    original = load_original(root)
    roles = {n: (kind, dest) for n, (kind, dest, _) in SOURCE_ROLES.items()}
    assert set(INDEPENDENT_HOLDOUTS).isdisjoint(RETROSPECTIVE_ROLES)
    predictions = {
        f"N{n:02}": {
            "predicted": list(role),
            "observed": list(original[n]),
            "complete_match": role == original[n],
        }
        for n, role in roles.items()
    }

    indices = sorted(roles)
    values = tuple(roles[n] for n in indices)
    role_null = Counter(
        sum(original[n] == role for n, role in zip(indices, perm))
        for perm in set(permutations(values))
    )
    assert sum(role_null.values()) == 42

    randomizer = Random(20261109)
    position_null = Counter()
    for _ in range(100_000):
        selected = randomizer.sample(range(1, 25), len(values))
        shuffled = list(values)
        randomizer.shuffle(shuffled)
        position_null[sum(original[n] == role for n, role in zip(selected, shuffled))] += 1

    original_loo = {}
    for withheld in RETROSPECTIVE_ROLES:
        remaining = {i: role for i, role in RETROSPECTIVE_ROLES.items() if i != withheld}
        original_loo[f"N{withheld:02}"] = rank(remaining, original)

    # A plausible alternative interpretation of N18's commissioning purpose.
    purpose_roles = dict(roles)
    purpose_roles[18] = ("RECOVER", "store")

    # Planted positive tests genuine full CLASS+DEST prediction from a heldout
    # seventh note after the six others identify the synthetic placement.
    planted = dict(original)
    for index, role in roles.items():
        planted[index + 37] = role
    train = {index: role for index, role in roles.items() if index != 12}
    scores = {offset: score(train, planted, offset) for offset in OFFSETS}
    assert scores[37] == 6 and sum(v == 6 for v in scores.values()) == 1
    assert planted[12 + 37] == roles[12]

    observed = score(roles, original, 0)
    result = {
        "original_notes": 24,
        "ordinary_original_packets": 128,
        "source_frozen_roles": 7,
        "source_only_offset_rank": rank(roles, original),
        "independent_holdouts": {
            "note_indices": list(INDEPENDENT_HOLDOUTS),
            "complete_hits_at_offset0": sum(roles[n] == original[n] for n in INDEPENDENT_HOLDOUTS),
        },
        "source_only_individual_predictions": predictions,
        "N18_purpose_sensitivity": rank(purpose_roles, original),
        "retrospective_five_role_rank": rank(RETROSPECTIVE_ROLES, original),
        "retrospective_leave_one_out": original_loo,
        "exact_permuted_seven_role_multiset": {
            "total": sum(role_null.values()),
            "histogram": dict(sorted(role_null.items())),
            "score_ge_actual": sum(count for points, count in role_null.items() if points >= observed),
        },
        "randomly_reassigned_position_and_role_null": {
            "n": 100_000,
            "seed": 20261109,
            "histogram": dict(sorted(position_null.items())),
            "score_ge_actual": sum(count for points, count in position_null.items() if points >= observed),
        },
        "planted_offset_37_six_train_one_blind_holdout": "PASS",
        "original_K08_component_recovered": False,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
