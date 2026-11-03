"""Source-only 24-permutation recorder field-producer order calibration.

No disputed printer coupon, K04 commitment, route mask or K08 is read.
Each hypothesis uses one native MT draw per EVENT/LATCH/AUX/CONTROL field
and zero rejected draws; this is a narrow falsifiable pilot. Test original
source-preindexed anchors separately from the 41 CONTROL-only path placements.
"""
from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
sys.path.insert(0, str(ROOT / "agents" / "agent2"))
sys.path.insert(0, str(ROOT / "agents" / "agent47"))
from k04_p951_symbolic_basis import source
from k04_node50_full_syndrome_gap_sft import recorder_controls
from k04_conditional_onebit_parity_sft import PATH, joint_basis
from k04_seq47_event_aux_joint_sft import recorder_metadata, ANCHORS
from k04_seq47_exact_joint_reject_sft import accepted, solvable

FIELD_N = {"E": 6, "L": 3, "A": 13}


def assignments(stage, fields, observations):
    event, latch, aux = observations
    values = {"E": event - 1, "L": latch, "A": aux - 2000}
    assert set(fields) == {"E", "L", "C", "A"}
    start = stage - fields.index("C")
    rows = []
    for j, field in enumerate(fields):
        if field != "C":
            rows.append((start + j, FIELD_N[field],
                         accepted(FIELD_N[field], values[field])))
    return rows


def main():
    printer, vectors = source(ROOT / "resources")
    assert printer.rank == 15365
    controls = recorder_controls()
    metadata = recorder_metadata()
    model = joint_basis(printer, vectors, controls, PATH)
    assert model.rank == 16663
    print("SOURCE",len(PATH),"records; original 15 CONTROL source anchors and 41 other placements")
    output = []
    for fields in permutations("ELCA"):
        codes = "".join(fields)
        hits = {"anchors": [], "other": []}
        for seq, stage in PATH:
            source_rows = assignments(stage, fields, metadata[seq])
            match, _ = solvable(model, vectors, source_rows)
            hits["anchors" if seq in ANCHORS else "other"].append(
                (seq, match is not None))
        ah = sum(x[1] for x in hits["anchors"])
        oh = sum(x[1] for x in hits["other"])
        output.append((ah, oh, codes, hits))
        print("ORDER",codes,"source_anchors",ah,"of",len(hits["anchors"]),
              "other_placed",oh,"of",len(hits["other"]),flush=True)
    output.sort(reverse=True)
    print("BEST_ORDERS",
          [(code, ah, oh) for ah,oh,code,_ in output[:8]],flush=True)
    print("BEST_ANCHOR_SUCCESS_SEQS",
          {code:[seq for seq,ok in x["anchors"] if ok]
           for _,_,code,x in output[:3]},flush=True)
    print("No original selected K04 payload or K08 caption authenticated.",flush=True)


if __name__ == "__main__":
    main()
