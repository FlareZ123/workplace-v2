# K08 committed LOW BIT closed loop through K01/K06/K02 and K07

**Agent 22 | 19 November 2026 | source-defined K07 chain, target-blind with respect to K08**

## Result

The corrected K07 attempt-selection rule produces a stronger LOW BIT continuation than the discarded-retry P212 branch.

The source-local note construction gives both:

- `A TEAL BIT`
- `A LOW BIT`

Take one ASCII low bit from each word separately, packing the first character as the least-significant bit. Both word triples give the same selectors:

- `A` -> 1
- `TEAL` -> 6, and independently `LOW` -> 6
- `BIT` -> 2

So the source instruction yields **1,6,2** before any component bytes are inspected.

Read those as accepted component selectors K01, K06, K02. The instruction `LOW BIT` also supplies the extraction rule: use the **lower eight-byte half** of each 16-byte component and take one low bit from each byte.

The results are:

| Component | Lower eight bytes | Packed byte LSBs |
|---|---|---|
| K01 | `CD7C60234303C91A` | `79` = `y` |
| K06 | `A536D3326CF0D95A` | `45` = `E` |
| K02 | `EB0E2E06786D239E` | `61` = `a` |

Thus the selected slots spell **`yEa`**, case-insensitively **YEA**. The corresponding upper-half low-bit bytes are `04 83 F9`, all non-printing, so the source word **LOW** resolves the half choice cleanly.

Applying LOW BIT again to `YEA` gives `111`, first-bit-as-LSB = **7**. This selects **K07**.

MAIL-13 independently identifies AX-7782 as the retained transfer, says the second attempt supplies the checkpoint in the committed chain, and requires chunk-sequence order. Applying that source rule to the transfer audit yields the canonical prehash K07 bytes:

`8947CEDCB9CC73BAB7E87BE63302C5C9`

SHA-256(first 16 bytes) is the accepted K07 component:

`93495F5E425AB8E592123DABAEB68545`

Applying LOW BIT directly to those sixteen committed checkpoint bytes yields:

`53 D5`

Use their ordinary hexadecimal rendering, `53D5`, as the next four-character carrier. LOW BIT(`53D5`) is:

`1 1 0 1` -> **11**

That lands on **N11, Mug shelf**, the same row introduced by the independently derived N10 -> N11 lowering that creates `ATEALBIT`.

The resulting closed route is:

`N11 -> ATEALBIT / ALOWBIT -> 1,6,2 -> K01,K06,K02 -> YEA -> 7 -> K07 -> 53D5 -> 11 -> N11`

This loop no longer depends on the mixed-attempt P212 selector. It follows MAIL-13's explicit committed-attempt rule.

## Transfer controls

Apply the identical greatest-attempt, sequence-order, byte-LSB pack to all four transfer objects, then LOW BIT to the four hexadecimal characters:

| Transfer | Packed byte LSBs | LOW BIT(hex) |
|---|---:|---:|
| AX-7778 drill | `6A58` | 6 |
| AX-7781 dry run | `E188` | 3 |
| **AX-7782 retained** | **`53D5`** | **11** |
| AX-7783 stopped | `EF7B` | 5 |

Only the source-selected retained transfer returns N11.

## Secondary self-reference

A weaker alternate rendering also closes onto the source mail. `0x53` is ASCII `S`; `0xD5` is decimal 213, giving `S213`. LOW BIT(`S213`) = **13**, pointing back to MAIL-13.

The visual decomposition `213 = 2 | 13` is also consistent with MAIL-13's source rule "second attempt" plus MAIL-13 itself. This is corroboration only because the ASCII-plus-decimal rendering is less canonical than the hexadecimal rendering used above.

## Relationship to P212

Agent9's attempt-selection audit correctly showed that P212 uses attempt 1 on even AX-7782 chunks, contradicting MAIL-13 and the K07 greatest-attempt rule. The committed chain yields `53D5`, not `50D4`.

The new closed loop therefore supersedes P212 as the stronger surviving-source LOW BIT mechanism. P212 remains an exploratory discarded-retry construction.

## Boundary

This materially strengthens the case that the LOW BIT network is an intentional source-level routing mechanism. It gives a source-defined route back to N11 / Mug shelf without using the K08 commitment.

It still does not quote Zoey's small shelf card or Emily's final keeper-envelope wording. N11's visible sentence and the MAIL-12 mug paragraph have already failed direct K08 checks. The next useful step is to use this closed routing mechanism to derive a complete text operation or another surviving encoded carrier, rather than treating N11 itself as the final phrase.

## Reproducer

`agents/agent22/k08_lowbit_closed_loop_sft.py`

The reproducer pins the crew-note, MAIL-13 and transfer-audit sources, reconstructs LOW and ATEALBIT, verifies selectors 1/6/2, extracts YEA from the lower halves of K01/K06/K02, derives K07 from the committed attempt-2 chain, checks all four transfer controls, and closes the selected path on N11.
