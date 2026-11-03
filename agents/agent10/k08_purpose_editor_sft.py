"""Retrospective purpose-conditioned K08 envelope editor; read-only original sources."""
from collections import Counter
from hashlib import sha256
from hmac import digest as hmac_digest
from itertools import product
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[2] / 'resources'
NOTES_PATH = ROOT / 'evidence/crew/noticeboard-and-desk-notes.txt'
NOTES_SHA = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
assert sha256(NOTES_PATH.read_bytes()).hexdigest() == NOTES_SHA

def norm(s):
    return ' '.join(re.sub(r'[^a-z0-9\s]', ' ', s.lower()).split())

notes = {int(k):v for k,v in re.findall(
    r'^N(\d\d) / [^\n]*\n([^\n]+)', NOTES_PATH.read_text(), re.M)}
assert len(notes)==24
controls = {'standby':norm(notes[17].split(': ',1)[1]),
            'commissioning':norm(notes[18].split(': ',1)[1])}
redacted=[]
for p in [NOTES_PATH, *sorted((ROOT/'evidence/mail').glob('*.eml'))]:
    txt=p.read_text()
    for original in (notes[17].split(': ',1)[1],notes[18].split(': ',1)[1]):
        txt=re.sub(re.escape(original.rstrip('.'))+r'\.?','[REDACTED]',txt,flags=re.I)
    assert all(t not in norm(txt) for t in controls.values())
    redacted.append(txt)
ACT=('leave','keep','put','hold','save','make','set','remember','wait for','give')
OBJECT=('light','lamp','room','table','chair','seat','cup','mug','door','window','place','tea','last cup','little lamp')
STATE=('on','open','ready','warm','waiting','by the window','at the table','near the window','where it belongs','for whoever comes next')
RECIPIENT=('next watch','last watch','night crew','next pair of hands','people coming after','people coming in','one more','each other','us','someone else')
RETURN=('back','here','home','still here','come back','come home','together','all together','stay','stay awhile')
REL=('before','after','by','until')
ORDINAL=('first','last','next','early','late')
EVENT=('boat','watch','light','morning','crossing','cup','shift','sunrise','night')
SCENE=('the sea waits outside','the sea is outside','the sea beyond the window','the sea is still there',
       'the water waits outside','the water is turning light','the night is almost over','the last of the night fades',
       'the little lamp stays on','the mugs wait by the window','the last cup is on the table','the voices are at the table',
       'the night has nearly finished','the light comes back over the sea')
PEOPLE=('there is room for one more','there is room for the next watch','we make room for each other',
        'there is always room at the table','leave room at the table','we have left a place at the table',
        'someone has kept a place','someone stays until the last cup','there is room for whoever comes next',
        'the next watch will find a place','the mugs are waiting for the next watch')
TIME=('at the end of the night','when morning comes','after the last cup','after a long watch',
      'before the next watch','as the sea turns light','when the water turns light','until morning')
CONJ=('and','while','as','when','but')
CONTEXT={'standby':[2,6,7,12,13], 'commissioning':[5,14,15,24],
         'keeper':[1,2,6,9,10,11,13,19,20,23]}
# This optional assisted mode intentionally includes words from the known labels.
# It is a hindsight upper bound, not an unbiased predictor.
HINTS={'standby':'watch ready next on lamp lights light leave standby duty',
       'commissioning':'boat first crossing before back sunrise start commissioning depart',
       'keeper':'sea water night voices table mugs cup room each other late watch last lamp window'}
MORPH={'light':'lights','place':'places','mug':'mugs','seat':'seats','boat':'boats','watch':'watches'}
DOCS=[norm(t) for t in redacted]
TOKENS=Counter(w for t in DOCS for w in t.split())
BIGRAMS=Counter(p for t in DOCS for p in zip(t.split(),t.split()[1:]))

def candidates():
    for a,o,s,r in product(ACT,OBJECT,STATE,RECIPIENT):
        yield f'{a} the {o} {s} for the {r}'
        yield f'{a} the {o} {s}'
    for b,rel,ord_,ev in product(RETURN,REL,ORDINAL,EVENT):
        yield f'{b} {rel} the {ord_} {ev}'
        yield f'{b} {rel} {ord_} {ev}'
    for scene,people,conj in product(SCENE,PEOPLE,CONJ):
        yield f'{scene} {conj} {people}'
        yield f'{people} {conj} {scene}'
    for people,t in product(PEOPLE,TIME):
        yield f'{people} {t}'
        yield f'{t} {people}'
    for a,o,t in product(ACT,OBJECT,TIME):
        yield f'{a} the {o} {t}'

def score(s,purpose,assisted=False):
    words=s.split()
    context=norm(' '.join(notes[n] for n in CONTEXT[purpose])+
                 (' '+HINTS[purpose] if assisted else ''))
    ctx=Counter(context.split())
    topical=sum(min(ctx[w],2)*1.1 for w in set(words) if len(w)>2)
    unseen=sum(.6 if w in MORPH and MORPH[w] in TOKENS else 1.5
               for w in set(words) if w not in TOKENS)
    bigram=sum(.05 if BIGRAMS[(a,b)] else 0 for a,b in zip(words,words[1:]))
    mid=8 if purpose!='keeper' else 14
    length=abs(len(words)-mid)*.23
    genre=(.0 if len(words)>=9 else 1.2) if purpose=='keeper' else (.0 if len(words)<=11 else .8)
    return round(length+genre+unseen-topical-bigram,5)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assisted',action='store_true')
    assisted=parser.parse_args().assisted
    unique=set(map(norm,candidates()))
    assert len(unique)==21836
    routing=json.loads((ROOT/'evidence/recovery-routing.json').read_text())
    acceptance=json.loads((ROOT/'acceptance.json').read_text())
    nonce=bytes.fromhex(routing['K08']['desk_nonce'])
    want=bytes.fromhex(acceptance['slot_sha256']['K08'])
    def component(s): return hmac_digest(nonce,s.encode('utf-8'),'sha256')[:16]
    assert component(norm(notes[2].split(': ',1)[1])).hex().upper()=='BF889359B0303F2B2B2FD96AE841210B'
    plant='back before the first cup'
    assert plant in unique
    plant_digest=sha256(component(plant)).digest()
    assert sum(sha256(component(s)).digest()==plant_digest for s in unique)==1
    ranks={}
    tops={}
    for purpose in CONTEXT:
        ordered=sorted(unique,key=lambda s:(score(s,purpose,assisted),s))
        ranks[purpose]={s:i+1 for i,s in enumerate(ordered)}
        tops[purpose]=set(ordered[:1000])
    outputs={}
    for purpose in controls:
        phrase=controls[purpose]
        outputs[purpose]={'normalized_label':phrase,'rank':ranks[purpose].get(phrase),
            'wrong_purpose_ranks':{p:ranks[p].get(phrase) for p in CONTEXT if p!=purpose}}
    hit=None
    for s in ranks['keeper']:
        k=component(s)
        if sha256(k).digest()==want: hit={'phrase':s,'component':k.hex().upper()}
    outputs['keeper']={'checked':len(unique),'hit':hit}
    outputs['meta']={'source_sha256':NOTES_SHA,'candidates':len(unique),
      'assisted_hindsight_words':assisted,'synthetic_positive':plant,
      'top1000_intersections':{f'{a}/{b}':len(tops[a]&tops[b])
          for a,b in [('standby','commissioning'),('standby','keeper'),('commissioning','keeper')]}}
    print(json.dumps(outputs,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
