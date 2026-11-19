# K08 MILK/STORES cycle and N14 LOW-IF-EVEN bridge

**Date:** 19 November 2026  
**Agent:** 9  
**Status:** source-pinned K08 routing refinement; terminal phrase still unresolved  
**Reproducer:** `agents/agent9/k08_milk_stores_spool_bridge_sft.py`

## Result

The exact K08 HMAC low-bit note router reported in
`h17-k08-hmac-lowbit-cycle-n14-convergence-20261119.md` has one stronger
source-level reading when its unique four-cycle is rotated to its Emily-authored
member N13:

```text
N13 -> N09 -> N12 -> N11 -> N13
 13     9      12     11
  M     I       L      K
```

Under ordinary A1Z26 numbering, the cycle is exactly **MILK**.

The source note file contains no literal word `milk`, so this word is generated
by the router rather than copied from note prose.

The four numerically aligned retained printer rows are also unusually coherent:

| note | printer row | CLASS | DEST |
|---|---|---|---|
| N13 | PS-261003-0313 | STORES | store |
| N09 | PS-261003-0309 | STORES | store |
| N12 | PS-261003-0312 | STORES | store |
| N11 | PS-261003-0311 | STORES | desk |

Thus the exact HMAC cycle independently gives **MILK**, while every aligned
printer row says **STORES**. This is a materially tighter source join to the
already-authenticated browser bookmark
`R:/Stores/consumables/mug-stock.xls` than the earlier generic tea/mug
resemblance.

The note-number to PS-03NN alignment remains an inferred crosswalk. The supplied
spool log itself does not state that N13 authored PS-0313, so the shared
`CLASS=STORES` observation is corroborating structure rather than custody proof.

## N14 literalizes LOW IF EVEN

Three independent frozen inputs now select 14 under the same LOW BIT reducer:

```text
K04 route mask -> byte-LSB pack D939 -> hex LOW BIT 14
K08 desk nonce -> byte-LSB pack F797 -> hex LOW BIT 14
N20 K08-HMAC16 -> byte-LSB pack DA53 -> hex LOW BIT 14
```

N14 is:

```text
Sunrise photograph: If the horizon has disappeared, ...
```

N14 is numbered **14**, therefore **EVEN**, and its body begins with **IF**.
The existing source-derived directive **LOW IF EVEN** consequently has a literal
source locus at N14: apply LOW to the IF-bearing even photograph row.

Using the aligned PS-0314 retained payload:

```text
E393E5CD05564F3CCA0D8E575FC63FEB
-> byte-LSB pack 5FDA
-> hex-character LOW BIT 9
-> N09
```

N09 is explicitly **Caption for the galley board**. This provides a compact
local continuation from the N14 photograph locus to a caption locus, without
inventing caption vocabulary.

The complete aligned PS-0301..0324 low-bit map contains another four-cycle:

```text
N09 -> N12 -> N01 -> N04 -> N09
```

This second cycle is retained as secondary structure only because the numeric
note/printer alignment is not authenticated by a native manifest.

## Interpretation

The combined route is now:

```text
exact K08 HMAC note cycle
        -> MILK
        -> four STORES-class aligned rows
        -> bookmarked Stores/consumables/mug-stock.xls

K04 mask + K08 nonce + N20
        -> N14 Sunrise photograph
        -> IF + EVEN
        -> LOW on PS-0314
        -> N09 galley caption
```

This converges the previously separate mug-stock and photograph/caption lanes
using frozen source operations. It still does not reveal Emily's final keeper
words. The native workbook, shelf card, original photograph/caption carrier and
final envelope are absent from the supplied export and checked repository
surfaces.

The practical consequence is to stop expanding semantic phrase grammars.
The next complete-object test should operate on an independently available
native `mug-stock.xls`, original N14-related photograph/caption artifact, or
equivalent preserved profile/cache copy using the already pre-registered intake
tools. Until such bytes are available, this report supplies a sharper selector
but no K08 component.
