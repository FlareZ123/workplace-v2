"""Bounded SFT for the TRP2 seq300-303 / PS0300-0303 numeric suffix join.

The join is a locator hypothesis only. This test checks a finite set of
source-motivated direct, checksum, CPython, xorshift/xoshiro, and PCG mappings.
It does not claim the recorder sequence is a printer job identifier.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import hmac
import itertools
import random
import re
import struct
import zlib

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
START = int(datetime(2026, 10, 3, 21, 14, 0, tzinfo=timezone.utc).timestamp())
END = START + 8
U32 = 0xFFFFFFFF
U64 = 0xFFFFFFFFFFFFFFFF
PCG_MULT = 6364136223846793005
TRP2_SHA256 = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def selected_k05_records():
    raw = (EVIDENCE / "recorder" / "trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TRP2_SHA256
    magic, version, record_size, count = struct.unpack_from("<8sHHI", raw)
    assert (magic, version, record_size) == (b"TRP2DUMP", 2, 24)
    by_latch = {}
    for i in range(count):
        rec = raw[16 + i * 24:16 + (i + 1) * 24]
        if len(rec) != 24:
            continue
        if zlib.crc32(rec[:20]) != struct.unpack_from("<I", rec, 20)[0]:
            continue
        ts, node, event, latch, seq, control, aux, crc = struct.unpack("<IHBBI4sII", rec)
        if node == 49 and event == 82 and START <= ts < END and 0 <= latch <= 3:
            if latch not in by_latch or seq > by_latch[latch]["seq"]:
                by_latch[latch] = {
                    "ts": ts, "latch": latch, "seq": seq,
                    "control": control, "aux": aux,
                }
    assert set(by_latch) == {0, 1, 2, 3}
    return [by_latch[i] for i in range(4)]


def spool_jobs():
    path = EVIDENCE / "print" / "spool-reconstruction.log"
    jobs = {}
    pattern = re.compile(
        r"^(\S+)\s+JOB=PS-261003-(\d{4}).*?PAYLOAD=([0-9A-F]{32})"
    )
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA256
    for line in raw.decode("utf-8").splitlines():
        match = pattern.search(line)
        if not match:
            continue
        stamp, suffix, payload = match.groups()
        suffix = int(suffix)
        if 300 <= suffix <= 303:
            jobs[suffix] = {
                "timestamp": stamp,
                "payload": bytes.fromhex(payload),
            }
    assert set(jobs) == {300, 301, 302, 303}
    assert all(len(row["payload"]) == 16 for row in jobs.values())
    return jobs


def words32(payload, endian):
    return [int.from_bytes(payload[i:i + 4], endian) for i in range(0, 16, 4)]


def xorshift128_step(state):
    x, y, z, w = state
    t = (x ^ (x << 11)) & U32
    new_w = (w ^ (w >> 19) ^ t ^ (t >> 8)) & U32
    return [y, z, w, new_w], new_w


def xoshiro128ss_step(state):
    x, y, z, w = state
    out = (((y * 5) & U32) << 7 | ((y * 5) & U32) >> 25) & U32
    out = (out * 9) & U32
    t = (y << 9) & U32
    z ^= x
    w ^= y
    y ^= z
    x ^= w
    z ^= t
    w = (((w << 11) & U32) | (w >> 21)) & U32
    return [x & U32, y & U32, z & U32, w & U32], out


def stream(step, state, count):
    state = list(state)
    out = []
    for _ in range(count):
        state, value = step(state)
        out.append(value)
    return out


def pcg_step(state, inc):
    old = state
    state = (old * PCG_MULT + inc) & U64
    shifted = (((old >> 18) ^ old) >> 27) & U32
    rot = (old >> 59) & 31
    out = ((shifted >> rot) | (shifted << ((-rot) & 31))) & U32
    return state, out


def pcg_seed(initstate, initseq):
    inc = ((initseq << 1) | 1) & U64
    state = 0
    state, _ = pcg_step(state, inc)
    state = (state + initstate) & U64
    state, _ = pcg_step(state, inc)
    return state, inc


def pcg_stream(state, inc, count):
    out = []
    for _ in range(count):
        state, value = pcg_step(state, inc)
        out.append(value)
    return out


def main():
    records = selected_k05_records()
    jobs = spool_jobs()
    assert [r["seq"] for r in records] == [300, 301, 302, 303]
    assert [r["latch"] for r in records] == [0, 1, 2, 3]
    assert len({r["ts"] for r in records}) == 1
    assert len({r["aux"] for r in records}) == 1

    direct_hits = []
    for rec in records:
        for job, row in jobs.items():
            for offset in range(0, 16, 4):
                chunk = row["payload"][offset:offset + 4]
                if chunk in (rec["control"], rec["control"][::-1]):
                    direct_hits.append((rec["seq"], job, offset))

    hash_hits = []
    for rec in records:
        seq = rec["seq"]
        payload = jobs[seq]["payload"]
        for control in (rec["control"], rec["control"][::-1]):
            for seq_bytes in (seq.to_bytes(4, "big"), seq.to_bytes(4, "little")):
                for aux_bytes in (
                    rec["aux"].to_bytes(4, "big"),
                    rec["aux"].to_bytes(4, "little"),
                ):
                    for fields in itertools.permutations((control, seq_bytes, aux_bytes)):
                        message = b"".join(fields)
                        digests = (
                            hashlib.md5(message).digest(),
                            hashlib.sha1(message).digest()[:16],
                            hashlib.sha256(message).digest()[:16],
                            hashlib.blake2s(message, digest_size=16).digest(),
                        )
                        keys = (control, seq_bytes, aux_bytes)
                        digests += tuple(
                            hmac.new(key, message, hashlib.sha256).digest()[:16]
                            for key in keys
                        )
                        if any(d in (payload, payload[::-1]) for d in digests):
                            hash_hits.append(seq)

    python_hits = []
    for rec in records:
        seq, control, aux = rec["seq"], rec["control"], rec["aux"]
        payload = jobs[seq]["payload"]
        seeds = set()
        for c in (control, control[::-1]):
            for s in (seq.to_bytes(4, "big"), seq.to_bytes(4, "little")):
                for a in (aux.to_bytes(4, "big"), aux.to_bytes(4, "little")):
                    seeds.update((c, c + s, s + c, c + a, a + c, c + a + s))
        for seed in seeds:
            for mode in ("bytes_v1", "bytes_v2", "int_be", "int_le", "hex", "ascii_hex"):
                rng = random.Random()
                if mode == "bytes_v1":
                    rng.seed(seed, version=1)
                elif mode == "bytes_v2":
                    rng.seed(seed, version=2)
                elif mode == "int_be":
                    rng.seed(int.from_bytes(seed, "big"))
                elif mode == "int_le":
                    rng.seed(int.from_bytes(seed, "little"))
                elif mode == "hex":
                    rng.seed(seed.hex().upper())
                else:
                    rng.seed(seed.hex().upper().encode("ascii"))
                generated = b"".join(
                    rng.getrandbits(32).to_bytes(4, "big") for _ in range(4)
                )
                if generated in (payload, payload[::-1]):
                    python_hits.append((seq, mode))

    k05 = b"".join(r["control"] for r in records)
    compact_hits = []
    expected = [
        word
        for job in range(300, 304)
        for word in words32(jobs[job]["payload"], "big")
    ]
    for input_endian in ("big", "little"):
        for input_order in ("forward", "reverse"):
            state = [
                int.from_bytes(k05[i:i + 4], input_endian)
                for i in range(0, 16, 4)
            ]
            if input_order == "reverse":
                state.reverse()
            for name, step in (
                ("xorshift128", xorshift128_step),
                ("xoshiro128ss", xoshiro128ss_step),
            ):
                generated = stream(step, state, 16)
                for output_endian in ("big", "little"):
                    for output_order in ("forward", "reverse"):
                        candidate = generated if output_order == "forward" else generated[::-1]
                        target = [
                            word
                            for job in range(300, 304)
                            for word in words32(jobs[job]["payload"], output_endian)
                        ]
                        if candidate == target:
                            compact_hits.append((name, input_endian, input_order, output_endian, output_order))

    pcg_hits = []
    for endian in ("big", "little"):
        first = int.from_bytes(k05[:8], endian)
        second = int.from_bytes(k05[8:], endian)
        for half_order in ("forward", "reverse"):
            initstate, initseq = (first, second) if half_order == "forward" else (second, first)
            modes = {"canonical": pcg_seed(initstate, initseq)}
            direct_inc = initseq
            if direct_inc & 1:
                modes["direct"] = (initstate, direct_inc)
            for mode, (state, inc) in modes.items():
                if not (inc & 1):
                    continue
                generated = pcg_stream(state, inc, 16)
                for output_endian in ("big", "little"):
                    target = [
                        word
                        for job in range(300, 304)
                        for word in words32(jobs[job]["payload"], output_endian)
                    ]
                    if generated == target or generated[::-1] == target:
                        pcg_hits.append((endian, half_order, mode, output_endian))

    print("K05 selected records:", [(r["seq"], r["latch"], r["aux"]) for r in records])
    print("same-suffix jobs:", [(job, row["timestamp"]) for job, row in sorted(jobs.items())])
    print("direct word hits:", len(direct_hits))
    print("per-pair checksum/MAC hits:", len(hash_hits))
    print("per-record CPython seed hits:", len(python_hits))
    print("K05-state xorshift/xoshiro hits:", len(compact_hits))
    print("K05-state PCG32 hits:", len(pcg_hits))
    assert not direct_hits
    assert not hash_hits
    assert not python_hits
    assert not compact_hits
    assert not pcg_hits
    print("PASS: tested finite mappings do not explain the numeric suffix join")


if __name__ == "__main__":
    main()
