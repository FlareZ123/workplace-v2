"""K08 cross-record model: eight AX-7782 final checkpoints index eight Emily notes.

Original authoring relationship is unproved. There are 80,640 frozen assignments
across exact chunk/author note correspondence, two endian views, and one
permutation of the eight checkpoint selectors; no arbitrary prose generator.
Run: python agents/agent12/k08_ax7782_eight_emily_index_sft.py
"""
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

RESOURCE = Path(__file__).resolve().parents[2] / 'resources'
NOTE_SHA = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
AUDIT_SHA = '32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf'


def source():
    note_raw = (RESOURCE / 'evidence/crew/noticeboard-and-desk-notes.txt').read_bytes()
    audit_raw = (RESOURCE / 'evidence/transfers/transfer-audit.jsonl').read_bytes()
    assert hashlib.sha256(note_raw).hexdigest() == NOTE_SHA
    assert hashlib.sha256(audit_raw).hexdigest() == AUDIT_SHA
    notes = [
        (note, re.findall(r'[a-z0-9]+', body.lower()))
        for note, author, body in re.findall(
            r'(N\d\d) / ([^\n]+)\n([^\n]+)', note_raw.decode('utf-8')
        ) if author.startswith('Emily')
    ]
    assert [name for name, _ in notes] == [
        'N02', 'N06', 'N10', 'N13', 'N17', 'N18', 'N20', 'N23'
    ]
    chunks = {}
    for line in audit_raw.splitlines():
        row = json.loads(line)
        if row.get('kind') == 'CHUNK' and row.get('transfer') == 'AX-7782':
            idx = row['seq']
            if idx not in chunks or row['attempt'] > chunks[idx]['attempt']:
                chunks[idx] = row
    assert sorted(chunks) == list(range(8))
    assert all(re.fullmatch('[0-9A-F]{4}', chunks[i]['checkpoint']) for i in range(8))
    return notes, [bytes.fromhex(chunks[i]['checkpoint']) for i in range(8)]


def component(phrase, nonce):
    return hmac.new(nonce, phrase.encode('utf-8'), hashlib.sha256).digest()[:16]


def main():
    notes, checkpoint_bytes = source()
    route = json.loads((RESOURCE / 'evidence/recovery-routing.json').read_text())
    targets = json.loads((RESOURCE / 'acceptance.json').read_text())
    nonce = bytes.fromhex(route['K08']['desk_nonce'])
    target = targets['slot_sha256']['K08']
    assert component('a good watch leaves the room ready for the next pair of hands', nonce).hex().upper() == 'BF889359B0303F2B2B2FD96AE841210B'
    counts = {'original_hits': 0, 'planted_hits': 0, 'assignments': 0}
    phrases = set()
    first = [int.from_bytes(v, 'big') for v in checkpoint_bytes]
    selected_phrase = ' '.join(notes[i][1][v % len(notes[i][1])] for i, v in enumerate(first))
    planted_target = hashlib.sha256(component(selected_phrase, nonce)).hexdigest()

    for endian in ('big', 'little'):
        selectors = [int.from_bytes(b, endian) for b in checkpoint_bytes]
        for perm in itertools.permutations(range(8)):
            phrase = ' '.join(
                notes[i][1][selectors[j] % len(notes[i][1])]
                for i, j in enumerate(perm)
            )
            digest = hashlib.sha256(component(phrase, nonce)).hexdigest()
            counts['assignments'] += 1
            phrases.add(phrase)
            counts['original_hits'] += digest == target
            counts['planted_hits'] += digest == planted_target
    assert counts == {
        'original_hits': 0,
        'planted_hits': 1,
        'assignments': 80640,
    }, counts
    assert len(phrases) == 64041, len(phrases)
    print('K08 AX checkpoint to note word indexing:')
    print('canonical output:', selected_phrase)
    print('assignments=80640 distinct_phrases=64041 original_hits=0 planted_hits=1')
    print('K08 original component: UNRECOVERED')


if __name__ == '__main__':
    main()
