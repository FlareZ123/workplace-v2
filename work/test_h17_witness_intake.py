"""Single-file reproducible historical-witness intake checks (offline, stdlib)."""

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from h17_witness_intake import RESOURCES, assess, normalize_caption

KNOWN_ACK = "A9A9DC5731A5E2AE879C47215C2559D5"
JOB = "PS-261003-0417"


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    source_files = (
        RESOURCES / "evidence/print/spool-reconstruction.log",
        RESOURCES / "evidence/recovery-routing.json",
        RESOURCES / "evidence/archive-labels.ini",
        RESOURCES / "acceptance.json",
        RESOURCES / "candidate.json",
    )
    originals = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in source_files}
    with tempfile.TemporaryDirectory(prefix="h17-intake-sft-") as temporary:
        home = Path(temporary)
        original = home / "coupon-original.bin"
        original.write_bytes(b"Synthetic historical-witness container; not an authentic coupon.")
        transcript = home / "coupon-transcription.json"
        write_json(transcript, {
            "job": JOB, "attempt": 2, "state": "ACK", "class": "RECOVER",
            "timestamp_utc": "2026-10-03T18:02:00Z", "payload_hex": KNOWN_ACK,
        })
        caption = home / "caption-transcription.txt"
        caption.write_text("The little lamp stays on until the corridor has gone quiet!", encoding="utf-8")
        print("TEST 1: reject historically recovered ACK payload and draft caption")
        rejected = assess(transcript, original, caption, original)
        assert rejected["acceptance"]["passed"] == 6
        assert rejected["witnesses"]["K04"]["slot_status"] == "NO_MATCH"
        assert rejected["witnesses"]["K08"]["slot_status"] == "NO_MATCH"
        assert rejected["acceptance"]["accepted"] is False
        print("PASS: six accepted; K04/K08 NO_MATCH; combined NO_MATCH")

        print("TEST 2: show source-original digest independently of transcription")
        assert rejected["witnesses"]["K04"]["original_sha256"] == hashlib.sha256(original.read_bytes()).hexdigest()
        assert rejected["witnesses"]["K04"]["transcription_sha256"] == hashlib.sha256(transcript.read_bytes()).hexdigest()
        print("PASS: independent witness original and transcription SHA-256")

        print("TEST 3: reject conflicting historical selector")
        wrong = json.loads(transcript.read_text())
        wrong["attempt"] = 3
        write_json(transcript, wrong)
        try:
            assess(transcript, original, None, None)
        except ValueError as error:
            assert "selector" in str(error)
            print("PASS: REQUESTED/non-final attempt rejected")
        else:
            raise AssertionError("Incorrect coupon selector should raise")
        wrong["attempt"] = 2
        write_json(transcript, wrong)

        print("TEST 4: verify normalization equivalence")
        assert normalize_caption("  THE, Little LAMP!  ") == normalize_caption("the little lamp")
        print("PASS: case, punctuation, and repeated whitespace normalize")

        print("TEST 5: positive acceptance calibration against isolated synthetic commitments")
        fake_resources = home / "resources"
        for relative in (
            "evidence/print/spool-reconstruction.log",
            "evidence/archive-labels.ini",
            "evidence/recovery-routing.json",
            "candidate.json",
            "acceptance.json",
        ):
            destination = fake_resources / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(RESOURCES / relative, destination)
        targets = json.loads((fake_resources / "acceptance.json").read_text(encoding="utf-8"))
        constructed = rejected["witnesses"]
        for slot in ("K04", "K08"):
            targets["slot_sha256"][slot] = hashlib.sha256(bytes.fromhex(constructed[slot]["derived_component"])).hexdigest()
        fake_candidate = json.loads((fake_resources / "candidate.json").read_text(encoding="utf-8"))
        for slot in ("K04", "K08"):
            fake_candidate[slot] = constructed[slot]["derived_component"]
        combined = targets["combined_prefix"] + "".join(fake_candidate[f"K{i:02d}"] + "\n" for i in range(1, 9))
        targets["combined_sha256"] = hashlib.sha256(combined.encode("ascii")).hexdigest()
        write_json(fake_resources / "acceptance.json", targets)
        positive = assess(transcript, original, caption, original, resources=fake_resources)
        assert positive["acceptance"]["passed"] == 8
        assert positive["acceptance"]["combined"] == "PASS"
        assert positive["acceptance"]["accepted"] is True
        assert positive["candidate"] == fake_candidate
        print("PASS: 8/8 and combined PASS, synthetic commitments only")

    print("TEST 6: original evidence, candidate and acceptance bytes unchanged")
    for path in source_files:
        assert originals[str(path)] == hashlib.sha256(path.read_bytes()).hexdigest(), path
    print("PASS: five source integrity comparisons unchanged")
    print("SUMMARY: 6/6 tests passed. Historical K04/K08 remain unverified.")


if __name__ == "__main__":
    main()
