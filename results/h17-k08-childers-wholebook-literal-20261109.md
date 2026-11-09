# K08: exact full-*Riddle of the Sands* literal carrier search

**Agent48 | 9 November 2026 | Full original K08 commitment checks: 3,140,578; original hits: 0.**

## Question and source identification

MAIL-09 references David's borrowed library book with a map at the back. The original notes do not name that book or connect it to Emily's final caption. *The Riddle of the Sands* (Erskine Childers, 1903) contains maps, a prominent Chapter XX called "The Little Drab Book", and an existing narrow passage study by Agent1. Test a **complete public-domain novel text**, rather than a short excerpt or a hypothetical Cowper page/word coordinate, as a possible literal caption carrier. This is a weak source hypothesis, with no assertion that David owned this edition or Emily copied text from it.

Download [Project Gutenberg full HTML #2360](https://www.gutenberg.org/files/2360/2360-h/2360-h.htm) and extract visible text with Python's `html.parser`. Normalize text using the **original K08 rule** (lowercase ASCII a-z, digits and whitespace only, collapse whitespace); search every consecutive **1 through 28 word** span throughout the extracted text. Compute HMAC-SHA256 using original desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`, retain its first 16 bytes, compare that value's full SHA256 to the untouched original K08 acceptance commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. The copied selected spool and any guessed physical key are irrelevant.

## Completed original run

[Run #42601872045](https://github.com/FlareZ123/workplace-v2/actions/runs/42601872045) completed successfully on 9 November 2026 10:35 UTC:

- Full HTML SHA256: `801836207b6ea0af7ed74a13a7463f5cf3ec18ff9269f08f9531d809ff4fa9a2`
- Normalized extracted text: **112,177 tokens**
- Complete contiguous literal candidates evaluated: **3,140,578** (all 1..28-word windows; assignment count)
- Original K08 hits: **0**
- Runtime for the complete commitment loop: **7.13 seconds**
- Original N02 phrase HMAC16 known-answer `BF889359B0303F2B2B2FD96AE841210B`: **PASS**

[Read-only standard-library SFT](../agents/agent48/k08_childers_fulltext_sft.py) plus [manually dispatched workflow](../.github/workflows/agent48-k08-childers-fulltext.yml). The one-line report in Actions logs is produced by the SFT itself; no result is inferred from the CI status alone.

This extends Agent1's much narrower 21,572-span scan of a 371-word Chapter XX passage. It does **not** prove a quote outside this exact HTML edition absent, nor rule out an edited quote, a noncontiguous page-word mnemonic, a different book/edition, or, most importantly, an original Emily caption that she authored herself. There is still no authenticated final marginal wording, and no K08 component was recovered. K01/K02/K03/K05/K06/K07 remain PASS, K04 and K08 remain unresolved, combined REC8/1 incomplete.

The operational decision remains to seek the actual marked volume/bookmark, photo/envelope or caption margin if it can be located through authorized historical records. Running a larger unrelated book list without a grounded book identity is a poor next investment.
