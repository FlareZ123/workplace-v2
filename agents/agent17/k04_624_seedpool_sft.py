"""Source-pinned 624-word MT state-pool K04 candidate experiment.

Run from repository root: python agents/agent17/k04_624_seedpool_sft.py
Requires C++17, g++ and OpenSSL libcrypto. Use --mode N to run one shard.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", HERE.parents[1] / "resources"))
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
RECORDER_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
K04_COMMIT = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MASK = "8556C8CB6140A7F9A5123AC7571BEE1C"


def pinned_bytes(path: Path, expected_sha256: str) -> bytes:
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected_sha256, path
    return data


def extract() -> bytes:
    spool = pinned_bytes(ROOT / "evidence/print/spool-reconstruction.log", SPOOL_SHA)
    rows = [bytes.fromhex(m.decode("ascii")) for m in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(rows) == 133
    selected_line = b"JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5"
    assert spool.count(selected_line) == 1
    assert rows[129].hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
    printer = b"".join(r for i, r in enumerate(rows) if i != 129)

    recorder = pinned_bytes(ROOT / "evidence/recorder/trip-recorder.raw", RECORDER_SHA)
    assert recorder[:8] == b"TRP2DUMP" and len(recorder) == 16 + 88 * 24
    controls = b"".join(recorder[16 + 24 * i + 12:16 + 24 * i + 16] for i in range(88))

    groups: dict[str, str] = {}
    for number in (3, 6):
        message = (ROOT / f"evidence/mail/{number:02d}.eml").read_text(encoding="utf-8")
        groups.update(re.findall(r"WN-14 / group ([ABCD]) / ([0-9A-F]{8})", message))
    assert set(groups) == set("ABCD")
    ink = bytes.fromhex("".join(groups[c] for c in "ABCD"))

    pages = (ROOT / "evidence/procedures/RC-17-scans.txt").read_text(encoding="utf-8").split("\f")
    strips: dict[str, str] = {}
    for page in pages:
        if "DOCUMENT RC-17 / REV C / SECTION " in page:
            section = re.search(r"DOCUMENT RC-17 / REV C / SECTION ([A-Z]+)", page)
            footer = re.search(r"Footer control strip: ([0-9A-F]{8})", page)
            assert section is not None and footer is not None
            assert section.group(1) not in strips
            strips[section.group(1)] = footer.group(1)
    assert set(strips) == {"DRAIN", "ISOLATE", "PURGE", "VERIFY"}
    service_order = (ROOT / "evidence/archive-labels.ini").read_text(encoding="utf-8")
    order = re.search(r"^service_order=([A-Z,]+)$", service_order, flags=re.M)
    assert order is not None
    procedure = bytes.fromhex("".join(strips[x] for x in order.group(1).split(",")))

    acceptance = json.loads((ROOT / "acceptance.json").read_text(encoding="utf-8"))
    routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text(encoding="utf-8"))
    assert routing["K04"]["masked_component"] == MASK
    assert acceptance["slot_sha256"]["K04"] == K04_COMMIT
    for name, value in (("K01", ink), ("K06", procedure)):
        assert hashlib.sha256(value).hexdigest() == acceptance["slot_sha256"][name]
    assert [len(group) // 4 for group in (printer, controls, ink, procedure)] == [528, 88, 4, 4]
    return printer + controls + ink + procedure


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", type=int, choices=range(16))
    args = parser.parse_args()
    fixture = extract()
    print("SOURCE_PIN_PASS: 624 original 4-byte words, selected copied ACK excluded", flush=True)
    modes = [args.mode] if args.mode is not None else range(16)
    with tempfile.TemporaryDirectory(prefix="h17-a17-pool-") as directory:
        temporary = Path(directory)
        source = HERE / "k04_624_seedpool.cpp"
        executable = temporary / ("pool.exe" if os.name == "nt" else "pool")
        subprocess.run(["g++", "-O3", "-std=c++17", str(source), "-lcrypto", "-o", str(executable)], check=True)
        data_path = temporary / "input.bin"
        data_path.write_bytes(fixture)
        total = 0
        controls = 0
        for mode in modes:
            run = subprocess.run([str(executable), str(data_path), str(mode), "620"], check=True, text=True, capture_output=True)
            result = re.fullmatch(r"COMPLETE assignments=(\d+) original_hits=(\d+) synthetic_hits=(\d+) modes=(\d+) windows=(\d+)", run.stdout.strip())
            assert result is not None, run.stdout
            assigned, original, planted, actual_mode, windows = map(int, result.groups())
            assert assigned == 61_046_784 and original == 0 and planted > 0
            assert actual_mode == mode and windows == 621
            total += assigned
            controls += planted
            print(f"MODE {mode:02d}: {assigned:,} complete K04 assignments, 0 original matches, {planted} planted positives", flush=True)
    print(f"COMPLETE: {total:,} assignments, 0 original matches, {controls} synthetic positives")


if __name__ == "__main__":
    main()
