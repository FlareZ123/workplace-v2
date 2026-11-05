"""Source-wide K04 two-share XOR candidate generator.

Extracts every original raw 16-byte or ASCII-hex32 window, deduplicates and
sorts all 67,470 whole-source objects, then passes them to the exact full-hash
C/OpenMP checker on stdin. Historical evidence is read-only.

The hypothesis is speculative: no surviving record attests XOR-splitting the
original physical ESC-N coupon into two source-contained fragments.
"""
from pathlib import Path
import hashlib
import re
import subprocess
import sys
from zipfile import ZipFile

ORIGINAL_ZIP = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
CARRIER_SHA = "e75d45a2b9e95ed99ce911dc9c4d19ff04cd3bbd2d5fd7ef54e08d2c8f948ab5"


def archive_members(source: Path) -> dict[str, bytes]:
    if source.is_file():
        raw = source.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == ORIGINAL_ZIP
        with ZipFile(source) as archive:
            members = {entry.filename: archive.read(entry.filename)
                       for entry in archive.infolist() if not entry.is_dir()}
    else:
        root = source / "resources" if (source / "resources").is_dir() else source
        names = ["START_HERE.md", "verify.py", "acceptance.json",
                 "candidate.template.json"]
        names.extend(path.relative_to(root).as_posix()
                     for path in (root / "evidence").rglob("*") if path.is_file())
        members = {name: (root / name).read_bytes() for name in names}
    assert len(members) == 46, (len(members), sorted(members))
    assert hashlib.sha256(members["evidence/crew/noticeboard-and-desk-notes.txt"]).hexdigest() == NOTES_SHA
    assert hashlib.sha256(members["evidence/print/spool-reconstruction.log"]).hexdigest() == SPOOL_SHA
    return members


def main(source: Path, checker: Path) -> None:
    members = archive_members(source)
    candidates = set()
    raw_windows = hex_windows = 0
    for content in members.values():
        for pos in range(len(content) - 15):
            candidates.add(content[pos:pos + 16])
            raw_windows += 1
        for match in re.finditer(rb"[0-9A-Fa-f]{32,}", content):
            hx = match.group().decode("ascii")
            for pos in range(len(hx) - 31):
                candidates.add(bytes.fromhex(hx[pos:pos + 32]))
                hex_windows += 1

    assert (raw_windows, hex_windows, len(candidates)) == (117583, 892, 67470)
    payload = b"".join(sorted(candidates))
    assert hashlib.sha256(payload).hexdigest() == CARRIER_SHA
    print("ORIGINAL_SOURCE 46 FILES, RAW16_WINDOWS", raw_windows,
          "HEX32_WINDOWS", hex_windows, "UNIQUE", len(candidates), flush=True)

    completed = subprocess.run([str(checker.resolve())], input=payload,
                               capture_output=True, check=False)
    print(completed.stdout.decode("utf-8", errors="replace"), end="")
    if completed.stderr:
        print(completed.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
    assert completed.returncode == 0, completed.returncode


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Provide original ZIP or repo root, and compiled checker path")
    main(Path(sys.argv[1]), Path(sys.argv[2]))
