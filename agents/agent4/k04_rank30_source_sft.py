"""H-17 K04 rank-30 native MT coupon spaces: every original stage, 16 disjoint shards.

Source geometry is inherited from the SHA-pinned Agent49 printer-only basis.
The disputed selected 18:02 ACK2 copied payload is excluded by that source module.
Uses Agent7's completed rank spectrum to identify precisely 32 rank-30 stages,
then Agent3's independently exercised full-coupon projection.
"""
import contextlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: k04_rank30_source_sft.py shard(0..15)")
    shard = int(sys.argv[1])
    assert 0 <= shard < 16

    with contextlib.redirect_stdout(sys.stderr):
        stages = load("h17_rank_spectrum",
                      ROOT / "agents/agent7/k04_stage_rank_gap_sft.py")
    affine = load("h17_affine_coupon",
                  ROOT / "agents/agent3/k04_affine_source_sft.py")
    all_rank30 = sorted(s for s, rank in stages.ranks.items() if rank == 30)
    assert len(all_rank30) == 32
    assert all_rank30 == sorted(set(all_rank30))
    assert stages.source.rank == 15365
    assert affine.mt.STARTS[129] == 951
    packets, selected = affine.mt.packets(ROOT)
    assert selected == 129 and packets[selected] == b""

    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
    assert acceptance["slot_sha256"]["K04"] == (
        "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
    )
    # Every shard owns exactly two rank-30 stages, with no overlap.
    assigned = all_rank30[shard::16]
    assert len(assigned) == 2
    output = []
    for stage in assigned:
        printer_base, directions = affine.project_stage(
            stages.source, stages.words, stage)
        assert len(directions) == 30, (stage, len(directions))
        component_base = bytes(a ^ b for a, b in zip(printer_base, mask))
        output.append((stage, component_base, directions))
        print(f"ORIGINAL_SOURCE_COMPLETE rank=30 stage={stage} "
              f"directions={len(directions)}", file=sys.stderr)

    print(len(output))
    for stage, base, directions in output:
        print("30", stage, base.hex().upper())
        for direction in directions:
            print(direction.hex().upper())


if __name__ == "__main__":
    main()
