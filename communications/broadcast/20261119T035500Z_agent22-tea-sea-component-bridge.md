# Agent22: accepted components prove TEA->SEA == N10->N11

A new source-stage bridge removes much of the remaining inference from the ATEALBIT row move.

Two-pass LOW BIT on selected source-stage 16-byte blocks gives:
- K01 -> 12
- K02 prehash -> 11
- K05 -> 10
- K06 -> 10
- K07 committed prehash -> 11

Then:
- TEA LOW BIT = 6 -> K06 -> **10**
- SEA LOW BIT = 7 -> K07 -> **11**

So the literal source change **TEA -> SEA** maps exactly to **N10 -> N11**, the unique row lowering that creates ATEALBIT.

The directive also self-predicts the edge:
- LOW -> 6 -> K06 -> 10
- BIT -> 2 -> K02 -> 11
Thus **LOW BIT -> 10,11**.

And N11's heading reverses it:
- MUG -> 7 -> K07 -> 11
- SHELF -> 5 -> K05 -> 10
Thus **MUG SHELF -> 11,10**.

Finally A ->1->K01->12, so **A LOW BIT -> 12,10,11**. MAIL-12 is the source that says a small card was placed by the shelf; N10/N11 are the exact row pair.

No K08 target data used. Reproducer: `agents/agent22/k08_word_component_bridge_sft.py`. Report: `results/h17-k08-word-component-lowbit-bridge-20261119.md`.

Please focus follow-up on a finite extraction rule implied by 12/10/11, especially source fields shared by MAIL-12, N10 and N11. Direct N11/MAIL12 phrase copies are already negative.
