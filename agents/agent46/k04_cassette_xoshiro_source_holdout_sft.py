"""Read-only paired cassette return-seed PRNG original-source holdout.

Hypothesis: five office return ticket numbers seeded printer's full 16-byte coupon.
Calibrate against intact ESC-S/PS-261003-0448 RECOVER ACK1 before applying
the same complete model to disputed ESC-N/PS-261003-0417 ACK2.
This is speculative; the register attests asset custody, not RNG firmware.

Run from workplace-v2 root: python agents/agent46/k04_cassette_xoshiro_source_holdout_sft.py
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(SPOOL).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
REGISTER = (ROOT / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt").read_bytes()
assert hashlib.sha256(REGISTER).hexdigest() == "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf"
SOUTH = bytes.fromhex("234BE186E97EE05830909790E336109E")
assert b"JOB=PS-261003-0448 ATTEMPT=1 STATE=ACK CLASS=RECOVER PAYLOAD=234BE186E97EE05830909790E336109E" in SPOOL

M32 = (1 << 32) - 1
M64 = (1 << 64) - 1
NORTH_TICKETS = (94, 81, 106, 99, 112)
SOUTH_TICKETS = (130, 151, 121, 135, 142)

def rol(x, k, n):
    return ((x << k) | (x >> (n-k))) & ((1 << n)-1)

def stream(seed, algorithm):
    a, b, c, d = (int.from_bytes(seed[i:i+4], "little") for i in (0,4,8,12))
    if algorithm in ("xoshiro128ss", "xoshiro128plus"):
        for _ in range(44):
            output = (rol((b * 5) & M32, 7, 32) * 9) & M32 if algorithm == "xoshiro128ss" else (a+d) & M32
            t = (b << 9) & M32
            c ^= a
            d ^= b
            b ^= c
            a ^= d
            c ^= t
            d = rol(d, 11, 32)
            yield output.to_bytes(4, "little")
    elif algorithm == "xorshift128":
        for _ in range(44):
            t = d
            t ^= (t << 11) & M32
            t ^= t >> 8
            d, c, b, a = c, b, a, (t ^ a ^ (a >> 19)) & M32
            yield a.to_bytes(4, "little")
    elif algorithm == "sfc32":
        for _ in range(44):
            output = (a+b+d) & M32
            d = (d+1) & M32
            a = b ^ (b >> 9)
            b = (c + (c << 3)) & M32
            c = (rol(c, 21, 32)+output) & M32
            yield output.to_bytes(4, "little")
    elif algorithm == "splitmix64":
        x = int.from_bytes(seed[:8], "little")
        for _ in range(44):
            x = (x + 0x9E3779B97F4A7C15) & M64
            z = x
            z = (z^(z >> 30)) * 0xBF58476D1CE4E5B9 & M64
            z = (z^(z >> 27)) * 0x94D049BB133111EB & M64
            yield (z ^ (z >> 31)).to_bytes(8, "little")
    elif algorithm in ("xorshift128plus", "xoroshiro128plus"):
        s0, s1 = (int.from_bytes(seed[i:i+8], "little") for i in (0, 8))
        for _ in range(44):
            if algorithm == "xorshift128plus":
                t = s0 ^ ((s0 << 23) & M64)
                t ^= t >> 17
                t ^= s1 ^ (s1 >> 26)
                s0, s1 = s1, t & M64
            else:
                t = s0 ^ s1
                s0 = rol(s0, 24, 64) ^ t ^ ((t << 16) & M64)
                s1 = rol(t, 37, 64)
            yield ((s0+s1) & M64).to_bytes(8, "little")

def representations(tickets, side):
    d = {}
    for width in (1, 2, 4):
        for endian in ("big", "little"):
            d[f"words/{width}/{endian}"] = b"".join(x.to_bytes(width, endian) for x in tickets)
    for sep in ("", "|", ":", "-", "/", " ", ".", "_", "\n"):
        for fmt, format_ticket in (
            ("ticket", lambda x: f"ST-{x:03d}"),
            ("decimal", str),
            ("zero3", lambda x: f"{x:03d}"),
        ):
            d[f"text/{sep}/{fmt}"] = sep.join(format_ticket(x) for x in tickets).encode()
        d[f"ticket-tabs/{sep}"] = sep.join(f"{i:02d}=ST-{x:03d}" for i, x in enumerate(tickets, 1)).encode()
    for key, raw in list(d.items()):
        labels = {
            "lane": f"L-29/{side}",
            "job": f"PS-261003-{417 if side=='N' else 448:04d}",
            "route": f"ESC-{side}",
            "account": "FA-17" if side == "N" else "LV-42",
            "filing": "H17-POL-17/A3" if side == "N" else "CS-18/5",
        }
        for label, prefix in labels.items():
            for sep in (b"/", b"|", b":"):
                d[f"{key}/prefix-{label}/{sep}"] = prefix.encode()+sep+raw
    return d

def seeds(raw):
    for name, digest in (
        ("md5", hashlib.md5), ("sha256", hashlib.sha256),
        ("blake2s", hashlib.blake2s), ("sha512", hashlib.sha512)
    ):
        value = digest(raw).digest()
        yield name+"-first", value[:16]
        yield name+"-last", value[-16:]
    for mode in ("left", "right", "repeat"):
        value = ((raw+bytes(16))[:16] if mode == "left" else
                 (bytes(16)+raw)[-16:] if mode == "right" else
                 (raw*((16//len(raw))+1))[:16])
        yield "raw-"+mode, value

N, S = representations(NORTH_TICKETS, "N"), representations(SOUTH_TICKETS, "S")
assert N.keys() == S.keys()
control_seed = dict(seeds(S["words/1/big"]))["sha256-first"]
control_coupon = b"".join(list(stream(control_seed, "xoshiro128ss"))[7:11])
assert control_coupon != SOUTH
checks = 0
south_hits = []
control_hits = 0
for fmt in S:
    n_seeds = dict(seeds(N[fmt]))
    for seedname, s_seed in seeds(S[fmt]):
        n_seed = n_seeds[seedname]
        for perm in ("raw", "reversewords", "reverseall", "swap64"):
            seed = {
                "raw": s_seed,
                "reversewords": b"".join(s_seed[i:i+4] for i in (12, 8, 4, 0)),
                "reverseall": s_seed[::-1],
                "swap64": s_seed[8:]+s_seed[:8],
            }[perm]
            for algo in ("xoshiro128ss", "xoshiro128plus", "xorshift128",
                         "sfc32", "splitmix64", "xorshift128plus", "xoroshiro128plus"):
                unit = 8 if algo in ("splitmix64", "xorshift128plus", "xoroshiro128plus") else 4
                output = list(stream(seed, algo))
                for position in range(33):
                    chunk = output[position:position+16//unit]
                    if len(chunk) < 16//unit:
                        continue
                    for endian in ("little", "big"):
                        for direction in ("forward", "reverse"):
                            words = chunk if direction == "forward" else chunk[::-1]
                            coupon = b"".join(w if endian == "little" else w[::-1] for w in words)
                            checks += 1
                            if coupon == SOUTH:
                                south_hits.append((fmt,seedname,perm,algo,position,endian,direction,n_seed.hex()))
                            if (fmt,seedname,perm,algo,position,endian,direction) == (
                                "words/1/big","sha256-first","raw","xoshiro128ss",7,"little","forward"
                            ) and coupon == control_coupon:
                                control_hits += 1

assert len(S) == 672
assert checks == 27320832
assert not south_hits, south_hits
assert control_hits == 1, control_hits
print(json.dumps({
    "selected_print_cassette_source_pairs": len(S),
    "seed_rules": len(list(seeds(b"sample"))),
    "PRNG_families": 7,
    "original_south_complete_coupon_checks": checks,
    "exact_original_south_matches": len(south_hits),
    "planted_source_coupon_control": "PASS exactly once",
}, indent=2))
