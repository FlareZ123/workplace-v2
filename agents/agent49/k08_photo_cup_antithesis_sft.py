"""K08: photograph/galley first-versus-last cup, N13-independent complete-caption test.

Original REC8/1 HMAC16/SHA256 unchanged. Run 4 disjoint time shards:
  H17_TSTART=0  H17_TSTOP=6  python agents/agent49/k08_photo_cup_antithesis_sft.py /path/to/original.zip
  H17_TSTART=6  H17_TSTOP=12 python agents/agent49/k08_photo_cup_antithesis_sft.py /path/to/original.zip
  H17_TSTART=12 H17_TSTOP=18 python agents/agent49/k08_photo_cup_antithesis_sft.py /path/to/original.zip
  H17_TSTART=18 H17_TSTOP=24 python agents/agent49/k08_photo_cup_antithesis_sft.py /path/to/original.zip

Original run: 4x2,073,600 assignments, original_hits 0 every shard.
This is an uncalibrated N01/N09/N10/N20 first/last-cup editorial hypothesis,
not an attested author-final caption or selected version history.
"""
import hashlib,hmac,itertools,os,re,sys,time,zipfile
from pathlib import Path
NOTES_SHA="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
NONCE=bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET=bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")
TIME="""from the first cup to the last
from the first cup to the last cup
between the first cup and the last
between the first cup and the last cup
after the last cup
after the last cup of tea
when the last cup is finished
when the last cup is empty
when the tea is finished
at the end of the night
near the end of the night
at the end of a long night
from the first watch to the last
from the first light to the last
when the night is nearly over
as the night is nearly over
when the night is almost finished
as the night is almost finished
after the long watch
after a long watch
when the long watch ends
when the last watch is over
after the last cup at the table
after the last tea by the window""".splitlines()
SEA="""the sea waits outside
the sea is still outside
the sea stays outside
the sea is outside
the sea looks different
the sea looks different now
the sea looks different after tea
the sea keeps moving
the sea goes on
the sea carries on
the sea is still there
the water stays outside
the water is still outside
the water goes on outside
the water keeps moving
the water looks different
the water gives back the daylight
the sea beyond the window
the sea beyond the glass
the sea outside the window
the dark sea beyond the window
the sea beyond the table
the sea at the end of the night
the sea is quiet
the sea is never quiet
the sea is still awake
the sea sees the last light
the last light over the sea
the sea holds the night
the sea keeps its own watch""".splitlines()
PEOPLE="""there is room at the table
there is still room at the table
there is room for one more
there is always room for one more
we make room at the table
we make room for one another
we leave room for one another
we leave room at the table
we leave room for the next watch
we leave a place at the table
someone leaves a place at the table
someone keeps a place for the next watch
the voices are still at the table
the voices stay at the table
the voices remain at the table
the voices are there at the table
the table is still full of voices
the table holds the last voices
the last voices stay at the table
the voices at the table stay
the first cup is never taken alone
the first cup is never alone
nobody takes the first cup alone
nobody finishes the last cup alone
the last cup is never taken alone
the last cup is for one more
somebody stays for the last cup
somebody waits by the window
we are still here at the table
we are together at the table
someone has saved a chair
someone has left a chair
someone remembers the next watch
somebody has kept the lamp on
the lamp stays on for the next watch
there is a light for the next watch
the mugs belong to the night crew
the mugs are still on the table
we keep a place for whoever comes next
a place waits for whoever comes next""".splitlines()
CONNECT=["and","but","while","as","when","with"]
def norm(s):
    return " ".join(re.findall("[a-z0-9]+",s.lower()))
def commit(s):
    return hashlib.sha256(hmac.digest(NONCE,s.encode("utf8"),"sha256")[:16]).digest()
def note(text,i):
    return text.split(f"N{i:02d} / ")[1].split("\n",1)[1].split("\n\n",1)[0].strip()
def main(source):
    if source.is_file():
        with zipfile.ZipFile(source) as z: raw=z.read("evidence/crew/noticeboard-and-desk-notes.txt")
    else: raw=(source/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==NOTES_SHA
    text=raw.decode("ascii")
    assert all(cue in note(text,i).lower() for i,cue in
            ((1,"sea looks different"),(9,"first cup alone"),(10,"after the last cup"),(20,"voices at the table")))
    first=note(text,2).split("First draft for the crew board: ",1)[1]
    assert hmac.digest(NONCE,norm(first).encode(),"sha256")[:16].hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
    assert [len(TIME),len(SEA),len(PEOPLE),len(CONNECT)]==[24,30,40,6]
    lo=int(os.environ.get("H17_TSTART","0"));hi=int(os.environ.get("H17_TSTOP","24"))
    assert 0<=lo<hi<=24
    planted=commit(norm(TIME[0]+" "+SEA[0]+" and "+PEOPLE[0]))
    cnt=original=positive=0
    start=time.monotonic()
    for t,s,p,c1,c2 in itertools.product(TIME[lo:hi],SEA,PEOPLE,CONNECT,CONNECT):
        for a,b in ((s,p),(p,s)):
            variants=(t+" "+a+" "+c1+" "+b,
                      t+" "+c1+" "+a+" "+c2+" "+b,
                      a+" "+c1+" "+b+" "+c2+" "+t,
                      t+" "+a+" "+c1+" "+b+" "+c2+" "+t)
            for variant in variants:
                h=commit(norm(variant))
                cnt+=1;original+=h==TARGET;positive+=h==planted
    assert cnt==(hi-lo)*30*40*6*6*2*4
    assert (positive==6) if lo==0 else (positive==0)
    print(f"K08_CUP_EDITOR time_shard={lo}:{hi} source_sha=PASS n02=PASS "
          f"complete_assignments={cnt} original_hits={original} planted_hits={positive} "
          f"seconds={time.monotonic()-start:.2f}")
if __name__=="__main__":
    main(Path(sys.argv[1] if len(sys.argv)>1 else "resources"))
