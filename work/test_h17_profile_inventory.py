"""Single-file SFT for the H-17 retired-profile inventory tool."""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from h17_profile_inventory import build_inventory, write_inventory


def put(root: Path, relative: str, data: bytes) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="h17-profile-sft-") as temporary:
        base = Path(temporary)
        root = base / "profile"
        root.mkdir()
        output = base / "out" / "profile-inventory.json"

        files = {
            "AppData/Local/Microsoft/Outlook/Archive.ost": b"!BDN" + b"outlook-cache",
            "AppData/Local/Microsoft/OneNote/OneNoteOfflineCache.onecache": b"onenote-cache",
            "AppData/Local/Packages/Microsoft.MicrosoftStickyNotes/LocalState/plum.sqlite": b"SQLite format 3\x00notes",
            "Windows/System32/spool/PRINTERS/00017.SPL": b"printer-spool-object",
            "Windows/System32/winevt/Logs/Microsoft-Windows-PrintService%4Operational.evtx": b"ElfFile\x00print-log",
            "Pictures/crew-caption.jpg": b"\xff\xd8\xffphoto-bytes",
            "Stores/mug-stock.xls": b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1workbook",
            "Downloads/scanrelease.txt": b"scan-release-note",
            "Windows/Search/Data/Applications/Windows.edb": b"search-index",
            "Recent/AutomaticDestinations/example.automaticDestinations-ms": b"jump-list",
            "Unrelated/random.bin": b"unclassified",
            "Chrome/Profile/Cookies/Cookies.sqlite": b"must-not-be-opened-or-listed",
            "Chrome/Profile/Login Data": b"must-not-be-opened-or-listed",
            "Microsoft/Credentials/secret.dat": b"must-not-be-opened-or-listed",
            "Windows/System32/config/SAM": b"must-not-be-opened-or-listed",
            "Windows/System32/config/SECURITY": b"must-not-be-opened-or-listed",
        }
        created = {name: put(root, name, data) for name, data in files.items()}

        try:
            (root / "ExternalLink").symlink_to(root / "Pictures", target_is_directory=True)
            symlink_created = True
        except (OSError, NotImplementedError):
            symlink_created = False

        inventory = build_inventory(root)
        by_path = {item["path"]: item for item in inventory["files"]}
        assert inventory["schema"] == "h17-profile-inventory/v1"
        assert inventory["summary"]["files_listed"] == len(by_path)
        assert "Chrome/Profile/Cookies/Cookies.sqlite" not in by_path
        assert "Chrome/Profile/Login Data" not in by_path
        assert "Microsoft/Credentials/secret.dat" not in by_path
        assert inventory["summary"]["skipped_sensitive_paths"] == 5

        expected = {
            "AppData/Local/Microsoft/Outlook/Archive.ost": ("mail", "PST_OR_OST"),
            "AppData/Local/Microsoft/OneNote/OneNoteOfflineCache.onecache": ("notes", "UNKNOWN"),
            "AppData/Local/Packages/Microsoft.MicrosoftStickyNotes/LocalState/plum.sqlite": ("notes", "SQLITE3"),
            "Windows/System32/spool/PRINTERS/00017.SPL": ("printer", "UNKNOWN"),
            "Windows/System32/winevt/Logs/Microsoft-Windows-PrintService%4Operational.evtx": ("printer", "EVTX"),
            "Pictures/crew-caption.jpg": ("photo_caption", "JPEG"),
            "Stores/mug-stock.xls": ("office_document", "OLE_COMPOUND"),
            "Downloads/scanrelease.txt": ("office_document", "UNKNOWN"),
            "Windows/Search/Data/Applications/Windows.edb": ("profile_metadata", "UNKNOWN"),
            "Recent/AutomaticDestinations/example.automaticDestinations-ms": ("profile_metadata", "UNKNOWN"),
        }
        for relative, (category, magic) in expected.items():
            item = by_path[relative]
            assert category in item["categories"], (relative, item["categories"])
            assert item["sha256"] == hashlib.sha256(created[relative].read_bytes()).hexdigest(), relative
            assert item["magic"] == magic, (relative, item["magic"])
            assert item["hash_status"] == "stable", relative

        unrelated = by_path["Unrelated/random.bin"]
        assert unrelated["hash_status"] == "not_hashed_non_candidate"
        assert unrelated["sha256"] is None
        if symlink_created:
            assert inventory["summary"]["skipped_links_or_reparse_points"] == 1
            assert not any(path.startswith("ExternalLink/") for path in by_path)

        try:
            write_inventory(inventory, root / "inside.json")
            raise AssertionError("output inside source root was accepted")
        except ValueError:
            pass

        output.parent.mkdir(parents=True)
        written = write_inventory(inventory, output)
        assert written == output
        loaded = json.loads(output.read_text(encoding="utf-8"))
        assert loaded["summary"] == inventory["summary"]
        assert not output.with_name(output.name + ".lock").exists()
        assert not list(output.parent.glob(f".{output.name}.*.tmp"))

        lock_path = output.with_name(output.name + ".lock")
        lock_path.write_text("test lock", encoding="utf-8")
        try:
            write_inventory(inventory, output)
            raise AssertionError("concurrent output lock was ignored")
        except FileExistsError:
            pass
        lock_path.unlink()

        print("PASS: relevant profile stores classified and SHA-256 pinned")
        print("PASS: credential/cookie paths excluded before file hashing")
        print("PASS: symlinks not followed" if symlink_created else "SKIP: symlink creation unavailable")
        print("PASS: output outside source root, locked, and atomically replaced")
        print(f"PASS: {inventory['summary']}")


if __name__ == "__main__":
    main()
