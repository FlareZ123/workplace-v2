import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h17_biff_officeart

from h17_k08_m10_raw_biff_probe import (
    EXPECTED_SYNTHETIC_HMAC16, component, decode_xl_unicode, extract_cell, extract_m10,
    inspect_workbook, normalize, parse_a1_address, parse_workbook_stream,
)

NONCE = bytes(range(16))
PHRASE = "The sea is quiet and the mugs are waiting by the window."


def rec(rid, payload=b""):
    return struct.pack("<HH", rid, len(payload)) + payload


def xlstr(text):
    raw = text.encode("utf-16le")
    return struct.pack("<HB", len(text), 1) + raw


def workbook_stream(sheet_records, global_extras=()):
    name = b"Stock"
    bounds_payload = struct.pack("<IBBBB", 0, 0, 0, len(name), 0) + name
    globals0 = rec(0x0809, struct.pack("<HH", 0x0600, 0x0005)) + rec(0x0085, bounds_payload) + b"".join(global_extras) + rec(0x000A)
    sheet_offset = len(globals0)
    bounds_payload = struct.pack("<IBBBB", sheet_offset, 0, 0, len(name), 0) + name
    globals1 = rec(0x0809, struct.pack("<HH", 0x0600, 0x0005)) + rec(0x0085, bounds_payload) + b"".join(global_extras) + rec(0x000A)
    assert len(globals0) == len(globals1)
    return globals1 + rec(0x0809, struct.pack("<HH", 0x0600, 0x0010)) + b"".join(sheet_records) + rec(0x000A)


def label_record(text, row=9, col=12):
    payload = struct.pack("<HHH", row, col, 4) + xlstr(text)
    return rec(0x0204, payload)


def labelsst_record(index=0, row=9, col=12):
    return rec(0x00FD, struct.pack("<HHHI", row, col, 4, index))


def sst_record(strings):
    payload = struct.pack("<II", len(strings), len(strings)) + b"".join(xlstr(s) for s in strings)
    return rec(0x00FC, payload)


def formula_string_record(text, row=9, col=12):
    cached = bytes([0, 0, 0, 0, 0, 0, 0xFF, 0xFF])
    tokens = b"\x1e\x01\x00"
    payload = (struct.pack("<HHH", row, col, 4) + cached + struct.pack("<HIH", 0, 0, len(tokens)) + tokens)
    return rec(0x0006, payload) + rec(0x0207, xlstr(text))


def multi_workbook_stream(sheet_specs, global_extras=()):
    """Build a small BIFF8 globals block with correctly offset worksheet streams."""
    def bounds_payload(offset, name, visibility=0):
        raw = name.encode("latin1")
        return struct.pack("<IBBBB", offset, visibility, 0, len(raw), 0) + raw

    placeholder = [rec(0x0085, bounds_payload(0, name, vis))
                   for name, _records, vis in sheet_specs]
    prefix = rec(0x0809, struct.pack("<HH", 0x0600, 0x0005))
    suffix = b"".join(global_extras) + rec(0x000A)
    global_length = len(prefix) + sum(map(len, placeholder)) + len(suffix)
    offsets = []
    current = global_length
    for _name, records, _vis in sheet_specs:
        offsets.append(current)
        current += len(rec(0x0809, struct.pack("<HH", 0x0600, 0x0010)))
        current += sum(map(len, records)) + len(rec(0x000A))
    actual_bounds = [rec(0x0085, bounds_payload(offset, name, vis))
                     for (name, _records, vis), offset in zip(sheet_specs, offsets)]
    globals_block = prefix + b"".join(actual_bounds) + suffix
    sheets = []
    for _name, records, _vis in sheet_specs:
        sheets.append(rec(0x0809, struct.pack("<HH", 0x0600, 0x0010))
                      + b"".join(records) + rec(0x000A))
    return globals_block + b"".join(sheets)


class RawM10BiffTests(unittest.TestCase):
    def test_normalization_control(self):
        phrase = "A good watch leaves the room ready for the next pair of hands"
        self.assertEqual(component(NONCE, phrase).hex().upper(), EXPECTED_SYNTHETIC_HMAC16)
        self.assertEqual(normalize("  A-GOOD, watch!\nLEAVES "), "a good watch leaves")

    def test_literal_label_is_read_from_original_record(self):
        stream = workbook_stream([label_record(PHRASE)])
        result = extract_m10(stream)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["sheet"], "Stock")
        self.assertEqual(result[0]["cell"], "M10")
        self.assertEqual(result[0]["value_kind"], "literal_label")
        self.assertEqual(result[0]["raw_text"], PHRASE)
        self.assertTrue(result[0]["raw_record_hex"].startswith("0402"))

    def test_shared_string_is_resolved_from_single_record_sst(self):
        stream = workbook_stream([labelsst_record(0)], [sst_record([PHRASE])])
        result = extract_m10(stream)
        self.assertEqual(result[0]["value_kind"], "shared_string")
        self.assertEqual(result[0]["sst_index"], 0)
        self.assertEqual(result[0]["raw_text"], PHRASE)

    def test_all_worksheets_are_examined_without_sheet_priority(self):
        stream = multi_workbook_stream([
            ("Visible", [label_record("decoy")], 0),
            ("Hidden", [label_record(PHRASE)], 2),
        ])
        result = extract_m10(stream)
        self.assertEqual(len(result), 2)
        self.assertEqual([x["sheet"] for x in result], ["Visible", "Hidden"])
        self.assertEqual(result[1]["sheet_visibility"], 2)
        self.assertEqual(result[1]["raw_text"], PHRASE)

    def test_formula_cached_string_uses_original_string_record(self):
        stream = workbook_stream([formula_string_record(PHRASE)])
        result = extract_m10(stream)
        self.assertEqual(result[0]["value_kind"], "formula_cached_string")
        self.assertEqual(result[0]["raw_text"], PHRASE)
        self.assertEqual(result[0]["formula_tokens_hex"], "1E0100")
        self.assertIn("string_record_hex", result[0])

    def test_exact_p212_locator_is_supported_without_neighbor_scanning(self):
        self.assertEqual(parse_a1_address("P212"), (211, 15))
        stream = workbook_stream([label_record(PHRASE, row=211, col=15)])
        result = extract_cell(stream, "P212")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cell"], "P212")
        self.assertEqual(result[0]["raw_text"], PHRASE)
        self.assertEqual(extract_cell(stream, "M10"), [])
        with self.assertRaisesRegex(ValueError, "outside BIFF8 limits"):
            parse_a1_address("IW1")

    def test_neighbor_cell_is_ignored(self):
        stream = workbook_stream([label_record(PHRASE, row=9, col=11)])
        self.assertEqual(extract_m10(stream), [])

    def test_sst_continue_chain_fails_closed(self):
        stream = workbook_stream([labelsst_record(0)], [sst_record([PHRASE]), rec(0x003C, b"continuation")])
        with self.assertRaisesRegex(ValueError, "SST CONTINUE chain is unsupported"):
            parse_workbook_stream(stream)

    def test_rich_text_string_runs_are_skipped_but_text_is_preserved(self):
        text = "quiet watch"
        raw = struct.pack("<HBH", len(text), 0x09, 1) + text.encode("utf-16le") + b"\x00" * 4
        decoded, end = decode_xl_unicode(raw)
        self.assertEqual(decoded, text)
        self.assertEqual(end, len(raw))

    def test_formula_numeric_cache_is_not_phrase_text(self):
        cached = struct.pack("<d", 123.5)
        payload = struct.pack("<HHH", 9, 12, 4) + cached + struct.pack("<HIH", 0, 0, 0)
        stream = workbook_stream([rec(0x0006, payload)])
        result = extract_m10(stream)
        self.assertEqual(result[0]["value_kind"], "numeric_or_nontext")
        self.assertNotIn("raw_text", result[0])

    def test_encrypted_workbook_rejected(self):
        stream = rec(0x0809, struct.pack("<HH", 0x0600, 0x0005)) + rec(0x002F, b"password") + rec(0x000A)
        with self.assertRaisesRegex(ValueError, "encrypted BIFF8 workbook"):
            parse_workbook_stream(stream)

    def test_end_to_end_read_only_raw_biff_commitment_hit(self):
        stream = workbook_stream([label_record(PHRASE)])
        target = hashlib.sha256(component(NONCE, PHRASE)).hexdigest()

        class FakeCompoundFile:
            def __init__(self, _data):
                pass

            def read_stream(self, _names):
                return "Workbook", stream

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            resources = root / "resources"
            (resources / "evidence").mkdir(parents=True)
            (resources / "evidence" / "recovery-routing.json").write_text(
                json.dumps({"K08": {"desk_nonce": NONCE.hex()}}), encoding="utf-8")
            (resources / "acceptance.json").write_text(
                json.dumps({"slot_sha256": {"K08": target}}), encoding="utf-8")
            workbook = root / "mug-stock.xls"
            workbook.write_bytes(b"original source placeholder")
            before = hashlib.sha256(workbook.read_bytes()).hexdigest()
            with patch.object(h17_biff_officeart, "CompoundFile", FakeCompoundFile):
                result = inspect_workbook(workbook, resources)
            after = hashlib.sha256(workbook.read_bytes()).hexdigest()

        self.assertEqual(result["status"], "MATCH_REQUIRES_SOURCE_REVIEW")
        self.assertEqual(result["match_count"], 1)
        self.assertTrue(result["workbook"]["source_unchanged"])
        self.assertTrue(result["candidate_material_redacted"])
        self.assertNotIn("raw_text", result["cell_records"][0])
        self.assertNotIn("hmac16", result["candidates"][0])
        self.assertNotIn("normalized_phrase", result["candidates"][0])
        self.assertNotIn("component_sha256", result["candidates"][0])
        self.assertNotIn("text_sha256", result["candidates"][0])
        self.assertNotIn("k08_desk_nonce_hex", result)
        self.assertNotIn("k08_target_sha256", result)
        self.assertNotIn("path", result["workbook"])
        self.assertEqual(before, after)

    def test_end_to_end_p212_commitment_hit_is_redacted(self):
        stream = workbook_stream([label_record(PHRASE, row=211, col=15)])
        target = hashlib.sha256(component(NONCE, PHRASE)).hexdigest()

        class FakeCompoundFile:
            def __init__(self, _data):
                pass

            def read_stream(self, _names):
                return "Workbook", stream

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            resources = root / "resources"
            (resources / "evidence").mkdir(parents=True)
            (resources / "evidence" / "recovery-routing.json").write_text(
                json.dumps({"K08": {"desk_nonce": NONCE.hex()}}), encoding="utf-8")
            (resources / "acceptance.json").write_text(
                json.dumps({"slot_sha256": {"K08": target}}), encoding="utf-8")
            workbook = root / "mug-stock.xls"
            workbook.write_bytes(b"original source placeholder")
            with patch.object(h17_biff_officeart, "CompoundFile", FakeCompoundFile):
                result = inspect_workbook(workbook, resources, "P212")

        self.assertEqual(result["status"], "MATCH_REQUIRES_SOURCE_REVIEW")
        self.assertEqual(result["cell"], "P212")
        self.assertEqual(result["match_count"], 1)
        self.assertTrue(result["candidate_material_redacted"])
        self.assertNotIn("raw_text", result["cell_records"][0])
        self.assertNotIn("hmac16", result["candidates"][0])
        self.assertNotIn("normalized_phrase", result["candidates"][0])
        self.assertNotIn("k08_desk_nonce_hex", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
