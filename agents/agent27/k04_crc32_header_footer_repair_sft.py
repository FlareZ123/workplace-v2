"""Agent27 source-pinned H17 K04 special ACK CRC32 header/footer repair SFT.
Python 3 standard library. Read-only official source and commitments.
"""
import hashlib,re,sys,zlib
from pathlib import Path
R=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources"
raw=(R/"evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
pat=rb"2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=([0-9A-F]{32}) DEST=bench"
row=re.search(pat,raw)
assert row is not None
copied=bytes.fromhex(row[1].decode())
assert copied.hex().upper()=="A9A9DC5731A5E2AE879C47215C2559D5"
mask=bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
target=bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
assert hashlib.sha256(bytes(x^y for x,y in zip(copied,mask))).digest()!=target

def crc_ieee(raw):return zlib.crc32(raw)
def adler(raw):return zlib.adler32(raw)
def crc_inverted(raw):return zlib.crc32(raw)^0xffffffff
def crc_init_ff(raw):return zlib.crc32(raw,0xffffffff)
def crc_init_ff_inv(raw):return zlib.crc32(raw,0xffffffff)^0xffffffff
formulas={"CRC32_IEEE":crc_ieee,"Adler32":adler,"CRC32_inverted":crc_inverted,
          "CRC32_initFFFFFFFF":crc_init_ff,"CRC32_initFFFFFFFF_inverted":crc_init_ff_inv}
planted_raw=bytes.fromhex("F00D")+copied[2:12]
planted_coupon=planted_raw+zlib.crc32(planted_raw).to_bytes(4,"big")
planted_target=hashlib.sha256(bytes(x^y for x,y in zip(planted_coupon,mask))).digest()
checks=0;original=[];positive=0
for header in range(65536):
    data=header.to_bytes(2,"big")+copied[2:12]
    for name,fn in formulas.items():
        value=fn(data)
        for endian in ("little","big"):
            coupon=data+value.to_bytes(4,endian)
            component=bytes(x^y for x,y in zip(coupon,mask))
            digest=hashlib.sha256(component).digest()
            checks+=1
            if digest==target:original.append((name,endian,header,coupon.hex()))
            if digest==planted_target:
                assert (name,endian,header)==("CRC32_IEEE","big",0xF00D)
                positive+=1
assert checks==655360 and not original and positive==1
print("original_spool_and_selected_identity=PASS")
print("K04_crc32_header_footer_assignments",checks,"original_hits",len(original))
print("planted_complete_coupon",planted_coupon.hex().upper(),"positive_count",positive)
