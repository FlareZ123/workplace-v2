#!/usr/bin/env python3
"""Regression tests for fail-closed K04 ACK selection."""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("h17_missing_source_intake.py")
SPEC = importlib.util.spec_from_file_location("h17_missing_source_intake", SCRIPT)
INTAKE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INTAKE)


def record(attempt, state="ACK", cls="RECOVER", payload="A" * 32,
           timestamp="2026-10-03T18:02:00Z", dest="bench"):
    return (
        f"{timestamp} JOB=PS-261003-0417 ATTEMPT={attempt} STATE={state} "
        f"CLASS={cls} PAYLOAD={payload} DEST={dest}\n"
    )


class K04AckSelectionTests(unittest.TestCase):
    def test_later_requested_attempt_does_not_displace_ack(self):
        rows = [
            record(1, cls="LABEL", payload="1" * 32),
            record(2, payload="2" * 32),
            record(3, state="REQUESTED", payload="3" * 32),
        ]
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "spool-reconstruction.log"
            p.write_text("".join(rows))
            parsed = INTAKE.print_rows(p)
        selected, top, _ = INTAKE.select_k04_ack(parsed)
        self.assertEqual(selected["attempt"], 2)
        self.assertEqual(selected["payload"], "2" * 32)
        self.assertEqual(len(top), 1)

    def test_conflicting_highest_ack_payloads_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "conflicting payloads"):
            INTAKE.select_k04_ack([
                {"attempt": 2, "state": "ACK", "class": "RECOVER", "payload": "A" * 32,
                 "path": "a/queue.log", "line": 1, "timestamp": "2026-10-03T18:02:00Z", "dest": "bench"},
                {"attempt": 2, "state": "ACK", "class": "RECOVER", "payload": "B" * 32,
                 "path": "b/queue.log", "line": 1, "timestamp": "2026-10-03T18:02:00Z", "dest": "bench"},
            ])

    def test_identical_duplicate_highest_ack_is_deterministic(self):
        selected, top, _ = INTAKE.select_k04_ack([
            {"attempt": 2, "state": "ACK", "class": "RECOVER", "payload": "A" * 32,
             "path": "a/queue.log", "line": 1, "timestamp": "2026-10-03T18:02:00Z", "dest": "bench"},
            {"attempt": 2, "state": "ACK", "class": "RECOVER", "payload": "A" * 32,
             "path": "b/queue.log", "line": 3, "timestamp": "2026-10-03T18:03:00Z", "dest": "bench"},
        ])
        self.assertEqual(len(top), 2)
        self.assertEqual(selected["path"], "b/queue.log")
        self.assertEqual(selected["timestamp"], "2026-10-03T18:03:00Z")

    def test_highest_ack_must_be_recover(self):
        with self.assertRaisesRegex(ValueError, "non-RECOVER"):
            INTAKE.select_k04_ack([
                {"attempt": 1, "state": "ACK", "class": "RECOVER", "payload": "A" * 32,
                 "path": "a/queue.log", "line": 1, "timestamp": "", "dest": "bench"},
                {"attempt": 2, "state": "ACK", "class": "LABEL", "payload": "B" * 32,
                 "path": "b/queue.log", "line": 1, "timestamp": "", "dest": "bench"},
            ])

    def test_source_path_line_timestamp_and_destination_are_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "queue.log"
            p.write_text(record(2, payload="A" * 32, timestamp="2026-10-03T18:02:00Z", dest="bench"))
            rows = INTAKE.print_rows(p)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["path"], str(p))
        self.assertEqual(rows[0]["line"], 1)
        self.assertEqual(rows[0]["timestamp"], "2026-10-03T18:02:00Z")
        self.assertEqual(rows[0]["dest"], "bench")

    def test_cli_exits_nonzero_on_conflicting_highest_ack(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a").mkdir()
            (root / "b").mkdir()
            (root / "a" / "queue.log").write_text(record(2, payload="A" * 32))
            (root / "b" / "queue.log").write_text(record(2, payload="B" * 32))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(root)],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("K04 FAIL-CLOSED", result.stdout)
        self.assertNotIn("K04 component", result.stdout)

    def test_current_export_shape_selects_attempt2_recover_ack(self):
        expected = "A9A9DC5731A5E2AE879C47215C2559D5"
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "spool-reconstruction.log"
            p.write_text(
                record(1, cls="LABEL", payload="E1E60D5F6B6DD2225FA6D5A2A63AD932",
                       timestamp="2026-10-03T16:45:00+00:00", dest="bench")
                + record(1, state="REQUESTED", payload="CD3E4F216ADB2FB180DA2AA90B33F7A4",
                         timestamp="2026-10-03T18:01:00Z", dest="bench")
                + record(2, payload=expected, timestamp="2026-10-03T18:02:00Z", dest="bench")
                + record(3, state="REQUESTED", payload="44D53DFC29D7943A95D89371DA58EC64",
                         timestamp="2026-10-03T18:03:00Z", dest="bench")
            )
            rows = INTAKE.print_rows(p)
        selected, top, _ = INTAKE.select_k04_ack(rows)
        self.assertEqual(selected["attempt"], 2)
        self.assertEqual(selected["class"], "RECOVER")
        self.assertEqual(selected["payload"], expected)
        self.assertEqual(len(top), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
