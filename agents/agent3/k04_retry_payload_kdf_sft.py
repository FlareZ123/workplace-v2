"""Source-pinned H-17 prior-payload retry KDF probe, with intact attempt-2 holdout.

The known 0420 ACK2 acts as an unmodified, event-matched full-packet
control; the disputed 0417 ACK2 is used only for its metadata and
original commitment. All source/verification files are read-only.
"""
from __future__ import annotations
from hashlib import blake2b, blake2s, sha256
import hashlib
import hmac
import json
from pathlib import Path
import random
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
DATA = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert sha256(DATA).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTING = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
ACCEPT = json.loads((ROOT / "acceptance.json").read_text())
MASK = bytes.fromhex(ROUTING["K04"]["masked_component"])
TARGET = ACCEPT["slot_sha256"]["K04"]
assert MASK.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
assert TARGET == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

rows = []
for line in DATA.decode("ascii").splitlines():
    m = re.fullmatch(
        r"(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)",
        line,
    )
    if m:
        time, job, attempt, state, category, payload, dest = m.groups()
        rows.append(
            dict(time=time, job=job, attempt=attempt, state=state, category=category,
                 payload=bytes.fromhex(payload), dest=dest)
        )
assert len(rows) == 133


def choose(job, attempt, state):
    matches = [
        r for r in rows
        if r["job"].endswith(job) and r["attempt"] == attempt and r["state"] == state
    ]
    assert len(matches) == 1
    return matches[0]


c1 = choose("0420", "1", "ACK")
c2 = choose("0420", "2", "ACK")
s1 = choose("0417", "1", "ACK")
s2 = choose("0417", "1", "REQUESTED")
selected = choose("0417", "2", "ACK")
assert c2["category"] == "RECOVER"
assert selected["time"] == "2026-10-03T18:02:00Z"


def messages(new):
    t = new["time"]
    a = dict(job=new["job"], short=new["job"][-4:], attempt=new["attempt"],
             state=new["state"], category=new["category"], dest=new["dest"],
             date=t[:10], clock=t[11:19], utc=t)
    shapes = [
        ("job",), ("short",), ("utc",), ("date", "clock"), ("job", "attempt"),
        ("job", "category"), ("job", "dest"), ("job", "attempt", "category"),
        ("job", "attempt", "state", "category", "dest"), ("job", "utc", "attempt"),
        ("utc", "job", "attempt"), ("job", "category", "dest", "attempt"),
        ("job", "attempt", "category", "dest", "utc"), ("short", "attempt"),
        ("short", "category", "dest"), ("date", "short", "attempt"),
        ("date", "short", "category"), ("clock", "short", "attempt"),
    ]
    for i, fields in enumerate(shapes):
        for sep in ("", "|", ":", "-", "_", " ", "/"):
            for lowercase in (False, True):
                msg = sep.join(a[x] for x in fields)
                yield (i, sep, lowercase), (
                    msg.lower() if lowercase else msg
                ).encode()


def producers(old, new):
    for desc, m in messages(new):
        for spec, b in [
            ("previous", old["payload"]),
            ("hex", old["payload"].hex().encode()),
            ("prev+header", old["payload"] + m),
            ("header+prev", m + old["payload"]),
            ("hex+header", old["payload"].hex().encode() + b"|" + m),
        ]:
            label = (desc, spec)
            for algo in ("md5", "sha1", "sha256", "sha512", "sha3_256", "blake2b"):
                d = hashlib.new(algo, b).digest()
                yield (label, algo, "first"), d[:16]
                yield (label, algo, "last"), d[-16:]
            for seedid, seed in [
                ("raw", b), ("digest", sha256(b).digest()),
                ("int", int.from_bytes(sha256(b).digest(), "big")),
            ]:
                for method in (
                    "randbytes", "bitsbe", "bitsle", "bytewise",
                    "randrange", "wordbe", "wordle",
                ):
                    rng = random.Random(seed)
                    if method == "randbytes":
                        out = rng.randbytes(16)
                    elif method == "bitsbe":
                        out = rng.getrandbits(128).to_bytes(16, "big")
                    elif method == "bitsle":
                        out = rng.getrandbits(128).to_bytes(16, "little")
                    elif method == "bytewise":
                        out = bytes(rng.getrandbits(8) for _ in range(16))
                    elif method == "randrange":
                        out = bytes(rng.randrange(256) for _ in range(16))
                    else:
                        endian = "big" if method == "wordbe" else "little"
                        out = b"".join(rng.getrandbits(32).to_bytes(4, endian)
                                       for _ in range(4))
                    yield (label, seedid, method), out
        for algo in ("sha1", "sha256", "sha512"):
            for name, key, body in [
                ("old-key", old["payload"], m),
                ("header-key", m, old["payload"]),
            ]:
                d = hmac.digest(key, body, algo)
                yield (desc, algo, name, "first"), d[:16]
                yield (desc, algo, name, "last"), d[-16:]
        yield (desc, "blake2b-key"), blake2b(
            m, key=old["payload"], digest_size=16
        ).digest()
        yield (desc, "blake2s-key"), blake2s(
            m, key=old["payload"], digest_size=16
        ).digest()


def commitment(coupon):
    return sha256(bytes(x ^ y for x, y in zip(coupon, MASK))).hexdigest()


control = list(producers(c1, c2))
control_full = [label for label, v in control if v == c2["payload"]]
control_prefix = [label for label, v in control if v[:4] == c2["payload"][:4]]
selected_hits = []
counts = {}
for name, previous in [("early_LABEL", s1), ("RECOVER_REQUESTED", s2)]:
    tests = list(producers(previous, selected))
    counts[name] = len(tests)
    selected_hits += [
        (name, label, v.hex())
        for label, v in tests if commitment(v) == TARGET
    ]
assert len(control) == counts["early_LABEL"] == counts["RECOVER_REQUESTED"]
assert len(control) == 45108

# The independently planted complete coupon passes source generation,
# XOR reduction and SHA256 commitment without changing the official target.
_, planted = control[1234]
planted_target = commitment(planted)
assert any(commitment(v) == planted_target for _, v in producers(c1, c2))

print(json.dumps({
    "test": "prior-same-job-payload KDF",
    "0420_control_models": len(control),
    "0420_full_matches": len(control_full),
    "0420_prefix4_matches": len(control_prefix),
    "selected_complete_assignments": sum(counts.values()),
    "selected_original_hits": selected_hits,
    "synthetic_positive": True,
}, indent=2))
