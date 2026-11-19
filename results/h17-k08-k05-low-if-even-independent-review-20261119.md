# K05 alternate-retry LOW-IF-EVEN review

**Agent 43 · 19 November 2026 · independent source replay**

## Question

Does the proposed K08-side `LOW IF EVEN` interpretation uniquely select the K05 alternate retry rows, and how specific is the resulting `0A4D = M10` output?

This is an independent review of Agent35's frozen reproducer, not a new retry-stratum search. The review independently parses the original TRP2 records, reproduces the official K05 reducer, and enumerates all 16 low/high choices.

## Inputs and method

Pinned inputs:

- `resources/evidence/recorder/trip-recorder.raw`, SHA-256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`.
- `resources/evidence/recovery-routing.json`, SHA-256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`.
- `resources/evidence/recorder/format-note.txt`, which defines offset 16 as a uint32 auxiliary process reading and offset 20 as CRC32.

The independent parser checks the TRP2 header (`TRP2DUMP`, version 2, 24-byte records, 88 records), rejects bad CRCs, then applies only the published K05 node, event and UTC window. It finds exactly eight valid matches: two for each latch 0–3. The matching sequences are 200+latch and 300+latch.

The authoritative route selects the greatest sequence per latch. It therefore selects sequences 300,301,302,303 and produces:

`FF8B78200A56E8586DCDA00EF01E4572`

This exactly matches the existing K05 candidate and K05 acceptance commitment. Its byte-LSB / first-bit-as-LSB pack is `0343` (the existing C3 reading).

## Frozen alternate interpretation

The reviewed interpretation treats “LOW IF EVEN” as: choose the lower sequence for even latch ordinals and the higher sequence for odd latch ordinals. With bit 1 meaning “higher”, this is mask 10 / `LHLH` across latches 0–3. It selects:

| Latch | Selected sequence | Control word |
|---:|---:|---|
| 0 | 200 | `42BFD053` |
| 1 | 301 | `0A56E858` |
| 2 | 202 | `6FC2B743` |
| 3 | 303 | `F01E4572` |

The resulting alternate 16-byte block is:

`42BFD0530A56E8586FC2B743F01E4572`

Its byte-LSB pack is `0A4D` (`M10`). The alternate block does **not** hash to the K05 acceptance commitment; it is not an alternate K05 recovery value.

## Exhaustive mask specificity

All 16 per-latch low/high masks were enumerated. `L` means the lower sequence; `H` means the higher sequence.

| Mask | Latches 0–3 | Sequences | LOW BIT output |
|---:|:---:|---|---|
| 0 | LLLL | 200,201,202,203 | `0A1D` |
| 1 | HLLL | 300,201,202,203 | `031D` |
| 2 | LHLL | 200,301,202,203 | `0A1D` |
| 3 | HHLL | 300,301,202,203 | `031D` |
| 4 | LLHL | 200,201,302,203 | `0A13` |
| 5 | HLHL | 300,201,302,203 | `0313` |
| 6 | LHHL | 200,301,302,203 | `0A13` |
| 7 | HHHL | 300,301,302,203 | `0313` |
| 8 | LLLH | 200,201,202,303 | `0A4D` |
| 9 | HLLH | 300,201,202,303 | `034D` |
| 10 | LHLH | 200,301,202,303 | `0A4D` |
| 11 | HHLH | 300,301,202,303 | `034D` |
| 12 | LLHH | 200,201,302,303 | `0A43` |
| 13 | HLHH | 300,201,302,303 | `0343` |
| 14 | LHHH | 200,301,302,303 | `0A43` |
| 15 | HHHH | 300,301,302,303 | `0343` |

There are eight distinct two-byte outputs. `M10` (`0A4D`) occurs for **two** masks: 8 (`LLLH`) and 10 (`LHLH`). The difference is latch 1, whose two control words (`8052760C` and `0A56E858`) have identical byte-LSB vectors (`0000`). Changing that latch's row therefore cannot change the two-byte LOW BIT output. The exact M10 match is real, but the output does not uniquely identify the proposed LHLH selector; it occurs for 2/16 possible masks. This finite share is not a formal probability for the historical process.

The official `HHHH` mask yields `0343`, but `HLHH` (mask 13) yields the same low-bit output. Thus the two-byte low-bit result is not an injective encoding of the four row choices.

Controls:

- Reverse parity (`HLHL`, mask 5) gives `0313`, not M10.
- All-low (`LLLL`, mask 0) gives `0A1D`.
- Official all-high (`HHHH`, mask 15) gives `0343`.
- The alternate raw block's SHA-256 is `d0cc084d08aa766786f2e724a91827bfc15cb454d4a44946374f3199726008e3`, not the K05 commitment.

## What “even” is applied to

The K05 sources do not say “LOW IF EVEN”; that cue comes from the separate note-chain interpretation. The mapping of “even” to *latch ordinal parity* is an additional assumption.

Two source-field observations make the ambiguity concrete:

1. Both candidate sequence numbers for a given latch have the same parity as that latch, because the two sequence bases (200 and 300) are even. So “even sequence” cannot distinguish the lower and higher row within a latch.
2. The auxiliary process readings are 4312 for all lower-sequence rows and 4318 for all higher-sequence rows; both are even. If “even” were applied to this defined uint32 field, every row would qualify and “LOW” would select all lower rows (`LLLL`, output `0A1D`), not `M10`.

The LHLH result therefore depends on choosing latch ordinal as the parity variable. That is a plausible cross-record interpretation, but it is not specified by the recorder format or K05 route.

The note-side cue is itself conditional. The earlier note decoder assembles “LOW IF EVEN” from the selected count string and N11's opening word; Agent9's independent audit found the optional low-if-even byte was not unique across the seven valid one-row lowerings (it yielded A for three). This review does not independently validate that note decoder or turn the cue into a source-authenticated K05 selection rule.

## Assessment

Preserve the `0A4D = M10` equality as a **conditional cross-carrier LOW BIT consistency observation**. It is not:

- the accepted K05 component;
- a uniquely selected alternate K05 block;
- proof that the historical recorder used latch-parity selection;
- independent evidence that `mug-stock.xls` is the active K08 carrier; or
- any recovered K08 wording.

The exact low-bit equality remains potentially useful, but its selector specificity is limited by the two-mask alias and the unbound parity variable. Do not widen retry/revision strata on this basis alone.

## Reproduction

From the repository root:

`python agents/agent43/k08_k05_low_if_even_independent_review.py`

The standard-library reproducer pins the original recorder and route, checks the official K05 commitment only, enumerates all 16 masks, and never reads the K08 commitment or candidate phrase.

**Outcome:** official K05 remains accepted; K04/K08 and combined REC8/1 are unchanged. No source, route, candidate, acceptance commitment, or verifier was modified.
