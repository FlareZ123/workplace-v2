"""Bounded original-source K08 literal-caption/reducer-serialization falsifier.
Read-only; verify original key semantics before alternate interpretations.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sys
from email.parser import BytesParser
from email.policy import default
from zipfile import ZipFile

NOTES_SHA = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
ROUTE_SHA = 'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5'
TARGET = '285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747'
BASE_FIXTURE = 'BF889359B0303F2B2B2FD96AE841210B'


def normalize(s: str) -> str:
    return ' '.join(re.findall(r'[a-z0-9]+', s.lower()))


def candidate_texts(z: ZipFile) -> set[str]:
    note = z.read('evidence/crew/noticeboard-and-desk-notes.txt').decode()
    texts = set()
    for _, _, body in re.findall(r'^N(\d+) / (\w+)[^\n]*\n([^\n]+)', note, re.M):
        for s in (body, body.split(':', 1)[-1].strip()):
            texts.add(normalize(s))
    for i in range(1, 21):
        msg = BytesParser(policy=default).parsebytes(z.read(f'evidence/mail/{i:02d}.eml'))
        assert not msg.is_multipart()
        body = msg.get_content()
        for s in [body, *re.split(r'\n\s*\n', body), *re.split(r'(?<=[.!?])\s+', body)]:
            s = normalize(s)
            if s:
                texts.add(s)
    return texts


def main(path: str) -> None:
    with ZipFile(path) as z:
        notes = z.read('evidence/crew/noticeboard-and-desk-notes.txt')
        rawroute = z.read('evidence/recovery-routing.json')
        assert hashlib.sha256(notes).hexdigest() == NOTES_SHA
        assert hashlib.sha256(rawroute).hexdigest() == ROUTE_SHA
        route = json.loads(rawroute)
        noncehex = route['K08']['desk_nonce']
        key = bytes.fromhex(noncehex)
        texts = candidate_texts(z)
        assert len(key) == 16
        assert normalize('A good watch leaves the room ready for the next pair of hands.') in texts
    n02 = b'a good watch leaves the room ready for the next pair of hands'
    assert hmac.digest(key, n02, 'sha256')[:16].hex().upper() == BASE_FIXTURE
    key_forms = {
        'hex-decoded-original': key,
        'ascii-upper': noncehex.encode(),
        'ascii-lower': noncehex.lower().encode(),
        'ascii-0x-hex': ('0x'+noncehex).encode(),
        'byte-reversed': key[::-1],
        'word-reversed': b''.join(key[i:i+4] for i in (12,8,4,0)),
        'bytes-in-word-reversed': b''.join(key[i:i+4][::-1] for i in (0,4,8,12)),
    }
    reductions = ('hmac-sha256-first', 'hmac-sha256-last', 'hmac-sha512-first',
                  'hmac-sha512-last', 'hmac-sha1-first', 'hmac-md5',
                  'sha256-key-message', 'sha256-message-key')
    unique = set()
    original_hits = []
    count = 0
    for text in sorted(texts):
        basic = text.encode('utf-8')
        forms = (
            basic, basic+b'\n', basic+b'\r\n', basic+b'\0', basic.upper(),
            text.encode('utf-16le'), text.encode('utf-16be'),
        )
        for key_name, k in key_forms.items():
            for message_index, msg in enumerate(forms):
                for reduction in reductions:
                    if reduction.startswith('hmac'):
                        hash_name = reduction.split('-')[1]
                        digest = hmac.digest(k, msg, hash_name)
                        component = digest[-16:] if reduction.endswith('-last') else digest[:16]
                    elif reduction == 'sha256-key-message':
                        component = hashlib.sha256(k+msg).digest()[:16]
                    else:
                        component = hashlib.sha256(msg+k).digest()[:16]
                    count += 1
                    unique.add(component)
                    if hashlib.sha256(component).hexdigest() == TARGET:
                        original_hits.append((text, key_name, message_index, reduction, component.hex()))
    positive_key = key_forms['ascii-upper']
    positive_msg = (n02+b'\n')
    plant = hmac.digest(positive_key, positive_msg, 'sha512')[-16:]
    assert plant in unique
    assert hashlib.sha256(plant).hexdigest() != TARGET
    print(json.dumps({
        'original_source_control':'PASS', 'original_N02_HMAC16':'PASS',
        'candidate_normalized_literals':len(texts),
        'key_serializations':len(key_forms), 'message_serializations':7,
        'reducer_algorithms':len(reductions),
        'complete_assignments':count, 'distinct_complete_components':len(unique),
        'sorted_component_sha256':hashlib.sha256(b''.join(sorted(unique))).hexdigest(),
        'original_matches':original_hits, 'planted_full_reducer_positive':1,
    },sort_keys=True,indent=2))
    assert not original_hits


if __name__ == '__main__':
    main(sys.argv[1])
