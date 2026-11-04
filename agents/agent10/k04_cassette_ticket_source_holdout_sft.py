"""Paired L-29/S heldout vs L-29/N hypothetical ticket-keyed printer producers.

Read-only original-archive SFT. Pass the extracted archive root as the first argument;
defaults to the repository resources/ directory when installed in agents/agent10/.
"""
import collections
import hashlib
import hmac
import random
import re
import struct
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
note_bytes = (root / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt").read_bytes()
spool_bytes = (root / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(note_bytes).hexdigest() == "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf"
assert hashlib.sha256(spool_bytes).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
note, spool = note_bytes.decode("utf-8"), spool_bytes.decode("utf-8")
tickets = {lane: re.findall(rf"L-29/{lane}\s+0\d\s+ST-(\d{{3}})", note) for lane in ("N", "S")}
assert all(len(values) == 5 for values in tickets.values())
rows = [line for line in spool.splitlines() if "JOB=PS-261003-0448 " in line and "ATTEMPT=1 STATE=ACK CLASS=RECOVER" in line]
assert len(rows) == 1
reference = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", rows[0]).group(1))
metadata = {
    "N": dict(job="PS-261003-0417", route="ESC-N", set="L-29/N", account="FA-17", ref="H17-POL-17/A3", timestamp="2026-10-03T18:02:00Z", attempt="2", dest="bench"),
    "S": dict(job="PS-261003-0448", route="ESC-S", set="L-29/S", account="LV-42", ref="CS-18/5", timestamp="2026-10-03T18:24:00Z", attempt="1", dest="desk"),
}


def base_forms(lane):
    values = tickets[lane]
    ints = [int(value) for value in values]
    for delimiter in ("", " ", "|", ",", ":", "-", "\n"):
        spellings = [values, [str(value) for value in ints], ["ST-" + value for value in values]]
        for variant, words in enumerate(spellings):
            yield f"string:{delimiter!r}:{variant}", delimiter.join(words).encode()
    for fmt in ("B", "<H", ">H", "<I", ">I"):
        yield fmt, b"".join(struct.pack(fmt, value) for value in ints)


def all_forms(lane):
    bases = list(base_forms(lane))
    yield from bases
    for delimiter in ("", "|", ":", " ", "\n"):
        for field in ("job", "route", "set", "account", "ref", "timestamp", "attempt", "dest"):
            value = metadata[lane][field].encode()
            for label, base in bases:
                sep = delimiter.encode()
                yield f"{label}:post:{field}:{delimiter!r}", base + sep + value
                yield f"{label}:pre:{field}:{delimiter!r}", value + sep + base


def digest_parts(raw):
    for algorithm in ("md5", "sha1", "sha256", "sha512", "sha3_256", "blake2s", "blake2b"):
        digest = hashlib.new(algorithm, raw).digest()
        yield algorithm + ":front", digest[:16]
        yield algorithm + ":middle", digest[(len(digest) - 16) // 2:(len(digest) + 16) // 2]
        yield algorithm + ":back", digest[-16:]
    for algorithm in ("sha256", "sha512"):
        for key_name, key in (("nonce", bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")),
                              ("K01", bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"))):
            yield f"hmac:{algorithm}:{key_name}", hmac.digest(key, raw, algorithm)[:16]


def seed_value(raw, mode):
    if mode == "bytes":
        return raw
    if mode == "text":
        return raw.decode("latin1")
    return int.from_bytes(raw, "big" if mode == "intbe" else "little")


south = list(all_forms("S"))
north = list(all_forms("N"))
assert [label for label, raw in south] == [label for label, raw in north]
paired = []
seen = set()
for (label, s), (_, n) in zip(south, north):
    if (s, n) not in seen:
        seen.add((s, n))
        paired.append((label, s, n))
assert len(paired) == 2106
mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
k04_commitment = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
plant_digest = hashlib.md5(paired[0][1]).digest()
plant_random = random.Random(paired[0][1])
for _ in range(124):
    plant_random_output = plant_random.randbytes(16)
counts = collections.Counter()
synthetic = collections.Counter()
original_matches = []


def probe(output, counterpart, model):
    if output == plant_digest:
        synthetic["digest"] += 1
    if model.endswith(":phase123") and output == plant_random_output:
        synthetic["python"] += 1
    if output == reference:
        component = bytes(a ^ b for a, b in zip(counterpart, mask))
        original_matches.append((model, component.hex(), hashlib.sha256(component).hexdigest() == k04_commitment))


for label, s, n in paired:
    for (algorithm, s_out), (_, n_out) in zip(digest_parts(s), digest_parts(n)):
        counts["digest"] += 1
        probe(s_out, n_out, label + ":" + algorithm)
    for mode in ("bytes", "text", "intbe", "intle"):
        rs = random.Random(seed_value(s, mode))
        rn = random.Random(seed_value(n, mode))
        for phase in range(256):
            counts["python"] += 1
            probe(rs.randbytes(16), rn.randbytes(16), label + f":python:{mode}:phase{phase}")

assert counts == {"digest": 52650, "python": 2156544}
assert synthetic["digest"] >= 1 and synthetic["python"] >= 1
print("SOURCE HOLDOUT: ESC-S 0448 payload", reference.hex())
print("PAIRED INPUTS", len(paired), "MODEL CHECKS", dict(counts))
print("PLANTED CONTROLS", dict(synthetic))
print("ORIGINAL ESC-S HITS", len(original_matches), original_matches)
assert not original_matches
