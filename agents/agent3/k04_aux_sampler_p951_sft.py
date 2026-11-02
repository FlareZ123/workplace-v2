"""SFT: independently retained TRP2 auxiliary readings test p951 MT metadata draw.

Original printer-only state is imported from Agent2's pinned/source-only
p951 fixed-point closure. Match the original node50 control words first.
Test whether the next 13-bit RNG draw follows a *hypothetical*
2000 + randrange(6000) auxiliary sampler, allowing draw rejection.
No selected ACK2, K04/K08 commitments, or routing mask read.

Run: python agents/agent3/k04_aux_sampler_p951_sft.py resources
"""
import hashlib
import importlib.util
import random
import struct
import sys
import zlib
from pathlib import Path

U = 0xffffffff
SCRIPT = (Path(__file__).resolve().parents[1] /
          "agent2/20261102_k04_multicarrier_p951_sft.py")
spec = importlib.util.spec_from_file_location("p951_source", SCRIPT)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


def codes(word, mask):
    assert mask in (U, 0x7fffffff)
    top = ((0, 1) if mask != U else ((word >> 31),))
    return [(bit, source.temper((word & mask) | (bit << 31)) >> 19)
            for bit in top]


def original_node50(root, word, known, offset):
    raw = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source.REC_SHA
    result = {}
    for row in range(88):
        at = 16 + 24 * row
        ts, node, event, latch, seq, val, aux, crc = struct.unpack_from(
            "<IHBBI4sII", raw, at)
        if node != 50 or zlib.crc32(raw[at:at+20]) != crc:
            continue
        value = source.untemper(int.from_bytes(val, "little"))
        hits = [i-offset for i, m in enumerate(known)
                if m.bit_count() >= 31 and not ((word[i] ^ value) & m)]
        if hits:
            assert len(hits) == 1
            result[seq] = (hits[0], aux)
    assert sorted(result) == [7, 12, 13, 24, 25, 41, 45, 70]
    return result


def propagate(word, known, offset, edits):
    before = sum(m.bit_count() for m in known)
    def add(at, value, mask):
        pos = offset + at
        assert ((word[pos] ^ value) & known[pos] & mask) == 0
        added = mask & ~known[pos]
        if added:
            word[pos] = (word[pos] & ~added) | (value & added)
            known[pos] |= added

    for at, bit in edits.items():
        add(at, bit << 31, 0x80000000)
    for step in range(30):
        earlier = sum(m.bit_count() for m in known)
        for t in range(len(word) - 624):
            mask = ((known[t] & 0x80000000) |
                    (known[t+1] & 0x7fffffff))
            pair = ((word[t] & 0x80000000) |
                    (word[t+1] & 0x7fffffff))
            if known[t+397] == U and known[t+624] == U:
                reverse = source.inverse_twist(word[t+397] ^ word[t+624])
                add(t-offset, reverse, 0x80000000)
                add(t+1-offset, reverse, 0x7fffffff)
            if mask == U:
                if known[t+397] == U:
                    add(t+624-offset,
                        word[t+397] ^ source.twist(pair), U)
                if known[t+624] == U:
                    add(t+397-offset,
                        word[t+624] ^ source.twist(pair), U)
        if earlier == sum(m.bit_count() for m in known):
            break
    return sum(m.bit_count() for m in known) - before


def main(root):
    # Python's actual randrange(6000) uses getrandbits(13) rejection.
    for seed in (0, 1, 8131, 20261003, 0xdeadbeef):
        a, b = random.Random(seed), random.Random(seed)
        for _ in range(100):
            actual = a.randrange(6000)
            candidate = b.getrandbits(13)
            while candidate >= 6000:
                candidate = b.getrandbits(13)
            assert candidate == actual
    print("PASS synthetic Python randrange(6000) 13-bit rejection controls")

    word, known, offset = source.source_closure(root)
    node = original_node50(root, word, known, offset)
    edits = {}
    for seq, (pos, aux) in sorted(node.items()):
        wanted = aux - 2000
        next_mask = known[offset+pos+1]
        if next_mask.bit_count() < 31:
            print("SEQ", seq, "next output unknown, no inferred bit")
            continue
        options = codes(word[offset+pos+1], next_mask)
        direct = [b for b, value in options
                  if value == wanted and value < 6000]
        rejected = [b for b, value in options if value >= 6000]
        if direct:
            assert len(direct) == 1
            if next_mask != U:
                edits[pos+1] = direct[0]
            print("SEQ", seq, "accepted +1", options)
        else:
            assert len(rejected) == 1, (seq, aux, options)
            if next_mask != U:
                edits[pos+1] = rejected[0]
            print("SEQ", seq, "rejected +1", options)
        if seq == 41:
            assert options == [(1, 6630)]
            mask2 = known[offset+pos+2]
            options2 = codes(word[offset+pos+2], mask2)
            successful = [b for b, value in options2
                          if value == wanted and value < 6000]
            assert options2 == [(0, 6661), (1, 2823)]
            assert successful == [1] and aux == 4823
            edits[pos+2] = 1
            print("SEQ 41 accepted +2 after rejected +1", options2)

    assert edits == {-809: 0, -774: 1, -768: 1,
                     -682: 0, -676: 1, -566: 1}
    full_before = sum(m == U for m in known)
    partial_before = sum(0 < m < U for m in known)
    learned = propagate(word, known, offset, edits)
    full_after = sum(m == U for m in known)
    partial_after = sum(0 < m < U for m in known)
    print("CONDITIONAL new 1-bit observations:", len(edits))
    print("CONDITIONAL propagation bit increase:", learned,
          "full words", full_before, "to", full_after,
          "partial", partial_before, "to", partial_after)
    assert (learned, full_before, full_after, partial_before, partial_after) == (
        70, 968, 975, 306, 302)
    selected = [known[offset+source.STARTS[129]+k] for k in range(4)]
    print("selected word masks", [f"{x:08X}" for x in selected])
    assert selected == [0, 0, 0, 0]
    print("CAUTION: p951 chronology and AUX producer unverified; K04 unresolved")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else
         Path(__file__).resolve().parents[2] / "resources")
