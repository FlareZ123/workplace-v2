#!/usr/bin/env python3
"""Source-safe, confidential SAT bucket ledger and exact UNKNOWN-only retry selector.

A successful proof of UNSAT within a fixed firstpacket P12 cube is reusable;
a timeout/partial model budget is *not*. This preserves branch identities in
private chmod0600 local files, never the public Git repository or CI output.
The ledger records only solver dispositions, not recovery material.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import stat

MODEL_ID = 'xoroshiro128pp-1.0-firstpair-P12-modelblock'


def validate_private_path(path: Path, repository_root: Path, must_exist: bool=False)->Path:
    """Fail closed for public repository paths, symlinks and weak permissions."""
    path=Path(path)
    if path.is_symlink():raise ValueError('Refusing symlink as private ledger path')
    resolved=path.resolve()
    root=Path(repository_root).resolve()
    if resolved==root or root in resolved.parents:
        raise ValueError('Private ledger must reside outside the Git repository')
    if not resolved.parent.is_dir():
        raise ValueError('Private ledger parent directory must exist')
    if must_exist:
        if not resolved.is_file():raise FileNotFoundError(resolved)
        if stat.S_IMODE(resolved.stat().st_mode) & 0o077:
            raise PermissionError('Private ledger has group/other permissions')
    return resolved


def append_record(path:Path,record:dict)->None:
    """Durable per-bucket dispositions with private file permissions."""
    if record.get('terminal') not in ('unsat','unknown'):
        raise ValueError('Cannot record SAT without terminal closure')
    if record.get('model_id') != MODEL_ID:
        raise ValueError('Model fingerprint mismatch')
    flags=os.O_CREAT|os.O_APPEND|os.O_WRONLY|getattr(os,'O_NOFOLLOW',0)
    fd=os.open(path,flags,0o600)
    with os.fdopen(fd,'a',encoding='utf-8') as handle:
        os.fchmod(handle.fileno(),0o600)
        handle.write(json.dumps(record,sort_keys=True,separators=(',',':'))+'\n')
        handle.flush();os.fsync(handle.fileno())


def unknown_buckets(path:Path,source_sha256:str,layout:str,start:int,stop:int)->list[int]:
    """Retry only cubes lacking any exact UNSAT certificate for same model.

    Records from other original sources or serializers are ignored, and once
    UNSAT is logged a later shorter UNKNOWN cannot negate that certificate.
    Not logging a cube is *not* proof of its status; this function explicitly
    returns only previously observed UNKNOWN cubes, not never-visited cubes.
    """
    states:dict[int,str]={}
    with Path(path).open('r',encoding='utf-8') as infile:
        for lineno,line in enumerate(infile,1):
            if not line.strip():continue
            row=json.loads(line)
            if (row.get('model_id')!=MODEL_ID or
                row.get('source_sha256')!=source_sha256 or
                row.get('layout')!=layout):
                continue
            idx=row.get('bucket')
            if not isinstance(idx,int) or isinstance(idx,bool) or not start<=idx<stop:
                continue
            status=row.get('terminal')
            if status not in ('unknown','unsat'):
                raise ValueError(f'Invalid recorded terminal at line {lineno}')
            if states.get(idx)=='unsat':continue
            states[idx]=status
    return sorted(idx for idx,status in states.items() if status=='unknown')


def _selftest():
    import tempfile
    root=Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory() as tmp:
        ledger=validate_private_path(Path(tmp)/'ledger.jsonl',root)
        def put(bucket,terminal,layout='big/ab',source='a'*64):
            append_record(ledger,{'model_id':MODEL_ID,'source_sha256':source,
                    'layout':layout,'bucket':bucket,'terminal':terminal,
                    'states_examined':0,'timeout_ms':5000})
        put(2,'unknown');put(3,'unsat');put(4,'unknown')
        put(2,'unsat');put(2,'unknown')  # later timeout cannot negate proof
        put(5,'unknown',source='b'*64);put(6,'unknown',layout='little/ab')
        assert unknown_buckets(ledger,'a'*64,'big/ab',0,7)==[4]
        assert unknown_buckets(ledger,'a'*64,'big/ab',4,7)==[4]
        assert unknown_buckets(ledger,'a'*64,'big/ab',0,4)==[]
        assert stat.S_IMODE(ledger.stat().st_mode)==0o600
        try:validate_private_path(root/'my_repo_file',root)
        except ValueError:pass
        else:raise AssertionError('Public in-repo ledger path was allowed')
        try:append_record(ledger,{'model_id':MODEL_ID,'terminal':'sat'})
        except ValueError:pass
        else:raise AssertionError('SAT was treated as a closed bucket')
    print({'source_free':True,'synthetic_ledger_controls_passed':True,
           'unknown_only_retries':True,'monotonic_unsat_proof':True,
           'confidential_permissions':True,'source_bytes_used':False})

if __name__=='__main__':_selftest()
