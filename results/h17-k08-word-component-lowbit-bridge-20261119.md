# K08 LOW BIT component bridge: TEA -> SEA exactly predicts N10 -> N11

**Agent 22 | 19 November 2026 | target-blind source-stage cross-check**

## New bridge

The earlier K08 chain derived a unique one-row substitution N10 -> N11, producing `ATEALBIT`, then inferred a source-local TEA -> SEA word change from N01. This report supplies an independent accepted-component bridge that makes those two changes coincide exactly.

For a selected 16-byte source-stage block:

1. take the least-significant bit of each byte;
2. pack each eight-bit group first-bit-as-LSB, yielding two bytes;
3. render those bytes as four hexadecimal characters;
4. take the ASCII low bit of those four characters, again first-bit-as-LSB.

Use the selected source-stage material that already reproduces each accepted component:

| Component | Selected source-stage bytes | First LOW BIT | Second LOW BIT |
|---|---|---:|---:|
| K01 | accepted WN-14 ink block | `0479` | **12** |
| K02 | accepted telemetry prehash `E1A5...D507` | `A3FC` | **11** |
| K05 | accepted recorder controls | `0343` | **10** |
| K06 | accepted revision-C strips | `8345` | **10** |
| K07 | committed AX-7782 checkpoints `8947...C5C9` | `53D5` | **11** |

The K02 and K07 source blocks are independently checked by hashing to the accepted K02/K07 components. K01/K05/K06 are already direct 16-byte accepted source blocks.

## TEA -> SEA maps to N10 -> N11

Apply the established ASCII LOW BIT operation to the literal source words:

- `TEA` -> **6**
- `SEA` -> **7**

Read those as component selectors:

- K06 source-stage LOW BIT bridge -> **10**
- K07 source-stage LOW BIT bridge -> **11**

Therefore:

`TEA -> SEA`

maps exactly to:

`N10 -> N11`

This is the same unique row lowering that transforms Emily's source-fixed `ATTALBIT` heads into `ATEALBIT`.

N10 itself says it kept returning to the photograph after the last cup. N01 is the only explicit photograph-labelled source note containing `tea`, and it places `sea` and `tea` in the same sentence. The accepted-component bridge now independently fixes the same 10 -> 11 transition. The earlier tea->sea interpretation no longer stands only on wordplay.

## LOW BIT predicts the same edge directly

The words of the decoded directive give:

- `LOW` -> 6 -> K06 -> **10**
- `BIT` -> 2 -> K02 -> **11**

So the phrase **LOW BIT** itself maps to **10,11** under the selected-component bridge.

The leading `A` maps:

- `A` -> 1 -> K01 -> **12**

Thus **A LOW BIT** maps to **12,10,11**.

Index 12 has two relevant source namespaces. N12 is a card-labelled note, while MAIL-12 is the dated source that says Zoey placed a **small card by the shelf**. The 10/11 outputs are the exact N10/N11 pair already fixed by the row operation. The 12 interpretation therefore remains a carrier locator rather than an exact-text witness.

## Mug shelf gives the reverse pair

N11's source heading is `Mug shelf`.

- `MUG` -> 7 -> K07 -> **11**
- `SHELF` -> 5 -> K05 -> **10**

So **MUG SHELF** maps to **11,10**, the same adjacent pair in reverse order.

This supplies an additional source-local explanation for why N11 is the terminal row of the LOW BIT loop and why its heading is unusually important.

## Why this matters

Three independently structured phrases converge on the same pair:

- `TEA -> SEA` -> **10 -> 11**
- `LOW BIT` -> **10,11**
- `MUG SHELF` -> **11,10**

The inputs come from different source roles: N01 photograph wording, the decoded instruction, and N11's heading. The intermediate selectors traverse independently accepted K02/K05/K06/K07 source material. No K08 digest or target phrase is used to choose the outputs.

This materially strengthens the existing N10 -> N11 / ATEALBIT mechanism and removes the mixed-retry P212 dependency from the strongest local loop.

## Remaining boundary

The bridge identifies the source transition and carrier cluster more sharply. It still does not quote Zoey's missing shelf-card text or Emily's final keeper-envelope wording, so K08 remains unrecovered.

The next useful attack should treat the now-calibrated `12,10,11` and `10,11` selectors as a deterministic extraction instruction over surviving source fields. Broad natural-language generation remains lower value than testing a finite operation implied by these selectors.

## Reproducer

`agents/agent22/k08_word_component_bridge_sft.py`

It verifies the selected K02/K07 prehashes against the accepted components, computes the source-stage LOW BIT map, and asserts the three convergences above.
