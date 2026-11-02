"""Source-only K04 p951 candidate transfer-block target leverage atlas.

Uses prior Agent35 exactly checked symbolic MT/AX7778 provenance and
scans the not-yet-observed 16x high16 transfer block hypothesis.
The K04 ACK, XOR mask, SHA commitment and K08 are never read.
"""
import importlib.util
from pathlib import Path
from time import monotonic

ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'agents/agent35/k04_p951_minimal_future_donor_sft.py'
spec=importlib.util.spec_from_file_location('mt',path)
mt=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)

def main():
    started=monotonic()
    symbols=mt.states(3600)
    mt.synthetic_control(symbols)
    source=mt.fit_source(symbols)
    assert len(source)==15495
    target=[expr for t in range(951,955) for expr in symbols[t-mt.ORIGIN]]
    assert mt.rank_overlap([],target,source)[0]==128
    upper={t:mt.temper_expr(symbols[t-mt.ORIGIN])[16:] for t in range(965,3015)}
    gains={}
    for first in range(965,3000):
        donors=[expr for t in range(first,first+16) for expr in upper[t]]
        gain=mt.rank_overlap(donors,target,source)[2]
        if gain:
            gains[first]=gain
    assert len(gains)==69, len(gains)
    assert max(gains.values())==44
    expected={1166:44,1179:44,1393:44,1406:44,1623:12,2305:29}
    assert all(gains.get(k)==v for k,v in expected.items()), gains
    print('Single block search: 2035 future starts; 69 gain>0; maximum target gain 44/128')
    for positions in ((1166,1393,1623),(1166,1393,2305),
                      (1166,1623,2305),(1393,1623,2305)):
        donors=[expr for start in positions for t in range(start,start+16) for expr in upper[t]]
        gain=mt.rank_overlap(donors,target,source)[2]
        assert gain==44,(positions,gain)
        print('Triple blocks',positions,'joint target gain',gain,'/128')
    print('These are hypothetical donor positions, not identified historical checkpoint phases.')
    print('Elapsed',round(monotonic()-started,2),'seconds')

if __name__=='__main__':main()
