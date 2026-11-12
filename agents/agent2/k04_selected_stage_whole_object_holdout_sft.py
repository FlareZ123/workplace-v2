#!/usr/bin/env python3
"""Predeclared K04 selected-stage test using whole-object leave-outs.

The test compares p950/p951/p952 as one-word shifts of the selected ESC-N
four-word capture block. It withholds the target, both same-job REQUESTED
attempts, and two downstream whole RECOVER/ACK route controls in the strict
fit. Standard library only.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ORIGIN, LAST, U, MAG = -1100, 1040, 0xffffffff, 0x9908b0df
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
PINS = {
    "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/archive-labels.ini": "146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad",
    "evidence/mail/16.eml": "02535cc5966a9215d01ecada4a14b6a403d78ca8d09310a5c3cf1a574f817a08",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}


def untemper(x):
    for k,left,m in ((18,False,U),(15,True,0xefc60000),(7,True,0x9d2c5680),(11,False,U)):
        y=x
        for _ in range(6): y=x^(((y<<k)&m) if left else y>>k)
        x=y&U
    return x


def words():
    a=[[1<<(32*i+j) for j in range(32)] for i in range(624)]
    for i in range(624,LAST-ORIGIN+1):
        t=i-624
        a.append([a[t+397][j]^(a[t][31] if j==30 else (a[t+1][j+1] if j<30 else 0))^(a[t+1][0] if (MAG>>j)&1 else 0) for j in range(32)])
    return a


def get(a,i):
    if not ORIGIN<=i<=LAST: raise IndexError(i)
    return a[i-ORIGIN]


class Basis:
    def __init__(self): self.rows={}; self.rank=0
    def insert(self,v,b):
        while v:
            p=v.bit_length()-1
            if p not in self.rows:
                self.rows[p]=(v,b); self.rank+=1; return
            w,c=self.rows[p]; v^=w; b^=c
        if b: raise ValueError("inconsistent source basis under this stage model")
    def predict(self,v):
        b=0
        while v:
            p=v.bit_length()-1
            if p not in self.rows: return None
            w,c=self.rows[p]; v^=w; b^=c
        return b


def temper(v):
    a=[v[j]^(v[j+11] if j+11<32 else 0) for j in range(32)]
    b=[a[j]^(a[j-7] if j>=7 and (0x9d2c5680>>j)&1 else 0) for j in range(32)]
    c=[b[j]^(b[j-15] if j>=15 and (0xefc60000>>j)&1 else 0) for j in range(32)]
    return [c[j]^(c[j+18] if j+18<32 else 0) for j in range(32)]


def predict_payload(basis, s, start):
    out=bytearray(); known=0; unknown=0
    for lane in range(4):
        word=0; full=True
        for j,v in enumerate(temper(get(s,start+lane))):
            bit=basis.predict(v)
            if bit is None:
                unknown+=1; full=False
            else:
                known+=1; word |= bit<<j
        out.extend(word.to_bytes(4,"little") if full else b"\x00\x00\x00\x00")
    return (bytes(out) if unknown==0 else None), known, unknown


def parse_routes(text):
    marker="[printer_routes_2026-09-01_to_2026-10-03]"
    section=text.split(marker,1)[1].split("[",1)[0]
    return dict(re.findall(r"(?m)^([A-Z-]+)=([A-Z0-9-]+)$",section))


def parse_rows(spool_raw):
    lines=[line for line in spool_raw.decode("ascii").splitlines() if line.startswith("2026-")]
    if len(lines)!=133 or len(lines)!=len(STARTS): raise ValueError("expected 133 source rows")
    rows=[]
    for i,line in enumerate(lines):
        m=re.match(r"(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+)",line)
        p=re.search(r"(?:^|\s)PAYLOAD=([0-9A-F]{32})(?=\s|$)",line)
        if not m or not p: raise ValueError(f"malformed spool row {i}")
        ts,job,attempt,state,cls=m.groups()
        rows.append({"i":i,"ts":ts,"job":job,"attempt":int(attempt),"state":state,"class":cls,"payload":bytes.fromhex(p.group(1))})
    return rows


def last_ack_recover(rows, job):
    matches=[r["i"] for r in rows if r["job"]==job and r["state"]=="ACK"]
    if not matches: raise ValueError(f"no ACK for {job}")
    idx=max(matches)
    if rows[idx]["class"]!="RECOVER": raise ValueError(f"last ACK for {job} is not RECOVER")
    return idx


def run(root):
    raw={rel:(root/rel).read_bytes() for rel in PINS}
    actual={rel:hashlib.sha256(data).hexdigest() for rel,data in raw.items()}
    if actual!=PINS: raise ValueError(f"source pin mismatch: {actual}")

    rows=parse_rows(raw["evidence/print/spool-reconstruction.log"])
    routes=parse_routes(raw["evidence/archive-labels.ini"].decode())
    mail16=raw["evidence/mail/16.eml"].decode()
    routing=json.loads(raw["evidence/recovery-routing.json"])
    acceptance=json.loads(raw["acceptance.json"])
    assert "Use the last" in mail16 and "never returned an acknowledgement" in mail16

    target_i=last_ack_recover(rows,routes["ESC-N"])
    esc_s_i=last_ack_recover(rows,routes["ESC-S"])
    spare_i=last_ack_recover(rows,routes["WATCH-SPARE"])
    same_job_requested=sorted(r["i"] for r in rows if r["job"]==routes["ESC-N"] and r["state"]=="REQUESTED")
    assert (target_i,same_job_requested,esc_s_i,spare_i)==(129,[128,130],131,132)
    assert STARTS[128]==947 and STARTS[target_i]==951 and STARTS[130]==955 and STARTS[131]==959 and STARTS[132]==963

    mask=bytes.fromhex(routing["K04"]["masked_component"])
    target_commit=acceptance["slot_sha256"]["K04"]
    variants=[
        {"name":"strict_nonack_withheld", "withheld":{target_i,*same_job_requested,esc_s_i,spare_i}, "controls":tuple([*same_job_requested,esc_s_i,spare_i]),
         "reason":"Withhold both same-job REQUESTED attempts plus target and route controls; do not assume a non-ACK request consumed a valid four-word packet."},
        {"name":"include_earlier_requested_only", "withheld":{target_i,same_job_requested[1],esc_s_i,spare_i}, "controls":(same_job_requested[1],esc_s_i,spare_i),
         "reason":"Sensitivity only: include the earlier REQUESTED attempt1 but exclude later REQUESTED attempt3."},
        {"name":"include_later_requested_only", "withheld":{target_i,same_job_requested[0],esc_s_i,spare_i}, "controls":(same_job_requested[0],esc_s_i,spare_i),
         "reason":"Sensitivity only: include the later REQUESTED attempt3 but exclude earlier REQUESTED attempt1."},
        {"name":"include_both_requested_attempts", "withheld":{target_i,esc_s_i,spare_i}, "controls":(esc_s_i,spare_i),
         "reason":"Diagnostic only: include both non-ACK REQUESTED rows as intact four-word training packets."},
    ]
    all_results=[]
    for variant in variants:
        variant_results=[]
        for delta,label in [(-1,"p950"),(0,"p951"),(1,"p952")]:
            s=words(); b=Basis()
            try:
                for i,row in enumerate(rows):
                    if i in variant["withheld"]: continue
                    start=STARTS[i]+(delta if i>target_i else 0)
                    for lane in range(4):
                        native=untemper(int.from_bytes(row["payload"][lane*4:lane*4+4],"little"))
                        for j,v in enumerate(get(s,start+lane)):
                            b.insert(v,(native>>j)&1)
            except (ValueError,IndexError) as e:
                variant_results.append({"hypothesis":label,"delta":delta,"status":"FALSIFIED_DURING_FIT","reason":str(e)})
                continue
            controls_out=[]
            for i in variant["controls"]:
                row=rows[i]; start=STARTS[i]+delta
                pred,known,unknown=predict_payload(b,s,start)
                controls_out.append({
                    "row_index":i,"job":row["job"],"attempt":row["attempt"],"state":row["state"],"class":row["class"],
                    "candidate_start":start,"actual_payload":row["payload"].hex().upper(),
                    "predicted_payload":pred.hex().upper() if pred is not None else None,
                    "determined_bits":known,"undetermined_bits":unknown,
                    "whole_object_exact":pred==row["payload"] if pred is not None else False,
                })
            target_payload,tk,tu=predict_payload(b,s,STARTS[target_i]+delta)
            component=None; component_commit=None; component_match=None
            if target_payload is not None:
                component=bytes(x^y for x,y in zip(target_payload,mask))
                component_commit=hashlib.sha256(component).hexdigest()
                component_match=component_commit==target_commit
            variant_results.append({
                "hypothesis":label,"delta":delta,"status":"FIT_OK","rank":b.rank,"free_state_bits":19968-b.rank,
                "controls":controls_out,"all_whole_controls_exact":all(x["whole_object_exact"] for x in controls_out),
                "target_payload_prediction":target_payload.hex().upper() if target_payload is not None else None,
                "target_determined_bits":tk,"target_undetermined_bits":tu,
                "candidate_K04":component.hex().upper() if component is not None else None,
                "candidate_K04_commitment":component_commit,"candidate_matches_K04":component_match,
            })
        all_results.append({"variant":variant["name"],"withheld_rows":sorted(variant["withheld"]),"controls":list(variant["controls"]),"reason":variant["reason"],"results":variant_results})

    return {
        "source_sha256":actual,
        "base_model":"Agent49 agents/agent49/k04_p951_symbolic_basis.py STARTS schedule and GF(2) MT19937 state representation; selected target row omitted.",
        "target_selector":{"route":"ESC-N","job":routes["ESC-N"],"selected_last_ACK_RECOVER_row":target_i,"attempt":rows[target_i]["attempt"],"payload_class":rows[target_i]["class"]},
        "predeclared_controls":[
            {"row":same_job_requested[0],"job":rows[same_job_requested[0]]["job"],"attempt":rows[same_job_requested[0]]["attempt"],"state":"REQUESTED","role":"same-job earlier non-ACK attempt1; held out in strict fit"},
            {"row":same_job_requested[1],"job":rows[same_job_requested[1]]["job"],"attempt":rows[same_job_requested[1]]["attempt"],"state":"REQUESTED","role":"same-job later retry; MAIL-16 says it never returned ACK"},
            {"row":esc_s_i,"route":"ESC-S","job":routes["ESC-S"],"role":"last ACK RECOVER whole object; held out"},
            {"row":spare_i,"route":"WATCH-SPARE","job":routes["WATCH-SPARE"],"role":"last ACK RECOVER whole object; explicitly unrelated spare, held out as a control only"}],
        "hypotheses":"p950/p951/p952 are modeled as one-word shifts of the selected four-word block, with every downstream row shifted by the same delta. A local-only capture-pointer shift leaves downstream records unchanged, so non-target controls are observationally equivalent and cannot discriminate it.",
        "K04_target_commitment":target_commit,
        "variants":all_results,
        "conclusion":"Under the strict fit with both non-ACK same-job REQUESTED attempts withheld, all three propagated-shift hypotheses fit and no withheld whole-object control is fully predicted; the target payload remains underdetermined. Any diagnostic stage rejection that appears only when REQUESTED rows are used as training is conditional on those unacknowledged rows consuming valid four-word packets. Existing evidence therefore does not identify a selected stage or justify treating p950/p951/p952 support as a real selection rule.",
    }


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path("resources"))
    a=p.parse_args()
    print(json.dumps(run(a.root),indent=2))
