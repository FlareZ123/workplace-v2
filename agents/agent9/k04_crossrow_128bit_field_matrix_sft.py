"""H17 K04: original-source 128-bit field selectors through 128x128 printer parity maps."""
from pathlib import Path
import hashlib
import json
import re
import hmac
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "resources")
spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
route = (ROOT / "evidence/recovery-routing.json").read_bytes()
notes = (ROOT / "evidence/crew/noticeboard-and-desk-notes.txt").read_text()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(route).hexdigest() == "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
sheet = json.loads(route)
lines = [line for line in spool.decode().splitlines() if "PAYLOAD=" in line]
rows = []
for job in range(300, 428):
    matching = [line for line in lines if f"JOB=PS-261003-{job:04d} " in line
                and "STATE=ACK" in line and "ATTEMPT=1" in line]
    assert len(matching) == 1
    rows.append(int.from_bytes(bytes.fromhex(re.search(
        r"PAYLOAD=([A-F0-9]{32})", matching[0]).group(1)), "little"))
assert len(rows) == 128
FULL = (1 << 128) - 1


def invert(matrix):
    a = [matrix[i] | (1 << (128 + i)) for i in range(128)]
    for j in range(128):
        p = next(i for i in range(j, 128) if (a[i] >> j) & 1)
        a[j], a[p] = a[p], a[j]
        for i in range(128):
            if i != j and (a[i] >> j) & 1:
                a[i] ^= a[j]
    assert all((a[i] & FULL) == (1 << i) for i in range(128))
    return [v >> 128 for v in a]


inverse = invert(rows)


def dot_rows(matrix, x):
    return sum((((r & x).bit_count() & 1) << i) for i, r in enumerate(matrix))


def xor_rows(matrix, x):
    v = 0
    while x:
        b = x & -x
        v ^= matrix[b.bit_length() - 1]
        x ^= b
    return v


def bitflip(source):
    return bytes(int(f"{x:08b}"[::-1], 2) for x in source)


def layouts(s):
    views = [s, s[::-1], bitflip(s), bitflip(s[::-1]),
             b"".join(s[i:i + 4][::-1] for i in range(0, 16, 4)),
             s[8:] + s[:8],
             b"".join(reversed([s[i:i + 4] for i in range(0, 16, 4)]))]
    assert len(set(views)) == 7
    return views


source = {
    "K04_mask": sheet["K04"]["masked_component"],
    "K08_nonce": sheet["K08"]["desk_nonce"],
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
}
nonce = bytes.fromhex(sheet["K08"]["desk_nonce"])
for n in (2, 6, 17, 18):
    line = re.search(rf"N{n:02d} / Emily[^\n]*\n([^\n]+)", notes).group(1)
    line = line.split(": ", 1)[-1]
    normalized = " ".join(re.findall(r"[a-z0-9]+", line.lower()))
    source[f"N{n:02d}_HMAC"] = hmac.new(
        nonce, normalized.encode(), hashlib.sha256).digest()[:16].hex()
assert source["N02_HMAC"].upper() == "BF889359B0303F2B2B2FD96AE841210B"

mask = bytes.fromhex(sheet["K04"]["masked_component"])
true_digest = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
functions = {
    "rows_by_cols": lambda x: dot_rows(rows, x),
    "cols_by_rows": lambda x: xor_rows(rows, x),
    "inverse_rows": lambda x: dot_rows(inverse, x),
    "inverse_cols": lambda x: xor_rows(inverse, x),
}
plant_coupon = dot_rows(rows, int.from_bytes(mask, "little")).to_bytes(16, "little")
plant_digest = hashlib.sha256(bytes(a ^ b for a, b in zip(plant_coupon, mask))).hexdigest()
source_values = {bytes.fromhex(v): k for k, v in source.items()}
checks = 0
hits = []
source_matches = []
plant_hits = []
for name, hex_value in source.items():
    for layout, s in enumerate(layouts(bytes.fromhex(hex_value))):
        x = int.from_bytes(s, "little")
        for transform, fn in functions.items():
            out = fn(x)
            for packing, coupon in (("little", out.to_bytes(16, "little")),
                                    ("big", out.to_bytes(16, "big"))):
                component = bytes(a ^ b for a, b in zip(coupon, mask))
                digest = hashlib.sha256(component).hexdigest()
                checks += 1
                tag = (name, layout, transform, packing)
                if digest == true_digest:
                    hits.append((tag, component.hex()))
                if digest == plant_digest:
                    plant_hits.append(tag)
                if coupon in source_values:
                    source_matches.append((tag, source_values[coupon]))
assert checks == 12 * 7 * 4 * 2
assert plant_hits == [("K04_mask", 0, "rows_by_cols", "little")]
assert not hits
print(json.dumps({"source_fields": len(source), "matrix_rank": 128,
                  "complete_checks": checks, "K04_matches": hits,
                  "source_field_matches": source_matches,
                  "planted_matches": plant_hits}, sort_keys=True))
