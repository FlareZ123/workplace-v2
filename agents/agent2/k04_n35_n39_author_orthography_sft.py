"""Author-writing alphabet version of Agent2's exact original-source joint solver.

This is a narrowly labeled *source-inspired hypothesis*: the unnormalized
original caption was written in ordinary Latin letters, digits, spaces, and
the punctuation found in ordinary crew-board prose. It must be kept distinct
from unconditional n35/n39 printable-ASCII model exclusions.
"""
from __future__ import annotations

import argparse
import k04_n35_n39_global_source_joint_feasible_sft as joint

AUTHORED_CAPTION = frozenset(
    b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    b"0123456789 .,;:!?'-\"()"
)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--n",type=int,choices=(35,39),required=True)
    p.add_argument("--shard",type=int,choices=range(8),required=True)
    args=p.parse_args()
    assert joint.PRINTABLE.issuperset(AUTHORED_CAPTION)
    joint.PRINTABLE=AUTHORED_CAPTION
    joint.run(args.n,args.shard)

if __name__=="__main__":
    main()
