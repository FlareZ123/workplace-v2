#!/usr/bin/env python3
"""Source-free model ledger for repeatable K04 coupon reduction.

Original-source use: only in a local mode0700 root outside the Git repository,
never in public CI; store full first-packet SAT states locally, not in GitHub.
This test uses synthetic words only and makes no historical K04 claim.
"""
from __future__ import annotations
import hashlib, json, os, secrets, stat, tempfile
from pathlib import Path

M = (1 << 64) - 1
ROOT = Path(__file__).resolve().parents[2]
P12 = (0, 1, 2, 3, 22, 23, 24, 25, 45, 46, 47, 48)


def rot(x, n): return ((x << n) | (x >> (64 - n))) & M


def stream(a, b, length):
    out = []
    for _ in range(length):
        out.append((rot((a + b) & M, 17) + a) & M)
        t = a ^ b
        a, b = rot(a, 49) ^ t ^ ((t << 21) & M), rot(t, 28)
    return out


def _secure_dir(root):
    root = Path(root).expanduser()
    # Neither the private ledger nor its path components may be a symlink.
    if any(part.is_symlink() for part in (root, *root.parents)):
        raise ValueError('Symlink in private ledger root')
    rp = root.resolve(strict=True)
    if rp == ROOT or ROOT in rp.parents or not rp.is_dir():
        raise ValueError('Private ledger must be an existing directory outside the repo')
    if stat.S_IMODE(rp.stat().st_mode) & 0o077:
        raise PermissionError('Private ledger root must deny group/other access')
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        raise RuntimeError('No private states in public CI')
    return rp


def namespace(meta):
    """Source-free fingerprint: binding to source, serializer, circuit and mask.

    The caller must provide source SHA256 and firstpacket SHA256, rather than
    original source values. The fingerprint is itself not a recovery key.
    """
    required = {'source_sha256', 'firstpair_sha256', 'serializer',
                'circuit_sha256', 'generator', 'P12'}
    if set(meta) != required:
        raise ValueError('Exactly the frozen namespace fields are required')
    for key in ('source_sha256', 'firstpair_sha256', 'circuit_sha256'):
        if len(meta[key]) != 64 or any(c not in '0123456789abcdef' for c in meta[key]):
            raise ValueError('Malformed SHA256 namespace input')
    if meta['serializer'] not in ('big/ab', 'big/ba', 'little/ab', 'little/ba'):
        raise ValueError('Unknown serializer')
    if tuple(meta['P12']) != P12 or meta['generator'] != 'xoroshiro128++ 1.0':
        raise ValueError('Unknown exact producer/anchor mask')
    return hashlib.sha256(json.dumps(meta, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _attempt_files(root, ns, cube):
    return sorted(root.glob(f'{ns}_{cube:04d}_*.json'))


def read_cube(root, meta, cube):
    root = _secure_dir(root)
    if cube not in range(4096): raise ValueError('Invalid P12 cube')
    ns = namespace(meta)
    all_states, sealed = set(), False
    attempts = 0
    for path in _attempt_files(root, ns, cube):
        if path.is_symlink() or stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise PermissionError('Insecure private attempt file')
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
        with os.fdopen(fd, 'r', encoding='ascii') as f:
            d = json.load(f)
        if d['namespace'] != ns or d['cube'] != cube:
            raise ValueError('Ledger entry does not belong to this source/circuit')
        if d['terminal'] not in ('unsat', 'unknown', 'model-limit'):
            raise ValueError('Invalid solver disposition')
        attempt_states = {tuple(pair) for pair in d['states']}
        if any(len(pair) != 2 or any(type(x) != int or not 0 <= x <= M for x in pair)
               for pair in attempt_states):
            raise ValueError('Invalid 128-bit state')
        all_states.update(attempt_states)
        sealed |= d['terminal'] == 'unsat'  # only full from-scratch enumeration qualifies
        attempts += 1
    return {'states': sorted(all_states), 'status': 'sealed' if sealed else
            ('open' if attempts else 'unvisited'), 'attempts': attempts}


def write_attempt(root, meta, cube, states, terminal, timeout_ms):
    root = _secure_dir(root)
    ns = namespace(meta)
    if cube not in range(4096) or terminal not in ('unsat', 'unknown', 'model-limit'):
        raise ValueError('Invalid cube/disposition')
    if not 100 <= timeout_ms <= 3600000: raise ValueError('Invalid solver timeout')
    before = read_cube(root, meta, cube)
    if before['status'] == 'sealed':
        raise ValueError('Cannot overwrite a sealed, complete cube')
    checked = sorted({tuple(x) for x in states})
    if any(len(s) != 2 or any(type(v) != int or not 0 <= v <= M for v in s)
           for s in checked):
        raise ValueError('Invalid state')
    # Exact original model must be the claimed P12 cube. No hint bits guessed.
    if any(sum(((s[0] >> p) & 1) << j for j, p in enumerate(P12)) != cube
           for s in checked):
        raise ValueError('Model in wrong cube')
    entry = {'namespace': ns, 'cube': cube, 'terminal': terminal,
             'timeout_ms': timeout_ms, 'states': checked,
             'complete_from_scratch': terminal == 'unsat'}
    # Immutable append-only attempt file. The only atomic publish is link() of
    # an already fsync'd O_EXCL 0600 temporary file; no reader sees half-state.
    stem = f'{ns}_{cube:04d}_{secrets.token_hex(12)}'
    tmp, final = root / (stem + '.tmp'), root / (stem + '.json')
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='ascii') as f:
            json.dump(entry, f, sort_keys=True)
            f.write('\n')
            f.flush(); os.fsync(f.fileno())
        os.link(tmp, final, follow_symlinks=False)
        directory_fd = os.open(root, os.O_RDONLY)
        try: os.fsync(directory_fd)
        finally: os.close(directory_fd)
    finally:
        tmp.unlink(missing_ok=True)
    return final


def coverage(root, meta, universe=range(4096)):
    out = {'sealed': 0, 'open': 0, 'unvisited': 0, 'cached_states': 0}
    for cube in universe:
        c = read_cube(root, meta, cube)
        out[c['status']] += 1
        out['cached_states'] += len(c['states'])
    return out


def reduce_cached(states, mask, target_sha256, serializer, starts):
    """Cheap exact full coupon reducer, no SAT or original-source input.

    Historical caller must escrow returned hits in private mode0600 storage,
    never print/save them in a public summary. Later retry isn't an input gate.
    """
    if len(mask) != 16 or len(target_sha256) != 64:
        raise ValueError('Malformed mask/target')
    endian, order = serializer.split('/')
    if endian not in ('big', 'little') or order not in ('ab', 'ba'):
        raise ValueError('Unknown serializer')
    if not starts or any(not 2 <= s <= 19 for s in starts):
        raise ValueError('Full 16-byte start must be 2..19')
    results = []
    for a, b in states:
        words = stream(a, b, max(starts) + 2)
        for pos in starts:
            pair = words[pos:pos + 2]
            if order == 'ba': pair = pair[::-1]
            raw = b''.join(x.to_bytes(8, endian) for x in pair)
            part = bytes(x ^ y for x, y in zip(raw, mask))
            if hashlib.sha256(part).hexdigest() == target_sha256:
                results.append(part)
    return results


def synthetic_test():
    # This is an entirely synthetic source-free no-SMT test; no printer data.
    a, b = (0xB02543CFB686BB4A, 0xF9DA21F56A996103)
    c, d = (0xCE695E4122B2739A, 0xFF6DF861F134F29D)
    cube = sum(((a >> p) & 1) << j for j, p in enumerate(P12))
    assert cube == sum(((c >> p) & 1) << j for j, p in enumerate(P12))
    meta = {'source_sha256': '1'*64, 'firstpair_sha256': '2'*64,
            'serializer': 'little/ab', 'circuit_sha256': '3'*64,
            'generator': 'xoroshiro128++ 1.0', 'P12': P12}
    with tempfile.TemporaryDirectory() as r:
        os.chmod(r, 0o700)
        assert coverage(r, meta, [cube, (cube+1)%4096, (cube+2)%4096])['unvisited'] == 3
        write_attempt(r, meta, cube, [(a,b), (c,d)], 'unsat', 5000)
        write_attempt(r, meta, (cube+1)%4096, [], 'unknown', 5000)
        cc = coverage(r, meta, [cube,(cube+1)%4096,(cube+2)%4096])
        assert cc == {'sealed':1,'open':1,'unvisited':1,'cached_states':2}
        got = read_cube(r, meta, cube)
        assert set(map(tuple,got['states'])) == {(a,b),(c,d)}
        mask = bytes(range(16)); vals = stream(a,b,21)
        raw = b''.join(x.to_bytes(8,'little') for x in vals[19:21])
        expected = bytes(x^y for x,y in zip(raw, mask))
        target = hashlib.sha256(expected).hexdigest()
        assert reduce_cached(got['states'],mask,target,'little/ab',[2]) == []
        assert reduce_cached(got['states'],mask,target,'little/ab',list(range(2,20))) == [expected]
        # Adding an output window needs *zero* additional solver invocations.
        assert read_cube(r,meta,cube)['attempts'] == 1
        wrong = dict(meta); wrong['circuit_sha256'] = '4'*64
        assert coverage(r,wrong,[cube])['unvisited'] == 1
        try:
            write_attempt(r,meta,cube,[(a,b)],'unsat',5000)
            raise AssertionError('Sealed overwrite accepted')
        except ValueError: pass
        try:
            write_attempt(r,meta,(cube+2)%4096,[(a,b)],'unsat',5000)
            raise AssertionError('Cross-cube model accepted')
        except ValueError: pass
        for p in Path(r).glob('*'):
            assert stat.S_IMODE(p.stat().st_mode)==0o600
    print({'synthetic_only':True,'sealed_cubes':1,'open_unknown':1,
           'never_visited':1,'cached_models':2,'18_word_start_replay':True,
           'reducer_updated_without_SMT':True,'source_circuit_mismatch_rejected':True,
           'private_file_mode_0600':True,'original_component_recovered':False})

if __name__ == '__main__': synthetic_test()
