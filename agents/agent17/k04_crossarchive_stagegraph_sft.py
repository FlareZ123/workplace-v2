"""Stage-free K04 printer-source index bridge from original AX, recorder and RC17.

Standalone source-pinned original-evidence SFT. Intended from repository root:
    python agents/agent17/k04_crossarchive_stagegraph_sft.py

Selected printer row129 is omitted before its payload is parsed. Physical
producer identity is unproven; all reported stage bounds are conditional.
"""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json
import re
import struct
import sys
import zlib

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "agents" / "agent13"))
import k04_stagefree_31bit_hidden_predecessor_graph_sft as graph

EVIDENCE = REPO / "resources" / "evidence"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TRANSFERS_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
MAG = 0x9908B0DF
LOW31 = 0xBFFFFFFF


def original_printer():
    raw = (EVIDENCE / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    rows = [line for line in raw.decode().splitlines() if "PAYLOAD=" in line]
    assert len(rows) == 133
    assert "ATTEMPT=2 STATE=ACK CLASS=RECOVER" in rows[129]
    flat = []
    words = {}
    for r, line in enumerate(rows):
        if r == 129:
            continue
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert match
        payload = bytes.fromhex(match.group(1))
        native = [graph.untemper(int.from_bytes(payload[4*j:4*j+4], "little"))
                  for j in range(4)]
        words[r] = native
        flat.extend((r, j, native[j]) for j in range(4))
    assert len(flat) == 528
    return flat, words


def original_externals():
    raw = (EVIDENCE / "recorder" / "trip-recorder.raw").read_bytes()
    assert raw[:8] == b"TRP2DUMP"
    assert int.from_bytes(raw[10:12], "little") == 24
    count = int.from_bytes(raw[12:16], "little")
    external = []
    for i in range(count):
        record = raw[16+24*i:16+24*(i+1)]
        assert len(record) == 24
        if zlib.crc32(record[:20]) != int.from_bytes(record[20:24], "little"):
            continue
        node = int.from_bytes(record[4:6], "little")
        seq = int.from_bytes(record[8:12], "little")
        for role, start in (("control", 12), ("aux", 16)):
            external.append((f"TRP2:node{node}:seq{seq}:{role}", record[start:start+4]))
    text = (EVIDENCE / "procedures" / "RC-17-scans.txt").read_text()
    for part in text.split("\f"):
        header = re.search(r"DOCUMENT RC-17 / REV ([^ /]+) / SECTION ([^\n]+)", part)
        code = re.search(r"Footer control strip:\s*([0-9A-F]{8})", part)
        if header and code:
            external.append((f"RC17:{header.group(1)}:{header.group(2)}",
                             bytes.fromhex(code.group(1))))
    return external


def external_stage_edges(words):
    by_xor = defaultdict(list)
    for ra, a in words.items():
        for rb, b in words.items():
            if rb <= ra:
                continue
            for ja, first in enumerate(a):
                for jb, last in enumerate(b):
                    by_xor[(first ^ last) & LOW31].append((ra, ja, rb, jb))
    assert sum(map(len, by_xor.values())) == 138336
    external = original_externals()
    triples = []
    for source, raw in external:
        for endian in ("little", "big"):
            value = int.from_bytes(raw, endian)
            for presentation in ("tempered", "native"):
                native = graph.untemper(value) if presentation == "tempered" else value
                mix = ((native & 0x7FFFFFFF) >> 1) ^ (MAG if native & 1 else 0)
                for ra, ja, rb, jb in by_xor.get(mix & LOW31, ()):
                    delta = 227 + ja - jb
                    if delta < 4 * (rb-ra):
                        continue
                    triples.append((source, endian, presentation, ra, ja, rb, jb, delta))
    assert len(external) == 180, len(external)
    assert len(triples) == 8, triples
    edges = sorted({(ra, rb, delta) for _, _, _, ra, _, rb, _, delta in triples})
    assert edges == [(7, 38, 230), (9, 40, 229), (10, 41, 227), (28, 59, 226)]
    print("CROSSARCHIVE_31BIT_TRIPLES", len(triples),
          Counter(row[0].split(":")[0] for row in triples))
    for source, endian, presentation, ra, ja, rb, jb, delta in triples:
        print("EXTERNAL", source, endian, presentation,
              (ra, ja), (rb, jb), "stage_diff", delta)
    return edges


def ax_bridge(words):
    raw = (EVIDENCE / "transfers" / "transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TRANSFERS_SHA
    transfer = [json.loads(line) for line in raw.splitlines()]
    items = sorted((r for r in transfer if r["kind"] == "CHUNK"
                    and r["transfer"] == "AX-7778"),
                   key=lambda r: (r["seq"], r["attempt"]))
    assert len(items) == 16
    checkpoint = [int.from_bytes(bytes.fromhex(r["checkpoint"]), "little")
                  for r in items][11:15]
    assert checkpoint == [0x35AE, 0x78FE, 0x42DD, 0xFD35]
    def temper(value):
        value ^= value >> 11
        value ^= (value << 7) & 0x9D2C5680
        value ^= (value << 15) & 0xEFC60000
        value ^= value >> 18
        return value & 0xFFFFFFFF
    for lane, actual in enumerate(checkpoint):
        difference = (words[34][lane] ^ words[64][lane]) & LOW31
        parity = difference >> 31
        lower = (((difference ^ (MAG if parity else 0)) & 0x3FFFFFFF) << 1) | parity
        allowed = {temper(lower) >> 16, temper(lower | 0x80000000) >> 16}
        assert actual in allowed, (lane, actual, allowed)
    print("AX_4HALFWORD_HELDOUT", [f"{v:04X}" for v in checkpoint])
    return (34, 64, 227)


def stagegraph(relations, extra):
    union = graph.WeightedUnion()
    edges = []
    for r, j, s, k, d, l, msb in relations:
        for other, gap in ((s, 396+j-k), (d, 623+j-l)):
            union.join(r, other, gap)
            edges.extend(((r, other, gap), (other, r, -gap)))
    for a, b, gap in extra:
        union.join(a, b, gap)
        edges.extend(((a, b, gap), (b, a, -gap)))
    for r in range(132):
        edges.append((r+1, r, -4))
    lo = -graph.shortest(edges, 129)[0]
    hi = graph.shortest(edges, 0)[129]
    components = len({union.find(i)[0] for i in range(133) if i != 129})
    return int(lo), int(hi), components


def main():
    flat, words = original_printer()
    relations = graph.discover(flat)
    assert len(relations) == 42
    old = stagegraph(relations, [])
    assert old == (917, 971, 83), old
    controls = external_stage_edges(words)
    ax = ax_bridge(words)
    with_controls = stagegraph(relations, controls)
    with_ax = stagegraph(relations, [ax])
    together = stagegraph(relations, [ax] + controls)
    print("PRINTER_ONLY", old)
    print("RECORDER_RC17", with_controls)
    print("AX_ONLY", with_ax)
    print("JOINT", together)
    assert with_controls == (917, 971, 80)
    assert with_ax == (940, 971, 82)
    assert together == (940, 971, 79)
    print("STATUS conditional new stage lower bound +23; no selected K04 bits")


if __name__ == "__main__":
    main()
