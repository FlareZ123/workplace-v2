# K04: exact V.17/V.29 self-synchronizing scrambler test

**Agent 6 — 16 November 2026. Original K04 commitment: NO_MATCH.** This is a bounded, source-motivated complete-object constructor test, not a recovered component. K04 and K08 remain unresolved; the six accepted slots are unchanged.

## Hypothesis and source boundary

Crew note N22 says the label printer had been behaving “like a fax machine.” This is an informal observation, **not** engineering documentation that ESC-N used a fax modem. It motivates one narrowly specified hypothesis: the selected 16-byte spool payload may be a fragment of a V.17/V.29 self-synchronizing scrambled bitstream, with an unknown preceding 23-bit history.

The official ITU-T V.17 and V.29 recommendations specify the generator polynomial (1+x^{-18}+x^{-23}):

- [ITU-T V.17 (1991), §4](https://www.itu.int/rec/dologin_pub.asp?id=T-REC-V.17-199102-I%21%21PDF-E&lang=e&type=items)
- [ITU-T V.29 (1988), §9](https://www.itu.int/rec/dologin_pub.asp?id=T-REC-V.29-198811-I%21%21PDF-E&lang=e&type=items)

This is distinct from the previously tested additive 16-bit LFSR family. The 23-bit state here is the unknown preceding transmitted-bit history of a self-synchronizing scrambler/descrambler.

## Pinned input

- Source: `evidence/print/spool-reconstruction.log`
- Source SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- Selected row: `2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER`
- Payload: `A9A9DC5731A5E2AE879C47215C2559D5`
- Route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`
- Original K04 SHA256 commitment: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`

The candidate operation remained the source-prescribed XOR with the route mask after applying the hypothesized bitstream transform. No source file, route, mask, acceptance commitment, candidate file or verifier was changed.

## Exhaustive construction

For received scrambled bits (s[n]), the descrambler recurrence is:

```text
d[n] = s[n] XOR s[n-18] XOR s[n-23]
```

For message bits (d[n]), the transmitter recurrence is:

```text
s[n] = d[n] XOR s[n-18] XOR s[n-23]
```

The preceding 23 bits were enumerated exhaustively, not guessed. For each candidate output, the unchanged 16-byte route-mask XOR and full original SHA256 commitment were checked.

| Branch | Preceding states | Full K04 checks | Matches |
|---|---:|---:|---:|
| MSB-first descramble | 8,388,608 | 8,388,608 | 0 |
| LSB-first descramble | 8,388,608 | 8,388,608 | 0 |
| MSB-first scramble | 8,388,608 | 8,388,608 | 0 |
| LSB-first scramble | 8,388,608 | 8,388,608 | 0 |
| **Total** | **33,554,432** | **33,554,432** | **0** |

The search uses Gray-code enumeration over the 23-bit history. The transform is linear in that history, so 23 basis streams suffice to generate every state without recomputing the recurrence for every candidate.

## Validation

- Synthetic scramble/descramble inverse controls passed in both bit orders.
- Basis reconstruction matched direct recurrence evaluation for representative states in all four branches.
- A full planted positive test recovered the unique synthetic history `0x5A3C12` and the exact planted 16-byte component.
- The original spool hash, selector, mask and K04 target were pinned before the candidate search.

The local execution took approximately 86.7 seconds for the four original branches, excluding the separate synthetic positive control.

## Interpretation and limits

**No original K04 bits were recovered.** This excludes only the specified V.17/V.29 polynomial, the two tested byte-bit serializations, the two transform directions, byte-aligned 16-byte input, the source-prescribed post-transform XOR mask, and every possible 23-bit preceding history.

It does not prove anything about ESC-N firmware. N22 remains an informal clue. This test does not cover bit-phase offsets, byte permutations, other fax standards, a different mask, or a different producer/copy stage. Do not widen the fax-standard or framing grid without new physical ESC-N documentation or an authenticated native job.

Reproducer: [`agents/agent6/k04_v17_v29_scrambler_sft.py`](../agents/agent6/k04_v17_v29_scrambler_sft.py).

No additional verifier PASS, K04 value or K08 phrase was obtained.
