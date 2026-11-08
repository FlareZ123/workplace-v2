#!/usr/bin/env python3
"""Source-pinned K04/K08 transcription and cross-class screens; stdlib only."""
from pathlib import Path
import hashlib
import hmac
import itertools
import json
import re
import sys
import time

RESOURCES = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
EXPECTED = {
    "evidence/archive-labels.ini": "146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad",
    "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
    "evidence/crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "evidence/crew/galley-and-stores.log": "23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46",
}
HEX = "0123456789ABCDEF"

def digest(data):
    return hashlib.sha256(data).digest()

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def normalize(text):
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())

def load():
    raw = {p: (RESOURCES / p).read_bytes() for p in EXPECTED}
    actual = {p: hashlib.sha256(v).hexdigest() for p, v in raw.items()}
    assert actual == EXPECTED, actual
    routing = json.loads(raw["evidence/recovery-routing.json"])
    acceptance = json.loads(raw["acceptance.json"])
    labels = raw["evidence/archive-labels.ini"].decode()
    spool = raw["evidence/print/spool-reconstruction.log"].decode()
    notes = raw["evidence/crew/noticeboard-and-desk-notes.txt"].decode()
    galley = raw["evidence/crew/galley-and-stores.log"].decode()
    return actual, routing, acceptance, labels, spool, notes, galley

def spool_rows(text):
    rx = re.compile(r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32})")
    rows = []
    for line in text.splitlines():
        m = rx.search(line)
        if m:
            job, attempt, state, cls, payload = m.groups()
            rows.append((job, int(attempt), state, cls, bytes.fromhex(payload)))
    return rows

def ack(rows, job, cls):
    found = [r for r in rows if r[0] == job and r[2] == "ACK" and r[3] == cls]
    assert found
    return max(found, key=lambda r: r[1])

def mask_screen(payload, mask, target):
    planted = bytearray(mask)
    planted[2] ^= 0x5A
    planted[13] ^= 0xC3
    planted = bytes(planted)
    planted_target = digest(xor_bytes(payload, planted))
    hits, planted_hits, checked = [], [], 0
    for i, j in itertools.combinations(range(16), 2):
        for bi in range(256):
            if bi == mask[i]:
                continue
            for bj in range(256):
                if bj == mask[j]:
                    continue
                candidate = bytearray(mask)
                candidate[i], candidate[j] = bi, bj
                candidate = bytes(candidate)
                value = digest(xor_bytes(payload, candidate))
                checked += 1
                if value == target:
                    hits.append(candidate.hex().upper())
                if value == planted_target:
                    planted_hits.append(candidate.hex().upper())
    assert checked == 7_803_000
    assert planted_hits == [planted.hex().upper()]
    return {"candidates": checked, "commitment_hits": hits,
            "synthetic_mask": planted.hex().upper(), "synthetic_hits": planted_hits}

def full_note_galley_phrases(notes, galley):
    lines = notes.splitlines()
    variants, note_count = [], 0
    for i, line in enumerate(lines):
        m = re.match(r"(N\\d{2}) / (.*)$", line)
        if not m:
            continue
        body, author = lines[i + 1].strip(), m.group(2)
        variants.extend((body, author + " " + body))
        if ":" in body:
            variants.append(body.split(":", 1)[1].strip())
        note_count += 1
    galley_lines = [line.strip() for line in galley.splitlines() if line.strip()]
    for line in galley_lines:
        variants.extend((line, line.split(":", 1)[1].strip() if ":" in line else line))
    phrases = sorted({normalize(v) for v in variants if normalize(v)})
    assert note_count == 24 and len(galley_lines) == 7 and len(phrases) == 81
    return phrases, note_count, len(galley_lines)

def nonce_screen(phrases, note_count, galley_count, nonce, target):
    keys = []
    for i, j in itertools.combinations(range(32), 2):
        for a in HEX:
            if a == nonce[i]:
                continue
            for b in HEX:
                if b == nonce[j]:
                    continue
                chars = list(nonce)
                chars[i], chars[j] = a, b
                keys.append("".join(chars))
    assert len(keys) == len(set(keys)) == 111_600
    hits, checked = [], 0
    for key_hex in keys:
        key = bytes.fromhex(key_hex)
        for phrase in phrases:
            component = hmac.new(key, phrase.encode("ascii"), hashlib.sha256).digest()[:16]
            if digest(component) == target:
                hits.append((key_hex, phrase))
            checked += 1
    planted = list(nonce)
    planted[3] = "A" if planted[3] != "A" else "B"
    planted[27] = "5" if planted[27] != "5" else "6"
    planted_key = "".join(planted)
    planted_phrase = phrases[17]
    planted_component = hmac.new(bytes.fromhex(planted_key), planted_phrase.encode("ascii"), hashlib.sha256).digest()[:16]
    planted_target = digest(planted_component)
    planted_hits = []
    for key_hex in keys:
        component = hmac.new(bytes.fromhex(key_hex), planted_phrase.encode("ascii"), hashlib.sha256).digest()[:16]
        if digest(component) == planted_target:
            planted_hits.append(key_hex)
    assert checked == 9_039_600
    assert planted_hits == [planted_key]
    return {"full_notes": note_count, "galley_entries": galley_count,
            "full_normalized_strings": len(phrases), "nonce_variants": len(keys),
            "checks": checked, "commitment_hits": hits, "synthetic_key": planted_key,
            "synthetic_phrase": planted_phrase, "synthetic_hits": planted_hits}

def crossclass_screen(rows, target):
    n_label = ack(rows, "PS-261003-0417", "LABEL")[4]
    n_recover = ack(rows, "PS-261003-0417", "RECOVER")[4]
    w_stores = ack(rows, "PS-261003-0420", "STORES")[4]
    w_recover = ack(rows, "PS-261003-0420", "RECOVER")[4]
    assert ack(rows, "PS-261003-0417", "LABEL")[1] == 1
    assert ack(rows, "PS-261003-0417", "RECOVER")[1] == 2
    assert ack(rows, "PS-261003-0420", "STORES")[1] == 1
    assert ack(rows, "PS-261003-0420", "RECOVER")[1] == 2
    xor_hits, add_hits, label_hits = [], [], []
    for a in (1, 3, 5, 7, 9, 11, 13, 15):
        for b in range(16):
            p = [(a * j + b) % 16 for j in range(16)]
            dx1 = bytes(n_recover[j] ^ n_label[p[j]] for j in range(16))
            dx2 = bytes(w_recover[j] ^ w_stores[p[j]] for j in range(16))
            da1 = bytes((n_recover[j] - n_label[p[j]]) & 255 for j in range(16))
            da2 = bytes((w_recover[j] - w_stores[p[j]]) & 255 for j in range(16))
            if dx1 == dx2:
                xor_hits.append((a, b, dx1.hex().upper()))
            if da1 == da2:
                add_hits.append((a, b, da1.hex().upper()))
            if digest(bytes(n_label[k] for k in p)) == target:
                label_hits.append((a, b))
    # Plant and uniquely recover one affine permutation plus shared XOR delta.
    a0, b0, delta = 5, 7, bytes(range(16))
    p0 = [(a0 * j + b0) % 16 for j in range(16)]
    fake_n = bytes(n_label[p0[j]] ^ delta[j] for j in range(16))
    fake_w = bytes(w_stores[p0[j]] ^ delta[j] for j in range(16))
    controls = []
    for a in (1, 3, 5, 7, 9, 11, 13, 15):
        for b in range(16):
            p = [(a * j + b) % 16 for j in range(16)]
            d1 = bytes(fake_n[j] ^ n_label[p[j]] for j in range(16))
            d2 = bytes(fake_w[j] ^ w_stores[p[j]] for j in range(16))
            if d1 == d2:
                controls.append((a, b, d1.hex().upper()))
    assert controls == [(a0, b0, delta.hex().upper())]
    return {"pairs": ["0417 LABEL ACK1 -> RECOVER ACK2", "0420 STORES ACK1 -> RECOVER ACK2"],
            "affine_permutations": 128, "common_xor_hits": xor_hits,
            "common_add_hits": add_hits, "permuted_label_hash_hits": label_hits,
            "synthetic_control": controls}

def main():
    start = time.perf_counter()
    source_hashes, routing, acceptance, labels, spool, notes, galley = load()
    rows = spool_rows(spool)
    route_job = re.search(r"^ESC-N=(\S+)$", labels, re.MULTILINE).group(1)
    selected = ack(rows, route_job, "RECOVER")
    assert route_job == "PS-261003-0417" and selected[1] == 2
    payload = selected[4]
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    k04_target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    k08_target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    phrases, note_count, galley_count = full_note_galley_phrases(notes, galley)
    result = {
        "source_hashes": source_hashes,
        "K04_selected": {"job": selected[0], "attempt": selected[1], "payload": payload.hex().upper(),
                         "mask": mask.hex().upper(), "two_byte_mask_screen": mask_screen(payload, mask, k04_target)},
        "K04_crossclass_affine_screen": crossclass_screen(rows, k04_target),
        "K08_two_nibble_nonce_screen": nonce_screen(phrases, note_count, galley_count, routing["K08"]["desk_nonce"].upper(), k08_target),
        "elapsed_seconds": round(time.perf_counter() - start, 3),
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
