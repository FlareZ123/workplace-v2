#!/usr/bin/env python3
"""Original-source complete minimal SCS: selected N01 and N20 P20,
with zero or one independently source-evidenced N02/MAIL11 ROOM.
Reports aggregate only; no original candidate text/component is emitted.
"""
from pathlib import Path
from hashlib import sha256
import hmac, itertools, json, re, sys, math

CREW_SHA='13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
P20_SHA='4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c'
N02_HMAC16='bf889359b0303f2b2b2fd96ae841210b'
def words(s):
    return re.findall(r'[a-z0-9]+',s.lower())

def main(root):
    root=Path(root)
    raw=(root/'evidence/crew/noticeboard-and-desk-notes.txt').read_bytes()
    assert sha256(raw).hexdigest()==CREW_SHA
    notes={}
    for m in re.finditer(r'^N(\d{2}) / [^\n]+\n([^\n]+)',raw.decode(),re.M):
        n=int(m.group(1))
        body=m.group(2).split(':',1)[-1].lstrip()
        notes[n]=words(body)
    assert set(notes)==set(range(1,25))
    a=notes[1]
    b=notes[20][6:19]
    assert len(a)==11 and len(b)==13
    assert a[:2]==b[:2]==['the','sea']
    assert sha256(' '.join(b).encode()).hexdigest()==P20_SHA
    # Outside the identical two-word prefix, no further word is shared.
    assert not set(a[2:]).intersection(b[2:])
    assert 'room' in notes[2] and 'room' not in a+b
    route=json.loads((root/'evidence/recovery-routing.json').read_text())
    acceptance=json.loads((root/'acceptance.json').read_text())
    key=bytes.fromhex(route['K08']['desk_nonce'])
    target=acceptance['slot_sha256']['K08']
    def reduced(w):
        msg=' '.join(w).encode('utf8')
        return sha256(hmac.new(key,msg,'sha256').digest()[:16]).hexdigest()
    assert hmac.new(key,' '.join(notes[2]).encode(),'sha256').digest()[:16].hex()==N02_HMAC16
    n=20;choose=9
    count_plain=count_room=hits_plain=hits_room=plant_plain=plant_room=0
    # Entire first row followed by second row beyond shared THE SEA.
    positive_plain=a[:2]+a[2:]+b[2:]
    positive_room=['room']+positive_plain
    tgt_plant_plain=reduced(positive_plain)
    tgt_plant_room=reduced(positive_room)
    for positions in itertools.combinations(range(n),choose):
        chosen=set(positions)
        ai=bi=0
        out=[]
        for pos in range(n):
            if pos in chosen:
                out.append(a[2+ai]);ai+=1
            else:
                out.append(b[2+bi]);bi+=1
        assert ai==9 and bi==11
        phrase=a[:2]+out
        dig=reduced(phrase)
        count_plain+=1
        hits_plain+=dig==target
        plant_plain+=dig==tgt_plant_plain
        for gap in range(23):
            phrase_room=phrase[:gap]+['room']+phrase[gap:]
            dig=reduced(phrase_room)
            count_room+=1
            hits_room+=dig==target
            plant_room+=dig==tgt_plant_room
    assert count_plain==math.comb(20,9)==167960
    assert count_room==23*count_plain==3863080
    assert plant_plain==plant_room==1
    print(json.dumps({
        'model':'full_N01_P20_minimal_two_strand_SCS_plus_optional_one_source_ROOM',
        'source_sha':'PASS','P20_SHA':'PASS','N02_HMAC16':'PASS',
        'plain_complete_unique':count_plain,'plus_room_complete_unique':count_room,
        'total_complete_unique':count_plain+count_room,
        'original_hits':hits_plain+hits_room,
        'planted_plain_hits':plant_plain,'planted_room_hits':plant_room
    },sort_keys=True))
if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('Usage: python SCRIPT extracted-original-archive-root')
    main(sys.argv[1])
