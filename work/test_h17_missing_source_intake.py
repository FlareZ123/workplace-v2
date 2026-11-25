"""Synthetic regression tests for the redacted H-17 missing-source intake."""
import hashlib
import hmac
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from work.h17_missing_source_intake import normalize, print_rows, run_intake, select_k04_ack

SCRIPT = Path(__file__).with_name("h17_missing_source_intake.py")


def record(attempt, state="ACK", cls="RECOVER", payload="A" * 32,
           timestamp="2026-10-03T18:02:00Z", dest="bench", job="PS-261003-0417"):
    return (
        f"{timestamp} JOB={job} ATTEMPT={attempt} STATE={state} "
        f"CLASS={cls} PAYLOAD={payload} DEST={dest}\n"
    )


class K04AckSelectionTests(unittest.TestCase):
    def test_job_identifier_must_match_exactly(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "spool-reconstruction.log"
            p.write_text(record(2, job="PS-261003-04170"))
            parsed = print_rows(p, reveal=True)
        self.assertEqual(parsed, [])

    def test_later_requested_attempt_does_not_displace_ack(self):
        rows = [
            record(1, cls="LABEL", payload="1" * 32),
            record(2, payload="2" * 32),
            record(3, state="REQUESTED", payload="3" * 32),
        ]
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "spool-reconstruction.log"
            p.write_text("".join(rows))
            parsed = print_rows(p, reveal=True)
        selected, top, _ = select_k04_ack(parsed, reveal=True)
        self.assertEqual(selected["attempt"], 2)
        self.assertEqual(selected["payload"], "2" * 32)
        self.assertEqual(len(top), 1)

    def test_conflicting_highest_ack_payloads_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "conflicting payloads"):
            select_k04_ack([
                {"attempt": 2, "state": "ACK", "class": "RECOVER", "payload": "A" * 32,
                 "path": "a/queue.log", "line": 1, "timestamp": "2026-10-03T18:02:00Z", "dest": "bench"},
                {"attempt": 2, "state": "ACK", "class": "RECOVER", "payload": "B" * 32,
                 "path": "b/queue.log", "line": 1, "timestamp": "2026-10-03T18:02:00Z", "dest": "bench"},
            ], reveal=True)

    def test_identical_duplicate_highest_ack_is_deterministic(self):
        selected, top, _ = select_k04_ack([
            {"attempt": 2, "state": "ACK", "class": "RECOVER", "payload": "A" * 32,
             "path": "a/queue.log", "line": 1, "timestamp": "2026-10-03T18:02:00Z", "dest": "bench"},
            {"attempt": 2, "state": "ACK", "class": "RECOVER", "payload": "A" * 32,
             "path": "b/queue.log", "line": 3, "timestamp": "2026-10-03T18:03:00Z", "dest": "bench"},
        ], reveal=True)
        self.assertEqual(len(top), 2)
        self.assertEqual(selected["path"], "b/queue.log")
        self.assertEqual(selected["timestamp"], "2026-10-03T18:03:00Z")

    def test_highest_ack_must_be_recover(self):
        with self.assertRaisesRegex(ValueError, "non-RECOVER"):
            select_k04_ack([
                {"attempt": 1, "state": "ACK", "class": "RECOVER", "payload": "A" * 32,
                 "path": "a/queue.log", "line": 1, "timestamp": "", "dest": "bench"},
                {"attempt": 2, "state": "ACK", "class": "LABEL", "payload": "B" * 32,
                 "path": "b/queue.log", "line": 1, "timestamp": "", "dest": "bench"},
            ], reveal=True)

    def test_source_path_line_timestamp_and_destination_are_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "queue.log"
            p.write_text(record(2, timestamp="2026-10-03T18:02:00Z", dest="bench"))
            rows = print_rows(p, reveal=True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["path"], str(p))
        self.assertEqual(rows[0]["line"], 1)
        self.assertEqual(rows[0]["timestamp"], "2026-10-03T18:02:00Z")
        self.assertEqual(rows[0]["dest"], "bench")

    def test_parser_helpers_redact_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "queue.log"
            path.write_text(record(2, payload="C" * 32))
            safe_rows = print_rows(path)
        self.assertNotIn("payload", safe_rows[0])
        self.assertEqual(safe_rows[0]["path"], "queue.log")


class MissingSourceIntakeRedactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.resources = Path(self.temp.name) / "resources"
        self.evidence = self.resources / "evidence"
        (self.evidence / "print").mkdir(parents=True)
        (self.evidence / "crew").mkdir(parents=True)

        self.mask = bytes(range(16, 32))
        self.nonce = bytes(range(32, 48))
        self.component = bytes(range(16))
        self.coupon = bytes(a ^ b for a, b in zip(self.component, self.mask))
        self.phrase = "A synthetic watch at the table"
        k08_component = hmac.new(
            self.nonce, normalize(self.phrase).encode("ascii"), hashlib.sha256
        ).digest()[:16]
        routing = {
            "K04": {"masked_component": self.mask.hex()},
            "K08": {"desk_nonce": self.nonce.hex()},
        }
        acceptance = {
            "slot_sha256": {
                "K04": hashlib.sha256(self.component).hexdigest(),
                "K08": hashlib.sha256(k08_component).hexdigest(),
            }
        }
        (self.evidence / "recovery-routing.json").write_text(json.dumps(routing), encoding="utf-8")
        (self.resources / "acceptance.json").write_text(json.dumps(acceptance), encoding="utf-8")
        self.spool = self.evidence / "print" / "spool-reconstruction.log"
        self.spool.write_text(record(2, payload=self.coupon.hex().upper()), encoding="utf-8")
        self.notes = self.evidence / "crew" / "noticeboard-and-desk-notes.txt"
        self.notes.write_text(self.phrase, encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_synthetic_matches_emit_status_but_no_recovery_material(self):
        report = run_intake(self.evidence)
        rendered = json.dumps(report)
        self.assertTrue(report["k04"]["commitment_match"])
        self.assertEqual(report["k08"]["commitment_matches"], 1)
        self.assertTrue(report["redaction_applied"])
        for secret in (self.coupon.hex(), self.component.hex(), self.mask.hex(), self.nonce.hex(), self.phrase):
            self.assertFalse(secret in rendered, "sensitive material leaked")
        for key in ('"payload"', '"component"', '"phrase"', '"nonce"', '"mask"', '"sha256"'):
            self.assertFalse(key in rendered, "sensitive field emitted")

    def test_pdf_is_not_a_k08_text_carrier(self):
        self.notes.unlink()
        desk_images = self.evidence / "desk-images"
        desk_images.mkdir()
        (desk_images / "BX25-08.pdf").write_text(self.phrase, encoding="utf-8")
        report = run_intake(self.evidence)
        self.assertEqual(report["k08"]["commitment_matches"], 0)

    def test_nonrecover_highest_ack_fails_closed_without_payload(self):
        with self.spool.open("a", encoding="utf-8") as stream:
            stream.write(record(3, cls="LABEL", payload=self.coupon.hex().upper()))
        report = run_intake(self.evidence)
        rendered = json.dumps(report)
        self.assertEqual(report["k04"]["status"], "ambiguous_or_invalid")
        self.assertFalse(self.coupon.hex() in rendered, "payload leaked on selection failure")

    def test_cli_exits_nonzero_on_conflicting_highest_ack_without_leaking(self):
        with tempfile.TemporaryDirectory() as td:
            resources = Path(td) / "resources"
            evidence = resources / "evidence"
            (evidence / "a").mkdir(parents=True)
            (evidence / "b").mkdir(parents=True)
            mask = bytes(range(16))
            nonce = bytes(range(16, 32))
            (evidence / "recovery-routing.json").write_text(json.dumps({
                "K04": {"masked_component": mask.hex()},
                "K08": {"desk_nonce": nonce.hex()},
            }), encoding="utf-8")
            (resources / "acceptance.json").write_text(json.dumps({
                "slot_sha256": {"K04": "0" * 64, "K08": "1" * 64}
            }), encoding="utf-8")
            (evidence / "a" / "queue.log").write_text(record(2, payload="A" * 32), encoding="utf-8")
            (evidence / "b" / "queue.log").write_text(record(2, payload="B" * 32), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(evidence)],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("ambiguous_or_invalid", result.stdout)
        self.assertNotIn("A" * 32, result.stdout)
        self.assertNotIn("B" * 32, result.stdout)
        self.assertNotIn('"payload"', result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
