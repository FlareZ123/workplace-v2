#!/usr/bin/env python3
"""Target-blind K08 ATTEMPT/TAILBIT instruction interlock.

Composes source-selected note operations with transfer metadata. Never reads
acceptance.json, the K08 desk nonce, or any target commitment.
"""
from __future__ import annotations
import hashlib, itertools, json, re
from pathlib import Path

PINS = {
    "crew": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "m10": "ccfc592fe570ca6928a74de813c378443030e841bba169434c0f413721122e48",
    "m11": "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    "m13": "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
    "audit": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "spool": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
}
ROOT = Path(__file__).resolve().parents[2] / "resources" / "evidence"

def load(rel, pin):
    raw=(ROOT/rel).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==pin
    return raw

def words(s): return re.findall(r"[A-Za-z0-9]+", s)

def pack(bits): return sum((b&1)<<i for i,b in enumerate(bits))

def longest(a,b):
    a=[x.lower() for x in a]; b=[x.lower() for x in b]
    best=0; runs=set()
    for i in range(len(a)):
        for j in range(len(b)):
            k=0
            while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]: k+=1
            if k>best:
                best=k; runs={tuple(a[i:i+k])} if k else set()
            elif k and k==best: runs.add(tuple(a[i:i+k]))
    return best,runs

def main():
    crew=load("crew/noticeboard-and-desk-notes.txt",PINS["crew"]).decode()
    mails={
        10:load("mail/10.eml",PINS["m10"]).decode(),
        11:load("mail/11.eml",PINS["m11"]).decode(),
        13:load("mail/13.eml",PINS["m13"]).decode(),
    }
    audit_raw=load("transfers/transfer-audit.jsonl",PINS["audit"])
    spool=load("print/spool-reconstruction.log",PINS["spool"]).decode()

    notes={}; authors={}
    for m in re.finditer(r"^N(\d{2}) / (\w+) \[censored\]\n([^\n]+)$",crew,re.M):
        n=int(m.group(1)); authors[n]=m.group(2)
        line=m.group(3); notes[n]=line.split(": ",1)[1] if ": " in line else line
    assert set(notes)==set(range(1,25))
    nw={n:words(notes[n]) for n in notes}

    # Accepted K05/K06/K07 source mails select Simon/Emily/Gabriel.
    senders={}
    for slot,n in (("K05",10),("K06",11),("K07",13)):
        m=re.search(r"(?m)^From: (\w+) \[censored\]",mails[n]); assert m
        senders[slot]=m.group(1)
    assert senders=={"K05":"Simon","K06":"Emily","K07":"Gabriel"}
    chosen=set(senders.values())
    ids=[n for n in range(1,25) if authors[n] in chosen]
    heads="".join(nw[n][0][0].upper() for n in ids)
    assert ids==[2,5,6,7,10,12,13,14,17,18,20,22,23,24]
    assert heads=="ATTPTTAILBITTE"

    # Among all 20 three-author masks this exact source-selected mask is the only
    # one whose body-head stream contains TAILBIT.
    names=sorted(set(authors.values())); hits=[]
    for subset in itertools.combinations(names,3):
        stream="".join(nw[n][0][0].upper() for n in range(1,25) if authors[n] in subset)
        if "TAILBIT" in stream: hits.append((subset,stream))
    assert hits==[(("Emily","Gabriel","Simon"),"ATTPTTAILBITTE")]
    at=heads.index("TAILBIT"); stem=heads[:at]
    assert stem=="ATTPT"

    # Independent overlap census: N13/N20 is the sole >=5-word maximal overlap.
    ge5=[]
    for a,b in itertools.combinations(range(1,25),2):
        length,runs=longest(nw[a],nw[b])
        if length>=5:
            assert len(runs)==1
            ge5.append((a,b,length,next(iter(runs))))
    assert ge5==[(13,20,5,("the","end","of","the","night"))]
    len_letter=chr(64+ge5[0][2])       # 5 -> E
    partner_letter=chr(64+ge5[0][0])  # N13 -> M
    assert (len_letter,partner_letter)==("E","M")

    # Enumerate every insertion boundary and both E/M orders. Select via literal
    # source schema vocabulary, not an English-word list.
    rows=[json.loads(x) for x in audit_raw.decode().splitlines() if x.strip()]
    fields=set(re.findall(r"\b([A-Z][A-Z0-9_]*)=",spool))
    for row in rows: fields.update(k.upper() for k in row)
    assert "ATTEMPT" in fields
    completions=[]
    for i in range(len(stem)+1):
        for pair in ("EM","ME"):
            token=stem[:i]+pair+stem[i:]
            if token in fields: completions.append((i,pair,token))
    assert completions==[(3,"EM","ATTEMPT")]
    instruction="ATTEMPT TAILBIT"

    # Existing source-local continuation.
    pids=[2,6,11,13,17,18,20,23]
    pheads="".join(nw[n][0][0].upper() for n in pids)
    counts=[len(nw[n]) for n in pids]
    letters="".join(chr(65+c) if c<26 else "?" for c in counts)
    assert pheads=="ATEALBIT" and letters=="NLOWIF?V"
    assert nw[11][0].upper()=="EVEN"
    full_instruction=instruction+" LOW IF EVEN"
    assert full_instruction=="ATTEMPT TAILBIT LOW IF EVEN"

    # MAIL13 independently fixes AX-7782 and the two-attempt shape.
    assert "final custodian handoff is AX-7782" in mails[13]
    assert "Each chunk was retried once." in mails[13]
    assert "There are eight chunks, numbered from zero." in mails[13]
    checkpoints={(r["transfer"],r["seq"],r["attempt"]):bytes.fromhex(r["checkpoint"])
                 for r in rows if r.get("kind")=="CHUNK"}
    transfers=sorted({r["transfer"] for r in rows if r.get("kind")=="CHUNK"})
    controls={}
    selected={}
    for tr in transfers:
        raw=b"".join(checkpoints[(tr,s,1 if s%2==0 else 2)] for s in range(8))
        selected[tr]=raw.hex().upper()
        bits=[b&1 for b in raw]
        controls[tr]=bytes(pack(bits[o:o+8]) for o in (0,8)).hex().upper()
    assert selected["AX-7782"]=="6224CEDCF3B873BA18887BE63DB0C5C9"
    assert controls=={"AX-7778":"694A","AX-7781":"C28A","AX-7782":"50D4","AX-7783":"CF59"}
    out=bytes.fromhex(controls["AX-7782"])
    assert out[0]==ord("P") and out[1]==212

    print({
      "source_pins":"PASS","target_or_nonce_read":False,
      "selected_heads":heads,"three_author_tailbit_hits":len(hits),
      "unique_ge5_pair":"N13/N20","completion_hits":completions,
      "instruction":full_instruction,
      "AX7782_mixed_attempt_bytes":selected["AX-7782"],
      "transfer_tailbit_controls":controls,"selected_output":"P212",
      "complete_author_final_wording_emitted":False,
    })

if __name__=="__main__": main()
