"""Source-only p951 printer CLASS decoding alternative, 2 Nov 2026.

The p951 chronology is hypothetical. This tests a modulo-three, no-rejection
producer stage at the terminal pre-payload raw MT output, versus the earlier
rejection-sampler interpretation. No target coupon/commitment is consulted.
Usage: python agents/agent12/k04_p951_mod3_metadata_sft.py
"""
import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = runpy.run_path(str(ROOT / "agents/agent2/20261102_k04_multicarrier_p951_sft.py"))
STARTS = MODEL["STARTS"]
MASK = MODEL["MASK"]
words, known, offset = MODEL["source_closure"](ROOT / "resources")
rows = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_text().splitlines()[1:]
assert len(rows) == len(STARTS) == 133
names = ["LABEL", "STORES", "RECOVER"]
labels = [names.index(re.search(r"CLASS=(\\w+)", row).group(1)) for row in rows]
assert [code % 3 for code in range(8)] == [0, 1, 2, 0, 1, 2, 0, 1]
predicted = {}
for i, start in enumerate(STARTS):
    if i == 129:
        continue
    pos = offset + start - 1
    if known[pos] != MASK:
        continue
    raw = MODEL["temper"](words[pos])
    predicted[i] = (raw >> 29) % 3

ordinary = {i: code for i, code in predicted.items() if i < 128}
late = {i: code for i, code in predicted.items() if i >= 128}
ordinary_wrong = [i for i, code in ordinary.items() if code != labels[i]]
late_wrong = [i for i, code in late.items() if code != labels[i]]
assert len(ordinary) == 29
assert ordinary_wrong == [76, 80, 101, 119]
assert len(late) == 2 and late_wrong == [131, 132]
assert sum(code == labels[i] for i, code in ordinary.items()) == 25
first = sorted(ordinary)[:18]
last = sorted(ordinary)[18:]
assert sum(ordinary[i] == labels[i] for i in first) == 16
assert sum(ordinary[i] == labels[i] for i in last) == 9
shift_scores = [sum(code == labels[(i + s) % 128] for i, code in ordinary.items())
                for s in range(1, 128)]
assert max(shift_scores) == 17
print("Ordinary CLASS terminal high3 modulo 3: 25/29, wrong rows", ordinary_wrong)
print("Chronological first 18: 16 matches; remaining 11: 9 matches")
print("127 cyclic original-label shift controls: maximum", max(shift_scores))
print("Late REQUESTED/ACK cohort with fixed RECOVER metadata: 0/2", late_wrong)
print("Historical chronology, generator and terminal stage remain unproved.")
print("Selected K04 payload bits determined by this experiment: zero.")
