"""Complete K04 coupon search under the two-gap native MT identity.

Reuses the source-pinned 186 original complete donor fields of Agent12
and the exact four-word recurrence and seeded positives of Agent18.
Run from repository root: python agents/agent2/k04_two_gap_portfolio_sft.py
Optional first argument: path to the unchanged original H-17 ZIP.
"""
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent12.k04_future_quartet_sourcecarriers_sft import (
    source_carriers, layouts, untemper, temper, ZIP_SHA, K04_SHA,
)
from agents.agent18.k04_mt_causal_gap_residual_sft import (
    reconstruct_selected_native, synthetic_coupon_controls,
)

MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")


class DirectoryReader:
    def __init__(self, root):
        self.root = Path(root)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self, path):
        return (self.root / path).read_bytes()


def main(path):
    synthetic_coupon_controls()
    path = Path(path)
    if path.is_file():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == ZIP_SHA
    with (zipfile.ZipFile(path) if path.is_file() else DirectoryReader(path)) as z:
        carriers = source_carriers(z)
        original_spool = z.read("evidence/print/spool-reconstruction.log")
        rows = [r for r in original_spool.splitlines() if r.startswith(b"2026-")]
        assert len(rows) == 133
        assert b"JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in rows[129]
        selected = bytes.fromhex(
            re.search(rb"PAYLOAD=([0-9A-F]{32})", rows[43]).group(1).decode()
        )
        known327 = untemper(int.from_bytes(selected[-4:], "little"))
        route = json.loads(z.read("evidence/recovery-routing.json"))
        assert bytes.fromhex(route["K04"]["masked_component"]) == MASK
        acceptance = json.loads(z.read("acceptance.json"))
        assert acceptance["slot_sha256"]["K04"] == K04_SHA

    encoded = [
        (name, word_view)
        for original_bytes, name in carriers.items()
        for word_view in layouts(original_bytes)
    ]
    assert len(carriers) == 186
    assert len(encoded) == 1488

    checks = 0
    hits = []
    for first_label, native328 in encoded:
        for second_label, native724 in encoded:
            selected_native = reconstruct_selected_native(
                known327, native328, native724
            )
            physical = b"".join(
                temper(word).to_bytes(4, "little") for word in selected_native
            )
            component = bytes(a ^ b for a, b in zip(physical, MASK))
            checks += 1
            if hashlib.sha256(component).hexdigest() == K04_SHA:
                hits.append((first_label, second_label, component.hex().upper()))
    assert checks == 2_214_144
    print("original_carriers", len(carriers))
    print("native_views", len(encoded))
    print("complete_original_K04_checks", checks)
    print("original_K04_hits", len(hits))
    for hit in hits:
        print("ORIGINAL_K04_HIT", hit)


if __name__ == "__main__":
    main(
        sys.argv[1] if len(sys.argv) > 1
        else ROOT / "resources"
    )
