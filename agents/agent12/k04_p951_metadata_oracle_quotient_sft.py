"""H-17 p951: exact selected K04 quotient after hypothetical CLASS/DEST oracles.

Uses Agent35's source-pinned original printer + AX GF(2) model.
The selected ACK2 payload, K04 route mask, acceptance and verifier are not read.
Run from repository tree with Python 3: python agents/agent12/k04_p951_metadata_oracle_quotient_sft.py
"""
from pathlib import Path
from runpy import run_path

model = run_path(str(Path(__file__).resolve().parents[1] /
                     "agent35/k04_p951_minimal_future_donor_sft.py"))
states = model["states"]()
source = model["fit_source"](states)
starts = model["STARTS"]
origin = model["ORIGIN"]
temper = model["temper_expr"]
overlap = model["rank_overlap"]
target = [bit for t in range(951, 955) for bit in states[t-origin]]

assert overlap([], target, source) == (128, 0, 0)

# Hypothetical last CLASS draw at s_i-1, with full 3-bit code known.
# Although the observed class reveals less than the complete code, granting
# a perfect 3-bit oracle gives an *upper bound* on target recoverability.
class_oracle = [
    bit for i in range(1, 128)
    for bit in temper(states[starts[i]-1-origin])[29:]
]

# Hypothetical first DEST draw immediately after each ordinary packet,
# with its full 2-bit code known, irrespective of rejection/acceptance.
dest_oracle = [
    bit for i in range(128) if starts[i]+4 < starts[i+1]
    for bit in temper(states[starts[i]+4-origin])[30:]
]

row43_dest = temper(states[starts[43]+4-origin])[30:]
assert starts[43]+4 == 328
assert overlap(row43_dest, target, source) == (128, 2, 0)
assert overlap(row43_dest[1:], target, source) == (128, 1, 0)

a = overlap(class_oracle, target, source)
b = overlap(dest_oracle, target, source)
c = overlap(class_oracle + dest_oracle, target, source)
assert len(class_oracle) == 127*3
assert len(dest_oracle) == 127*2
assert a == (128, 252, 0), a
assert b == (128, 169, 0), b
assert c == (128, 417, 0), c

# Positive rank control: Agent35's seven independently indexed future
# native output donors would fully determine the same target quotient.
future = [bit for t in (1179,1180,1181,1347,1348,1574,1575)
          for bit in states[t-origin]]
assert overlap(future, target, source) == (128, 224, 128)

print("K04 source-only quotient: 128 unknown bits")
print("127 hypothetical CLASS 3-bit observations: 0 target bits recovered")
print("127 hypothetical first-DEST 2-bit observations: 0 target bits recovered")
print("All 254 metadata oracle draws jointly: 0 target bits recovered")
print("Row43 first-DEST 2-bit oracle: 0 target bits recovered")
print("Positive seven future-native donor control: 128 target bits recovered")
print("No authenticated selected coupon or new REC8 PASS.")
