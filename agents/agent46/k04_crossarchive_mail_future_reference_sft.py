"""Original read-only cross-document chronology and forward-reference SFT."""
from __future__ import annotations

from datetime import datetime
from email.parser import BytesParser
from email import policy
from email.utils import parsedate_to_datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import re

ROOT=Path(os.environ.get("H17_RESOURCE_ROOT",Path(__file__).resolve().parents[2]/"resources"))
PINS={
    "evidence/mail/13.eml":"80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
    "evidence/mail/16.eml":"02535cc5966a9215d01ecada4a14b6a403d78ca8d09310a5c3cf1a574f817a08",
    "evidence/transfers/transfer-audit.jsonl":"32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "evidence/print/spool-reconstruction.log":"7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
}
for rel,expected in PINS.items():
    assert sha256((ROOT/rel).read_bytes()).hexdigest()==expected

def mail_date(n):
    msg=BytesParser(policy=policy.default).parsebytes((ROOT/f"evidence/mail/{n:02}.eml").read_bytes())
    return parsedate_to_datetime(str(msg["Date"]))

records=[json.loads(s) for s in (ROOT/"evidence/transfers/transfer-audit.jsonl").read_text().splitlines()]
commits=[r for r in records if r.get("kind")=="COMMIT" and r.get("transfer")=="AX-7782"]
assert len(commits)==1 and commits[0]["dry_run"] is False
receipt=datetime.fromisoformat(commits[0]["receipt_utc"].replace("Z","+00:00"))
m13=mail_date(13)
assert m13.isoformat()=="2026-10-02T09:56:00+00:00"
assert receipt.isoformat()=="2026-10-03T20:55:10+00:00"
assert receipt>m13

rows=[]
for line in (ROOT/"evidence/print/spool-reconstruction.log").read_text().splitlines():
    if "JOB=PS-261003-0417" not in line or "CLASS=RECOVER" not in line:continue
    stamp=line.split()[0]
    attempt=int(re.search(r"ATTEMPT=(\d+)",line).group(1))
    state=re.search(r"STATE=(\w+)",line).group(1)
    rows.append((datetime.fromisoformat(stamp.replace("Z","+00:00")),attempt,state))
rows.sort()
assert len(rows)==3
assert [(r[1],r[2]) for r in rows]==[(1,"REQUESTED"),(2,"ACK"),(3,"REQUESTED")]
m16=mail_date(16)
assert m16.isoformat()=="2026-10-03T07:49:00+00:00"
assert all(t>m16 for t,_,_ in rows)
print("PINNED_ORIGINAL_SOURCE_PASS",len(PINS))
print("MAIL13",m13.isoformat(),"AX7782_COMMIT",receipt.isoformat(),"FORWARD_GAP",receipt-m13)
print("MAIL16",m16.isoformat())
for stamp,attempt,state in rows:
    print("0417",attempt,state,stamp.isoformat(),"FORWARD_GAP",stamp-m16)
print("INTERPRETATION: two apparent future-event references, not proof of historical source fabrication")
