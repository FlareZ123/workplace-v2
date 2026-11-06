"""Read-only original ZIP Base64-decoded 16byte K04 carrier search.

Run as a standalone script from a repository checkout with the original ZIP
file mounted at the path specified by user or in the current work directory.
"""
from pathlib import Path
import base64
import hashlib
import re
import sys
import zipfile

ZIP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("h17-archive-dump.zip")
assert hashlib.sha256(ZIP.read_bytes()).hexdigest() == "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
COPIED = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
BASE64 = re.compile(rb"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{22,}={0,2}(?![A-Za-z0-9+/])")


def extract(data):
    runs = invalid = 0
    carriers = set()
    for match in BASE64.finditer(data):
        runs += 1
        for shift in range(4):
            token = match.group(0)[shift:].rstrip(b"=")
            if len(token) < 22:
                continue
            try:
                decoded = base64.b64decode(token + b"=" * (-len(token) % 4), validate=True)
            except ValueError:
                invalid += 1
                continue
            for off in range(max(0, len(decoded) - 15)):
                carriers.add(decoded[off:off+16])
    return carriers, runs, invalid


members = sequences = bad = 0
carriers = set()
with zipfile.ZipFile(ZIP) as z:
    for name in z.namelist():
        if name.endswith("/"):
            continue
        members += 1
        found, runs, invalid = extract(z.read(name))
        sequences += runs
        bad += invalid
        carriers.update(found)

matches = []
for c in carriers:
    candidates = (
        ("coupon", bytes(a ^ b for a, b in zip(c, MASK))),
        ("mask", bytes(a ^ b for a, b in zip(COPIED, c))),
        ("raw", c),
    )
    for name, candidate in candidates:
        if hashlib.sha256(candidate).hexdigest() == TARGET:
            matches.append((name, c.hex()))

print(
    "ZIP_MEMBERS", members,
    "BASE64_SOURCE_RUNS", sequences,
    "UNIQUE_DECODED16", len(carriers),
    "INVALID_PHASES", bad,
    "TARGET_MATCHES", matches,
)
assert members == 46 and sequences == 183 and len(carriers) == 5753 and bad == 173
assert not matches

planted = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
control, runs, _ = extract(b"begin-binary\n" + base64.b64encode(planted) + b"\nend-binary\n")
assert runs == 1 and planted in control
synthetic = hashlib.sha256(bytes(a ^ b for a, b in zip(planted, MASK))).hexdigest()
assert any(
    hashlib.sha256(bytes(a ^ b for a, b in zip(c, MASK))).hexdigest() == synthetic
    for c in control
)
print("PLANTED_COUPON_BASE64_POSITIVE=1")
