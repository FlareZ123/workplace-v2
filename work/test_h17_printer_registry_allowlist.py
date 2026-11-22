import tempfile
import unittest
from pathlib import Path

from h17_printer_registry_allowlist import parse_reg_text, parse_reg_file

BASE = r"HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion"


class RegistryAllowlistTests(unittest.TestCase):
    def test_only_allowlisted_values_are_emitted(self):
        text = f'''Windows Registry Editor Version 5.00

[{BASE}\\Devices]
"Office Printer"="winspool,Ne03:"
"Fax"="winspool,Ne04:"

[{BASE}\\PrinterPorts]
"Office Printer"="winspool,Ne03:,15,45"

[{BASE}\\Windows]
"Device"="Office Printer,winspool,Ne03:"
"LegacyDevice"="must-not-appear"

[{BASE}\\Printers\\Connections\\,,PRINTSRV,OfficePrinter]
"Port"="Ne03:"

[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run]
"Secret"="must-not-appear"

[HKEY_LOCAL_MACHINE\\SAM\\Domains\\Account]
"NeverRead"=hex:01,02,03
'''
        got = parse_reg_text(text)
        self.assertEqual(got["value_count"], 5)
        self.assertEqual({x["allowlist_group"] for x in got["values"]},
                         {"Devices", "PrinterPorts", "Windows.Device", "Printers\\Connections"})
        raw = "\n".join(str(x) for x in got["values"])
        self.assertNotIn("must-not-appear", raw)
        self.assertNotIn("NeverRead", raw)
        self.assertEqual(got["values"][3]["value_name"], "Device")
        self.assertEqual(got["values"][3]["decoded_string"], "Office Printer,winspool,Ne03:")

    def test_multiline_hex_is_preserved_without_decoding(self):
        text = f'''Windows Registry Editor Version 5.00
[{BASE}\\Devices]
"Example"=hex(2):77,00,69,00,6e,00,\\
  73,00,70,00,6f,00,6f,00,6c,00,00,00
'''
        got = parse_reg_text(text)
        self.assertEqual(got["value_count"], 1)
        self.assertEqual(got["values"][0]["value_type"], "REG_EXPAND_SZ")
        self.assertIn("6c,00,00,00", got["values"][0]["raw_data"])

    def test_case_insensitive_allowlist(self):
        text = f'''Windows Registry Editor Version 5.00
[{BASE.upper()}\\DEVICES]
"P"="winspool,Ne01:"
'''
        self.assertEqual(parse_reg_text(text)["value_count"], 1)

    def test_utf16le_reg_export_and_source_hash(self):
        text = f'''Windows Registry Editor Version 5.00
[{BASE}\\Windows]
"Device"="P,winspool,Ne01:"
'''
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "profile.reg"
            p.write_bytes(b"\xff\xfe" + text.encode("utf-16le"))
            got = parse_reg_file(p)
            self.assertEqual(got["source_size_bytes"], p.stat().st_size)
        self.assertEqual(got["value_count"], 1)
        self.assertEqual(len(got["source_sha256"]), 64)
        self.assertEqual(got["values"][0]["decoded_string"], "P,winspool,Ne01:")

    def test_refuses_binary_hive_wrong_extension_and_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "NTUSER.DAT"
            p.write_bytes(b"regf" + b"\0" * 32)
            with self.assertRaises(ValueError):
                parse_reg_file(p)
            p2 = Path(d) / "NTUSER.reg"
            p2.write_bytes(b"regf" + b"\0" * 32)
            with self.assertRaises(ValueError):
                parse_reg_file(p2)
            p3 = Path(d) / "link.reg"
            p3.symlink_to(p2)
            with self.assertRaises(ValueError):
                parse_reg_file(p3)

    def test_refuses_missing_header_and_oversize(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.reg"
            p.write_text("[HKEY_CURRENT_USER\\Software\\x]\n\"a\"=\"b\"\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                parse_reg_file(p)
            p.write_text("Windows Registry Editor Version 5.00\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                parse_reg_file(p, max_bytes=5)


if __name__ == "__main__":
    unittest.main()
