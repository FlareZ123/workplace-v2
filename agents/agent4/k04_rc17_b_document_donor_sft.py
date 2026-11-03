"""Source-only RC-17 revision B footer-to-MT donor test (3 Nov 2026).

Run with repository root: python agents/agent4/k04_rc17_b_document_donor_sft.py
Uses p951 speculative generator. Selected printer ACK and commitments never fitted.
"""
import hashlib
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "p951_source", ROOT / "agents/agent49/k04_p951_symbolic_basis.py"
)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
U = 0xFFFFFFFF
DOC_SHA = "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d"


def read_footers():
    raw = (ROOT / "resources/evidence/procedures/RC-17-scans.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == DOC_SHA
    text = raw.decode("utf-8")
    regex = (r"DOCUMENT RC-17 / REV (B|C|D-draft) / SECTION (\\w+)"
             r".*?Footer control strip: ([0-9A-F]{8})")
    items = {(m.group(1), m.group(2)): m.group(3)
             for m in re.finditer(regex, text, flags=re.S)}
    assert len(items) == 12
    return items


def observe(basis, expr, value):
    bits = model.temper(expr)
    known = [(j, basis.predict(v)) for j, v in enumerate(bits)]
    fixed = [(j, bit) for j, bit in known if bit is not None]
    agree = sum(bit == (value >> j) & 1 for j, bit in fixed)
    return len(fixed), agree, bits


def quotient(basis, symbolic):
    reduced = {}
    rank = 0
    for idx in (951, 952, 953, 954):
        for expr in model.get(symbolic, idx):
            x = expr
            while x:
                p = x.bit_length() - 1
                if p in basis.rows:
                    x ^= basis.rows[p][0]
                elif p in reduced:
                    x ^= reduced[p]
                else:
                    reduced[p] = x
                    rank += 1
                    break
    return rank


def main():
    footers = read_footers()
    basis, states = model.source(ROOT / "resources")
    assert basis.rank == 15365
    assert quotient(basis, states) == 128
    eligible = []
    for idx in range(model.ORIGIN, model.LAST + 1):
        expr = model.get(states, idx)
        for view, bits in (("native", expr), ("tempered", model.temper(expr))):
            for (rev, section), h in footers.items():
                for endian in ("little", "big"):
                    raw = int.from_bytes(bytes.fromhex(h), endian)
                    known = [(j, basis.predict(x)) for j, x in enumerate(bits)]
                    fixed = [(j, bit) for j, bit in known if bit is not None]
                    if len(fixed) < 14:
                        continue
                    if all(bit == ((raw >> j) & 1) for j, bit in fixed):
                        eligible.append((rev, section, h, idx, view, endian, len(fixed)))
    assert eligible == [
        ("B", "VERIFY", "C130C9BB", -186, "tempered", "little", 32),
        ("B", "PURGE", "759E0027", -185, "tempered", "little", 26),
    ], eligible
    print("ORIGINAL_HELDOUT_FOOTER_MATCHES", eligible)
    # Synthetic falsifier: flipping a source-fixed bit in the second
    # authentic B page must be rejected by the same original-source basis.
    second = int.from_bytes(bytes.fromhex("759E0027"), "little")
    fixed, agree, bits = observe(basis, model.get(states, -185), second)
    assert (fixed, agree) == (26, 26)
    one_fixed = next(i for i, v in enumerate(bits) if basis.predict(v) is not None)
    assert observe(basis, model.get(states, -185), second ^ (1 << one_fixed))[:2] == (26, 25)
    print("PRESERVED_SECOND_PAGE_AND_ONEBIT_NEGATIVE_CONTROL PASS")
    order = ("VERIFY", "PURGE", "ISOLATE", "DRAIN")
    gains = []
    for idx, section in zip(range(-186, -182), order):
        data = bytes.fromhex(footers["B", section])
        raw = int.from_bytes(data, "little")
        start_rank = basis.rank
        for bit, expr in enumerate(model.temper(model.get(states, idx))):
            basis.insert(expr, (raw >> bit) & 1)
        gains.append(basis.rank - start_rank)
    assert gains == [0, 1, 32, 32], gains
    assert basis.rank == 15430
    assert quotient(basis, states) == 128
    print("CONDITIONAL_B_REVERSE_STAGES", list(zip(order, range(-186, -182))))
    print("INCREMENTAL_RANK_GAINS", gains, "JOINT_RANK", basis.rank)
    print("SELECTED_K04_NATIVE_QUOTIENT", 128, "OF", 128)
    print("NO_K04_VALUE_RECOVERED")


if __name__ == "__main__":
    main()
