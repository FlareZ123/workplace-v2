"""Single-file original source-heldout PTW seal/bay stage test.

Run: python agents/agent46/k04_ptw_bay_heldout_sft.py resources
Printer p951 source is a hypothetical producer, and the global generator
assignment has previously published contradictions. The original copied
K04 coupon, route mask, acceptance and K08 are not accessed.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'agent49'))
from k04_p951_symbolic_basis import source,get,temper,untemper

ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources'
SEAL_SHA='c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32'


def predictions(b,s,lo,hi):
    result={}
    for pos in range(lo,hi):
        n_value=n_mask=o_value=o_mask=0
        for j,expression in enumerate(get(s,pos)):
            bit=b.predict(expression)
            if bit is not None:
                n_value|=bit<<j
                n_mask|=1<<j
        for j,expression in enumerate(temper(get(s,pos))):
            bit=b.predict(expression)
            if bit is not None:
                o_value|=bit<<j
                o_mask|=1<<j
        result[pos]=(n_value,n_mask,o_value,o_mask)
    return result


def stage(pred,prior,bay,cap=9):
    """Possible (next_serial_index, discarded_draws), read no next serial."""
    out=[]
    for discards in range(cap+1):
        at=prior+1+discards
        if at not in pred:
            break
        def high3(pos):
            _,_,val,mask=pred[pos]
            return val>>29,mask>>29
        rejected=[high3(prior+1+j) for j in range(discards)]
        if any((v|(~m&7))<4 for v,m in rejected):
            break
        value,mask=high3(at)
        if not ((value^bay)&mask):
            out.append((at+1,discards))
    return out


def seeded_controls():
    class TracingRandom(random.Random):
        def __init__(self,seed):
            super().__init__(seed)
            self.stream=[]
        def getrandbits(self,k):
            full=super().getrandbits(32)
            self.stream.append(full)
            return full>>(32-k)
    for seed in range(100):
        rng=TracingRandom(12345+seed)
        _=rng.getrandbits(32)
        prior=len(rng.stream)-1
        bay=rng.randrange(4)
        next_serial=len(rng.stream)
        _=rng.getrandbits(32)
        pred={pos:(0,0,x,0xffffffff) for pos,x in enumerate(rng.stream)}
        assert stage(pred,prior,bay,9)==[(next_serial,next_serial-prior-2)],(seed,bay)
    print('PASS 100 seeded CPython bay/rejection stage controls')


def main():
    seeded_controls()
    raw=(ROOT/'evidence/maintenance/seal-receipts.jsonl').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SEAL_SHA
    by_id={}
    for line in raw.splitlines():
        rec=json.loads(line)
        number=int(rec['permit'].split('-')[1])
        if number<417:
            assert number not in by_id
            by_id[number]=rec
    assert set(by_id)==set(range(390,417))
    b,s=source(ROOT)
    assert b.rank==15365
    predicted=predictions(b,s,-970,-920)
    for permit,index in ((405,-964),(412,-944),(414,-937)):
        original=untemper(int.from_bytes(bytes.fromhex(by_id[permit]['serial'][3:]),'little'))
        value,mask,_,_=predicted[index]
        assert mask==0xffffffff and value==original,(permit,index)
    print('3 independent source-matched anchor serials: PTW405 -964, PTW412 -944, PTW414 -937')

    bay406='ABCD'.index(by_id[406]['bay'])
    places=stage(predicted,-964,bay406,9)
    assert places==[(-961,1)],places
    at=places[0][0]
    expected,mask,_,_=predicted[at]
    assert mask.bit_count()==9
    original406=untemper(int.from_bytes(bytes.fromhex(by_id[406]['serial'][3:]),'little'))
    assert ((expected^original406)&mask)==0
    print('HELDOUT_SERIAL406 predicted 9/9 native bits, from permit405 serial and 406 bay only')
    print('PTW406 source native mask:',hex(mask),'masked value:',hex(expected&mask))
    assert (predicted[-963][2]>>29)==7 and (predicted[-963][3]>>29)==7
    assert (predicted[-962][2]>>29)==2 and (predicted[-962][3]>>29)==7
    print('Source-predicted first bay code7 rejected; second code2 accepted (BAY C)')

    # A strictly forward candidate generator uses only PTW405's anchored
    # original, and the BAY labels 406..414. The withheld downstream
    # serial words do not enter index selection or candidate construction.
    possible={-964}
    for permit in range(406,415):
        bay='ABCD'.index(by_id[permit]['bay'])
        possible={nxt for prior in possible
                  for nxt,_ in stage(predicted,prior,bay,9)}
        assert possible
        if permit in (412,414):
            full={pos:predicted[pos][0] for pos in possible
                  if predicted[pos][1]==0xffffffff}
            expected_count={412:3,414:4}[permit]
            original=untemper(int.from_bytes(
                bytes.fromhex(by_id[permit]['serial'][3:]),'little'))
            assert len(full)==expected_count and list(full.values()).count(original)==1
            print(f'BLIND SERIAL{permit}: {expected_count} complete native candidates; '
                  'original matched exactly once')

    # Without consulting BAY414, the two anchor serials and a two-bay
    # rejection stage require its label C. BAY413 remains ambiguous.
    viable=[]
    for intermediate in range(-942,-938):
        for bay413 in range(4):
            for bay414 in range(4):
                a=(intermediate,intermediate-(-944)-2)
                b2=(-937,(-937)-intermediate-2)
                if a in stage(predicted,-944,bay413,9) and b2 in stage(predicted,intermediate,bay414,9):
                    viable.append((intermediate,bay413,bay414))
    assert len(viable)==10 and {bay for _,_,bay in viable}=={2},viable
    assert 'ABCD'.index(by_id[414]['bay'])==2
    print('HELDOUT_BAY414 source stage predicts BAY C across all 10 admissible 412->414 paths')

    # Exact Bay-label-shuffle calibration of the 405->412->414 constrained
    # stage, not a producer-authentication probability. Repeated Bay labels
    # are deduplicated before testing; the two source anchor indices were
    # discovered retrospectively and are deliberately fixed.
    from itertools import permutations
    codes=tuple('ABCD'.index(by_id[p]['bay']) for p in range(406,415))
    permutations_distinct=set(permutations(codes))
    assert len(permutations_distinct)==2520
    matched=0
    for trial in permutations_distinct:
        positions={-964}
        for permit,bay in zip(range(406,415),trial):
            positions={nxt for prior in positions
                       for nxt,_ in stage(predicted,prior,bay,9)
                       if permit not in (412,414) or
                       nxt==({412:-944,414:-937}[permit])}
            if not positions:
                break
        matched+=-937 in positions
    assert matched==420
    print('Exact shuffled-bay calibration: 420/2520 rearrangements retain '
          'both retrospective anchor indices. Not historical producer proof.')

    # Falsify the uniform post-414 extension with original 416 serial
    # withheld until after source-derived stage placement. Stage at 414
    # was identified by retrospective source matching, a model assumption.
    downstream={-937}
    for permit in (415,416):
        downstream={nxt for prior in downstream
                    for nxt,_ in stage(predicted,prior,
                         'ABCD'.index(by_id[permit]['bay']),9)}
    assert downstream=={-929,-930,-931,-932}
    original416=untemper(int.from_bytes(
        bytes.fromhex(by_id[416]['serial'][3:]),'little'))
    contradictions={pos:(((predicted[pos][0]^original416)&predicted[pos][1]).bit_count(),
                         predicted[pos][1].bit_count()) for pos in downstream}
    assert all(errors>0 for errors,known in contradictions.values())
    print('FALSIFIED PTW414->416 stage: every allowed 416 position '
          'contradicts the original heldout 416 serial',contradictions)

    # Only source-defined immediate placements gain +33 native input
    # equations at 406 and 413; none fixes even one selected K04 bit.
    from k04_p951_symbolic_basis import Basis
    augmented=Basis()
    augmented.rows=b.rows.copy();augmented.rank=b.rank
    for permit,index in ((406,-961),(413,-940)):
        native=untemper(int.from_bytes(bytes.fromhex(by_id[permit]['serial'][3:]),'little'))
        for bit,expr in enumerate(get(s,index)):
            augmented.insert(expr,(native>>bit)&1)
    assert augmented.rank-b.rank==33
    target=[get(s,951+j//32)[j%32] for j in range(128)]
    assert sum(augmented.predict(expr) is not None for expr in target)==0
    print('Conditional source increase +33 equations, selected K04 quotient still 128/128')
    print('No historically authenticated selected-coupon bits or final K08 words')


if __name__=='__main__':main()
