#!/usr/bin/env python3
"""Positive/negative controls for H17 direct original coupon and caption intake."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import h17_verified_manual_intake as cli

ROOT=Path(__file__).resolve().parents[2]
if not (ROOT/'resources'/'acceptance.json').is_file():
    ROOT=Path('/mnt/data/h17source')

def main():
    acc,rt,base,verify=cli.paths(ROOT)
    targets=json.loads(acc.read_text());route=json.loads(rt.read_text());prior=json.loads(base.read_text())
    coupon='7B68DAAA4C2AE2D6A2C042B921315267'
    caption='The sea waits by the window until the night is over.'
    k4,k8,normalized=cli.manual_components(coupon,caption,route)
    assert normalized=='the sea waits by the window until the night is over'
    assert hashlib.sha256(bytes.fromhex(k4)).hexdigest()!=targets['slot_sha256']['K04']
    assert hashlib.sha256(bytes.fromhex(k8)).hexdigest()!=targets['slot_sha256']['K08']
    complete={**prior,'K04':k4,'K08':k8}
    synthetic=dict(targets)
    synthetic['slot_sha256']=dict(targets['slot_sha256'])
    for name,value in (('K04',k4),('K08',k8)):
        synthetic['slot_sha256'][name]=hashlib.sha256(bytes.fromhex(value)).hexdigest()
    material=synthetic['combined_prefix']+''.join(complete[f'K{i:02d}']+'\n' for i in range(1,9))
    synthetic['combined_sha256']=hashlib.sha256(material.encode('ascii')).hexdigest()
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);(root/'evidence').mkdir()
        (root/'acceptance.json').write_text(json.dumps(synthetic))
        (root/'evidence'/'recovery-routing.json').write_text(json.dumps(route))
        (root/'candidate.json').write_text(json.dumps(prior))
        shutil.copy2(verify,root/'verify.py')
        out=root/'complete.json'
        result=cli.execute(root,coupon,caption,out,allow_synthetic_targets=True)
        assert result['accepted'] is True
        assert result['verification']['passed']==8
        assert result['verification']['combined']=='PASS'
        assert json.loads(out.read_text())==complete
        assert out.stat().st_mode & 0o777 == 0o600
        rawcoupon=root/'coupon.bin';rawcoupon.write_bytes(bytes.fromhex(coupon))
        asciihex=root/'coupon.txt';asciihex.write_text(coupon+'\n')
        phrase_file=root/'caption.txt';phrase_file.write_text(caption+'\n')
        assert cli.read_coupon(rawcoupon)==coupon
        assert cli.read_coupon(asciihex)==coupon
        assert cli.read_caption(phrase_file).strip()==caption
        try:cli.execute(root,coupon,caption,out,allow_synthetic_targets=True)
        except FileExistsError:pass
        else:raise AssertionError('Must not overwrite existing accepted key')
        badout=root/'bad.json'
        bad=cli.execute(root,'00'*16,caption,badout,allow_synthetic_targets=True)
        assert not bad['accepted'] and bad['verification']['slots']['K04']=='NO_MATCH'
        assert not badout.exists()
        # Synthetic targets must be explicitly opted in to by internal test.
        try:cli.execute(root,coupon,caption,None)
        except ValueError as exc: assert 'acceptance has changed' in str(exc)
        else:raise AssertionError('Must reject altered commitments by default')
    original=cli.execute(ROOT,'A9A9DC5731A5E2AE879C47215C2559D5',
        'The sea looks different when you have finally finished your tea',None)
    assert not original['accepted'] and original['verification']['passed']==6
    assert original['verification']['slots']['K04']=='NO_MATCH'
    assert original['verification']['slots']['K08']=='NO_MATCH'
    for bad_hex in ('1234','XX'*16,''):
        try:cli.manual_components(bad_hex,'test',route)
        except ValueError:pass
        else:raise AssertionError('invalid coupon accepted')
    for text in ('', '  < > :::'):
        try:cli.manual_components(coupon,text,route)
        except ValueError:pass
        else:raise AssertionError('invalid caption accepted')
    print('PASS: synthetic 8/8 plus combined; original 6/8; refusals; no overwrite; blank/invalid inputs')

if __name__=='__main__':
    main()
