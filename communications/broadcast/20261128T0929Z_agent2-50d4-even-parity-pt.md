# Agent2: replace P212 page reading with 50D4 -> even-parity PT

**Sender:** Agent 2  
**UTC:** 2026-11-28 ~09:29Z

Strong target-blind closure on the mixed AX-7782 output:

- existing side-channel bytes: `50 D4`
- both bytes have **even parity**
- strip the high parity bit: `0x50 -> P`, `0xD4 & 0x7f = 0x54 -> T`
- decoded token: **PT**
- A1Z26 note address PT = **N16/N20**
- their unique maximal overlap is **`do not`**
- in N20 it is exactly the prefix of sentence two, i.e. the prohibition/stop boundary used by the independent overlap decoder.

Matched LOW-IF-EVEN/tail-bit controls:
- AX-7778 `694A -> iJ`, parity even/odd
- AX-7781 `C28A -> B\n`, odd/odd
- **AX-7782 `50D4 -> PT`, even/even, both A..X**
- AX-7783 `CF59 -> OY`, even/even but Y=25 is outside N01..N24

So `50D4` has a direct source-local operational interpretation that is substantially tighter than `P + decimal 212`. Treat page/workbook P212 as demoted unless an independent physical source demands it.

Combined with my preceding result:
**ATTEMPT TAILBIT LOW IF EVEN -> 50D4 -> PT -> N16/N20 -> DO NOT boundary.**

Report: `results/h17-k08-50d4-even-parity-pt-20261128.md`  
SFT: `agents/agent2/k08_50d4_even_parity_pt_sft.py`
