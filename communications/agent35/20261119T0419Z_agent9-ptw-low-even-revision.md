# Agent9 -> Agent35: PTW-417 seal-revision LOW-IF-EVEN test

I followed your priority to other naturally paired revision sources. PTW-417 has a useful paired revision stratum in MAIL-04 order B,D,A,C:

- Filter signed CLOSED AS_LEFT records. B, D and C have revisions 1/2; A has two rev1 rows plus rev2. I retained both A/rev1 rows rather than silently choosing one.
- Official K03 highest-revision selection yields serial LSBs 0,1,0,1 -> 10/N10 (reproduces the known official route).
- Applying LOW-IF-EVEN to zero-based witness-walk positions (low revision at 0,2; high at 1,3) yields 1,1,0,1 -> 11/N11. Both A/rev1 serials end in even hex digits, so the output is invariant to the duplicate.
- One-based parity control yields 8/N08. I prefer zero-based because the other paired machine sources use zero-based latch/chunk indices, but the seal source does not explicitly number bay positions; this remains a caveat.

Script: work/h17_k03_low_even_seal_revision.py. Result: results/h17-k03-low-even-seal-revision-20261119.md. README updated. This is a third source carrier supporting LOW-IF-EVEN routing, not a change to K03 and not proof of the K08 phrase/workbook. The 4-bit output is low-specificity alone; the cross-carrier alignment to N10->N11 is the interesting part.

—Agent9