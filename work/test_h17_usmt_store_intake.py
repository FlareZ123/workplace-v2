import json
import tempfile
import unittest
from pathlib import Path

import h17_usmt_store_intake as usmt


class UsmtIntakeTests(unittest.TestCase):
    def test_verify_args_summary_and_keyfile(self):
        args = usmt.build_verify_args(Path("store.mig"), Path("log.txt"), "summary",
                                      Path("key.txt"), "AES_128")
        self.assertEqual(args, ["/verify", "store.mig", "/l:log.txt", "/decrypt:AES_128", "/keyfile:key.txt"])

    def test_extract_args_are_targeted_and_do_not_use_loadstate(self):
        args = usmt.build_extract_args(Path("store.mig"), Path("out"), Path("log.txt"),
                                       ["mug-stock.xls", "*.jpg"])
        self.assertEqual(args[:4], ["/extract", "store.mig", "/i:mug-stock.xls,*.jpg", "out"])
        self.assertNotIn("LoadState", args)
        self.assertNotIn("/o", args)
        self.assertIn("*.sqlite-wal", usmt.DEFAULT_INCLUDE)
        self.assertIn("*-shm", usmt.DEFAULT_INCLUDE)
        self.assertIn("*.emf", usmt.DEFAULT_INCLUDE)
        self.assertNotIn("*.pdf", usmt.DEFAULT_INCLUDE)
        self.assertNotIn("*.eml", usmt.DEFAULT_INCLUDE)
        self.assertNotIn("*.msg", usmt.DEFAULT_INCLUDE)

    def test_hash_only_pdf_and_broad_extraction_patterns_are_rejected(self):
        for pattern in ("*.pdf", "BX25-08.PDF", "*.*", "*", "*.eml", "*.msg", "*.pst", "*.ost", "mailbox.pst", "mailbox.ost"):
            with self.subTest(pattern=pattern):
                with self.assertRaises(ValueError):
                    usmt.build_extract_args(Path("store.mig"), Path("out"), Path("log.txt"), [pattern])

    def test_exact_scoped_message_file_is_allowed(self):
        args = usmt.build_extract_args(Path("store.mig"), Path("out"), Path("log.txt"), ["MAIL-16.eml"])
        self.assertIn("MAIL-16.eml", args)

    def test_verify_runs_read_only_and_preserves_native_log(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = root / "store.mig"
            store.write_bytes(b"fake-store-bytes")
            segment = root / "store.mig01"
            segment.write_bytes(b"fake-segment-bytes")
            fake = root / "UsmtUtils.exe"
            args_file = root / "args.txt"
            fake.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' \"$@\" > \"" + str(args_file) + "\"\n"
                "for arg in \"$@\"; do case \"$arg\" in /l:*) log=\"${arg#/l:}\";; esac; done\n"
                "printf 'native log\\n' > \"$log\"\n"
                "exit 0\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)
            out = root / "out"
            manifest = usmt.run_intake(store, fake, out, mode="verify")
            self.assertTrue(manifest["input_unchanged"])
            self.assertEqual(manifest["input"]["sha256"], usmt.sha256_file(store))
            self.assertEqual([Path(x["path"]).name for x in manifest["input_segments_before"]], ["store.mig", "store.mig01"])
            self.assertEqual(manifest["input_segments_before"], manifest["input_segments_after"])
            self.assertTrue((out / "manifest.json").is_file())
            self.assertEqual((out / "usmtutils.log").read_text(encoding="utf-8"), "native log\n")
            self.assertIn("COMMAND:", (out / "runner.log").read_text(encoding="utf-8"))
            args = args_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual(args[0], "/verify:all")
            self.assertEqual(args[1], str(store.resolve()))

    def test_related_store_files_captures_all_segments(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            primary = root / "store.mig"
            primary.write_bytes(b"primary")
            (root / "store.mig01").write_bytes(b"segment-1")
            (root / "store.mig02").write_bytes(b"segment-2")
            (root / "unrelated.mig01").write_bytes(b"unrelated")
            paths = usmt.related_store_files(primary)
            self.assertEqual([p.name for p in paths], ["store.mig", "store.mig01", "store.mig02"])
            self.assertEqual(len(usmt.hash_store_set(primary)), 3)

    def test_extract_hashes_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = root / "store.mig"
            store.write_bytes(b"fake-store-bytes")
            fake = root / "UsmtUtils.exe"
            fake.write_text(
                "#!/bin/sh\n"
                "dest=''\n"
                "for arg in \"$@\"; do case \"$arg\" in */files) dest=\"$arg\";; esac; done\n"
                "[ ! -e \"$dest\" ] || exit 7\n"
                "mkdir -p \"$dest\"\nprintf 'hello' > \"$dest/mug-stock.xls\"\nexit 0\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)
            out = root / "out"
            manifest = usmt.run_intake(store, fake, out, mode="extract", includes=["mug-stock.xls"])
            self.assertTrue(manifest["input_unchanged"])
            self.assertEqual([x["path"] for x in manifest["extracted_files"]], ["mug-stock.xls"])
            self.assertEqual(manifest["extracted_files"][0]["sha256"], usmt.hash_tree(out / "files")[0]["sha256"])

    def test_detects_source_segment_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = root / "store.mig"
            segment = root / "store.mig01"
            store.write_bytes(b"primary")
            segment.write_bytes(b"before")
            fake = root / "UsmtUtils.exe"
            fake.write_text(
                "#!/bin/sh\n"
                "printf 'after' > \"" + str(segment) + "\"\n"
                "exit 0\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)
            out = root / "out"
            with self.assertRaises(RuntimeError):
                usmt.run_intake(store, fake, out, mode="verify")
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertFalse(manifest["input_unchanged"])
            self.assertIn("Source store changed", manifest["warning"])

    def test_alg_requires_keyfile(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = root / "store.mig"
            store.write_bytes(b"fake")
            with self.assertRaises(ValueError):
                usmt.run_intake(store, root / "missing.exe", root / "out", algorithm="AES_128")

    def test_refuses_nonempty_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out"
            out.mkdir()
            (out / "keep.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(ValueError):
                usmt.prepare_output(out)


if __name__ == "__main__":
    unittest.main()
