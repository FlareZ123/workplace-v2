"""Full original K04 SHA test of stage-free MT predecessors of intact packet pairs.

Run with Python3 from original workplace-v2 checkout. Uses only standard library.
The selected row129 is withheld from all source precursor inferences.
"""
from hashlib import sha256
from itertools import combinations, product
import json
import struct
from k04_stagefree_ax_halfword_sft import ROOT, printer_rows, precursor_options


def main():
    rows = printer_rows()
    route = json.loads((ROOT / 'evidence/recovery-routing.json').read_text())
    target = json.loads((ROOT / 'acceptance.json').read_text())
    mask = bytes.fromhex(route['K04']['masked_component'])
    original = bytes.fromhex(target['slot_sha256']['K04'])
    assert len(mask) == 16 and len(original) == 32
    def encode(words, view):
        w = words[::-1] if view >= 2 else words
        return struct.pack('<4I' if view%2==0 else '>4I', *w)
    def reduced(opaque):
        return bytes(x^y for x,y in zip(opaque,mask))
    planted_early,planted_late=34,64
    planted_bits=(1,0,1,1)
    p=[precursor_options(rows[planted_early][j],rows[planted_late][j]) for j in range(4)]
    true_words=[p[j][planted_bits[j]] for j in range(4)]
    planted=sha256(reduced(encode(true_words,3))).digest()
    trials=0
    original_hits=[]
    planted_hits=0
    for early,late in combinations(sorted(rows),2):
        p=[precursor_options(rows[early][i],rows[late][i]) for i in range(4)]
        for choice in product((0,1),repeat=4):
            words=[p[i][choice[i]] for i in range(4)]
            for view in range(4):
                component=reduced(encode(words,view))
                digest=sha256(component).digest()
                trials+=1
                if digest==original:
                    original_hits.append((early,late,choice,view,component.hex().upper()))
                if digest==planted:
                    planted_hits+=1
                    assert (early,late,choice,view)==(planted_early,planted_late,planted_bits,3)
    assert trials==553344 and planted_hits==1 and not original_hits
    print(json.dumps({'intact_printer_pairs':8646,'full_K04_candidate_checks':trials,
                      'original_commitment_matches':original_hits,
                      'planted_full_candidate_matches':planted_hits,
                      'selected_row129_in_source':False},indent=2))


if __name__ == '__main__':
    main()
