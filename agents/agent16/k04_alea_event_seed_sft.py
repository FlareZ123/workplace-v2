"""H-17 K04 Alea event-derived text-seed pilot; original peer packet controls.

Run from the workplace-v2 repository root with Python 3. No source writes.
The selected 0417 ACK2 copied packet is never fitted as original media.
"""
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
A = 2091639
Q = 2**32
DISCARDS = 512
MODES = ("byte_hi", "word_be", "word_le", "word_be_reverse", "word_le_reverse")


class Alea:
    """Exact native word port of seedrandom/lib/alea.js; MIT license."""
    def __init__(self, seed):
        n = 0xEFC8249D

        def mash(value):
            nonlocal n
            for char in str(value):
                n += ord(char)
                h = 0.02519603282416938 * n
                n = int(h) & 0xFFFFFFFF
                h -= n
                h *= n
                n = int(h) & 0xFFFFFFFF
                h -= n
                n += h * Q
            return (int(n) & 0xFFFFFFFF) / Q

        self.c = 1
        self.s0 = mash(" ")
        self.s1 = mash(" ")
        self.s2 = mash(" ")
        self.s0 = (self.s0 - mash(seed)) % 1.0
        self.s1 = (self.s1 - mash(seed)) % 1.0
        self.s2 = (self.s2 - mash(seed)) % 1.0

    def next_word(self):
        t = A * self.s0 + self.c / Q
        self.s0 = self.s1
        self.s1 = self.s2
        self.c = int(t)
        self.s2 = t - self.c
        return int(self.s2 * Q)


def seed_templates(row):
    dt = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
    job = row["job"]
    suffix = job.rsplit("-", 1)[-1]
    alias = {"0417": "ESC-N", "0448": "ESC-S", "0420": "WATCH-SPARE"}[suffix]
    times = {
        "isoz": row["timestamp"],
        "isoplus": dt.isoformat(),
        "utc_seconds": str(int(dt.timestamp())),
        "utc_millis": str(int(dt.timestamp()) * 1000),
        "t_short": dt.strftime("%Y%m%d%H%M%S"),
    }
    jobs = {"job": job, "suffix": suffix, "route": alias}
    out = {}
    for jkey, jval in jobs.items():
        out[jkey] = jval
        for field in ("attempt", "state", "class", "dest"):
            for sep in ("|", ":", "-", "/", " ", "_"):
                out[f"{jkey}{sep}{field}"] = f"{jval}{sep}{row[field]}"
                out[f"{field}{sep}{jkey}"] = f"{row[field]}{sep}{jval}"
        for tkey, timevalue in times.items():
            out[tkey] = timevalue
            for sep in ("|", ":", "-", "/", " ", "_"):
                out[f"{jkey}{sep}{tkey}"] = f"{jval}{sep}{timevalue}"
                out[f"{tkey}{sep}{jkey}"] = f"{timevalue}{sep}{jval}"
                out[f"{jkey}{sep}{tkey}{sep}attempt"] = f"{jval}{sep}{timevalue}{sep}{row['attempt']}"
                out[f"{jkey}{sep}attempt{sep}{tkey}"] = f"{jval}{sep}{row['attempt']}{sep}{timevalue}"
    out["literal_fields"] = (
        f"JOB={job} ATTEMPT={row['attempt']} STATE={row['state']} "
        f"CLASS={row['class']} DEST={row['dest']}"
    )
    out["line_no_payload"] = f"{row['timestamp']} {out['literal_fields']}"
    out["json_sorted"] = json.dumps(
        {key: row[key] for key in ("timestamp", "job", "attempt", "state", "class", "dest")},
        sort_keys=True, separators=(",", ":")
    )
    assert len(out) == 515, len(out)
    return out


def packet(words, phase, mode):
    if mode == "byte_hi":
        return bytes(w >> 24 for w in words[phase:phase+16])
    section = words[phase:phase+4]
    if mode.endswith("reverse"):
        section = section[::-1]
    return b"".join(w.to_bytes(4, "little" if "le" in mode else "big") for w in section)


def probe(row, target, horizon):
    seed_sources = seed_templates(row)
    checks = 0
    first4 = 0
    matches = []
    for formula, value in seed_sources.items():
        rng = Alea(value)
        words = [rng.next_word() for _ in range(horizon + 16)]
        for phase in range(horizon):
            for mode in MODES:
                result = packet(words, phase, mode)
                checks += 1
                if result[:4] == target[:4]:
                    first4 += 1
                    if result == target:
                        matches.append((formula, phase, mode))
    return checks, first4, matches


def main():
    root = Path(os.environ.get(
        "H17_SOURCE_ROOT", str(Path(__file__).resolve().parents[2] / "resources")))
    data = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == SPOOL_SHA
    expr = re.compile(
        r"(?P<timestamp>\S+) JOB=(?P<job>\S+) ATTEMPT=(?P<attempt>\d+) "
        r"STATE=(?P<state>\w+) CLASS=(?P<class>\w+) "
        r"PAYLOAD=(?P<payload>[0-9A-F]{32}) DEST=(?P<dest>\S+)")
    rows = [match.groupdict() for line in data.decode().splitlines()
            if (match := expr.fullmatch(line))]
    assert len(rows) == 133
    selected = next(r for r in rows if r["job"].endswith("0417") and r["attempt"] == "2")
    assert selected["state"] == "ACK" and selected["class"] == "RECOVER"
    assert Alea("seed1").next_word() == int(0.061422935919836164 * Q)
    peers = [next(r for r in rows if r["job"].endswith(suffix) and r["attempt"] == attempt)
             for suffix, attempt in (("0448", "1"), ("0420", "2"))]

    formula, phase, mode = "job|isoz|attempt", 17, "word_le_reverse"
    fake_rng = Alea(seed_templates(peers[0])[formula])
    fake = packet([fake_rng.next_word() for _ in range(64+16)], phase, mode)
    control = probe(peers[0], fake, 64)
    assert control[2] == [(formula, phase, mode)], control
    print("PLANTED_SOURCE_PACKET_PASS", control)

    for peer in peers:
        checks, first4, hits = probe(peer, bytes.fromhex(peer["payload"]), DISCARDS)
        print("ORIGINAL_PEER", peer["job"], peer["attempt"], 
              "complete_checks", checks, "prefix4_hits", first4,
              "whole_packet_hits", len(hits))
        assert checks == 1_318_400 and first4 == 0 and hits == []
    print("K04: no source-selected Alea event issuer; copied ACK2 excluded")


if __name__ == "__main__":
    main()
