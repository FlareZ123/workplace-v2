"""K04: rolling four-bay PTW state as encrypted original printer issuer.

Original 390..416 same-suffix permit/printer pairs furnish 22 complete
four-bay register states; first pair fits a hidden AES-stage XOR pad, 21
entire original printer packets are held out. The selected copied 0417
ACK is never read. Requires cryptography >= 46.0.
"""
from collections import defaultdict
from hashlib import sha256
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
MAINT = ROOT / "evidence/maintenance/seal-receipts.jsonl"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
assert sha256(MAINT.read_bytes()).hexdigest() == "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
assert sha256(SPOOL.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

by_id = defaultdict(list)
for line in MAINT.read_text().splitlines():
    row = json.loads(line)
    if row["signed"] and row["state"] == "CLOSED" and row["fitment"] == "AS_LEFT":
        by_id[int(row["permit"].split("-")[-1])].append(row)

spool = {}
for line in SPOOL.read_text().splitlines():
    match = re.search(
        r"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32})",
        line
    )
    if match and 390 <= int(match[1]) <= 416 and match[2] == "1" and match[3] == "ACK":
        spool[int(match[1])] = bytes.fromhex(match[5])
assert len(spool) == 27

state = {}
records = []
for job in range(390, 417):
    assert len(by_id[job]) == 1
    row = by_id[job][0]
    state[row["bay"]] = bytes.fromhex(row["serial"][3:])
    if len(state) == 4:
        records.append((job, dict(state), spool[job]))
assert len(records) == 22
for bay in "ABCD":
    highest = max(
        (r for r in by_id[417] if r["bay"] == bay),
        key=lambda r: r["revision"]
    )
    state[bay] = bytes.fromhex(highest["serial"][3:])
assert b"".join(state[b] for b in "BDAC").hex().upper() == "D7DAD6BC9714519B7DAD0AD4BE8E87FD"

route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
keys = [mask, bytes.fromhex(route["K08"]["desk_nonce"])] + [
    bytes.fromhex(value) for value in (
        "049AAB2E1CDE7A82CD7C60234303C91A",
        "0D7E3AB56FB75DA3EB0E2E06786D239E",
        "1384AF96E25D6ADA666209CB55E062FA",
        "FF8B78200A56E8586DCDA00EF01E4572",
        "5DBF40EE52FAAED9A536D3326CF0D95A",
        "93495F5E425AB8E592123DABAEB68545"
    )
]
target = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"]

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def convert(block, mode):
    words = [block[i:i+4] for i in range(0, 16, 4)]
    if mode & 1:
        words.reverse()
    if mode & 2:
        words = [w[::-1] for w in words]
    return b"".join(words)

def encode_source(bays, order, view):
    return convert(b"".join(bays[b] for b in order), view)

def aes(key, block, decrypt):
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    op = cipher.decryptor() if decrypt else cipher.encryptor()
    return op.update(block) + op.finalize()

def emit(key, block, pad, decrypt, before):
    if before:
        return aes(key, xor(block, pad), decrypt)
    return xor(aes(key, block, decrypt), pad)

def fit_pad(key, block, observed, decrypt, before):
    if before:
        return xor(block, aes(key, observed, not decrypt))
    return xor(observed, aes(key, block, decrypt))

models = 0
source_fits = 0
minimum_failed_controls = 22
whole_candidates = set()
for order in ("ABCD", "BDAC"):
    for source_view in range(4):
        first_source = encode_source(records[0][1], order, source_view)
        target_source = encode_source(state, order, source_view)
        for packet_view in range(4):
            first_observed = convert(records[0][2], packet_view)
            for key_index, key in enumerate(keys):
                for decrypt in (False, True):
                    for before in (False, True):
                        models += 1
                        pad = fit_pad(key, first_source, first_observed, decrypt, before)
                        wrong = sum(
                            emit(key, encode_source(bays, order, source_view), pad, decrypt, before)
                            != convert(observed, packet_view)
                            for _, bays, observed in records[1:]
                        )
                        minimum_failed_controls = min(minimum_failed_controls, wrong)
                        source_fits += wrong == 0
                        predicted = convert(emit(key, target_source, pad, decrypt, before), packet_view)
                        for component in (predicted, xor(predicted, mask)):
                            whole_candidates.add(component)
                            if sha256(component).hexdigest() == target:
                                print("ORIGINAL_K04_PASS", order, source_view, packet_view,
                                      key_index, decrypt, before, component.hex().upper())
                                raise SystemExit(0)

planted_pad = bytes.fromhex("3E9AC8D75A0116B5F7C4C6356E9F2A0D")
key = keys[4]
for decrypt in (False, True):
    for before in (False, True):
        first_source = encode_source(records[0][1], "BDAC", 3)
        artificial = emit(key, first_source, planted_pad, decrypt, before)
        inferred = fit_pad(key, first_source, artificial, decrypt, before)
        assert inferred == planted_pad
        for _, bays, _ in records[1:]:
            x = encode_source(bays, "BDAC", 3)
            assert emit(key, x, inferred, decrypt, before) == emit(key, x, planted_pad, decrypt, before)
        selected_x = encode_source(state, "BDAC", 3)
        assert emit(key, selected_x, inferred, decrypt, before) == emit(
            key, selected_x, planted_pad, decrypt, before
        )

assert (models, source_fits, minimum_failed_controls, len(whole_candidates)) == (1024, 0, 21, 2048)
print("HISTORICAL complete original printer pairs:", len(records))
print("HISTORICAL entire independent heldouts:", len(records) - 1)
print("AES plus unknown-pad source-model assignments:", models)
print("MIN failed intact whole-record controls:", minimum_failed_controls, "/21")
print("HISTORICAL source-fitting models:", source_fits)
print("ORIGINAL complete K04 candidate values:", len(whole_candidates), "PASS 0")
print("SYNTHETIC AES directions/stages: four 21-holdout + target recovery PASS")
