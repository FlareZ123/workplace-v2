"""Original H-17 ZIP entry-order channel audit, 6 November 2026.

Source-bounded container check: local vs central order, depth-first path
structure, and deterministic case-insensitive sibling order. Standard library.
"""
from collections import defaultdict
from hashlib import sha256
from math import factorial, log2
from pathlib import Path
import sys
import zipfile

ORIGINAL_SHA = 'e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7'


def check_order(paths):
    children = defaultdict(list)
    for p in paths:
        stem = p.rstrip('/')
        head, slash, tail = stem.rpartition('/')
        parent = head+'/' if slash else ''
        children[parent].append(tail + ('/' if p.endswith('/') else ''))
    roots = children['']
    nonroot = [k for k in children if k]
    canonical = sum(children[k] == sorted(children[k], key=str.casefold) for k in nonroot)

    def walk(parent):
        order = []
        for name in children[parent]:
            full = parent + name
            order.append(full)
            if full.endswith('/'):
                order.extend(walk(full))
        return order

    depth_first = walk('')
    return roots, [len(children[k]) for k in nonroot], canonical, depth_first == paths


def main():
    archive = Path(sys.argv[1] if len(sys.argv)>1 else '/mnt/data/h17-archive-dump.zip')
    assert sha256(archive.read_bytes()).hexdigest() == ORIGINAL_SHA
    with zipfile.ZipFile(archive) as z:
        info = z.infolist()
        paths = [x.filename for x in info]
        physical = [x.filename for x in sorted(info,key=lambda x:x.header_offset)]
    assert len(paths)==56 and sum(p.endswith('/') for p in paths)==10
    assert physical == paths
    roots, groups, canonical, depth_first = check_order(paths)
    assert len(roots)==5 and len(groups)==10
    assert canonical==10 and depth_first
    assert roots == ['START_HERE.md','verify.py','evidence/','acceptance.json','candidate.template.json']
    canonical_remainder_bits = sum(log2(factorial(n)) for n in groups)
    # Source observed non-root sibling order is fully canonical by casefold.
    assert round(canonical_remainder_bits,4)==round(106.47508157920271,4)
    print('ORIGINAL_ZIP_SHA_OK members=56 files=46 dirs=10')
    print('LOCAL_CENTRAL_ENTRY_ORDER_EQUAL=True')
    print('RECURSIVE_CANONICAL_SIBLING_GROUPS=10/10')
    print('ONLY_NONCANONICAL_SIBLING_SET=root (5 members): '+str(roots))
    print('RESIDUAL_ROOT_ORDER_CAPACITY_BITS='+str(round(log2(factorial(5)),5)))
    print('CANONICAL_NONROOT_PERMUTATION_BITS='+str(round(canonical_remainder_bits,5)))
    changed=paths.copy()
    i=changed.index('evidence/mail/01.eml')
    changed[i],changed[i+1]=changed[i+1],changed[i]
    _,_,ncanon,ok = check_order(changed)
    assert ncanon==9 and ok
    print('SYNTHETIC_ONE_SIBLING_SWAP_FLAGGED=True')


if __name__=='__main__':
    main()
