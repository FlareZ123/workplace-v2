#!/usr/bin/env python3
"""Source-pinned factorized audit of the K08 LOW BIT downstream chain.

Exact finite enumeration; not a calibrated p-value. The 943,718,400-row
Cartesian product is counted by conditioning on one global operator and
factoring independent component-order, transfer-mask, and bookmark axes.
"""
import argparse, hashlib, hmac, itertools, json, math, re, struct, zlib
from datetime import datetime
from pathlib import Path

PINS = {
 "resources/acceptance.json":"681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
 "resources/evidence/recovery-routing.json":"f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
 "resources/evidence/telemetry/freeze-export.jsonl":"3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
 "resources/evidence/transfers/transfer-audit.jsonl":"32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
 "resources/evidence/recorder/trip-recorder.raw":"5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
 "resources/evidence/crew/noticeboard-and-desk-notes.txt":"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
 "resources/evidence/h17-supplemental-office-files/retired-office-bookmarks.html":"b9261ac17524e66bb5a6e3f3ce4996df65737aa34564b6d29a87ebab681a6096",
 "resources/evidence/mail/03.eml":"3cf886c12e094cb0362999c5a4d93f913c848a64471f833fbddbfdc2d57ff889",
 "resources/evidence/mail/06.eml":"6049994562a82e46afd3f0231e136a1e6911cc3040d848e32eaa5771a6f8c2f3",
 "resources/evidence/mail/09.eml":"1bda8bbf1e7b661a04fd58c36c38f2b66d2e2410265c311cc09c8e2bf810f08c",
 "resources/evidence/mail/13.eml":"80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
}
BASE={"K01":12,"K02":11,"K05":10,"K06":10,"K07":11}
SLOTS=("K01","K02","K03","K05","K06","K07")
ORDER=("K01","K06","K02")
TOKEN=re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?")

def sha(b): return hashlib.sha256(b).hexdigest()
def low(s,weight="LSB"):
    bits=[ord(c)&1 for c in s]
    return sum(v<<i for i,v in enumerate(bits)) if weight=="LSB" else sum(v<<(len(bits)-1-i) for i,v in enumerate(bits))
def pack(raw,plane,orient):
    bits=[(b>>plane)&1 for b in raw]
    return bytes(sum(v<<(j if orient=="LSB" else 7-j) for j,v in enumerate(bits[i:i+8]))
                 for i in range(0,len(bits),8))
def source_sel(raw,op):
    p=pack(raw,op["plane"],op["pack"])
    if op["byte_order"]=="reverse": p=p[::-1]
    h=p.hex().upper()
    if op["hex_order"]=="reverse": h=h[::-1]
    return low(h,op["char_weight"]),h,p.hex().upper()
def note_map(text,strip=True):
    out={}
    for n,a,b in re.findall(r"(?ms)^N(\d{2}) / ([^\n]+)\n(.+?)(?=\n\nN\d{2} /|\Z)",text):
        body=b.strip()
        if strip and ":" in body: body=body.split(":",1)[1].strip()
        w=TOKEN.findall(body)
        out[int(n)]={"author":a.split()[0],"body":body,"words":w,"head":w[0][0].upper(),"count":len(w)}
    assert set(out)==set(range(1,25))
    return out
def decode(mask,base,order):
    letters=[]
    for start in range(0,20,5):
        v=sum(((mask>>(start+j))&1)<<(j if order=="LSB" else 4-j) for j in range(5))
        letters.append(chr(65+v) if base==0 and v<26 else chr(64+v) if base==1 and 1<=v<=26 else "?")
    tail=sum(((mask>>(20+j))&1)<<(j if order=="LSB" else 3-j) for j in range(4))
    return "".join(letters)+str(tail)
def upstream(notes):
    crews=[]; bridges=[]
    for base,order in itertools.product((0,1),("LSB","MSB")):
        variant=f"A{base}_{order}"
        for comb in itertools.combinations(range(24),8):
            ids=[i+1 for i in comb]
            if decode(sum(1<<i for i in comb),base,order)!="CREW4": continue
            crews.append({"variant":variant,"subset":ids})
            for direction in (1,-1):
                for pos,old in enumerate(ids):
                    shifted=ids.copy(); shifted[pos]=old+direction
                    if shifted!=sorted(shifted) or len(set(shifted))!=8 or any(n not in notes for n in shifted): continue
                    heads="".join(notes[n]["head"] for n in shifted)
                    counts="".join(chr(65+notes[n]["count"]) if notes[n]["count"]<26 else "?" for n in shifted)
                    for hp,cs,ts in itertools.product(range(8),range(6),range(6)):
                        splice=heads[hp]+counts[cs:cs+3]+heads[ts:ts+3]
                        if heads=="ATEALBIT" and splice=="ALOWBIT":
                            bridges.append({"variant":variant,"subset":ids,"direction":direction,
                              "edit_from":old,"edit_to":old+direction,"selected_ids":shifted,
                              "heads":heads,"count_letters":counts,"splice_positions":[hp,cs,ts],"splice":splice})
    edits=[]
    for c in crews:
        for d in (1,-1):
            count=0
            for pos,old in enumerate(c["subset"]):
                x=c["subset"].copy(); x[pos]=old+d
                count+=int(x==sorted(x) and len(set(x))==8 and all(n in notes for n in x))
            edits.append({"variant":c["variant"],"subset":c["subset"],"direction":d,"valid_edits":count})
    return crews,bridges,edits
def k02_raw(root,route):
    rows=[json.loads(x) for x in (root/"resources/evidence/telemetry/freeze-export.jsonl").read_text().splitlines() if x.strip()]
    a=datetime.fromisoformat(route["K02"]["start_utc"]); z=datetime.fromisoformat(route["K02"]["end_utc_exclusive"])
    chosen={}
    for r in rows:
        if (r.get("tag"),r.get("field"),r.get("quality"),r.get("state"))!=("LT-204","DIAG_WORD","GOOD","HOLD"): continue
        t=datetime.fromisoformat(r["ts"]); i=int(r["seq"])
        if a<=t<z and i in range(8) and (i not in chosen or int(r["revision"])>int(chosen[i]["revision"])):
            chosen[i]=r
    assert set(chosen)==set(range(8))
    return b"".join(int(chosen[i]["value"]).to_bytes(2,"big") for i in range(8))
def transfers(root):
    rows=[json.loads(x) for x in (root/"resources/evidence/transfers/transfer-audit.jsonl").read_text().splitlines() if x.strip()]
    ids=sorted({r["transfer"] for r in rows if "transfer" in r}); out={}
    for t in ids:
        by={}
        for r in rows:
            if r.get("transfer")==t and r.get("kind")=="CHUNK":
                by.setdefault(int(r["seq"]),{})[int(r["attempt"])]=bytes.fromhex(r["checkpoint"])
        assert set(by)==set(range(8)) and all(set(x)=={1,2} for x in by.values())
        out[t]={m:b"".join(by[i][2 if (m>>i)&1 else 1] for i in range(8)) for m in range(256)}
    return ids,out
def k05_masks(root,route):
    b=(root/"resources/evidence/recorder/trip-recorder.raw").read_bytes()
    assert b[:8]==b"TRP2DUMP"
    ver,size,count=struct.unpack("<HHI",b[8:16]); assert (ver,size,len(b))==(2,24,16+24*count)
    start=int(datetime.fromisoformat(route["K05"]["start_utc"]).timestamp())
    end=int(datetime.fromisoformat(route["K05"]["end_utc_exclusive"]).timestamp())
    by={}
    for i in range(count):
        r=b[16+24*i:16+24*(i+1)]
        ts,node,event,latch,seq=struct.unpack("<I H B B I",r[:12])
        crc=struct.unpack("<I",r[20:24])[0]
        if zlib.crc32(r[:20])&0xffffffff!=crc or not start<=ts<end or node!=49 or event!=82 or latch not in range(4): continue
        by.setdefault(latch,[]).append((seq,r[12:16]))
    assert set(by)==set(range(4)) and all(len(v)==2 for v in by.values())
    for v in by.values(): v.sort()
    return {m:b"".join(by[i][1 if (m>>i)&1 else 0][1] for i in range(4)) for m in range(16)}
def group_values(k01,op):
    return {g:pack(k01[i*4:(i+1)*4],op["plane"],op["pack"])[0] for i,g in enumerate("ABCD")}
def component(order,values,op):
    start=0 if op["half"]=="upper" else 8
    return "".join(chr(pack(values[k][start:start+8],op["plane"],op["pack"])[0]) for k in order)
def id_views(t,op):
    prefix,suffix=t.split("-",1)
    s=suffix if op["id_direction"]=="forward" else suffix[::-1]
    return {"full":low(t,op["char_weight"]),"compact":low(t.replace("-",""),op["char_weight"]),
      "prefix":low(prefix,op["char_weight"]),"suffix":low(s,op["char_weight"]),"suffix_text":s}
def transfer_sel(raw,op):
    p=pack(raw,op["plane"],op["pack"])
    if op["byte_order"]=="reverse": p=p[::-1]
    h=p.hex().upper()
    if op["hex_order"]=="reverse": h=h[::-1]
    return low(h,op["char_weight"]),h
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]); ap.add_argument("--out",type=Path); a=ap.parse_args()
    root=a.root.resolve()
    for p,digest in PINS.items(): assert sha((root/p).read_bytes())==digest,p
    c=json.loads((root/"candidate.json").read_text()); accept=json.loads((root/"resources/acceptance.json").read_text())
    for k in ("K01","K02","K03","K05","K06","K07"):
        raw=bytes.fromhex(c[k]); assert len(raw)==16 and sha(raw)==accept["slot_sha256"][k]
    route=json.loads((root/"resources/evidence/recovery-routing.json").read_text())
    notes_text=(root/"resources/evidence/crew/noticeboard-and-desk-notes.txt").read_text()
    notes=note_map(notes_text,True); nonce=bytes.fromhex(route["K08"]["desk_nonce"])
    hmap={}
    for n,v in notes.items():
        norm=" ".join(re.sub(r"[^a-z0-9\s]"," ",v["body"].lower()).split())
        d=hmac.new(nonce,norm.encode(),hashlib.sha256).digest()[:16]
        hmap[n]=low(pack(d,0,"LSB").hex().upper())
    path=[]; seen=set(); node=19
    while node not in seen: seen.add(node); path.append(node); node=hmap[node]
    heads="".join(notes[n]["head"] for n in path)
    assert path==[19,13,9,12,11] and heads=="SANTE" and low(heads)==19
    assert [notes[20]["words"][i-1].lower() for i in (12,10,11)]==["the","end","of"]
    assert low("WANTED")==19 and low("WORDS")==19 and hmap[12]==11
    src=re.findall(r"[A-Za-z0-9]+",route["K08"]["source"])
    source_ids=[low(x.lower()) for x in src if 1<=low(x.lower())<=24]
    count_letters="".join(chr(65+notes[n]["count"]) for n in source_ids)
    assert source_ids==[23,1,14,13,1] and count_letters=="VLOWL" and low(count_letters)==12

    crews,bridges,edit_counts=upstream(notes)
    assert len(crews)==2 and len(bridges)==2
    sigs={(tuple(x["selected_ids"]),x["heads"],x["splice"],(1,6,2)) for x in bridges}
    assert len(sigs)==1
    mail03=" ".join((root/"resources/evidence/mail/03.eml").read_text().split())
    mail06=" ".join((root/"resources/evidence/mail/06.eml").read_text().split())
    mail09=" ".join((root/"resources/evidence/mail/09.eml").read_text().split())
    mail13=" ".join((root/"resources/evidence/mail/13.eml").read_text().split())
    assert all(x in mail03 for x in ("group A","group C","four boxes follow","their letters"))
    assert all(x in mail06 for x in ("group B","group D","5E67","4303C91A"))
    groups=dict(re.findall(r"WN-14 / group ([A-D]) / ([0-9A-F]{8})",mail03+" "+mail06))
    assert groups==dict(zip("ABCD",[c["K01"][i:i+8] for i in range(0,32,8)]))
    assert all(x in mail09 for x in ("map in the back","belongs to David, not the communal shelf","tea receipt as a bookmark"))
    assert all(x in mail13 for x in ("AX-7782","second attempt","chunk sequence"))
    html=(root/"resources/evidence/h17-supplemental-office-files/retired-office-bookmarks.html").read_text()
    anchors=re.findall(r'<A HREF="([^"]+)">([^<]+)</A>',html); assert len(anchors)==15 and anchors[2][1]=="Tea-room stock sheets"

    k02=k02_raw(root,route); assert sha(k02)[:32].upper()==c["K02"]
    tids,tx=transfers(root); assert tids==["AX-7778","AX-7781","AX-7782","AX-7783"]
    assert sha(tx["AX-7782"][255])[:32].upper()==c["K07"]
    km=k05_masks(root,route); assert km[15]==bytes.fromhex(c["K05"])
    accepted={k:bytes.fromhex(c[k]) for k in ("K01","K02","K03","K05","K06","K07")}
    rawmap={"K01":accepted["K01"],"K02":k02,"K05":accepted["K05"],"K06":accepted["K06"],"K07":tx["AX-7782"][255]}
    bookmarks=[]
    for direction,namespace in itertools.product(("forward","reverse"),("MAIL","NOTE")):
        for i,(_,title) in enumerate(anchors,1):
            mapped=i if direction=="forward" else (16-i if namespace=="MAIL" else 25-i)
            bookmarks.append({"index":i,"title":title,"direction":direction,"namespace":namespace,
                              "mapped":f"{namespace}{mapped:02d}","tea_to_MAIL13":title=="Tea-room stock sheets" and namespace=="MAIL" and mapped==13})
    assert len(bookmarks)==60 and sum(x["tea_to_MAIL13"] for x in bookmarks)==1

    ops=[dict(zip(("half","plane","pack","byte_order","hex_order","char_weight","id_direction"),v))
         for v in itertools.product(("upper","lower"),(0,7),("LSB","MSB"),("forward","reverse"),("forward","reverse"),("LSB","MSB"),("forward","reverse"))]
    orders=list(itertools.permutations(SLOTS,3)); assert len(ops)==128 and len(orders)==120
    rows=[]
    for oi,op in enumerate(ops):
        sm={k:source_sel(v,op)[0] for k,v in rawmap.items()}
        mapok=sm==BASE
        groups4=group_values(accepted["K01"],op)
        k05p=pack(km[15],op["plane"],op["pack"])
        k05ok=k05p.hex().upper()=="0343" and op["byte_order"]=="forward"
        groupok=groups4["C"]==9
        comp_counts={"numeric7":0,"literalYEA":0}
        for order in orders:
            txt=component(order,accepted,op)
            comp_counts["numeric7"]+=int(low(txt,op["char_weight"])==7)
            comp_counts["literalYEA"]+=int(txt.upper()=="YEA")
        transfer_counts={}; valid={}
        for t in tids:
            ss=[transfer_sel(tx[t][m],op)[0] for m in range(256)]
            transfer_counts[t]=sum(x==11 for x in ss); valid[t]=ss[255]==11
        ids={t:id_views(t,op) for t in tids}
        gate=mapok and k05ok and groupok
        def joint(rep,tea,kind,source_valid=False):
            n=comp_counts[kind]; total=0
            for t in tids:
                idx=ids[t][rep]
                matches=[b for b in bookmarks if ((b["tea_to_MAIL13"] if tea else b["mapped"]=="MAIL13") and b["index"]==idx)]
                if not matches: continue
                if source_valid: total+=n*int(t=="AX-7782" and valid[t])
                else: total+=n*transfer_counts[t]
            return total if gate else 0
        txt=component(ORDER,accepted,op)
        rows.append({"index":oi,"op":op,"source_map":sm,"mapok":mapok,"groups":groups4,
          "K05_mask15":k05p.hex().upper(),"K05_03C":k05ok,"K01_C9":groupok,
          "component_counts":comp_counts,"selected_text":txt,"selected_selector":low(txt,op["char_weight"]),
          "transfer_counts":transfer_counts,"AX7782_mask255_selector11":valid["AX-7782"],
          "ids":ids,"joint":{
            "fullID_tea_numeric7":joint("full",True,"numeric7"),
            "fullID_tea_literalYEA":joint("full",True,"literalYEA"),
            "suffix_tea_numeric7":joint("suffix",True,"numeric7"),
            "suffix_tea_literalYEA":joint("suffix",True,"literalYEA"),
            "suffix_tea_source_mask_numeric7":joint("suffix",True,"numeric7",True),
            "suffix_tea_source_mask_literalYEA":joint("suffix",True,"literalYEA",True),
            "compact_anyMAIL13_numeric7":joint("compact",False,"numeric7"),
            "compact_anyMAIL13_literalYEA":joint("compact",False,"literalYEA"),
            "compact_anyMAIL13_source_mask_numeric7":joint("compact",False,"numeric7",True),
            "compact_anyMAIL13_source_mask_literalYEA":joint("compact",False,"literalYEA",True)}})
    route_ops=[r for r in rows if r["mapok"] and r["K05_03C"] and r["K01_C9"]]
    assert len(route_ops)==8
    keys=list(route_ops[0]["joint"])
    sums={k:sum(r["joint"][k] for r in rows) for k in keys}
    denom=128*120*4*256*60
    selected=[]
    for r in route_ops:
        op=r["op"]; txt=component(ORDER,accepted,op); idv=r["ids"]["AX-7782"]
        trsel,th=transfer_sel(tx["AX-7782"][255],op)
        selected.append({"index":r["index"],"op":op,"component":txt,"component_selector":low(txt,op["char_weight"]),
          "transfer_mask255_hex":th,"transfer_selector":trsel,"full_ID_selector":idv["full"],
          "compact_ID_selector":idv["compact"],"suffix_ID_selector":idv["suffix"],"suffix_text":idv["suffix_text"]})
    mask_table=[{"mask":m,"raw":km[m].hex().upper(),"lowbit_pack":pack(km[m],0,"LSB").hex().upper()} for m in range(16)]
    id_table={}
    for weight in ("LSB","MSB"):
        id_table[weight]={}
        for t in tids:
            p,s=t.split("-",1)
            id_table[weight][t]={"full":low(t,weight),"compact":low(t.replace("-",""),weight),
              "prefix":low(p,weight),"suffix":low(s,weight),"reversed_suffix":low(s[::-1],weight),
              "full_reversed_digits":low(p+"-"+s[::-1],weight),"compact_reversed_digits":low(p+s[::-1],weight)}
    out={
      "status":"exact finite factorized sensitivity audit; not a calibrated p-value",
      "source_pins":PINS,
      "upstream":{"variant_subset_space":4*math.comb(24,8),"CREW4_hits":crews,
        "valid_adjacent_edit_counts":edit_counts,"full_bridge_configurations":bridges,
        "full_bridge_configuration_count":len(bridges),"unique_downstream_signature_count":len(sigs),
        "downstream_signature_multiplicity":len(bridges)},
      "note_route":{"N19_HMAC_path":path,"N19_path_heads":heads,"N20_word_count":len(notes[20]["words"]),
        "N20_positions_12_10_11":[notes[20]["words"][i-1].lower() for i in (12,10,11)],
        "N20_WANTED_lowbit":low("WANTED"),"N23_WORDS_lowbit":low("WORDS"),
        "K08_source_note_ids":source_ids,"K08_source_count_letters":count_letters,"K08_source_lowbit":low(count_letters)},
      "source_joins":{"MAIL03_MAIL06_K01_groups":groups,"K01_group_selectors_LSB_LSB":group_values(accepted["K01"],{"plane":0,"pack":"LSB"}),
        "MAIL09_mapback_and_tea_receipt_cue":True,"MAIL13_full_ID_and_attempt2_cue":True,
        "physical_tea_receipt_equals_browser_bookmark":False},
      "K05_masks":mask_table,
      "bookmarks":{"count":len(bookmarks),"tea_reverse_MAIL13":[b for b in bookmarks if b["tea_to_MAIL13"]],
        "tea_reverse_NOTE22":[b for b in bookmarks if b["title"]=="Tea-room stock sheets" and b["namespace"]=="NOTE" and b["direction"]=="reverse"],
        "blank_request_forward_MAIL13":[b for b in bookmarks if b["title"]=="Blank request form" and b["mapped"]=="MAIL13"]},
      "transfer_ID_renderings":id_table,
      "global_operator_count":128,"route_operator_count":len(route_ops),
      "route_operator_indices":[r["index"] for r in route_ops],
      "route_operator_controls":[{"index":r["index"],"op":r["op"],"K01_groups":r["groups"],"K05_mask15":r["K05_mask15"],"transfer_selector11_counts":r["transfer_counts"]} for r in route_ops],
      "component_order_counts_by_half":{h:next(r["component_counts"] for r in route_ops if r["op"]["half"]==h) for h in ("upper","lower")},
      "selected_source_path":selected,"downstream_factors":{"global_ops":128,"component_orders":120,"transfer_IDs":4,"retry_masks":256,"bookmark_mappings":60},
      "downstream_denominator":denom,"factorized_joint_counts":sums,
      "factorized_joint_rates":{k:f"{v}/{denom}" for k,v in sums.items()},
      "interpretation":[
        "The full source ID AX-7782 returns 29/92, outside the 1-15 bookmark domain; the source-exact tea-bookmark endpoint has zero hits.",
        "Suffix-only 7782 returns 3 and reverse MAIL bookmark 3 returns MAIL13, but discarding AX- and the hyphen is not instructed by MAIL13.",
        "Compact AX7782 returns 13 and forward bookmark 13 (Blank request form) returns MAIL13; this is a different representation and bookmark path.",
        "The 2 ALOWBIT splice positions are duplicate encodings of one selected note set and one downstream signature.",
        "The denominator is conditional on the observed upstream signature; do not multiply it by separate upstream null rates."
      ]}
    text=json.dumps(out,indent=2,sort_keys=True)
    if a.out: a.out.write_text(text+"\n",encoding="utf-8")
    print(text)

if __name__=="__main__": main()
