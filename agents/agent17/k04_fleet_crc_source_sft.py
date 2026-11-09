"""Source-selected ESC-N coupon using a shared, reversible CRC printer issuer."""
import hashlib
import itertools
import os
from pathlib import Path
import re
import zlib

E = Path(os.environ.get("H17_EVIDENCE_ROOT", Path(__file__).resolve().parents[2]/"resources/evidence"))
fleet = (E/"h17-supplemental-office-files/print-fleet-retirement-note.txt").read_bytes()
spool = (E/"print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(fleet).hexdigest() == "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf"
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
K04_TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
SOUTH = re.findall(rb"^2026-10-03T18:24:00Z JOB=PS-261003-0448 ATTEMPT=1 STATE=ACK CLASS=RECOVER PAYLOAD=([0-9A-F]{32}) DEST=desk$",spool,re.M)
assert len(SOUTH)==1
SOUTH=bytes.fromhex(SOUTH[0].decode())
NORTH_T = re.findall(rb"^L-29/N\s+\d\d\s+(ST-\d{3})\s+",fleet,re.M)
SOUTH_T = re.findall(rb"^L-29/S\s+\d\d\s+(ST-\d{3})\s+",fleet,re.M)
assert len(NORTH_T)==len(SOUTH_T)==5
N = ("ESC-N","PS-261003-0417","FA-17")
S = ("ESC-S","PS-261003-0448","LV-42")
U=0xffffffff


def write_input(tickets, identity, fmt, delim, layout):
    if fmt=="full":parts=tickets
    elif fmt=="3digit":parts=[v[3:] for v in tickets]
    elif fmt=="integer":parts=[str(int(v[3:])).encode() for v in tickets]
    elif fmt=="onebyte":parts=[bytes([int(v[3:])]) for v in tickets]
    elif fmt=="two_be":parts=[int(v[3:]).to_bytes(2,"big") for v in tickets]
    else:parts=[int(v[3:]).to_bytes(2,"little") for v in tickets]
    result=delim.join(parts)
    route,job,account=[v.encode() for v in identity]
    if layout=="plain":return result
    if layout=="lane":return route+b"|"+result
    if layout=="job":return job+b"|"+result
    if layout=="account":return account+b"|"+result
    if layout=="postlane":return result+b"|"+route
    if layout=="postjob":return result+b"|"+job
    return route+b"|"+job+b"|"+result


def message_lane(msg,scheme,j):
    if scheme=="suffixdec":return msg+str(j).encode()
    if scheme=="suffixone":return msg+bytes([j])
    if scheme=="prefixdec":return str(j).encode()+msg
    if scheme=="prefixone":return bytes([j])+msg
    if scheme=="separateST":return msg+b"|ST"+str(j+1).encode()
    if scheme=="separateL":return msg+b"|L"+bytes([65+j])
    if scheme=="fourslices":return msg[j:]+msg[:j]
    return msg+msg[:j+1]


def byte_view(buf,view):
    parts=[buf[k:k+4] for k in range(0,16,4)]
    if view&1:parts=parts[::-1]
    if view&2:parts=[x[::-1] for x in parts]
    return b"".join(parts)


def crc32c(msg,seed=0):
    state=seed^U
    for byte in msg:
        state^=byte
        for _ in range(8):state=(state>>1)^(0x82F63B78 if state&1 else 0)
    return state^U


def invert_crc(out,msg,poly):
    state=out^U
    for byte in reversed(msg):
        for j in range(7,-1,-1):
            b=(state>>31)&1
            state^=poly if b else 0
            state=((state<<1)&U)|(b^((byte>>j)&1))
    return state^U


def packet(msg,scheme,endian,seed,poly):
    f=zlib.crc32 if poly==0xEDB88320 else crc32c
    return b"".join(f(message_lane(msg,scheme,j),seed).to_bytes(4,endian) for j in range(4))


def parameters():
    return itertools.product(("full","3digit","integer","onebyte","two_be","two_le"),
        (b"",b"|",b",",b"\n",b":"),
        ("plain","lane","job","account","postlane","postjob","all"),
        ("suffixdec","suffixone","prefixdec","prefixone","separateST","separateL","fourslices","repeat"),
        ("big","little"),range(4))


def original():
    count=0;pad_out=set();fullfit={0xEDB88320:0,0x82F63B78:0}
    for fmt,sep,layout,scheme,endian,view in parameters():
        n=write_input(NORTH_T,N,fmt,sep,layout)
        s=write_input(SOUTH_T,S,fmt,sep,layout)
        count+=1
        if len(n)==len(s):
            nmask=byte_view(packet(n,scheme,endian,0,0xEDB88320),view)
            smask=byte_view(packet(s,scheme,endian,0,0xEDB88320),view)
            predicted=bytes(a^b^c for a,b,c in zip(SOUTH,nmask,smask))
            component=bytes(a^b for a,b in zip(predicted,MASK))
            pad_out.add(component)
            assert hashlib.sha256(component).hexdigest()!=K04_TARGET
        words=byte_view(SOUTH,view)
        for poly in fullfit:
            seeds=[invert_crc(int.from_bytes(words[j*4:j*4+4],endian),message_lane(s,scheme,j),poly) for j in range(4)]
            if len(set(seeds))==1:
                fullfit[poly]+=1
                proposed=byte_view(packet(n,scheme,endian,seeds[0],poly),view)
                component=bytes(a^b for a,b in zip(proposed,MASK))
                assert hashlib.sha256(component).hexdigest()!=K04_TARGET
    assert count==13440 and len(pad_out)==1060 and fullfit=={0xEDB88320:0,0x82F63B78:0}
    print("ORIGINAL 13440 source-paired models: shared unknown CRC32/XOR pad 11200 assignments, 1060 distinct K04, zero hits")
    print("ORIGINAL global CRC32 + CRC32C unknown 32-bit init: 13440 four-word south controls each; zero entire-packet fits")


def planted():
    for poly in (0xEDB88320,0x82F63B78):
        seed=0xA37D2C41
        n=write_input(NORTH_T,N,"integer",b"|","lane")
        s=write_input(SOUTH_T,S,"integer",b"|","lane")
        emitted_s=byte_view(packet(s,"prefixone","little",seed,poly),3)
        observed=byte_view(emitted_s,3)
        seeds=[invert_crc(int.from_bytes(observed[4*j:4*j+4],"little"),message_lane(s,"prefixone",j),poly) for j in range(4)]
        assert seeds==[seed]*4
        recovered=byte_view(packet(n,"prefixone","little",seeds[0],poly),3)
        assert recovered==byte_view(packet(n,"prefixone","little",seed,poly),3)
    pad=bytes.fromhex("41372DD3A926DC218738DEB457931DED")
    n=write_input(NORTH_T,N,"full",b"|","lane")
    s=write_input(SOUTH_T,S,"full",b"|","lane")
    issued_s=bytes(a^b for a,b in zip(pad,packet(s,"suffixone","little",0,0xEDB88320)))
    planted_n=bytes(a^b for a,b in zip(pad,packet(n,"suffixone","little",0,0xEDB88320)))
    recovered=bytes(a^b^c for a,b,c in zip(issued_s,packet(s,"suffixone","little",0,0xEDB88320),packet(n,"suffixone","little",0,0xEDB88320)))
    assert recovered==planted_n
    print("POSITIVE real CRC32/CRC32C global seeded producers and common unknown pad complete north recovery PASS")


if __name__=="__main__":
    planted()
    original()
