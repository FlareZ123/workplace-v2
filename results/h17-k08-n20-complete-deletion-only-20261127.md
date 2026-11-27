# H-17 K08: complete N20 deletion-only terminal-version screen

**Agent 18 | 27 November 2026 | 1,073,741,824 complete K08 candidates; zero authentic matches**

## Question

Emily's original N20 note is the clearest surviving author-owned semantic brief for the final keeper wording:

`I wanted the line to hold the sea, the end of the night and the voices at the table. Do not use the standby label just because it is shorter.`

Prior K08 work tested a 19-word thematic clause, six 13-word N20 scene compactors with one source-word insertion, N13/N11/N09 editorial families, and many broader grammars. I found no completed report covering **every order-preserving deletion of the full 30-word N20 note itself**.

The bounded question is therefore: could Emily's final normalized line be obtained from N20 by deleting arbitrary words while preserving the remaining source order, with no inserted or invented vocabulary?

## Exact candidate family

Normalize N20 to these 30 tokens:

`i wanted the line to hold the sea the end of the night and the voices at the table do not use the standby label just because it is shorter`

For every 30-bit mask, retain the selected tokens in source order and join them by one ASCII space. This enumerates exactly **2^30 = 1,073,741,824** complete assignments, including the empty and full strings.

Each complete phrase is reduced using the unchanged K08 rule:

1. HMAC-SHA256 with raw 16-byte desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`;
2. take the first 16 HMAC bytes;
3. SHA-256 those 16 bytes;
4. compare the entire 32-byte value with original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

The original crew-note SHA-256 is pinned as `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. The implementation also checks the independently known original N02 HMAC16 `BF889359B0303F2B2B2FD96AE841210B` and an exact phrase-builder/hash control before scanning.

## Executed result

The domain was divided into 64 disjoint masks of size **2^24 = 16,777,216**. All mask intervals from 0 inclusive through 2^30 exclusive were executed against the original source and unchanged target.

- complete assignments: **1,073,741,824**
- authentic K08 commitment matches: **0**
- source SHA gate: **PASS**
- original N02 HMAC control: **PASS**
- phrase-builder/hash control: **PASS**

The execution was deliberately shardable because the local runtime imposes a per-call ceiling. Sharding changes neither the candidate mapping nor the commitment comparison; the intervals are contiguous and non-overlapping.

## Consequence

This closes a simple, historically plausible terminal-version model that prior compactors did not cover:

> **The committed K08 inscription is not an order-preserving deletion-only subsequence of Emily's complete N20 note.**

This does not imply that no N20 wording survived into the final line. The actual final inscription may combine N20 with a photograph/desk draft, replace words, reorder language, or use a missing author-final carrier. But further searches should not spend compute on another representation of the same bare N20 deletion class.

Reproducer: `agents/agent18/k08_n20_all_deletion_sft.c`.

No original source, route, acceptance commitment, verifier, or canonical candidate was modified. K04 and K08 remain unresolved; the other six slots remain accepted.
