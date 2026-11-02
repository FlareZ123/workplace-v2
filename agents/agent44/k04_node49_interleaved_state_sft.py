"""Agent44 source-only test: 12 node49 recorder controls interleave in p951 MT.

Run: python agents/agent44/k04_node49_interleaved_state_sft.py resources

The original selected printer ACK, K04 mask/acceptance and all K08 inputs are
excluded. The proposed printer MT index vector is conditional and retrospectively
fitted, not authenticated firmware. CRC-bad controls remain labelled as such.
"""
import hashlib
import importlib.util
import struct
import sys
import zlib
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
U = 0xFFFFFFFF
MSB = 0x80000000

def load_source_module():
    path = Path(__file__).resolve().parents[1] / "agent2/20261102_k04_multicarrier_p951_sft.py"
    spec = importlib.util.spec_from_file_location("agent2_p951", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def controls(root, module):
    raw = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == REC_SHA
    assert raw[:8] == b"TRP2DUMP" and len(raw) == 16 + 24 * 88
    data, failures = {}, []
    for row in range(88):
        pos = 16 + 24 * row
        ts, node, event, latch, seq, value, aux, crc = struct.unpack_from(
            "<IHBBI4sII", raw, pos)
        calc = zlib.crc32(raw[pos:pos+20])
        if node == 49 and event == 82:
            assert seq not in data
            data[seq] = (module.untemper(int.from_bytes(value, "little")),
                         crc == calc, crc ^ calc, ts, latch)
            if crc != calc:
                failures.append((row, seq, crc ^ calc))
    assert len(data) == 16
    assert failures == [(14,900,0x100), (41,901,0x100),
                        (72,903,0x100), (77,902,0x100)]
    return data

def placement():
    return [(prefix + lane, -324 + lane * 3 + phase)
            for lane in range(4)
            for prefix, phase in ((200,0), (900,1), (990,2))]

def propagate(module, word, known, offset):
    def add(at, value, mask):
        conflict = (word[at] ^ value) & known[at] & mask
        assert not conflict, (at-offset, hex(conflict))
        new = mask & ~known[at]
        if new:
            word[at] = (word[at] & ~new) | (value & new)
            known[at] |= mask
    for step in range(35):
        before = sum(m.bit_count() for m in known)
        for t in range(len(word)-624):
            mask = (known[t] & MSB) | (known[t+1] & 0x7fffffff)
            value = (word[t] & MSB) | (word[t+1] & 0x7fffffff)
            if known[t+397] == known[t+624] == U:
                inv = module.inverse_twist(word[t+397] ^ word[t+624])
                add(t, inv, MSB)
                add(t+1, inv, 0x7fffffff)
            if mask == U:
                if known[t+397] == U:
                    add(t+624, word[t+397] ^ module.twist(value), U)
                if known[t+624] == U:
                    add(t+397, word[t+624] ^ module.twist(value), U)
        if before == sum(m.bit_count() for m in known):
            break
    return word, known

def integrate(module, initial, data, omit=None):
    source_words, source_masks, offset = initial
    word, known = source_words.copy(), source_masks.copy()
    before = sum(m.bit_count() for m in known)
    directly_added = 0
    for seq, position in placement():
        if seq == omit:
            continue
        index = offset + position
        observed = data[seq][0]
        assert ((word[index] ^ observed) & known[index]) == 0
        directly_added += (U & ~known[index]).bit_count()
        word[index], known[index] = observed, U
    propagate(module, word, known, offset)
    total_gain = sum(m.bit_count() for m in known) - before
    return word, known, offset, directly_added, total_gain

def main(root):
    module = load_source_module()
    assert hashlib.sha256((root / "evidence/print/spool-reconstruction.log").read_bytes()).hexdigest() == SPOOL_SHA
    for v in (0, 1, 0x12345678, U):
        assert module.untemper(module.temper(v)) == v
        assert module.inverse_twist(module.twist(v)) == v
    initial = module.source_closure(root)
    data = controls(root, module)
    for seq, index in placement():
        m = initial[1][initial[2]+index]
        assert not ((initial[0][initial[2]+index] ^ data[seq][0]) & m)
        print("POSITION", seq, index, "printer_bits", m.bit_count(),
              "crc_valid", data[seq][1], "crc_delta", hex(data[seq][2]))
    words, masks, offset, direct, total = integrate(module, initial, data)
    print("new independent recorder-state bits", direct,
          "total conditional fixed-bit gain", total,
          "fully fixed words", sum(mask == U for mask in masks))
    assert (direct, total, sum(m == U for m in masks)) == (160, 320, 980)
    assert [masks[offset+951+j] for j in range(4)] == [0,0,0,0]
    for seq, pos in placement():
        w,k,o,_,_ = integrate(module, initial, data, omit=seq)
        m = k[o+pos]
        assert not ((w[o+pos] ^ data[seq][0]) & m)
        print("HOLDOUt", seq, "independently_fixed_bits", m.bit_count(),
              "whole_original_predicted", m == U)
    print("K04 selected coupon: zero determined bits; conditional model only")

if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else
         Path(__file__).resolve().parents[2] / "resources")
