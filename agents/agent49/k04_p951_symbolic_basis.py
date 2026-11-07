"""Exact GF(2) MT source-only printer model; selected row129 omitted."""
from pathlib import Path
import re,hashlib,sys
ORIGIN,LAST,U,MAG=-1100,1040,0xffffffff,0x9908b0df
STARTS=[0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
def untemper(x):
 for k,left,m in ((18,False,U),(15,True,0xefc60000),(7,True,0x9d2c5680),(11,False,U)):
  y=x
  for _ in range(6):y=x^(((y<<k)&m) if left else y>>k)
  x=y&U
 return x
def words():
 a=[[1<<(32*i+j) for j in range(32)] for i in range(624)]
 for i in range(624,LAST-ORIGIN+1):
  t=i-624
  a.append([a[t+397][j]^(a[t][31] if j==30 else (a[t+1][j+1] if j<30 else 0))^(a[t+1][0] if (MAG>>j)&1 else 0) for j in range(32)])
 return a
def get(a,i):
 assert ORIGIN<=i<=LAST,(i,ORIGIN,LAST)
 return a[i-ORIGIN]
class Basis:
 def __init__(self):self.rows={};self.rank=0
 def insert(self,v,b):
  while v:
   p=v.bit_length()-1
   if p not in self.rows:self.rows[p]=(v,b);self.rank+=1;return
   w,c=self.rows[p];v^=w;b^=c
  assert b==0,'original printer contradiction'
 def predict(self,v):
  b=0
  while v:
   p=v.bit_length()-1
   if p not in self.rows:return None
   w,c=self.rows[p];v^=w;b^=c
  return b
def temper(v):
 a=[v[j]^(v[j+11] if j+11<32 else 0) for j in range(32)]
 b=[a[j]^(a[j-7] if j>=7 and (0x9d2c5680>>j)&1 else 0) for j in range(32)]
 c=[b[j]^(b[j-15] if j>=15 and (0xefc60000>>j)&1 else 0) for j in range(32)]
 return [c[j]^(c[j+18] if j+18<32 else 0) for j in range(32)]
def packets(root):
 evidence=Path(root)/'resources/evidence'
 raw=(evidence/'print/spool-reconstruction.log').read_bytes()
 assert hashlib.sha256(raw).hexdigest()=='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
 sys.path.insert(0,str(Path(root)/'work'))
 from h17_witness_intake import last_escrow_ack
 route,attempt,timestamp=last_escrow_ack(evidence)
 lines=[line for line in raw.decode('ascii').splitlines() if line.startswith('2026-')]
 assert len(lines)==len(STARTS)==133
 timestamp_text=timestamp.isoformat().replace('+00:00','Z')
 selected=[]
 for index,line in enumerate(lines):
  match=re.match(r'(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+)(?=\s|$)',line)
  if match is None:continue
  ts,job,attempt_text,state,job_class=match.groups()
  if (job==route and int(attempt_text)==attempt and state=='ACK'
      and job_class=='RECOVER' and ts==timestamp_text):
   selected.append(index)
 assert selected==[129],selected
 selected_index=selected[0]
 assert STARTS[selected_index]==951
 rows=[]
 for index,line in enumerate(lines):
  if index==selected_index:
   rows.append(b'')
   continue
  match=re.search(r'(?:^|\s)PAYLOAD=([0-9A-F]{32})(?=\s|$)',line)
  assert match is not None,('missing intact training payload',index)
  rows.append(bytes.fromhex(match.group(1)))
 return rows,selected_index

def source(root):
 rows,selected_index=packets(root)
 s=words();b=Basis()
 for row,(payload,pos) in enumerate(zip(rows,STARTS)):
  if row==selected_index:continue
  assert len(payload)==16
  for lane in range(4):
   native=untemper(int.from_bytes(payload[lane*4:lane*4+4],'little'))
   for j,v in enumerate(get(s,pos+lane)):b.insert(v,(native>>j)&1)
 assert b.rank==15365
 try:get(s,ORIGIN-1)
 except AssertionError:pass
 else:raise AssertionError('negative source index alias')
 return b,s
