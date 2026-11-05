"""Source-conditioned K08 HMAC test: BX25/08 PDF release 8131 -> N08,N13,N01.

The source-index reading is explicitly speculative and NOT an authentic final-caption
edit instruction. This finite test checks literal contiguous fragments (2..9 words)
of the three PIN-addressed caption sentences, plus four connector choices. The
original REC8/1 evidence, nonce and target are untouched.
"""
import argparse
import hashlib
import hmac
import itertools
import re
from pathlib import Path

NOTE_SHA256 = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
NONCE = bytes.fromhex('5F933DA6A1BD03C32DA5CBC25344F497')
TARGET = bytes.fromhex('285EB6B4196D21EAF47E251449E61E0BCE28749881CCC5A065CA733B0C3FD747')
CONTROLS = {'N02': 'BF889359B0303F2B2B2FD96AE841210B'}
ANCHORS = {
    'N08': {'water', 'daylight', 'overnight', 'colors', 'borrowed'},
    'N13': {'night', 'mugs', 'window', 'lamp', 'somebody'},
    'N01': {'sea', 'tea', 'finished', 'different'},
}
JOINERS = (' ', ' and ', ' while ', ' before ')


def component(text):
    normal = ' '.join(re.sub(r'[^a-z0-9\s]', ' ', text.lower()).split())
    return hmac.new(NONCE, normal.encode('utf-8'), hashlib.sha256).digest()[:16]


def fragments(text, anchors):
    words = re.findall(r'[a-z0-9]+', text.lower())
    return sorted({
        ' '.join(words[i:j]) for i in range(len(words))
        for j in range(i + 2, min(i + 10, len(words) + 1))
        if set(words[i:j]).intersection(anchors)
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('crew_notes', type=Path, help='Untouched evidence/crew/noticeboard-and-desk-notes.txt')
    args = parser.parse_args()
    raw = args.crew_notes.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == NOTE_SHA256
    entries = dict((n, text.strip()) for n, _, text in re.findall(
        r'(N\d+) / ([^\n]*)\n(.*?)(?=\n\nN\d+ /|\Z)', raw.decode(), re.S))
    assert component(entries['N02'].split(': ', 1)[1]).hex().upper() == CONTROLS['N02']

    # Semantic label prefixes are editorial scaffolding, never caption words.
    for key in ('N08', 'N01'):
        entries[key] = entries[key].split(': ', 1)[1]
    groups = {n: fragments(entries[n], ANCHORS[n]) for n in ANCHORS}
    assert {n: len(groups[n]) for n in ('N08', 'N13', 'N01')} == {'N08': 58, 'N13': 112, 'N01': 46}
    print('NOTE_SHA256', NOTE_SHA256, 'FRAGMENTS', {n: len(groups[n]) for n in ANCHORS}, flush=True)
    # All group fragments and joiners already satisfy the exact REC8 normalizer.
    # Cache inner/outer HMAC pad states to avoid millions of per-call key setups.
    ipad = bytes((b ^ 0x36) for b in NONCE) + bytes([0x36]) * 48
    opad = bytes((b ^ 0x5c) for b in NONCE) + bytes([0x5c]) * 48
    inner0 = hashlib.sha256(ipad)
    outer0 = hashlib.sha256(opad)

    def digest_normalized(caption):
        inner = inner0.copy()
        inner.update(caption.encode('ascii'))
        outer = outer0.copy()
        outer.update(inner.digest())
        return hashlib.sha256(outer.digest()[:16]).digest()

    planted = ' '.join((groups['N08'][0], groups['N13'][0], groups['N01'][0]))
    assert digest_normalized(planted) == hashlib.sha256(component(planted)).digest()
    plant_digest = digest_normalized(planted)
    plant_hits = 0
    hits = []
    checked = 0
    for order in (('N08', 'N13', 'N01'), ('N01', 'N13', 'N08')):
        for a, b, c in itertools.product(*(groups[n] for n in order)):
            for sep1, sep2 in itertools.product(JOINERS, repeat=2):
                caption = a + sep1 + b + sep2 + c
                digest = digest_normalized(caption)
                checked += 1
                if digest == TARGET:
                    hits.append((order, caption))
                    print('ORIGINAL_TARGET_HIT', order, caption, flush=True)
                if digest == plant_digest:
                    plant_hits += 1
        print('ORDER_DONE', order, 'CHECKED', checked, 'HITS', len(hits), flush=True)
    assert checked == 2 * 58 * 112 * 46 * len(JOINERS)**2
    assert plant_hits >= 1
    print('RESULT', {'assignments': checked, 'target_hits': len(hits),
                     'planted_target_hits': plant_hits, 'original_N02_control': 'PASS'}, flush=True)


if __name__ == '__main__':
    main()
