"""H17 K04: source-only glibc random() additive-feedback producer falsifier.

Tests TYPE_1..4 with 8- or 16-bit contiguous slices per generator call
and bounded unobserved calls between packets. No selected K04 payload or
acceptance digest is used. On GNU/Linux the self-test calls actual libc.
"""
import ctypes
import hashlib
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", str(Path(__file__).resolve().parents[2] / "resources")))
SOURCE = ROOT / "evidence/print/spool-reconstruction.log"
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SHA
rows = []
for line in SOURCE.read_text().splitlines():
    m = re.search(r"JOB=PS-261003-(\d+) ATTEMPT=1 STATE=ACK .*?PAYLOAD=([A-F0-9]{32}) ", line)
    if m and 300 <= int(m.group(1)) < 428:
        rows.append((int(m.group(1)), bytes.fromhex(m.group(2))))
assert len(rows) == 128 and [j for j,_ in rows] == list(range(300,428))

# For glibc's TYPE_n with lag d and separation s, its uint31 outputs have
# o[t] = (o[t-d] + o[t-s] + c) mod 2^31, c in {0,1}.
# Any contiguous 8/16-bit output slice retains this necessary relation,
# reducing modulo 2^8 or 2^16 with a new carry 0/1.
def sieve(packets, degree, sep, max_gap, bits, max_nodes=3000000, stop_after=1):
    plen = len(packets[0])
    assert all(len(p)==plen for p in packets)
    mod = 1 << bits
    seen = {}
    depth_nodes = [0]*len(packets)
    solutions = []
    capped = False
    total = 0
    def dfs(index, start, gaps):
        nonlocal capped, total
        if capped: return
        depth_nodes[index] += 1
        total += 1
        if total > max_nodes:
            capped = True
            return
        added = []
        good = True
        for j, val in enumerate(packets[index]):
            t = start + j
            a = seen.get(t-degree)
            b = seen.get(t-sep)
            if a is not None and b is not None and (val-a-b)%mod not in (0,1):
                good = False
                break
            seen[t] = val
            added.append(t)
        if good:
            if index == len(packets)-1:
                solutions.append(tuple(gaps))
            else:
                for gap in range(max_gap+1):
                    dfs(index+1,start+plen+gap,gaps+[gap])
                    if capped or len(solutions)>=stop_after: break
        for t in added:
            del seen[t]
    dfs(0,0,[])
    return solutions, depth_nodes, capped

def views(payload, unit):
    if unit == 1:
        return {
            "raw":list(payload),
            "reverse":list(payload[::-1]),
            "reverse_word_order":list(b"".join(payload[i:i+4] for i in (12,8,4,0))),
            "swap_word_bytes":list(b"".join(payload[i:i+4][::-1] for i in (0,4,8,12))),
        }
    output={}
    for endian in ("little","big"):
        words=[int.from_bytes(payload[i:i+unit],endian) for i in range(0,16,unit)]
        output[endian] = words
        output[endian+"_reverse"] = words[::-1]
    return output

# Genuine positive: GNU libc srandom/initstate produces a deterministic,
# nonlinear-seeded stream and the full source-known packet/gap pattern survives.
lib = ctypes.CDLL(None)
lib.initstate.argtypes=[ctypes.c_uint,ctypes.c_void_p,ctypes.c_size_t]
lib.initstate.restype=ctypes.c_void_p
lib.random.restype=ctypes.c_long
live_buffers=[]
gaps=(2,0,3,1,4,2,1)
for degree, sep, state_bytes in ((7,3,32),(15,1,64),(31,3,128),(63,1,256)):
    state=ctypes.create_string_buffer(state_bytes)
    live_buffers.append(state)
    assert lib.initstate(42,state,state_bytes)
    outputs=[lib.random() for _ in range(1000)]
    assert all((outputs[i]-outputs[i-degree]-outputs[i-sep])%(1<<31) in (0,1)
               for i in range(degree,1000))
    for bits in (8,16):
        seq=[o % (1<<bits) for o in outputs]
        assert all((seq[i]-seq[i-degree]-seq[i-sep])%(1<<bits) in (0,1)
                   for i in range(degree,1000))
        width=16//(bits//8)
        samples=[]
        start=0
        for index in range(8):
            samples.append(seq[start:start+width])
            if index<7:start+=width+gaps[index]
        matches,counts,capped=sieve(samples,degree,sep,5,bits,
                                     stop_after=1000000)
        assert not capped and gaps in matches, (degree,bits,counts)
        print("REAL_GLIBC_POSITIVE PASS",degree,sep,bits,"nodes",sum(counts))

outcomes=[]
for unit in (1,2,4):
    for orientation in views(rows[0][1],unit):
        samples=[views(packet,unit)[orientation] for _,packet in rows[:8]]
        if unit==4:
            # The output of glibc random() has just 31 bits.
            too_large=sum(v >= (1<<31) for packet in samples for v in packet)
            assert too_large>0
            print("DIRECT_32BIT_PACKING_EXCLUDED",orientation,too_large,"/32 values > uint31")
            continue
        for degree,sep in ((7,3),(15,1),(31,3),(63,1)):
            # Larger 63-word table has fewer observations per packet.
            # With >=7 missing outputs it admits an uninformative,
            # constraint-free alignment among the first eight packets.
            max_gap = 16 if unit==1 else (6 if degree==63 else 8)
            matches,counts,capped=sieve(samples,degree,sep,max_gap,unit*8)
            assert not capped, (unit,orientation,degree,counts)
            assert not matches, (unit,orientation,degree,matches)
            outcomes.append((unit,orientation,degree,sep,max_gap,sum(counts)))
            print("ORIGINAL_SOURCE_NEGATIVE",unit,orientation,degree,sep,
                  "max_gap",max_gap,"nodes",sum(counts))
assert len(outcomes)==32
print("COMPLETE_FAMILY_EXCLUSIONS",len(outcomes),"ORIGINAL_HASH",SHA)
