"""Synthetic-only static/runtime denial checks; never open an evidence file."""
import ast
from pathlib import Path
import unittest

WORK = Path(__file__).resolve().parent

class PreservationGateTests(unittest.TestCase):
    def gate(self, name, function):
        tree = ast.parse((WORK / name).read_text(encoding="utf-8"))
        fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == function)
        body = list(fn.body)
        if isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            body = body[1:]
        self.assertIsInstance(body[0], ast.Raise)
        # Execute only the actual first executable statement, not imports,
        # parser code, historical fixtures, or any archive material.
        with self.assertRaises(PermissionError):
            exec(compile(ast.Module(body=[body[0]], type_ignores=[]), "<synthetic-gate>", "exec"), {})

    def test_pdf_entrypoints(self):
        for name in ("iter_pdf_embedded_files", "iter_pdf_coupon_text", "iter_pdf_barcode_images"):
            with self.subTest(name=name):
                self.gate("h17_k04_pdf_barcode_intake.py", name)

    def test_profile_entrypoint(self):
        self.gate("h17_profile_k08_phrase_scan.py", "scan_inventory")

if __name__ == "__main__":
    unittest.main()
