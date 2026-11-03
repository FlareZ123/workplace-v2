"""SFT: alternate AX 16-bit checkpoint emitters in a source-only p951 MT model.

Uses all 132 intact original printer packets, excludes disputed selected row129,
then tests heldout AX transfer values under an explicit fixed source emitter.
Reuses Agent49's exact linear model and original source SHA-256 pin. Requires
Python 3 standard library and repo resources; writes no original files.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "resources"
BASE = HERE.parent / "agent49" / "k04_p951_symbolic_basis.py"
spec = importlib.util.spec_from_file_location("p951_symbolic", BASE)
p951 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p951)
END = 5300
AX_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"


def transfer_checkpoints(root):
    data = (root / "evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(data).hexdigest() == AX_SHA
    rows = [json.loads(x) for x in data.splitlines()]
    result = {}
    for name in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
        selected = sorted((x for x in rows if x["kind"] == "CHUNK" and
                           x["transfer"] == name),
                          key=lambda x: (x["seq"], x["attempt"]))
        assert len(selected) == 16
        assert [x["seq"] for x in selected] == [i // 2 for i in range(16)]
        result[name] = [int(x["checkpoint"], 16) for x in selected]
    return result


def symbols(root):
    basis, state = p951.source(root)
    for n in range(len(state), END - p951.ORIGIN + 1):
        t = n - 624
        state.append([
            state[t+397][j]
            ^ (state[t][31] if j == 30 else
               (state[t+1][j+1] if j < 30 else 0))
            ^ (state[t+1][0] if (p951.MAG >> j) & 1 else 0)
            for j in range(32)
        ])
    return basis, state


def predictions(basis, states, use_temper, upper):
    start_bit = 16 if upper else 0
    result = []
    for state in states:
        expression = p951.temper(state) if use_temper else state
        mask = value = 0
        for j in range(start_bit, start_bit + 16):
            bit = basis.predict(expression[j])
            if bit is not None:
                mask |= 1 << (j - start_bit)
                value |= bit << (j - start_bit)
        result.append((mask, value))
    return result


def scan(source_predictions, observed):
    direct = []
    xorsalt = []
    for stride in range(1, 17):
        for start in range(len(source_predictions) - stride * 15):
            direct_good = True
            xormask = xorvalue = bitcount = 0
            xor_good = True
            for j in range(8):
                mask, value = source_predictions[start + j * stride]
                residual = (observed[j] ^ value) & mask
                if residual:
                    direct_good = False
                if (xorvalue ^ residual) & xormask & mask:
                    xor_good = False
                    break
                xorvalue = (xorvalue & ~mask) | residual
                xormask |= mask
                bitcount += mask.bit_count()
            if not xor_good:
                continue
            redundant = bitcount - xormask.bit_count()
            if direct_good and bitcount >= 32:
                heldmatch = heldbad = 0
                for j in range(8, 16):
                    mask, value = source_predictions[start + j * stride]
                    heldmatch += (mask & ~(observed[j] ^ value)).bit_count()
                    heldbad += (mask & (observed[j] ^ value)).bit_count()
                direct.append((start + p951.ORIGIN, stride, bitcount, heldmatch, heldbad))
            if redundant >= 24:
                heldmatch = heldbad = 0
                for j in range(8, 16):
                    mask, value = source_predictions[start + j * stride]
                    checked = mask & xormask
                    heldmatch += (checked & ~(observed[j] ^ value ^ xorvalue)).bit_count()
                    heldbad += (checked & (observed[j] ^ value ^ xorvalue)).bit_count()
                xorsalt.append((start + p951.ORIGIN, stride, redundant,
                                xorvalue, xormask, heldmatch, heldbad))
    return direct, xorsalt


def main(root):
    basis, states = symbols(root)
    traces = transfer_checkpoints(root)
    findings = []
    for temp in (False, True):
        for upper in (False, True):
            source_predictions = predictions(basis, states, temp, upper)
            for transfer, original in traces.items():
                for swap in (False, True):
                    observed = [((x & 255) << 8) | (x >> 8) if swap else x
                                for x in original]
                    direct, xor = scan(source_predictions, observed)
                    for mode, candidates in (("direct", direct), ("xor", xor)):
                        if candidates:
                            findings.append((mode, transfer, temp, upper,
                                             swap, candidates))
                        print(mode, transfer, "temper", temp, "upper", upper,
                              "byte_swap", swap, "source-stage survivors",
                              len(candidates), flush=True)
    assert findings == [
        ("direct", "AX-7778", True, True, True, [(-157, 1, 45, 77, 0)]),
        ("xor", "AX-7778", True, True, True,
         [(-157, 1, 29, 0, 65535, 77, 0)]),
    ], findings
    print("PASS: authentic AX-7778 controls 45/45 training, 77/77 heldout; ")
    print("no other transfer under tested stage, stride, view or XOR-salt class")
    print("K04 selected coupon stays unknown; conditional historical producer only")


if __name__ == "__main__":
    main(ROOT)
