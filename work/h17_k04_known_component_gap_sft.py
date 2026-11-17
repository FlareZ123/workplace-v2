#!/usr/bin/env python3
"""Test known 16-byte components and routing values as the two p951 K04 gaps."""
import hashlib, itertools, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt


def insert(basis, symbolic, hx, start, endian):
    raw = bytes.fromhex(hx)
    for lane in range(4):
        word = int.from_bytes(raw[4 * lane:4 * lane + 4], endian)
        native = mt.untemper(word)
        for bit, form in enumerate(mt.get(symbolic, start + lane)):
            basis.insert(form, (native >> bit) & 1)


def main():
    candidate = json.loads((ROOT / "resources/candidate.json").read_text())
    routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    values = {k: v for k, v in candidate.items() if v is not None}
    values["K04-mask"] = routing["K04"]["masked_component"]
    values["K08-nonce"] = routing["K08"]["desk_nonce"]
    base, symbolic = mt.source(ROOT)
    checked = full = conflicts = 0
    hits = []
    for (name1, hx1), (name2, hx2) in itertools.permutations(values.items(), 2):
        for e1, e2 in itertools.product(("big", "little"), repeat=2):
            checked += 1
            basis = mt.Basis()
            basis.rows = dict(base.rows)
            basis.rank = base.rank
            try:
                insert(basis, symbolic, hx1, 328, e1)
                insert(basis, symbolic, hx2, 724, e2)
            except AssertionError:
                conflicts += 1
                continue
            payload = bytearray()
            determined = True
            for stage in range(951, 955):
                state = 0
                for bit, form in enumerate(mt.get(symbolic, stage)):
                    value = basis.predict(form)
                    if value is None:
                        determined = False
                        break
                    state |= value << bit
                if not determined:
                    break
                value = state
                value ^= value >> 11
                value ^= (value << 7) & 0x9D2C5680
                value ^= (value << 15) & 0xEFC60000
                value ^= value >> 18
                payload.extend((value & 0xFFFFFFFF).to_bytes(4, "little"))
            if not determined:
                continue
            full += 1
            mask = bytes.fromhex(routing["K04"]["masked_component"])
            component = bytes(a ^ b for a, b in zip(payload, mask))
            digest = hashlib.sha256(component).hexdigest()
            if digest == acceptance["slot_sha256"]["K04"]:
                hits.append({
                    "first": name1, "second": name2,
                    "endian1": e1, "endian2": e2,
                    "component": component.hex().upper(),
                })
    print(json.dumps({
        "values": list(values), "base_rank": base.rank,
        "pairs_checked": checked, "source_conflicts": conflicts,
        "fully_predicted": full, "hits": hits,
    }, indent=2))


if __name__ == "__main__":
    main()
