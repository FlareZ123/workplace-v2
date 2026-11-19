#!/usr/bin/env python3
"""Conditional source-preserving note-ID permutation null for K08 LOW BIT.

Run from the workplace-v2 root:
  python agents/agent9/k08_note_order_null.py --trials 50000 --seed 20261119
  python agents/agent9/k08_note_order_null.py --trials 50000 --seed 20261119 --preserve-colon-labels
  python agents/agent9/k08_note_order_null.py --trials 50000 --seed 20261119 --split-hyphenated-tokens
  python agents/agent9/k08_note_order_null.py --trials 50000 --seed 20261119 --preserve-colon-labels --split-hyphenated-tokens

Permutes complete note bodies only among IDs with the same author. The parser
mode is explicit: colon labels may be stripped or preserved, and hyphenated
note-body tokens may be preserved or split. The default remains the historical
label-stripped, hyphen-preserving baseline. Results are conditional, not a
global p-value or an archive-recovery claim.
"""
from __future__ import annotations
import argparse, hashlib, hmac, json, random, re
from collections import Counter
from math import factorial, prod
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
E=ROOT/"resources/evidence"
EXPECTED={
    "crew/noticeboard-and-desk-notes.txt":"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "recovery-routing.json":"f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "mail/11.eml":"f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
}
TOKEN=re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?")

def low_value(s: str) -> int:
    return sum((ord(c)&1)<<i for i,c in enumerate(s))

def low_pack(raw: bytes) -> bytes:
    bits=[b&1 for b in raw]
    return bytes(sum(bits[i+j]<<j for j in range(min(8,len(bits)-i))) for i in range(0,len(bits),8))

def words(s: str, split_hyphens: bool = False) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", s) if split_hyphens else TOKEN.findall(s)

def normalize(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]"," ",s.lower()).split())

def parse_notes(path: Path, nonce: bytes, strip_colon_labels: bool = True, split_hyphens: bool = False) -> dict[int,dict]:
    raw=path.read_text(encoding="utf-8")
    out={}
    for num,author,text in re.findall(r"(?ms)^N(\d\d) / ([^\n]+)\n(.+?)(?=\n\nN\d\d /|\Z)",raw):
        body=text.strip()
        if strip_colon_labels and ":" in body:
            body=body.split(":",1)[1].strip()
        toks=words(body,split_hyphens=split_hyphens)
        digest=hmac.new(nonce,normalize(body).encode(),"sha256").digest()[:16]
        low19=[(i,t.lower()) for i,t in enumerate(toks,1) if low_value(t.upper())==19]
        self_repeat=False
        if len(toks)>=12:
            tri=(toks[11].lower(),toks[9].lower(),toks[10].lower())
            low=[t.lower() for t in toks]
            self_repeat=any(tuple(low[j:j+3])==tri for j in range(len(low)-2))
        out[int(num)]={
            "author":author.split()[0],"body":body,"tokens":toks,
            "lower":[t.lower() for t in toks],"count":len(toks),
            "head":toks[0][0].upper(),"self_repeat":self_repeat,
            "hmac_selector":low_value(low_pack(digest).hex().upper()),
            "low19":low19,
        }
    if set(out)!=set(range(1,25)):
        raise AssertionError("expected N01..N24")
    return out

def flatten_strings(x,path=""):
    if isinstance(x,dict):
        for k,v in x.items():
            yield from flatten_strings(v,f"{path}/{k}")
    elif isinstance(x,list):
        for i,v in enumerate(x):
            yield from flatten_strings(v,f"{path}[{i}]")
    elif isinstance(x,str):
        yield path,x

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--trials",type=int,default=50000)
    ap.add_argument("--seed",type=int,default=20261119)
    ap.add_argument("--preserve-colon-labels",action="store_true",help="Keep colon-prefixed labels in note bodies")
    ap.add_argument("--split-hyphenated-tokens",action="store_true",help="Split hyphenated note-body tokens")
    args=ap.parse_args()
    for rel,expected in EXPECTED.items():
        actual=hashlib.sha256((E/rel).read_bytes()).hexdigest()
        if actual!=expected:
            raise AssertionError(f"source hash mismatch: {rel}")
    routing=json.loads((E/"recovery-routing.json").read_text())
    nonce=bytes.fromhex(routing["K08"]["desk_nonce"])
    base=parse_notes(E/"crew/noticeboard-and-desk-notes.txt",nonce,
                     strip_colon_labels=not args.preserve_colon_labels,
                     split_hyphens=args.split_hyphenated_tokens)
    authors=[base[n]["author"] for n in range(1,25)]
    first_order=list(dict.fromkeys(authors))
    groups={a:[n for n in range(1,25) if base[n]["author"]==a] for a in first_order}
    emily=[n for n in range(1,25) if base[n]["author"]=="Emily"]
    david=[n for n in range(1,25) if base[n]["author"]=="David"]
    route_strings=list(flatten_strings(routing))
    source_selectors={slot:[low_value(t) for t in re.findall(r"[A-Za-z0-9]+",routing[slot]["source"]) if 1<=low_value(t)<=24]
                      for slot in (f"K{i:02d}" for i in range(1,9))}
    route_controls=[(p,[low_value(t) for t in re.findall(r"[A-Za-z0-9]+",v) if 1<=low_value(t)<=24]) for p,v in route_strings]

    # Verify both independent source-prose witnesses before freezing selectors.
    mail11=(E/"mail/11.eml").read_text()
    mail_tokens=[t.lower() for t in words(mail11.split("\n\n",1)[1])]
    route_tokens=[t.lower() for t in words(routing["K08"]["rule"])]
    if not any(mail_tokens[i:i+3]==["long","watch","with"] for i in range(len(mail_tokens)-2)):
        raise AssertionError("MAIL-11 calibration phrase missing")
    if not any(route_tokens[i:i+3]==["late","watch","rather"] for i in range(len(route_tokens)-2)):
        raise AssertionError("K08 rule calibration phrase missing")
    mail11_selectors=[low_value(t) for t in ("long","watch","with")]
    route_selectors=[low_value(t) for t in ("late","watch","rather")]
    if mail11_selectors!=[10,11,3] or route_selectors!=[10,11,18]:
        raise AssertionError("source-prose selector calibration changed")

    def evaluate(a):
        edits=[]
        for pos,original in enumerate(emily):
            ids=emily.copy()
            ids[pos]+=1
            if ids!=sorted(ids) or len(set(ids))!=len(ids) or any(n not in a for n in ids):
                continue
            heads="".join(a[n]["head"] for n in ids)
            counts="".join(chr(65+a[n]["count"]) if a[n]["count"]<26 else "?" for n in ids)
            splice=heads[0]+counts[1:4]+heads[5:8]
            edits.append((original,ids[pos],heads,splice))
        edit_hit=[x for x in edits if x[2]=="ATEALBIT" and x[3]=="ALOWBIT"]
        david_word="".join(chr(65+a[n]["count"]) if a[n]["count"]<26 else "?" for n in david)
        n20=a[20]["lower"]
        pos_trip=tuple(n20[i-1] for i in (12,10,11)) if len(n20)>=12 else ()
        mail_trip=tuple(n20[i-1] for i in (10,11,3)) if len(n20)>=11 else ()
        route_trip=tuple(n20[i-1] for i in (10,11,18)) if len(n20)>=18 else ()
        motifs=all(m in n20 for m in ("sea","night","voices","table"))
        if motifs:
            positions=[n20.index(m) for m in ("sea","night","voices","table")]
            motifs=positions==sorted(positions)
            ends="ATSE"
            seat="SEAT"
        else:
            ends=seat=""
        n23=a[23]["lower"]
        hmap={n:a[n]["hmac_selector"] for n in range(1,25)}
        fixed=[]
        for start in range(1,25):
            seen=set()
            path=[]
            node=start
            while node not in seen and 1<=node<=24:
                seen.add(node)
                path.append(node)
                node=hmap[node]
            if node in seen:
                heads="".join(a[n]["head"] for n in path)
                if len(heads)<=8 and low_value(heads)==start:
                    fixed.append((start,tuple(path),heads))
        fixed_starts={x[0] for x in fixed}
        n23_fixed=[(t,low_value(t.upper())) for t in n23 if 1<=low_value(t.upper())<=24 and low_value(t.upper()) in fixed_starts]
        low19=[(n,i,t.lower()) for n in range(1,25) for i,t in enumerate(a[n]["tokens"],1) if low_value(t.upper())==19]
        def reduce(selectors):
            letters="".join(chr(65+a[n]["count"]) if a[n]["count"]<26 else "?" for n in selectors)
            return letters,low_value(letters)
        reductions={s:reduce(ix) for s,ix in source_selectors.items()}
        eligible=[]
        for path,selectors in route_controls:
            letters,sel=reduce(selectors)
            if 1<=len(letters)<=8:
                eligible.append((path,letters,sel))
        special=[r for r in eligible if "LOW" in r[1] or r[2]==12]
        self_repeat=[n for n in range(1,25) if a[n]["self_repeat"]]
        return {
            "david_LOW":david_word=="LOW",
            "unique_Emily_plus_one_ALOWBIT":len(edits)==7 and len(edit_hit)==1 and edit_hit[0][:2]==(10,11),
            "N20_positions_12_10_11_the_end_of":pos_trip==("the","end","of"),
            "MAIL11_and_route_calibration":mail_trip==("end","of","the") and route_trip==("end","of","the"),
            "N20_unique_self_repeat":self_repeat==[20],
            "N20_motif_ATSE_to_SEAT":motifs and ends=="ATSE" and seat=="SEAT",
            "N23_WORDS_to_19":"words" in n23 and low_value("WORDS")==19,
            "N20_WANTED_to_19":"wanted" in n20 and low_value("WANTED")==19,
            "unique_N19_SANTE_fixedpoint":fixed==[(19,(19,13,9,12,11),"SANTE")],
            "N23_unique_token_to_fixedpoint":len(fixed_starts)==1 and n23_fixed==[("words",19)],
            "WANTED_WORDS_only_LOW19_pair":low19==[(20,2,"wanted"),(23,16,"words")],
            "K08_source_VLOWL_to_12":reductions.get("K08")==("VLOWL",12),
            "K08_source_unique_across_slots":sum("LOW" in v[0] or v[1]==12 for v in reductions.values())==1 and ("LOW" in reductions["K08"][0] or reductions["K08"][1]==12),
            "K08_route_string_unique":len(special)==1 and special[0]==("/K08/source","VLOWL",12),
            "N12_HMAC_to_11_even":hmap[12]==11 and 12%2==0,
            "SEATS_to_N23":seat=="SEAT" and seat+"S"=="SEATS" and low_value("SEATS")==23 and "words" in n23,
        }

    observed=evaluate(base)
    if not all(observed.values()) and not args.preserve_colon_labels:
        raise AssertionError(f"observed source chain failed: {observed}")
    rng=random.Random(args.seed)
    counts=Counter()
    for _ in range(args.trials):
        a={n:base[n] for n in range(1,25)}
        for author,ids in groups.items():
            shuffled=[base[n] for n in ids]
            rng.shuffle(shuffled)
            for note_id,record in zip(ids,shuffled):
                a[note_id]=record
        flags=evaluate(a)
        for name,passed in flags.items():
            if passed:
                counts[name]+=1
        if all(flags.values()):
            counts["FULL_CHAIN"]+=1
    result={
        "trials":args.trials,"seed":args.seed,
        "parser_mode":{"colon_labels":"preserved" if args.preserve_colon_labels else "stripped",
                       "note_body_tokenizer":"split-hyphen" if args.split_hyphenated_tokens else "hyphen-preserving"},
        "observed_pass_count":sum(observed.values()),
        "possible_within_author_permutations":prod(factorial(len(ids)) for ids in groups.values()),
        "observed_flags":observed,
        "stage_hits":{k:{"hits":counts[k],"rate":counts[k]/args.trials} for k in sorted(counts)},
        "full_chain_hits":counts["FULL_CHAIN"],
        "full_chain_rate":counts["FULL_CHAIN"]/args.trials,
        "zero_hit_95pct_upper_bound_rule_of_three":3/args.trials if counts["FULL_CHAIN"]==0 else None,
        "scope":"Conditional matched null: permute complete note bodies only among IDs with the same author. Parser mode is explicit in parser_mode. Preserves authorship, author counts, all source texts, and body properties; disrupts only body-to-note-ID assignment. Not a global p-value and not corrected for post-hoc LOW BIT mechanism selection.",
    }
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
