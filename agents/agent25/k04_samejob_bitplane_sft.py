"""K04: same-job earlier acknowledged LABEL as a one-bitplane stale-copy donor.

No source certifies a common copier stage; this tests eight source-cued full
payload hypotheses only. It does not alter the REC8 evidence or commitments.
Run: python agents/agent25/k04_samejob_bitplane_sft.py [resources-directory]
"""
from __future__ import annotations

from configparser import ConfigParser
from hashlib import sha256
import json
from pathlib import Path
import sys

SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def candidate(label: bytes, recover: bytes, plane: int) -> bytes:
    mask = 1 << plane
    return bytes((r & (255 ^ mask)) | (l & mask) for l, r in zip(label, recover))


def main(root: Path) -> None:
    routes = ConfigParser()
    routes.read(root / "evidence/archive-labels.ini", encoding="utf-8")
    job = routes["printer_routes_2026-09-01_to_2026-10-03"]["ESC-N"]
    assert job == "PS-261003-0417"

    spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert sha256(spool).hexdigest() == SOURCE_SHA256
    source: dict[str, bytes] = {}
    for line in spool.decode("ascii").splitlines():
        if f"JOB={job} " not in line:
            continue
        timestamp, *fields = line.split()
        attrs = dict(item.split("=", 1) for item in fields)
        if attrs["STATE"] != "ACK":
            continue
        event = (timestamp, attrs["ATTEMPT"], attrs["CLASS"])
        if event == ("2026-10-03T16:45:00+00:00", "1", "LABEL"):
            source["LABEL"] = bytes.fromhex(attrs["PAYLOAD"])
        elif event == ("2026-10-03T18:02:00Z", "2", "RECOVER"):
            source["RECOVER"] = bytes.fromhex(attrs["PAYLOAD"])
    assert set(source) == {"LABEL", "RECOVER"}
    label, recover = source["LABEL"], source["RECOVER"]
    assert label.hex().upper() == "E1E60D5F6B6DD2225FA6D5A2A63AD932"
    assert recover.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"

    # Freeze full coupon proposals from original event bytes before reading
    # original acceptance. No arbitrary bit subsets, other donors or offsets.
    candidates = [candidate(label, recover, plane) for plane in range(8)]
    assert len(set(candidates)) == 8
    routing = json.loads((root / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "acceptance.json").read_text())
    original_mask = bytes.fromhex(routing["K04"]["masked_component"])
    expected = acceptance["slot_sha256"]["K04"]
    assert len(original_mask) == 16

    def digest(payload: bytes) -> str:
        return sha256(bytes(a ^ b for a, b in zip(payload, original_mask))).hexdigest()

    synthetic = digest(candidates[3])
    assert [i for i, value in enumerate(candidates) if digest(value) == synthetic] == [3]
    print("SOURCE_SHA256=PASS; SYNTHETIC_CONTROL=PASS")
    matches = [(i, value.hex().upper()) for i, value in enumerate(candidates)
               if digest(value) == expected]
    print("COMPLETE_ORIGINAL_CANDIDATES=8")
    print("ORIGINAL_K04_MATCHES", matches)
    assert not matches


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1
         else Path(__file__).resolve().parents[2] / "resources")
