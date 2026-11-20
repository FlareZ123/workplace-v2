"""Unit tests for the AX-7782 joint-intake orchestrator using stub tools."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h17_ax7782_joint_intake as joint  # noqa: E402


class JointIntakeTests(unittest.TestCase):
    def test_runs_three_existing_tools_and_preserves_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="h17-joint-test-") as tmp_name:
            root = Path(tmp_name)
            work = root / "work"
            resources = root / "resources"
            work.mkdir()
            resources.mkdir()
            source = root / "AX-7782.bin"
            source.write_bytes(b"synthetic-authorized-object" * 32)
            original_hash = hashlib.sha256(source.read_bytes()).hexdigest()

            for script_name in (
                "h17_ax7782_object_intake.py",
                "h17_k04_binary_window_intake.py",
                "h17_ax7782_k08_phrase_intake.py",
            ):
                (work / script_name).write_text(
                    "import json, pathlib, sys\n"
                    "args=sys.argv[1:]\n"
                    "out=pathlib.Path(args[args.index('--json-out')+1])\n"
                    "out.write_text(json.dumps({'stub': pathlib.Path(sys.argv[0]).name, 'args': args}))\n",
                    encoding="utf-8",
                )

            old_root, old_work = joint.ROOT, joint.WORK
            try:
                joint.ROOT, joint.WORK = root, work
                report = joint.inspect_joint(source, resources, timeout=10)
            finally:
                joint.ROOT, joint.WORK = old_root, old_work

            self.assertEqual(report["source"]["sha256_before"], original_hash)
            self.assertEqual(report["source"]["sha256_after"], original_hash)
            self.assertTrue(report["source"]["unchanged"])
            self.assertEqual(
                {name: item["status"] for name, item in report["intakes"].items()},
                {
                    "transfer_validation": "ok",
                    "k04_binary_window": "ok",
                    "k08_exact_phrase": "ok",
                },
            )
            self.assertEqual(
                report["intakes"]["transfer_validation"]["result"]["stub"],
                "h17_ax7782_object_intake.py",
            )
            self.assertEqual(
                report["intakes"]["k04_binary_window"]["result"]["stub"],
                "h17_k04_binary_window_intake.py",
            )
            self.assertEqual(
                report["intakes"]["k08_exact_phrase"]["result"]["stub"],
                "h17_ax7782_k08_phrase_intake.py",
            )

    def test_preserves_json_report_from_nonzero_subtool(self) -> None:
        with tempfile.TemporaryDirectory(prefix="h17-joint-nonzero-") as tmp_name:
            root = Path(tmp_name)
            output = root / "result.json"
            script = root / "nonzero.py"
            script.write_text(
                "import json, pathlib, sys\n"
                "pathlib.Path(sys.argv[1]).write_text(json.dumps({'partial': True}))\n"
                "raise SystemExit(1)\n",
                encoding="utf-8",
            )
            result = joint.run_tool(
                "deliberate-nonzero", [sys.executable, str(script), str(output)],
                output, timeout=10,
            )
            self.assertEqual(result["status"], "nonzero")
            self.assertEqual(result["returncode"], 1)
            self.assertTrue(result["result"]["partial"])


if __name__ == "__main__":
    unittest.main()
