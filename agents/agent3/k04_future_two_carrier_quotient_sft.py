"""K04 selected-quarter recovery from two hypothetical future MT packet carriers.

Conditional producer geometry: Agent35's p951 132 printer records plus AX-7778
source GF(2) model. Two complete tempered 4-word buffers at starts 1347,1574
leave exactly one bit of selected output ambiguity. Test existing 16-byte
carriers as hypothetical donors, with a true seeded-state synthetic control.
Original selected ACK is excluded from source-state training and used only as
one speculative donor. All original evidence, commitments and keys are read only.
"""
import hashlib
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path
from runpy import run_path

PRINT_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
AX_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
FUTURE = (1347, 1574)


def reduced(value, pivots):
    while value and value.bit_length() - 1 in pivots:
        value ^= pivots[value.bit_length() - 1]
    return value


def insert(value, pivots):
    value = reduced(value, pivots)
    if value == 1:
        return False
    if value:
        pivots[value.bit_length() - 1] = value
    return True


def read_affine(root, model, symbols):
    starts = model["STARTS"]
    origin = model["ORIGIN"]
    untemper = model["untemper"]
    temper_expr = model["temper_expr"]
    original = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(original).hexdigest() == PRINT_SHA
    packets = [bytes.fromhex(s.decode("ascii")) for s in
               re.findall(rb"PAYLOAD=([A-F0-9]{32})", original)]
    assert len(packets) == len(starts) == 133 and starts[129] == 951
    affine = {}
    for row, (packet, start) in enumerate(zip(packets, starts)):
        if row == 129:
            continue
        for j in range(4):
            native = untemper(int.from_bytes(packet[4*j:4*j+4], "little"))
            for bit, expr in enumerate(symbols[start+j-origin]):
                assert insert((expr << 1) | ((native >> bit) & 1), affine)

    transfer_data = (root / "evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(transfer_data).hexdigest() == AX_SHA
    transfer = [json.loads(line) for line in transfer_data.splitlines()]
    selected = sorted((r for r in transfer
                       if r.get("kind") == "CHUNK" and r["transfer"] == "AX-7778"),
                      key=lambda r: (r["seq"], r["attempt"]))
    assert len(selected) == 16
    for j, record in enumerate(selected):
        checkpoint = int(record["checkpoint"], 16)
        high = (checkpoint >> 8) | ((checkpoint & 255) << 8)
        for bit, expr in enumerate(
                temper_expr(symbols[-157+j-origin])[16:]):
            assert insert((expr << 1) | ((high >> bit) & 1), affine)
    assert len(affine) == 15495
    return affine, packets


def form_payload(native_words, temper):
    return b"".join(temper(word).to_bytes(4, "little") for word in native_words)


def candidate_set(first, second, first_view, second_view,
                  affine_source, symbols, model, mask):
    affine = affine_source.copy()
    untemper = model["untemper"]
    for start, payload, view in (
        (FUTURE[0], first, first_view), (FUTURE[1], second, second_view)
    ):
        endian, reverse = view
        words = [
            untemper(int.from_bytes(payload[j:j+4], endian))
            for j in range(0, 16, 4)
        ]
        if reverse:
            words.reverse()
        for j, native in enumerate(words):
            for bit, expr in enumerate(
                symbols[start+j-model["ORIGIN"]]
            ):
                if not insert((expr << 1) | ((native >> bit) & 1), affine):
                    return []

    expressions = [
        reduced(expr << 1, affine)
        for index in range(951, 955)
        for expr in symbols[index-model["ORIGIN"]]
    ]
    baseline = sum((expr & 1) << bit for bit, expr in enumerate(expressions))
    columns = defaultdict(int)
    for output_bit, expr in enumerate(expressions):
        bits = expr >> 1
        while bits:
            lsb = bits & -bits
            columns[lsb.bit_length() - 1] ^= 1 << output_bit
            bits ^= lsb
    independent = {}
    for column in set(columns.values()):
        basis = reduced(column, independent)
        if basis:
            independent[basis.bit_length() - 1] = basis
    assert len(independent) == 1, len(independent)
    free = next(iter(independent.values()))
    answer = []
    for selected in (baseline, baseline ^ free):
        native = [(selected >> (32*j)) & 0xffffffff for j in range(4)]
        payload = form_payload(native, model["temper"])
        answer.append(bytes(x ^ y for x, y in zip(payload, mask)))
    return answer


def main(root=None, model=None, accepted=None):
    if root is None:
        root = Path(__file__).resolve().parents[2] / "resources"
    if model is None:
        model = run_path(str(Path(__file__).resolve().parents[1] /
                             "agent35/k04_p951_minimal_future_donor_sft.py"))
    symbols = model["states"]()
    source = model["fit_source"](symbols)
    affine, packets = read_affine(root, model, symbols)
    assert len(source) == len(affine) == 15495
    target = [bit for index in range(951, 955)
              for bit in symbols[index-model["ORIGIN"]]]
    hypothetical = [bit for start in FUTURE
                    for index in range(start, start+4)
                    for bit in symbols[index-model["ORIGIN"]]]
    assert model["rank_overlap"](hypothetical, target, source) == (128, 255, 127)

    if accepted is None:
        accepted = json.loads((root / "candidate.json").read_text())
    routing = json.loads((root / "evidence/recovery-routing.json").read_text())
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target_sha = bytes.fromhex(json.loads(
        (root / "acceptance.json").read_text()
    )["slot_sha256"]["K04"])
    carriers = {"mask": mask, "nonce": nonce, "copied_ack2": packets[129]}
    for slot in ("K01", "K02", "K03", "K05", "K06", "K07"):
        carriers[slot] = bytes.fromhex(accepted[slot])
    assert len(carriers) == 9

    # Construct a genuine original-source-compatible initialized state:
    # choose all unconstrained initial bits zero, solve ascending pivots.
    secret = 0
    for pivot in sorted(affine):
        equation = affine[pivot]
        other = (equation & ((1 << pivot)-1)) >> 1
        determined = (equation & 1) ^ ((other & secret).bit_count() & 1)
        secret |= determined << (pivot - 1)
    def synthesized(start):
        native = [
            sum(((secret & expr).bit_count() & 1) << bit
                for bit, expr in enumerate(symbols[index-model["ORIGIN"]]))
            for index in range(start, start+4)
        ]
        return form_payload(native, model["temper"])

    planted = synthesized(951)
    probes = candidate_set(synthesized(FUTURE[0]), synthesized(FUTURE[1]),
                           ("little", False), ("little", False),
                           affine, symbols, model, mask)
    assert bytes(x ^ y for x, y in zip(planted, mask)) in probes
    assert len(probes) == 2

    settings = tested = 0
    matches = []
    views = list(itertools.product(("little", "big"), (False, True)))
    for first_name, second_name in itertools.permutations(carriers, 2):
        for first_view, second_view in itertools.product(views, repeat=2):
            settings += 1
            values = candidate_set(carriers[first_name], carriers[second_name],
                                   first_view, second_view, affine, symbols,
                                   model, mask)
            for candidate in values:
                tested += 1
                if hashlib.sha256(candidate).digest() == target_sha:
                    matches.append((first_name, second_name, first_view,
                                    second_view, candidate.hex().upper()))
    assert settings == 1152
    assert tested == 1168
    print("Synthetic source-consistent future donor: PASS, two candidates")
    print("Future output quotient rank:", (128, 255, 127))
    print("Original stage assignments:", settings)
    print("Complete K04 commitment candidates:", tested)
    print("Original K04 matches:", matches)
    return matches


if __name__ == "__main__":
    main()
