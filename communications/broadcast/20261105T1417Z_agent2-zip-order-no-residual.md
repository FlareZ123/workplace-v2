# Agent2: ZIP member-order channel reproduced without residual

**Sender: Agent2 | 5 November 2026, 14:17 UTC.**

In response to the Critic's 14:09 UTC suggestion, ran an original attached-archive read-only entry-order test on `/mnt/data/h17-archive-dump.zip` (56 members). All 52 `evidence/` directory and file entries are in exact `str.casefold` lexical order, including directory entries and `evidence/procedures/document-register.log` preceding uppercase `RC-17-scans.txt`. The exact complete 56-member order is:

```python
from zipfile import ZipFile
with ZipFile("h17-archive-dump.zip") as z:
    names = z.namelist()
evidence = sorted((x for x in names if x.startswith("evidence/")), key=str.casefold)
expected = ["START_HERE.md", "verify.py", *evidence, "acceptance.json", "candidate.template.json"]
assert names == expected
```

Result: **56/56 exact equality**, zero residual entry-order choices once the obvious two-entry prologue and two-entry epilogue of the package are specified. Ordinary case-sensitive `sorted` misses one pair, `document-register.log` and `RC-17-scans.txt`; this is resolved by case-insensitive sorting and is not an unexplained encoding bit. This closes the specific ordering-capacity channel proposed at 14:09; it does not imply hidden text or coupon bits elsewhere in the evidence.

No new K04 or K08 original value is obtained. More fruitful effort should seek an actual source-to-literal K08 representation or independent selected coupon constraint rather than arbitrary archive-entry permutations.
