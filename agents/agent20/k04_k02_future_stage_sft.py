"""H17 K02 DIAG_WORD -> K04 future MT-stage carrier probe.
Exact source p951 printer geometry, disputed row129 completely withheld.
Tests eight accepted-derivation DIAG readings as a source-derived external carrier,
in 8-value constant-stride direct, XOR-salt, and 16-bit modular-add models.
No claim of historical producer authenticity or recovered K04 bit.
"""
import datetime
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent49"))
from k04_p951_symbolic_basis import source, temper, ORIGIN, MAG

TELE_SHA = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
END = 3000
def original_values():
    data = (ROOT / "resources/evidence/telemetry/freeze-export.jsonl").read_bytes()
    assert hashlib.sha256(data).hexdigest() == TELE_SHA
    start = datetime.datetime(2026, 10, 3, 21, 13, 40, tzinfo=datetime.timezone.utc)
    end = start + datetime.timedelta(seconds=8)
    selected = {}
    for line in data.splitlines():
        r = json.loads(line)
        if r["field"] != "DIAG_WORD" or r["quality"] != "GOOD" or r["state"] != "HOLD":
            continue
        if not start <= datetime.datetime.fromisoformat(r["ts"]) < end:
            continue
        seq = r["seq"]
        if not 0 <= seq < 8:
            continue
        if seq not in selected or r["revision"] > selected[seq]["revision"]:
            selected[seq] = r
    assert sorted(selected) == list(range(8))
    return [selected[i]["value"] for i in range(8)]

def source_projection():
    basis, words = source(ROOT / "resources")
    assert basis.rank == 15365
    for i in range(len(words), END-ORIGIN+1):
        t = i-624
        words.append([words[t+397][j]
                      ^ (words[t][31] if j == 30 else (words[t+1][j+1] if j < 30 else 0))
                      ^ (words[t+1][0] if (MAG >> j) & 1 else 0)
                      for j in range(32)])
    out = []
    for stage in range(ORIGIN, END+1):
        mask = value = 0
        for bit, eq in enumerate(temper(words[stage-ORIGIN])):
            fixed = basis.predict(eq)
            if fixed is not None:
                mask |= 1 << bit
                value |= fixed << bit
        out.append((mask, value))
    return out

def scan(out, readings):
    direct = xor_salt = add_salt = eligible_add = 0
    best_xor_independent = 0
    for swap in (False, True):
        values = [int.from_bytes(x.to_bytes(2, "little"), "big") if swap else x for x in readings]
        for half in (0, 16):
            partial = [((m >> half) & 65535, (v >> half) & 65535) for m, v in out]
            for stride in range(1, 33):
                for start in range(len(partial)-7*stride):
                    slices = [partial[start+i*stride] for i in range(8)]
                    # Entire direct native eight-value stream, at least 32 source-fixed bits.
                    total = sum(m.bit_count() for m, _ in slices)
                    if total >= 32 and all(((v ^ x) & m) == 0 for (m, v), x in zip(slices, values)):
                        direct += 1
                    saltmask = saltval = 0
                    good = True
                    for (m, v), x in zip(slices, values):
                        desired = (v ^ x) & m
                        if (desired ^ saltval) & saltmask & m:
                            good = False
                            break
                        saltval |= desired
                        saltmask |= m
                    if good:
                        independent = total - saltmask.bit_count()
                        best_xor_independent = max(best_xor_independent, independent)
                        if independent >= 25:
                            xor_salt += 1
                    # A 16-bit additive salt is solved exhaustively from a
                    # source-fixed first reading, then every other reading is held out.
                    first_mask, first_value = slices[0]
                    if first_mask.bit_count() < 12:
                        continue
                    eligible_add += 1
                    free = [bit for bit in range(16) if not (first_mask >> bit) & 1]
                    for assignment in range(1 << len(free)):
                        native = first_value
                        for j, bit in enumerate(free):
                            native |= ((assignment >> j) & 1) << bit
                        salt = (values[0] - native) & 65535
                        if total >= 50 and all(
                            ((((x - salt) & 65535) ^ v) & m) == 0
                            for (m, v), x in zip(slices, values)
                        ):
                            add_salt += 1
    return dict(direct_alignments=direct, xor_salt_alignments=xor_salt,
                best_xor_independent_bits=best_xor_independent,
                additive_alignments=add_salt, additive_starts=eligible_add)

if __name__ == "__main__":
    values = original_values()
    assert values == [57765, 58484, 47831, 59475, 41704, 50973, 13079, 54535]
    projected = source_projection()
    actual = scan(projected, values)
    assert actual == dict(direct_alignments=0, xor_salt_alignments=0,
                          best_xor_independent_bits=13, additive_alignments=0,
                          additive_starts=198264), actual
    print(json.dumps(dict(source_rank=15365, source_window=[ORIGIN, END],
                          disputed_coupon_withheld=True, K02_winners=values,
                          results=actual, recovered_K04_bits=0), sort_keys=True))
