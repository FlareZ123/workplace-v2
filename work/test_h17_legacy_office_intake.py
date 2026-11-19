#!/usr/bin/env python3
"""Regression tests for the read-only H-17 legacy office intake."""
import hashlib
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook
from openpyxl.comments import Comment

SCRIPT=Path(__file__).with_name("h17_legacy_office_intake.py")
spec=importlib.util.spec_from_file_location("h17_legacy_office_intake",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class LegacyOfficeIntakeTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(mod.normalize("The END-of the night!"),"the end of the night")

    def test_hmac_windows_with_test_commitment(self):
        old_nonce,old_commit=mod.K08_NONCE,mod.K08_COMMIT
        try:
            mod.K08_NONCE=b"test-nonce-0123456789012345678901"
            digest=__import__("hmac").new(mod.K08_NONCE,b"the end of the",hashlib.sha256).digest()[:16]
            mod.K08_COMMIT=hashlib.sha256(digest).hexdigest()
            self.assertTrue(mod.hmac_hit("The END of the!"))
            self.assertFalse(mod.hmac_hit("the beginning of the"))
        finally:
            mod.K08_NONCE,mod.K08_COMMIT=old_nonce,old_commit

    def test_k04_hex_candidate_preserves_xor_and_commit_check(self):
        payload=bytes(range(16))
        hits=[]
        mod.scan_hex(payload.hex().upper(),{"sheet":"S","cell":"A1"},hits)
        self.assertEqual(len(hits),1)
        expected=bytes(a^b for a,b in zip(payload,mod.K04_MASK))
        self.assertEqual(hits[0]["component_hex"],expected.hex().upper())
        self.assertEqual(hits[0]["component_sha256"],hashlib.sha256(expected).hexdigest())
        self.assertFalse(hits[0]["matches_K04"])
        old_commit=mod.K04_COMMIT
        try:
            component=bytes(range(16))
            payload=bytes(a^b for a,b in zip(component,mod.K04_MASK))
            mod.K04_COMMIT=hashlib.sha256(component).hexdigest()
            matching=[]
            mod.scan_hex(payload.hex().upper(),{"sheet":"S","cell":"B1"},matching)
            self.assertTrue(matching[0]["matches_K04"])
        finally:
            mod.K04_COMMIT=old_commit

    def make_workbook(self,path):
        wb=Workbook()
        ws=wb.active
        ws.title="Visible"
        ws["A1"]="Emily final caption"
        ws["B1"]="test phrase"
        ws["C1"]="=1+2"
        ws["A1"].comment=Comment("comment phrase","test")
        hidden=wb.create_sheet("Hidden")
        hidden.sheet_state="hidden"
        hidden["A1"]="hidden sheet words"
        wb.save(path)

    def test_xlsx_visible_hidden_formula_and_comment(self):
        old_nonce,old_commit=mod.K08_NONCE,mod.K08_COMMIT
        try:
            mod.K08_NONCE=b"test-nonce-0123456789012345678901"
            digest=__import__("hmac").new(mod.K08_NONCE,b"the end of the",hashlib.sha256).digest()[:16]
            mod.K08_COMMIT=hashlib.sha256(digest).hexdigest()
            with tempfile.TemporaryDirectory() as td:
                path=Path(td)/"test.xlsx"
                self.make_workbook(path)
                wb=__import__("openpyxl").load_workbook(path)
                wb["Visible"]["A1"]="the end of the"
                wb["Visible"]["B1"]=bytes(range(16)).hex().upper()
                wb["Visible"]["B1"].comment=Comment("the end of the","test")
                wb["Hidden"]["A1"]="the end of the"
                wb.save(path)
                result=mod.extract_one(path,64,True)
                self.assertEqual([s["state"] for s in result["sheets"]],["visible","hidden"])
                self.assertGreaterEqual(result["cell_text_count"],5)
                self.assertTrue(any(h["sheet"]=="Visible" and h["cell"]=="A1" and h["kind"]=="formula_or_value" for h in result["K08_commitment_hits"]))
                self.assertTrue(any(h["sheet"]=="Hidden" and h["cell"]=="A1" for h in result["K08_commitment_hits"]))
                self.assertTrue(any(h["sheet"]=="Visible" and h["cell"]=="B1" and h["kind"]=="comment" for h in result["K08_commitment_hits"]))
                self.assertTrue(any(h["sheet"]=="Visible" and h["cell"]=="B1" for h in result["K04_hex_candidates"]))
                self.assertEqual(result["K04_matching_candidates"],[])
        finally:
            mod.K08_NONCE,mod.K08_COMMIT=old_nonce,old_commit

    @unittest.skipUnless(shutil.which("libreoffice"),"LibreOffice is required for legacy XLS conversion")
    def test_legacy_xls_conversion_is_temporary_and_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            xlsx=root/"test.xlsx"
            out=root/"out"
            out.mkdir()
            self.make_workbook(xlsx)
            subprocess.run(["libreoffice","--headless","--norestore","--nodefault","--nofirststartwizard",
                            "--convert-to","xls","--outdir",str(out),str(xlsx)],
                           capture_output=True,text=True,check=True,timeout=60)
            xls=out/"test.xls"
            before=hashlib.sha256(xls.read_bytes()).hexdigest()
            result=mod.extract_one(xls,64,True)
            after=hashlib.sha256(xls.read_bytes()).hexdigest()
            self.assertEqual(before,after)
            self.assertEqual(len(result["sheets"]),2)
            self.assertIn("hidden",[s["state"] for s in result["sheets"]])

if __name__=="__main__":
    unittest.main()
