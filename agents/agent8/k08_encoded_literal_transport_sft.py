"""H17 K08 encoded literal carrier: six textual encodings in original evidence."""
import base64
import hashlib
import hmac
import html
import quopri
import re
import sys
import urllib.parse
from pathlib import Path

NONCE = bytes.fromhex('5F933DA6A1BD03C32DA5CBC25344F497')
TARGET = bytes.fromhex('285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747')
NOTE_HASH = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
N02_HMAC = bytes.fromhex('BF889359B0303F2B2B2FD96AE841210B')

PATTERNS = {
    'hex': re.compile(rb'(?<![0-9A-Fa-f])[0-9A-Fa-f]{32,}(?![0-9A-Fa-f])'),
    'base64': re.compile(rb'(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{24,}={0,2}(?![A-Za-z0-9+/])'),
    'unicode': re.compile(rb'(?:\\u[0-9A-Fa-f]{4}){16,}'),
    'percent': re.compile(rb'(?:[A-Za-z0-9_%-]|%[0-9A-Fa-f]{2}){20,}'),
    'entity': re.compile(rb'(?:&#(?:x[0-9A-Fa-f]{1,6}|[0-9]{1,7});|&[A-Za-z]{2,10};|[A-Za-z0-9 ,.;:!?-]){20,}'),
    'qp': re.compile(rb'(?:=[0-9A-Fa-f]{2}|=\r?\n|[A-Za-z0-9_=-]){20,}'),
}

def norm(text):
    return ' '.join(''.join(c.lower() if c.isascii() and c.isalnum() else ' ' for c in text).split())

def comp(phrase):
    return hmac.new(NONCE, norm(phrase).encode('utf-8'), hashlib.sha256).digest()[:16]

def candidates(text):
    words=norm(text).split()
    for i in range(len(words)):
        for j in range(i+2,min(len(words)+1,i+33)):
            yield ' '.join(words[i:j])

def printable(buf):
    if len(buf)<16 or not all(b in (9,10,13) or 32<=b<=126 for b in buf):
        return ''
    return buf.decode('ascii')

def decode(kind,data):
    if kind=='hex':
        if len(data)%2:return ''
        try:return printable(bytes.fromhex(data.decode('ascii')))
        except ValueError:return ''
    if kind=='base64':
        try:return printable(base64.b64decode(data,validate=True))
        except ValueError:return ''
    if kind=='unicode':
        return printable(bytes(int(data[i+2:i+6],16) for i in range(0,len(data),6))) if all(int(data[i+2:i+6],16)<128 for i in range(0,len(data),6)) else ''
    if kind=='percent':
        if len(re.findall(rb'%[0-9A-Fa-f]{2}',data))<3:return ''
        return printable(urllib.parse.unquote_to_bytes(data.decode('ascii')))
    if kind=='entity':
        if len(re.findall(rb'&(?:#[A-Za-z0-9]+|[A-Za-z]+);',data))<3:return ''
        return printable(html.unescape(data.decode('ascii')).encode('utf-8'))
    if kind=='qp':
        if len(re.findall(rb'=[0-9A-Fa-f]{2}',data))<3:return ''
        return printable(quopri.decodestring(data))
    raise ValueError(kind)

def scan(buf,target):
    runs=[]; hits=[]; seen=set(); checked=0
    for kind,pat in PATTERNS.items():
        for m in pat.finditer(buf):
            text=decode(kind,m.group())
            if not text:continue
            runs.append((kind,m.start(),len(text),text[:100]))
            for phrase in candidates(text):
                if phrase in seen:continue
                seen.add(phrase);checked+=1
                if hashlib.sha256(comp(phrase)).digest()==target:
                    hits.append((kind,m.start(),phrase))
    return runs,checked,hits

def main(root):
    assert hashlib.sha256((root/'crew/noticeboard-and-desk-notes.txt').read_bytes()).hexdigest()==NOTE_HASH
    assert comp('A good watch leaves the room ready for the next pair of hands.')==N02_HMAC
    synth='The sea waited at the window and we saved one more place at the table'
    planted=hashlib.sha256(comp(synth)).digest()
    forms={
        'hex':synth.encode().hex().encode(),
        'base64':base64.b64encode(synth.encode()),
        'unicode':(''.join(f'\\u{ord(c):04x}' for c in synth)).encode(),
        'percent':urllib.parse.quote(synth,safe='').encode(),
        'entity':(''.join(f'&#{ord(c)};' for c in synth)).encode(),
        'qp':quopri.encodestring(synth.encode(),quotetabs=True),
    }
    for kind,encoded in forms.items():
        runs,checked,hits=scan(b'\xff\xff '+encoded+b' \xff\xff',planted)
        assert any(h[0]==kind and h[2]==norm(synth) for h in hits),(kind,runs,hits)
    files=sorted(p for p in root.rglob('*') if p.is_file())
    runs=[];checks=0;hits=[]
    for f in files:
        r,n,h=scan(f.read_bytes(),TARGET)
        runs.extend((f.relative_to(root).as_posix(),)+i for i in r)
        checks+=n
        hits.extend((f.relative_to(root).as_posix(),)+i for i in h)
    print('ORIGINAL_FILES',len(files),'PRINTABLE_DECODED_RUNS',len(runs),'COMPLETE_PHRASE_CHECKS',checks,
          'ORIGINAL_K08_MATCHES',len(hits),'SYNTHETIC_CONTROLS',len(forms))
    for row in runs[:100]:print('ORIGINAL_DECODED',repr(row))
    for row in hits:print('ORIGINAL_ACCEPTED',repr(row))
    return 0

if __name__=='__main__':
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv)>1 else Path('resources/evidence')))
