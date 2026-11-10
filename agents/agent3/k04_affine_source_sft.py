"""H-17 original-source affine printer-coupon generator.

Withholds the copied 18:02 ACK2 before decoding. Reads the SHA-pinned
Agent49 printer basis. Emits the complete rank29/31/32 coupon spaces as
a text stream for k04_affine_sha256_sft.cpp. Does not write files.
"""
from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "native_source", ROOT / "agents/agent49/k04_p951_symbolic_basis.py"
)
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)

STAGES = {
    29: (-1074, -1000, -965, -905, -671, -492, -486),
    31: (925, 931, 938, 939, 940, 941),
    32: (944, 945),
}


def reduce_original(source, value):
    constant = 0
    residual = 0
    while value:
        pivot = value.bit_length() - 1
        row = source.rows.get(pivot)
        if row is None:
            residual ^= 1 << pivot
            value ^= 1 << pivot
        else:
            value ^= row[0]
            constant ^= row[1]
    return constant, residual


def serialize_native(native):
    result = bytearray()
    for lane in range(4):
        word = (native >> (32 * lane)) & 0xFFFFFFFF
        word ^= word >> 11
        word ^= (word << 7) & 0x9D2C5680
        word ^= (word << 15) & 0xEFC60000
        word ^= word >> 18
        result.extend((word & 0xFFFFFFFF).to_bytes(4, "little"))
    return bytes(result)


def project_stage(source, words, stage):
    constant = 0
    residuals = []
    for lane in range(4):
        for bit, expression in enumerate(mt.get(words, stage + lane)):
            known, free = reduce_original(source, expression)
            constant |= known << (32 * lane + bit)
            residuals.append(free)

    all_positions = 0
    for value in residuals:
        all_positions |= value
    pivots = {}
    independent_deltas = []
    for position in range(all_positions.bit_length() - 1, -1, -1):
        if not ((all_positions >> position) & 1):
            continue
        column = sum(((value >> position) & 1) << j
                     for j, value in enumerate(residuals))
        reduced = column
        while reduced:
            bit = reduced.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = reduced
                independent_deltas.append(column)
                break
            reduced ^= pivots[bit]
    return serialize_native(constant), [serialize_native(x) for x in independent_deltas]


def main():
    source, words = mt.source(ROOT)
    assert source.rank == 15365
    assert mt.STARTS[129] == 951
    original_rows, selected = mt.packets(ROOT)
    assert selected == 129 and original_rows[selected] == b""
    assert len(original_rows) == 133
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
    assert target == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

    old_base, old_deltas = project_stage(source, words, -1082)
    assert old_base.hex().upper() == "020000000296C31CC1ABD694A9C9EAE2"
    assert len(old_deltas) == 28
    assert old_deltas[0].hex().upper() == "02110844000000000000000000000000"

    # Rank32 stages 944 and 945 each bridge an original interpacket gap:
    # the selected 18:02 copy is absent from source fitting.
    expected_fixed = {
        944: [(0, original_rows[127][8:16]), (12, original_rows[128][0:4])],
        945: [(0, original_rows[127][12:16]), (8, original_rows[128][0:8])],
    }
    candidates = []
    for rank, stages in STAGES.items():
        for stage in stages:
            printer_base, directions = project_stage(source, words, stage)
            assert len(directions) == rank, (stage, len(directions), rank)
            for offset, fixed in expected_fixed.get(stage, ()):
                assert printer_base[offset:offset + len(fixed)] == fixed
                assert all(d[offset:offset + len(fixed)] == bytes(len(fixed))
                           for d in directions)
            component_base = bytes(a ^ b for a, b in zip(printer_base, mask))
            candidates.append((rank, stage, component_base, directions))
            print(f"SOURCE_PASS rank={rank} stage={stage} affine_directions={rank}",
                  file=sys.stderr)

    print(len(candidates))
    for rank, stage, component_base, directions in candidates:
        print(rank, stage, component_base.hex().upper())
        for direction in directions:
            print(direction.hex().upper())


if __name__ == "__main__":
    main()
