"""Source-only all-window seven-donor MT coupon reconstruction.

Scans every original nonselected evidence byte window of length 12 and 16,
plus byte-aligned decoded hex runs, allowing all 3!/4! word permutations.
Uses the p951 conditional MT source chronology and original native556 anchor.
The selected 0417 ACK2 line is excluded from every source donor window.
Complete native coupons only are checked against the untouched K04 SHA256.
"""
import hashlib
import itertools
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from agents.agent22.k04_future_donor_source_syndrome_sft import native_coupon, untemper, twist

E = REPO / "resources" / "evidence"
PAIR = list(itertools.combinations(range(4), 2))
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
P0 = b"A9A9DC5731A5E2AE879C47215C2559D5"

def temper(y):
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    return (y ^ (y >> 18)) & 0xFFFFFFFF

def decode(raw, mode):
    little = bool(mode & 1)
    already_native = bool(mode & 2)
    words = tuple(int.from_bytes(raw[i:i + 4], "little" if little else "big")
                  for i in range(0, len(raw), 4))
    return words if already_native else tuple(untemper(x) for x in words)

def original_anchor():
    blob = (E / "print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(blob).hexdigest() == SPOOL_SHA
    lines = blob.splitlines(keepends=True)
    chosen = [line for line in lines if
              b"JOB=PS-261003-0417 " in line and b"ATTEMPT=2 " in line
              and b"STATE=ACK " in line and b"CLASS=RECOVER " in line]
    assert len(chosen) == 1 and b"PAYLOAD=" + P0 in chosen[0]
    packets = [bytes.fromhex(m.group(1).decode()) for line in lines
               for m in re.finditer(rb"PAYLOAD=([0-9A-F]{32})", line)]
    assert len(packets) == 133
    anchor = tuple(untemper(int.from_bytes(packets[73][i:i + 4], "little"))
                   for i in (0, 4, 8))
    return anchor, chosen[0]

def gather(selected):
    left, right = {}, {}
    file_count = 0
    for path in sorted(E.rglob("*")):
        if not path.is_file():
            continue
        blob = path.read_bytes()
        if path.name == "spool-reconstruction.log":
            assert blob.count(selected) == 1
            blob = blob.replace(selected, b"")
        name = str(path.relative_to(E))
        file_count += 1
        for i in range(max(0, len(blob) - 11)):
            left.setdefault(blob[i:i + 12], (name, "raw", i))
        for i in range(max(0, len(blob) - 15)):
            right.setdefault(blob[i:i + 16], (name, "raw", i))
        for match in re.finditer(rb"(?<![a-fA-F0-9])[a-fA-F0-9]{24,}(?![a-fA-F0-9])", blob):
            digits = match.group()
            binary = bytes.fromhex(digits[:len(digits) - len(digits) % 2].decode())
            for i in range(max(0, len(binary) - 11)):
                left.setdefault(binary[i:i + 12], (name, "hex", match.start() + 2 * i))
            for i in range(max(0, len(binary) - 15)):
                right.setdefault(binary[i:i + 16], (name, "hex", match.start() + 2 * i))
    return left, right, file_count

def complete_coupon(native, mask, target):
    words = [temper(w) for w in native]
    for permutation in itertools.permutations(words):
        for reverse in range(16):
            physical = b"".join(
                word.to_bytes(4, "big" if reverse & (1 << i) else "little")
                for i, word in enumerate(permutation))
            candidate = bytes(a ^ b for a, b in zip(physical, mask))
            if hashlib.sha256(candidate).digest() == target:
                return physical, candidate
    return None

def planted_check():
    rng = random.Random(364)
    native = [untemper(rng.getrandbits(32)) for _ in range(1580)]
    donor = [native[i] for i in (1179, 1180, 1181, 1347, 1348, 1574, 1575)]
    original = tuple(native[951:955])
    assert native_coupon(donor, *native[556:559]) == [original]
    corrupt = donor[:]
    corrupt[-1] ^= 2
    assert native_coupon(corrupt, *native[556:559]) == []
    mask = bytes.fromhex(json.loads((E / "recovery-routing.json").read_text())["K04"]["masked_component"])
    physical = b"".join(temper(x).to_bytes(4, "little") for x in original)
    digest = hashlib.sha256(bytes(a ^ b for a, b in zip(physical, mask))).digest()
    assert complete_coupon(original, mask, digest)[0] == physical
    # Both donor blocks can be permuted and serialised big-endian independently.
    l = (donor[2], donor[0], donor[1])
    r = (donor[5], donor[6], donor[3], donor[4])
    assert decode(b"".join(temper(x).to_bytes(4, "big") for x in l), 0) == l
    assert decode(b"".join(temper(x).to_bytes(4, "big") for x in r), 0) == r
    print("SYNTHETIC_SEVEN_DONOR_POSITIVE_AND_MUTATION_NEGATIVE_PASS", flush=True)

def main():
    planted_check()
    anchor, selected = original_anchor()
    left, right, nfiles = gather(selected)
    print("SOURCE_FILES", nfiles, "UNIQUE_LEFT12", len(left), "UNIQUE_RIGHT16", len(right), flush=True)
    right_blocks = list(right.items())
    right_words, by_key = [], defaultdict(list)
    for ri, (raw, loc) in enumerate(right_blocks):
        for mode in range(4):
            vals = decode(raw, mode)
            idx = ri * 4 + mode
            right_words.append(vals)
            for pidx, (a, b) in enumerate(PAIR):
                by_key[vals[a] ^ vals[b]].append(idx * 6 + pidx)
    print("RIGHT_SOURCE_PAIR_VIEWS", sum(map(len, by_key.values())),
          "DISTINCT_XOR_KEYS", len(by_key), flush=True)
    mask = bytes.fromhex(json.loads((E / "recovery-routing.json").read_text())["K04"]["masked_component"])
    target = bytes.fromhex(json.loads((REPO / "resources" / "acceptance.json").read_text())["slot_sha256"]["K04"])
    start = int(os.environ.get("H17_START", "0"))
    stop = int(os.environ.get("H17_END", str(len(left))))
    assert 0 <= start < stop <= len(left)
    seen = set()
    joins = assignments = 0
    hits = []
    pair_counts = Counter()
    for li, (lraw, lloc) in enumerate(left.items()):
        if li < start:
            continue
        if li >= stop:
            break
        for mode in range(4):
            lv = decode(lraw, mode)
            for first in range(3):
                rest_l = [j for j in range(3) if j != first]
                for h555 in (0, 0x80000000):
                    x952 = lv[first] ^ twist(h555, anchor[0])
                    for h951 in (0, 0x80000000):
                        key = twist(h951, x952)
                        for encoded in by_key.get(key, ()):
                            joins += 1
                            ridx, pidx = divmod(encoded, 6)
                            ri, _ = divmod(ridx, 4)
                            rv = right_words[ridx]
                            rloc = right_blocks[ri][1]
                            pair = PAIR[pidx]
                            rest_r = [j for j in range(4) if j not in pair]
                            for p in (pair, pair[::-1]):
                                for q in (rest_r, rest_r[::-1]):
                                    rh = (rv[q[0]], rv[p[0]], rv[q[1]], rv[p[1]])
                                    for rl in (rest_l, rest_l[::-1]):
                                        lh = (lv[first], lv[rl[0]], lv[rl[1]])
                                        for coupon in native_coupon([*lh, *rh], *anchor):
                                            assignments += 1
                                            pair_counts[(lloc[0], rloc[0])] += 1
                                            if coupon in seen:
                                                continue
                                            seen.add(coupon)
                                            recovered = complete_coupon(coupon, mask, target)
                                            if recovered is not None:
                                                raw, key = recovered
                                                hit = {"coupon": raw.hex().upper(), "K04": key.hex().upper(),
                                                       "left": lloc, "right": rloc}
                                                print("ORIGINAL_K04_MATCH", hit, flush=True)
                                                hits.append(hit)
    print("SOURCE_WINDOW_RANGE", start, stop, "XOR_JOIN_MATCHES", joins,
          "SOURCE_COMPATIBLE_ASSIGNMENTS", assignments,
          "UNIQUE_NATIVE_COUPONS", len(seen),
          "ORIGINAL_K04_MATCHES", len(hits), flush=True)
    print("TOP_FILE_PAIRS", pair_counts.most_common(12), flush=True)
    if hits:
        return 3
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
