#!/usr/bin/env python3
"""Detect nonstandard ZIP DEFLATE choices and variable metadata without opening PDF.

Original local archive only, no public CI original-source run. Counts only.
Check full compressed bytes against canonical zlib raw deflate levels1..9;
no high-risk PDF content (raw/decompressed) is opened or interpreted.
"""
import argparse, collections, json, os, struct, zipfile, zlib
from pathlib import Path

def check(source):
    hist=collections.Counter();method=collections.Counter();extras=collections.Counter()
    comments=collections.Counter();times=collections.Counter();sequence=[];nonstandard=[];files=0
    with zipfile.ZipFile(source) as zin, source.open('rb') as fh:
        archive_comment_len=len(zin.comment)
        for i in zin.infolist():
            if i.is_dir() or i.filename.lower().endswith('.pdf'):
                continue
            fh.seek(i.header_offset)
            hdr=fh.read(30)
            assert len(hdr)==30 and hdr[:4]==b'PK\x03\x04'
            filename_len,extra_len=struct.unpack_from('<HH',hdr,26)
            fh.seek(i.header_offset+30+filename_len+extra_len)
            compressed=fh.read(i.compress_size)
            text=zin.read(i)
            files+=1
            method[i.compress_type]+=1;extras[i.extra]+=1
            comments[len(i.comment)]+=1;times[i.date_time]+=1
            sequence.append((i.filename,i.date_time))
            if i.compress_type!=8:
                nonstandard.append(i.filename)
                continue
            levels=[]
            for level in range(1,10):
                enc=zlib.compressobj(level,zlib.DEFLATED,-15)
                other=enc.compress(text)+enc.flush()
                if other==compressed:levels.append(level)
            hist[tuple(levels)]+=1
            if 6 not in levels:nonstandard.append(i.filename)
    # Only one mail-vs-nonmail timing distinction, not 45 independent bits.
    classes=collections.defaultdict(set)
    for name,stamp in sequence:
        cls='mail-message' if name.startswith('evidence/mail/') and name.endswith('.eml') else 'other'
        classes[cls].add(stamp)
    return {'original_permitted_files':files,'deflate_files':method[8],
        'standard_level6_exact':sum(n for k,n in hist.items() if 6 in k),
        'nonstandard':len(nonstandard), 'zip_comment_bytes':archive_comment_len,
        'unique_extra_fields':len(extras),'unique_perfile_comments':len(comments),
        'distinct_file_timestamps':len(times),
        'mail_timestamps':len(classes['mail-message']),
        'nonmail_timestamps':len(classes['other']),
        'timestamp_assignments_only_by_mail_class':bool(classes['mail-message'].isdisjoint(classes['other'])),
        'restricted_PDF_processed':False}

def controls():
    data=(b'ABCD'*500)+(bytes(range(256))*3)
    canonical=zlib.compressobj(6,zlib.DEFLATED,-15)
    standard=canonical.compress(data)+canonical.flush()
    alternate=zlib.compressobj(6,zlib.DEFLATED,-15,zlib.DEF_MEM_LEVEL,zlib.Z_HUFFMAN_ONLY)
    different=alternate.compress(data)+alternate.flush()
    assert standard!=different
    assert zlib.decompress(standard,-15)==zlib.decompress(different,-15)==data
    print('SYNTHETIC_PASS '+json.dumps({'same_plaintext_different_deflate_detected':True}))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path)
    a=ap.parse_args();controls()
    if a.archive:
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            ap.error('original ZIP processing prohibited in CI')
        r=check(a.archive)
        print('AGGREGATE_ONLY '+json.dumps(r,sort_keys=True))
if __name__=='__main__':main()
