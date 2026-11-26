#!/usr/bin/env python3
"""Bounded bit-stuffed HDLC/T.30 FCS-16 screen for retained H-17 spool payloads."""
import argparse, hashlib, json, re
from pathlib import Path

PINS={
 "evidence/print/spool-reconstruction.log":"7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
 "evidence/recovery-routing.json":"f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
 "evidence/crew/noticeboard-and-desk-notes.txt":"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
 "acceptance.json":"681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
FLAG="01111110"

def crc16_x25(data):
    crc=0xffff
    for b in data:
        crc^=b
        for _ in range(8): crc=(crc>>1)^0x8408 if crc&1 else crc>>1
    return crc^0xffff

def bitstream(data,order):
    return "".join(f"{b:08b}" if order=="msb" else f"{b:08b}"[::-1] for b in data)

def destuff(bits):
    out=[]; run=0; i=0
    while i<len(bits):
        bit=bits[i]; out.append(bit)
        if bit=="1":
            run+=1
            if run==5:
                i+=1
                if i>=len(bits) or bits[i]!="0": return None
                run=0
        else: run=0
        i+=1
    return "".join(out)

def to_bytes(bits,order):
    bits=bits[:len(bits)//8*8]; out=bytearray()
    for i in range(0,len(bits),8):
        chunk=bits[i:i+8]
        if order=="lsb": chunk=chunk[::-1]
        out.append(int(chunk,2))
    return bytes(out)

def decode(data):
    for order in ("msb","lsb"):
        raw=bitstream(data,order)
        for invert in (False,True):
            bits=raw if not invert else "".join("1" if x=="0" else "0" for x in raw)
            for offset in range(8):
                unstuffed=destuff(bits[offset:])
                if unstuffed is None: continue
                for pad in range(8):
                    body=unstuffed[:-pad] if pad else unstuffed
                    frame=to_bytes(body,order)
                    if len(frame)>=4 and crc16_x25(frame[:-2])==int.from_bytes(frame[-2:],"little"):
                        yield order,invert,offset,pad,frame

def stuff(bits):
    out=[]; run=0
    for bit in bits:
        out.append(bit)
        if bit=="1":
            run+=1
            if run==5: out.append("0"); run=0
        else: run=0
    return "".join(out)

def positive_control():
    for first in range(0xf0,0x100):
        data=bytes([first])+bytes(12)
        frame=data+crc16_x25(data).to_bytes(2,"little")
        stuffed=stuff(bitstream(frame,"msb"))
        pad=128-len(stuffed)
        if 0<=pad<=7 and len(stuffed)<128:
            encoded=int(stuffed+"0"*pad,2).to_bytes(16,"big")
            if any(candidate==frame for *_,candidate in decode(encoded)):
                return len(stuffed)-120,pad
    raise AssertionError("synthetic positive control failed")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]/"resources")
    root=ap.parse_args().root.resolve()
    for rel,expected in PINS.items():
        actual=hashlib.sha256((root/rel).read_bytes()).hexdigest()
        if actual!=expected: raise SystemExit("source pin mismatch: "+rel)
    route=json.loads((root/"evidence/recovery-routing.json").read_text())
    acceptance=json.loads((root/"acceptance.json").read_text())
    mask=bytes.fromhex(route["K04"]["masked_component"])
    target=bytes.fromhex(acceptance["slot_sha256"]["K04"])
    rows=[]
    for line in (root/"evidence/print/spool-reconstruction.log").read_text().splitlines():
        if line.startswith("2026-"):
            f=dict(x.split("=",1) for x in line.split()[1:])
            rows.append((f,bytes.fromhex(f["PAYLOAD"])))
    if len(rows)!=133: raise SystemExit("unexpected spool row count")
    selected=[(f,b) for f,b in rows if f["JOB"]=="PS-261003-0417" and f["ATTEMPT"]=="2"
              and f["STATE"]=="ACK" and f["CLASS"]=="RECOVER"]
    if len(selected)!=1: raise SystemExit("selected ACK row is not unique")
    selected_f,selected_b=selected[0]
    flag_counts={"raw":0,"mask_xor":0}; selected_flags={}
    valid=0; selected_matches=0
    for masked in (False,True):
        label="mask_xor" if masked else "raw"
        for f,b in rows:
            view=bytes(x^y for x,y in zip(b,mask)) if masked else b
            row_flags=sum(len(re.findall(f"(?={FLAG})",bitstream(view,o))) for o in ("msb","lsb"))
            flag_counts[label]+=row_flags
            if f is selected_f: selected_flags[label]=row_flags
            for order,invert,offset,pad,frame in decode(view):
                valid+=1
                if f is selected_f:
                    candidate=bytes(x^y for x,y in zip(frame,mask))
                    if hashlib.sha256(candidate).digest()==target: selected_matches+=1
    stuffed,pad=positive_control()
    print(json.dumps({
      "rows":len(rows),"selected_job":"PS-261003-0417 attempt=2 ACK RECOVER",
      "flag_occurrences_both_bit_orders":flag_counts,
      "selected_row_flag_occurrences":selected_flags,
      "decode_configurations":len(rows)*2*2*2*8*8,
      "valid_fcs_decodes":valid,"selected_K04_commitment_matches":selected_matches,
      "synthetic_positive_control":"PASS","synthetic_stuffed_bits":stuffed,"synthetic_pad_bits":pad,
      "scope":"single retained 16-byte payloads; raw and route-mask-XOR; both bit orders/polarities; offsets 0-7; <=7 pad bits; CRC-16/X-25"
    },indent=2))
if __name__=="__main__": main()
