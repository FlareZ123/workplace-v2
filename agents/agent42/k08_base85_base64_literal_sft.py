"""H-17 K08 text carrier: source-pinned Base64/Base32/Base85/Ascii85 pilot.

Use original ZIP path from environment H17_ZIP. Standard library only.
The positive controls encode the exact N17 standby inscription.
"""
import base64
import binascii
from hashlib import sha256
import hmac
import os
import re
from zipfile import ZipFile

NONCE=bytes.fromhex('5F933DA6A1BD03C32DA5CBC25344F497')
TARGET=bytes.fromhex('285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747')
EXP={'b64':rb'[A-Za-z0-9+/=_-]{24,}',
     'b32':rb'[A-Z2-7=]{24,}',
     'b85':rb'[!-~]{25,}',
     'a85':rb'[!-u]{25,}'}


def parse(stream,kind):
    outputs=set()
    width={'b64':4,'b32':8,'b85':5,'a85':5}[kind]
    for offset in range(width):
        data=stream[offset:]
        if len(data)<24:continue
        if kind=='b64':
            data=data[:len(data)//4*4]
            for decoder in (lambda x:base64.b64decode(x,validate=True),
                            base64.urlsafe_b64decode):
                try:outputs.add(decoder(data))
                except (ValueError,binascii.Error):pass
        elif kind=='b32':
            data=data[:len(data)//8*8]
            try:outputs.add(base64.b32decode(data,casefold=True))
            except (ValueError,binascii.Error):pass
        elif kind=='b85':
            try:outputs.add(base64.b85decode(data))
            except (ValueError,OverflowError,binascii.Error):pass
        else:
            try:outputs.add(base64.a85decode(data,adobe=False))
            except (ValueError,OverflowError,binascii.Error):pass
    return outputs


def candidates(blob):
    result=set()
    for region in re.finditer(rb'[\t\r\n\x20-\x7e]{14,}',blob):
        words=re.findall(rb'[a-z0-9]+',region.group().lower())
        for start in range(len(words)):
            for end in range(start+2,min(start+24,len(words))+1):
                text=b' '.join(words[start:end])
                if len(text)>=14:result.add(text)
    return result


def recover(blob):
    stats={}
    phrases=set()
    for kind,expr in EXP.items():
        runs=list(re.finditer(expr,blob))
        decoded=set()
        for run in runs:decoded.update(parse(run.group(),kind))
        stats[kind]=(len(runs),len(decoded))
        for source in decoded:phrases.update(candidates(source))
    return stats,phrases


def main():
    with ZipFile(os.environ.get('H17_ZIP','h17-archive-dump.zip')) as z:
        assert sha256(z.read('evidence/crew/noticeboard-and-desk-notes.txt')).hexdigest()=='13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
        sources=[z.read(n) for n in z.namelist() if n.startswith('evidence/') and not n.endswith('/')]
    known=b'leave the light on for the next watch'
    for encode in (base64.b64encode,base64.b85encode,base64.a85encode):
        _,positive=recover(b' '+encode(known)+b' ')
        assert known in positive,(encode.__name__,positive)
    all_phrases=set()
    total={k:[0,0] for k in EXP}
    for blob in sources:
        counts,found=recover(blob)
        all_phrases.update(found)
        for kind,(runs,decoded) in counts.items():
            total[kind][0]+=runs
            total[kind][1]+=decoded
    hits=[text for text in all_phrases if sha256(hmac.new(NONCE,text,'sha256').digest()[:16]).digest()==TARGET]
    print('synthetic_controls PASS 3', 'evidence_files',len(sources))
    print('kind_run_decode_counts',total)
    print('complete_normalized_candidates',len(all_phrases),'original_K08_hits',len(hits))
    assert not hits and len(all_phrases)==0
if __name__=='__main__':main()
