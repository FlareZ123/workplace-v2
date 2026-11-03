"""SFT: test export order from stable sorting on shared-MT random keys.

Run: python agents/agent3/k04_export_sortkey_p951_sft.py resources
No selected ACK2 bytes, K04/K08 commitment, or route mask are used for fitting.
The historical producer and the candidate export-creation orders are unverified.
"""
from pathlib import Path
import importlib.util
import random
import sys

BASE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("h17_shuffle", BASE / "k04_export_shuffle_p951_sft.py")
shuffle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shuffle)


def build_tables(values, masks):
    """Exact next eight-bit value consistent with source-known bits."""
    tables = {}
    for value, mask in zip(values, masks):
        for oriented in (value, value ^ 255):
            key = (mask, oriented & mask)
            if key in tables:
                continue
            row = [256] * 257
            for i in range(255, -1, -1):
                row[i] = i if (i & mask) == key[1] else row[i + 1]
            tables[key] = row
    return tables


def possible_sorted(observed, original, values, masks, start, stride, desc, tables):
    labels = {record: index for index, record in enumerate(original)}
    order = [labels[record] for record in observed]
    minimum = 0
    for index in order:
        pos = start + stride * index
        value, mask = values[pos], masks[pos]
        if desc:
            value ^= 255
        minimum = tables[(mask, value & mask)][minimum]
        if minimum == 256:
            return False
    return True


def synthetic_controls():
    r = random.Random(382)
    values = [r.getrandbits(32) >> 24 for _ in range(145)]
    original = list(range(145))
    ascending = sorted(original, key=lambda i: values[i])
    descending = sorted(original, key=lambda i: -values[i])
    masks = [255] * len(values)
    tables = build_tables(values, masks)
    assert possible_sorted(ascending, original, values, masks, 0, 1, False, tables)
    assert possible_sorted(descending, original, values, masks, 0, 1, True, tables)
    assert not possible_sorted(list(reversed(ascending)), original, values, masks, 0, 1, False, tables)
    for mask in range(256):
        value = 213 & mask
        row = tables.get((mask, value))
        if row is None:
            row = [256] * 257
            for i in range(255, -1, -1):
                row[i] = i if (i & mask) == value else row[i + 1]
        for threshold in (0, 7, 64, 101, 213, 246, 255):
            expected = next((candidate for candidate in range(threshold, 256)
                             if candidate & mask == value), 256)
            assert row[threshold] == expected, (mask, threshold)
    print("Synthetic 145-row sort positives and 1,792 bit-constraint controls: PASS", flush=True)


def main(root):
    synthetic_controls()
    values, masks = shuffle.printer_top8(root)
    tables = build_tables(values, masks)
    for family, layouts_fn in (
        ("TRP2 recorder", shuffle.recorder_layouts),
        ("AX transfer", shuffle.transfer_layouts),
        ("freeze telemetry", shuffle.telemetry_layouts),
    ):
        layouts = stages = viable = 0
        for label, observed, original in layouts_fn(root):
            layouts += 1
            n = len(original)
            for stride in (1, 2):
                for start in range(len(values) - stride * (n - 1)):
                    known = sum(masks[start + stride * i].bit_count() for i in range(n))
                    if known < 80:
                        continue
                    for desc in (False, True):
                        stages += 1
                        if possible_sorted(observed, original, values, masks, start, stride, desc, tables):
                            viable += 1
                            print("UNEXPECTED SURVIVOR", label, start + shuffle.ORIGIN,
                                  stride, desc, known)
        print(f"{family}: {layouts} layouts; {stages} testable stage assignments; {viable} compatible")
        assert viable == 0
    print("K04/K08 remain unresolved under this bounded shared MT sort-key hypothesis.")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else BASE.parents[1] / "resources")
