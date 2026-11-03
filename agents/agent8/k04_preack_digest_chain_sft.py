"""H-17 K04 pre-ACK digest and hash-chain complete-coupon search. Read-only SFT."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
ACC = ROOT / "acceptance.json"
ROUTE = ROOT / "evidence/recovery-routing.json"
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ACC_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
HASHES = {"sha256": hashlib.sha256, "sha1": hashlib.sha1,
          "md5": hashlib.md5, "blake2s": hashlib.blake2s}


def source():
    raw = SPOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    assert hashlib.sha256(ACC.read_bytes()).hexdigest() == ACC_SHA
    pat = re.compile(r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$")
    rows = []
    for line in raw.decode("ascii").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        stamp, job, attempt, state, cl, value, dest = pat.fullmatch(line).groups()
        rows.append(dict(stamp=stamp, job=job, attempt=attempt, state=state,
                         cl=cl, raw=bytes.fromhex(value), hex=value, dest=dest, line=line))
    assert len(rows) == 133
    selected = [r for r in rows if (r["job"], r["attempt"], r["state"], r["cl"]) ==
                ("PS-261003-0417", "2", "ACK", "RECOVER")]
    assert len(selected) == 1 and selected[0]["hex"] == "A9A9DC5731A5E2AE879C47215C2559D5"
    earlier = [r for r in rows if r["stamp"] < selected[0]["stamp"]]
    assert len(earlier) == 129
    return earlier


def groups():
    classes = ("RECOVER", "LABEL", "STORES")
    dests = ("bench", "desk", "store")
    return [("all", lambda r: True),
            ("ACK", lambda r: r["state"] == "ACK"),
            ("REQUESTED", lambda r: r["state"] == "REQUESTED")] + [
             ("class:"+c, lambda r, c=c: r["cl"] == c) for c in classes] + [
             ("dest:"+d, lambda r, d=d: r["dest"] == d) for d in dests] + [
             ("pair:"+c+":"+d, lambda r, c=c, d=d: r["cl"] == c and r["dest"] == d)
             for c in classes for d in dests]


def pack(r, fmt):
    if fmt == "raw":
        return r["raw"]
    if fmt == "hex":
        return r["hex"].encode("ascii")
    return (r["line"] + "\n").encode("ascii")


def reduce(digest, mask, last=False):
    coupon = digest[-16:] if last else digest[:16]
    result = bytes(a ^ b for a, b in zip(coupon, mask))
    return hashlib.sha256(result).digest()


def main():
    rows = source()
    route = json.loads(ROUTE.read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
    target = bytes.fromhex(json.loads(ACC.read_text())["slot_sha256"]["K04"])
    seeded = hashlib.sha256(b"".join(x["raw"] for x in rows[10:86]
                                    if x["cl"] == "RECOVER")).digest()
    planted = reduce(seeded, mask)
    assert planted != target
    tally = Counter()
    for label, belongs in groups():
        for fmt in ("raw", "hex", "line"):
            for method in HASHES.values():
                for start in range(129):
                    h = method()
                    n = 0
                    for end in range(start, 129):
                        if belongs(rows[end]):
                            h.update(pack(rows[end], fmt))
                            n += 1
                        if n:
                            digest = h.digest()
                            for last in (False, True):
                                candidate = reduce(digest, mask, last)
                                tally["interval"] += 1
                                tally["synthetic"] += candidate == planted
                                if candidate == target:
                                    print("FOUND", label, fmt, method().name, start, end, last)
                                    raise AssertionError("Original K04 candidate found")
    assert tally["synthetic"] >= 1
    chain_positive = None
    seeds = (b"", bytes(32), mask, b"H17-IR-261003\n")
    for label, belongs in groups():
        filtered = [r for r in rows if belongs(r)]
        for fmt in ("raw", "hex", "line"):
            for reverse in (False, True):
                order = list(reversed(filtered)) if reverse else filtered
                for seed_no, seed in enumerate(seeds):
                    for state_first in (True, False):
                        state = seed
                        for i, row in enumerate(order):
                            data = pack(row, fmt)
                            state = hashlib.sha256((state + data) if state_first else (data + state)).digest()
                            for last in (False, True):
                                candidate = reduce(state, mask, last)
                                tally["chain"] += 1
                                if candidate == target:
                                    print("FOUND CHAIN", label, fmt, reverse, seed_no, state_first, i, last)
                                    raise AssertionError("Original K04 candidate found")
                                if label == "all" and fmt == "raw" and not reverse and seed_no == 0 and state_first and i == 10 and not last:
                                    chain_positive = candidate
    assert chain_positive is not None
    state = b""
    for row in rows[:11]:
        state = hashlib.sha256(state + row["raw"]).digest()
    assert reduce(state, mask) == chain_positive
    assert tally["interval"] == 3146256 and tally["chain"] == 61920
    print(json.dumps({"preack":129, "groups":len(groups()),
          "interval_checks":tally["interval"],"hash_chain_checks":tally["chain"],
          "original_matches":0,"synthetic_interval_hits":tally["synthetic"],
          "synthetic_chain": "PASS"},indent=2))


if __name__ == "__main__":
    main()
