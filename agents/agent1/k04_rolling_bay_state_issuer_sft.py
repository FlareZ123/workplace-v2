"""H-17 K04 rolling-four-bay state issuer, source-first heldout SFT.

The 27 PTW-390..416 seal receipts are tentatively linked by numeric suffix
to same-number printer jobs. A printer might have emitted the four most
recent signed seal serials, as raw bytes, a whitened block, or a digest.
The selected K04 copied ACK is excluded from fitting. Original inputs stay
unchanged. Run with Python 3 standard library from any working directory.
"""
from collections import defaultdict
from hashlib import sha256, sha512, sha1, sha3_256, md5, blake2s, blake2b
from hmac import new as hmac_new
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
MAINT = ROOT / "evidence/maintenance/seal-receipts.jsonl"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
PINS = {
    MAINT: "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    SPOOL: "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
}
for path, expected in PINS.items():
    assert sha256(path.read_bytes()).hexdigest() == expected

by_id = defaultdict(list)
for line in MAINT.read_text().splitlines():
    row = json.loads(line)
    if row["signed"] and row["state"] == "CLOSED" and row["fitment"] == "AS_LEFT":
        by_id[int(row["permit"].split("-")[-1])].append(row)

spool = {}
pattern = re.compile(
    r"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) "
    r"PAYLOAD=([0-9A-F]{32}) DEST=(\w+)"
)
for line in SPOOL.read_text().splitlines():
    match = pattern.search(line)
    if match:
        suffix, attempt, state, cls, payload, dest = match.groups()
        if 390 <= int(suffix) <= 416 and attempt == "1" and state == "ACK":
            spool[int(suffix)] = bytes.fromhex(payload)
assert len(spool) == 27

bay_state = {}
records = []
for job in range(390, 417):
    assert len(by_id[job]) == 1
    receipt = by_id[job][0]
    bay_state[receipt["bay"]] = bytes.fromhex(receipt["serial"][3:])
    if len(bay_state) == 4:
        records.append((job, dict(bay_state), spool[job]))
assert len(records) == 22

route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
keys = [mask, nonce] + [bytes.fromhex(x) for x in (
    "049AAB2E1CDE7A82CD7C60234303C91A",
    "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "1384AF96E25D6ADA666209CB55E062FA",
    "FF8B78200A56E8586DCDA00EF01E4572",
    "5DBF40EE52FAAED9A536D3326CF0D95A",
    "93495F5E425AB8E592123DABAEB68545",
)]

def representations(state):
    for order in ("ABCD", "BDAC"):
        blocks = [state[b] for b in order]
        for reversed_words in (False, True):
            words = [b[::-1] if reversed_words else b for b in blocks]
            name = order + ("/reverse" if reversed_words else "/native")
            yield name + "/binary", b"".join(words)
            yield name + "/hex", b"|".join(b.hex().upper().encode() for b in words)
            yield name + "/serial", b"|".join(
                b"SG-" + b.hex().upper().encode() for b in words
            )

def emitters(message):
    yield "MD5", md5(message).digest()
    yield "SHA1-prefix", sha1(message).digest()[:16]
    yield "SHA256-prefix", sha256(message).digest()[:16]
    yield "SHA256-suffix", sha256(message).digest()[-16:]
    yield "SHA512-prefix", sha512(message).digest()[:16]
    yield "SHA512-suffix", sha512(message).digest()[-16:]
    yield "SHA3-prefix", sha3_256(message).digest()[:16]
    yield "BLAKE2s-128", blake2s(message, digest_size=16).digest()
    yield "BLAKE2b-128", blake2b(message, digest_size=16).digest()
    for index, key in enumerate(keys):
        digest = hmac_new(key, message, "sha256").digest()
        yield f"HMAC{index}/prefix", digest[:16]
        yield f"HMAC{index}/suffix", digest[-16:]
        yield f"BLAKE2s{index}", blake2s(message, digest_size=16, key=key).digest()
        yield f"BLAKE2b{index}", blake2b(message, digest_size=16, key=key).digest()

first = records[0]
holdouts = records[1:]
assert len(holdouts) == 21
passes = {"direct": 0, "unknown_xor_pad": 0, "digest": 0}
models = 0
for rep, message in representations(first[1]):
    if len(message) == 16:
        pad = bytes(a ^ b for a, b in zip(message, first[2]))
        passes["direct"] += all(
            dict(representations(state))[rep] == observed
            for _, state, observed in holdouts
        )
        passes["unknown_xor_pad"] += all(
            bytes(a ^ b for a, b in zip(dict(representations(state))[rep], pad))
            == observed for _, state, observed in holdouts
        )
        models += 2
    for family, output in emitters(message):
        models += 1
        if output == first[2] and all(
            dict(emitters(dict(representations(state))[rep]))[family] == observed
            for _, state, observed in holdouts
        ):
            passes["digest"] += 1

# A planted source history, which reuses all actual receipt states, must
# recover the exact hidden pad and 21 full independent future coupons.
planted_pad = bytes.fromhex("20946D5B7E39AF08AA5C3B1D4F6E8219")
source_view = "BDAC/native/binary"
base = dict(representations(first[1]))[source_view]
synthetic_first = bytes(a ^ b for a, b in zip(base, planted_pad))
fitted_pad = bytes(a ^ b for a, b in zip(base, synthetic_first))
assert fitted_pad == planted_pad
for _, state, _ in holdouts:
    view = dict(representations(state))[source_view]
    assert bytes(a ^ b for a, b in zip(view, fitted_pad)) == bytes(
        a ^ b for a, b in zip(view, planted_pad)
    )

# Recover the precise signed highest-revision PTW417 A/B/C/D state.
for bay in "ABCD":
    highest = max((r for r in by_id[417] if r["bay"] == bay),
                  key=lambda r: r["revision"])
    bay_state[bay] = bytes.fromhex(highest["serial"][3:])
assert bytes.join(b"", [bay_state[b] for b in "BDAC"]).hex().upper() == (
    "D7DAD6BC9714519B7DAD0AD4BE8E87FD"
)

# Test any complete target that the candidate model predicts, even when
# intact historical controls veto that model. A genuine commitment PASS
# would override this exploratory source-control rejection.
target = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"]
candidates = set()
for rep, message in representations(bay_state):
    proposed = ([("direct", message)] if len(message) == 16 else [])
    proposed.extend(emitters(message))
    if len(message) == 16:
        early = dict(representations(first[1]))[rep]
        pad = bytes(a ^ b for a, b in zip(early, first[2]))
        proposed.append(("learned-pad", bytes(a ^ b for a, b in zip(message, pad))))
    for family, coupon in proposed:
        for stage, component in (
            ("direct", coupon),
            ("masked", bytes(a ^ b for a, b in zip(coupon, mask))),
        ):
            candidates.add(component)
            if sha256(component).hexdigest() == target:
                print("ORIGINAL K04 PASS", rep, family, stage, component.hex().upper())
                raise SystemExit(0)

assert models == 500 and len(candidates) == 1000
assert passes == {"direct": 0, "unknown_xor_pad": 0, "digest": 0}
print("HISTORICAL rolling-state whole-packet controls:", len(records))
print("HISTORICAL withheld complete packets:", len(holdouts))
print("SOURCE models:", models, "whole historical fits:", passes)
print("SYNTHETIC planted source control: PASS")
print("ORIGINAL K04 candidate values:", len(candidates), "original PASS: 0")
