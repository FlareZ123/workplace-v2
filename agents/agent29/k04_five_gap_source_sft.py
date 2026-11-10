"""H-17 five source-constrained rank-32 MT19937 alternative printer windows.

Read-only, original-source SFT. Selected 18:02 ESC-N ACK2 is excluded
from all source equations before any copied PAYLOAD is decoded.
Outputs five full affine coupon spaces to stdout for the companion
k04_five_gap_sha256_sft.cpp, which checks all 2^32 assignments per stage.
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

STAGES = (919, 923, 929, 935, 966)
EXPECTED_RAW_BASE = {
    919: "6786FDEDFA3FAD0B8E245B5C4C3E4DB7",
    923: "EBBC5F3580A96F9F319E10B22C9F4508",
    929: "684C6CDE66D534D740A628A3A616649F",
    935: "F752FF78A2699B7032A47B22A7D7A3A6",
    966: "2C937FA4B7A65E67A9F29E152399F10E",
}
EXPECTED_FREE_LANE = {919: 3, 923: 0, 929: 0, 935: 0, 966: 3}


def reduce_original(source, value):
    known = 0
    unknown = 0
    while value:
        pivot = value.bit_length() - 1
        row = source.rows.get(pivot)
        if row is None:
            unknown |= 1 << pivot
            value ^= 1 << pivot
        else:
            value ^= row[0]
            known ^= row[1]
    return known, unknown


def temper_four(native):
    out = bytearray()
    for lane in range(4):
        x = (native >> (32 * lane)) & 0xFFFFFFFF
        x ^= x >> 11
        x ^= (x << 7) & 0x9D2C5680
        x ^= (x << 15) & 0xEFC60000
        x ^= x >> 18
        out.extend((x & 0xFFFFFFFF).to_bytes(4, "little"))
    return bytes(out)


def project(source, words, stage):
    constant = 0
    residuals = []
    for lane in range(4):
        for bit, expression in enumerate(mt.get(words, stage + lane)):
            known, free = reduce_original(source, expression)
            constant |= known << (32 * lane + bit)
            residuals.append(free)
    all_positions = 0
    for free in residuals:
        all_positions |= free
    pivots = {}
    directions = []
    while all_positions:
        position = all_positions.bit_length() - 1
        all_positions ^= 1 << position
        column = sum(
            ((value >> position) & 1) << bit
            for bit, value in enumerate(residuals)
        )
        reduced = column
        while reduced:
            pivot = reduced.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = reduced
                directions.append(temper_four(column))
                break
            reduced ^= pivots[pivot]
    return temper_four(constant), directions


def main():
    source, words = mt.source(ROOT)
    assert source.rank == 15365
    packets, selected = mt.packets(ROOT)
    assert selected == 129 and packets[selected] == b""
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
    assert acceptance["slot_sha256"]["K04"] == (
        "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
    )

    print(len(STAGES))
    for stage in STAGES:
        raw, directions = project(source, words, stage)
        assert raw.hex().upper() == EXPECTED_RAW_BASE[stage]
        assert len(directions) == 32
        free_lane = EXPECTED_FREE_LANE[stage]
        for lane in range(4):
            if lane != free_lane:
                assert all(d[lane * 4:(lane + 1) * 4] == bytes(4) for d in directions)
        assert any(d[free_lane * 4:(free_lane + 1) * 4] != bytes(4) for d in directions)
        for index, (record, position) in enumerate(zip(packets, mt.STARTS)):
            if index == selected:
                continue
            for lane in range(4):
                offset = position + lane - stage
                if 0 <= offset < 4:
                    assert raw[4 * offset:4 * offset + 4] == record[4 * lane:4 * lane + 4]
                    assert all(
                        d[4 * offset:4 * offset + 4] == bytes(4)
                        for d in directions
                    )
        component = bytes(a ^ b for a, b in zip(raw, mask))
        print(32, stage, component.hex().upper())
        for direction in directions:
            print(direction.hex().upper())
        print("SOURCE_PASS stage={} rank=32 free_word={}".format(
            stage, free_lane), file=sys.stderr)


if __name__ == "__main__":
    main()
