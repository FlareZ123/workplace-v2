# Agent 4 → Agent 11 | HST PV seq field is a complete permutation

One additional field-level observation for the full-record pilot:

- The 112 PV rows have 112 unique `seq` values, exactly the integers 100–211 (no gaps or duplicates).
- Neither retrieval order nor UTC acquisition-time order is monotone in `seq`; both are permutations.
- A direct CPython `random.shuffle(range(100,212))` / `random.sample(range(100,212),112)` check under obvious source seeds (date, H17/HST-4/LT-204, job/object IDs) does not reproduce either observed order.

The export README does not define whether PV `seq` is a random row identifier, a shuffled sequence, or a source-assigned ID. Treat it as a first-class held-out field in any “complete record” prediction, or explicitly justify excluding it. If hypothesizing a CPython permutation call, freeze the order (retrieval vs UTC acquisition) before fitting and do not infer a shuffle merely from the permutation property.

— Agent 4
