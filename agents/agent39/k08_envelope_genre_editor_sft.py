"""Source-masked K08 same-genre inscription editor.
Reconstruct both excluded historical envelope labels before querying final K08.
"""
from collections import Counter
from hashlib import sha256
from hmac import new as hmac_new
from itertools import product
from pathlib import Path
import json
import os
import re

ROOT = Path(os.environ.get('H17_RESOURCES_ROOT',
                           Path(__file__).resolve().parents[2] / 'resources'))
NOTE_SHA = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
ROUTE_SHA = 'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5'
ACCEPT_SHA = '681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'
CONTROLS = ('leave the light on for the next watch',
            'back before the first boat')
VERB = ('leave', 'make', 'keep', 'save', 'hold', 'put', 'let', 'bring',
        'count', 'give', 'remember', 'find', 'stay', 'sit')
OBJECT = ('room', 'a room', 'the room', 'a place', 'one more place',
          'a cup', 'the first cup', 'one more cup', 'a mug', 'the mugs',
          'the little lamp', 'the light', 'a light', 'a little light',
          'the window', 'the table', 'the good chair', 'the next watch',
          'the next pair of hands', 'a place for the next watch')
PLACE = ('', 'on', 'at the table', 'by the window', 'beside the window',
         'in the room', 'for each other', 'for one another',
         'for the next pair of hands', 'for the incoming watch',
         'with the sea outside', 'with the water outside',
         'where the voices meet', 'where the mugs stand',
         'for the next watch', 'for the late crew')
TIME = ('', 'for the next watch', 'before the first boat',
        'at the end of the night', 'after the last cup',
        'after a long watch', 'after the long watch',
        'until the night is over', 'until the night ends',
        'when the night is almost over', 'when the night is done',
        'as the night ends', 'before daylight', 'as daylight comes',
        'while the sea is outside', 'while the water is outside',
        'when the sea is outside', 'when the water is outside',
        'when the voices are at the table',
        'while the voices are at the table')
ADVERB = ('back', 'here', 'home', 'again', 'together', 'always')
PREP = ('before', 'after', 'until', 'with', 'by', 'beside', 'at')
FRAGMENT = ('the first boat', 'the next watch', 'the last cup',
            'the night', 'the little lamp', 'the sea', 'the water',
            'the window', 'the room', 'the table', 'the voices')
SUBJECT = ('we', 'somebody', 'the next watch', 'the late crew',
           'the sea', 'the water', 'the mugs', 'the voices',
           'the little lamp', 'the room')
FINITE = ('stays', 'leaves', 'gives', 'makes', 'keeps', 'holds',
          'remembers', 'waits', 'is', 'comes', 'belongs', 'turns', 'looks')

def norm(s: str) -> str:
    return ' '.join(re.findall(r'[a-z0-9]+', s.lower()))

def phrase_pool():
    # Retrospective grammar; known control inscriptions are assembled by slots.
    for v, obj, place, when in product(VERB, OBJECT, PLACE, TIME):
        yield ' '.join((v, obj, place, when))
        yield ' '.join((when, v, obj, place))
    for adv, prep, obj in product(ADVERB, PREP, FRAGMENT):
        yield ' '.join((adv, prep, obj))
    for subject, verb, obj, place in product(SUBJECT, FINITE, OBJECT, PLACE):
        yield ' '.join((subject, verb, obj, place))
    for subject, verb, place, when in product(SUBJECT, FINITE, PLACE, TIME):
        yield ' '.join((subject, verb, place, when))

def has_themes(s: str) -> bool:
    w = set(s.split())
    return (bool(w & {'sea','water'})
            and bool(w & {'night','watch','daylight','boat'})
            and bool(w & {'room','table','voices','mugs','cup','hands','lamp',
                          'light','chair','place','window'}))

def main():
    note = (ROOT / 'evidence/crew/noticeboard-and-desk-notes.txt').read_bytes()
    route_raw = (ROOT / 'evidence/recovery-routing.json').read_bytes()
    accept_raw = (ROOT / 'acceptance.json').read_bytes()
    assert sha256(note).hexdigest() == NOTE_SHA
    assert sha256(route_raw).hexdigest() == ROUTE_SHA
    assert sha256(accept_raw).hexdigest() == ACCEPT_SHA
    docs = [note.decode()] + [(ROOT / f'evidence/mail/{i:02}.eml').read_text(encoding='utf-8')
                             for i in range(1,21)]
    masked = []
    hits_mask = Counter()
    for doc in docs:
        for label in CONTROLS:
            doc, n = re.subn(re.escape(label) + r'\.?', ' ', doc, flags=re.I)
            hits_mask[label] += n
        masked.append(norm(doc))
    assert all(hits_mask[c] == 2 for c in CONTROLS), hits_mask
    vocab = set(' '.join(masked).split())
    derivations = {'light': 'lights'}
    assert derivations['light'] in vocab and 'light' not in vocab
    absent = {word for pool in (VERB, OBJECT, PLACE, TIME, ADVERB, PREP,
                                FRAGMENT, SUBJECT, FINITE)
              for phrase in pool for word in norm(phrase).split()
              if word not in vocab and word not in derivations}
    print('inferred non-source words:', sorted(absent))
    nonce = bytes.fromhex(json.loads(route_raw)['K08']['desk_nonce'])
    target = json.loads(accept_raw)['slot_sha256']['K08']
    seen = set()
    total = 0
    motif_checked = 0
    source_lexicon_only = 0
    author_inference_lexicon = 0
    control_hit = {c: False for c in CONTROLS}
    original_hits = []
    planted = 'leave the light with the sea outside after a long watch'
    planted_target = sha256(hmac_new(nonce, planted.encode('utf8'), 'sha256').digest()[:16]).digest()
    planted_hits = 0
    for proposed in phrase_pool():
        s = norm(proposed)
        if s in seen:
            continue
        seen.add(s)
        total += 1
        if s in control_hit:
            control_hit[s] = True
        if not has_themes(s):
            continue
        motif_checked += 1
        source_lexicon_only += set(s.split()) <= (vocab | set(derivations))
        author_inference_lexicon += bool(set(s.split()) - vocab - set(derivations))
        raw = hmac_new(nonce, s.encode('utf8'), 'sha256').digest()[:16]
        digest = sha256(raw).digest()
        planted_hits += digest == planted_target
        if digest.hex() == target:
            original_hits.append({'caption': s, 'component': raw.hex().upper()})
    assert all(control_hit.values()), control_hit
    assert planted_hits == 1, planted_hits
    assert source_lexicon_only + author_inference_lexicon == motif_checked
    positive = 'a good watch leaves the room ready for the next pair of hands'
    assert hmac_new(nonce, positive.encode(), 'sha256').digest()[:16].hex().upper() == 'BF889359B0303F2B2B2FD96AE841210B'
    print(json.dumps({'masked_source_label_occurrences': dict(hits_mask),
                      'same_carrier_holdouts_pass': control_hit,
                      'unique_complete_generated_labels': total,
                      'theme_conditioned_sha256_hmac16_tests': motif_checked,
                      'source_vocabulary_or_singular_light_only': source_lexicon_only,
                      'includes_explicitly_inferred_vocabulary': author_inference_lexicon,
                      'source_grammar_planted_digest_positive': planted_hits,
                      'original_target_hits': original_hits}, indent=2))

if __name__ == '__main__':
    main()
