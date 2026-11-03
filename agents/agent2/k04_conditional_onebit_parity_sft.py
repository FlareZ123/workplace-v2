"""H17 original-source conditional K04 parity: exact 56-row chronology and three falsifiers.

Run: python agents/agent2/k04_conditional_onebit_parity_sft.py
The disputed printer row129 and K04 acceptance hash are excluded from fitting.
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import source, get, temper, untemper, Basis
from k04_node50_full_syndrome_gap_sft import recorder_controls

PATH = (
    (7,-810),(8,-799),(9,-793),(10,-787),(11,-779),(12,-775),
    (13,-769),(14,-759),(15,-748),(16,-737),(17,-730),(18,-722),
    (19,-714),(20,-703),(21,-697),(22,-691),(23,-687),(24,-683),
    (25,-677),(26,-673),(27,-666),(29,-652),(30,-646),(32,-634),
    (33,-630),(36,-609),(37,-605),(38,-594),(39,-585),(40,-576),
    (41,-568),(42,-562),(43,-552),(44,-545),(45,-540),(46,-531),
    (47,-523),(48,-512),(49,-504),(50,-497),(51,-487),(52,-481),
    (54,-459),(55,-452),(56,-447),(57,-440),(58,-434),(59,-428),
    (60,-423),(61,-417),(63,-397),(64,-390),(65,-381),(68,-353),
    (69,-347),(70,-339),
)


def joint_basis(printer, vectors, recorder, assignments):
    joint = Basis()
    joint.rows = dict(printer.rows)
    joint.rank = printer.rank
    for seq, stage in assignments:
        native = untemper(recorder[seq])
        for bit, expression in enumerate(get(vectors, stage)):
            joint.insert(expression, (native >> bit) & 1)
    return joint


def target_relations(joint, vectors):
    """Express each target tempered bit in target/source quotient basis."""
    target_rows = {}
    constraints = []
    for lane, stage in enumerate(range(951, 955)):
        for bit, equation in enumerate(temper(get(vectors, stage))):
            vector = equation
            value = 0
            mask = 1 << (32 * lane + bit)
            while vector:
                pivot = vector.bit_length()-1
                if pivot in joint.rows:
                    row, rhs = joint.rows[pivot]
                    vector ^= row
                    value ^= rhs
                elif pivot in target_rows:
                    row, rhs, selector = target_rows[pivot]
                    vector ^= row
                    value ^= rhs
                    mask ^= selector
                else:
                    target_rows[pivot] = (vector, value, mask)
                    break
            if not vector:
                constraints.append((mask, value))
    return target_rows, constraints


def complete_state(joint, rng):
    """Randomly fill free state coordinates and solve all source pivots."""
    state = rng.getrandbits(19968)
    for pivot, (row, rhs) in sorted(joint.rows.items()):
        wanted = rhs ^ (((row ^ (1 << pivot)) & state).bit_count() & 1)
        if wanted:
            state |= 1 << pivot
        else:
            state &= ~(1 << pivot)
    assert all(((state & row).bit_count() & 1) == rhs
               for row, rhs in joint.rows.values())
    return state


def selected_coupon(state, vectors):
    payload = bytearray()
    for stage in range(951, 955):
        word = sum((((state & equation).bit_count() & 1) << bit)
                   for bit, equation in enumerate(temper(get(vectors, stage))))
        payload.extend(word.to_bytes(4, "little"))
    return bytes(payload)


def parity(data, selector):
    return sum((a & b).bit_count() for a, b in zip(data, selector)) & 1


def main():
    printer, vectors = source(ROOT / "resources")
    assert printer.rank == 15365
    recorder = recorder_controls()  # original recorder SHA-256 and all CRCs
    assert len(PATH) == 56 and PATH[0] == (7, -810) and PATH[-1] == (70, -339)
    assert set(range(7, 71)) - {seq for seq, _ in PATH} == {
        28, 31, 34, 35, 53, 62, 66, 67
    }
    for (i, p), (j, q) in zip(PATH, PATH[1:]):
        assert 4*(j-i) <= q-p <= 11*(j-i), (i, j, p, q)
    joint = joint_basis(printer, vectors, recorder, PATH)
    assert joint.rank == 16663
    rows, relation = target_relations(joint, vectors)
    assert len(rows) == 127 and len(relation) == 1
    selector_int, rhs = relation[0]
    selector = selector_int.to_bytes(16, "little")
    assert selector.hex().upper() == "00800040000000000000000000000000"
    assert rhs == 1 and selector_int.bit_count() == 2

    route = json.loads(
        (ROOT / "resources/evidence/recovery-routing.json").read_text()
    )
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
    component_rhs = rhs ^ parity(mask, selector)
    assert component_rhs == 0

    copied = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
    assert parity(copied, selector) == 0  # disagrees with this model

    # Valid actual full-MT-state positive witnesses: different coupons,
    # identical sole target parity, all original source/recorder constraints.
    rng = random.Random(20261103)
    coupons = []
    for _ in range(2):
        coupon = selected_coupon(complete_state(joint, rng), vectors)
        assert parity(coupon, selector) == rhs
        coupons.append(coupon)
    assert coupons[0] != coupons[1]

    print("ORIGINAL printer and recorder source controls: PASS")
    print("original 56-record joint rank:", joint.rank)
    print("selected target independent bits:", len(rows))
    print("one target payload parity mask:", selector.hex().upper())
    print("payload selected parity:", rhs, "component selected parity:", component_rhs)
    print("copied ACK parity disagrees:", parity(copied, selector) != rhs)
    print("two distinct exact state completions:", [x.hex().upper() for x in coupons])

    # Crucial source-compatible alternatives: no historically fixed seq47
    # stage. None of these alternatives constrains ANY original target bit.
    for alternative in (-522, -521, -520):
        positions = tuple((seq, alternative if seq == 47 else stage)
                          for seq, stage in PATH)
        for (i,p),(j,q) in zip(positions, positions[1:]):
            assert 4*(j-i) <= q-p <= 11*(j-i)
        model = joint_basis(printer, vectors, recorder, positions)
        alternatives, constraints = target_relations(model, vectors)
        assert model.rank == 16664
        assert len(alternatives) == 128 and not constraints
        print("seq47 alternative", alternative,
              "joint rank", model.rank, "target unknown", len(alternatives))

    print("ORIGINAL K04 and K08 recovery: INCOMPLETE")
    print("conditional parity is NOT authenticated without seq47 stage proof")


if __name__ == "__main__":
    main()
