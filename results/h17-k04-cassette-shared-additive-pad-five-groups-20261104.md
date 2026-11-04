# K04: five carry-aware cancellable printer-pad group laws, complete source-paired negative

**Agent 41 | 4 November 2026 | actual 11,045,970 complete original K04 checks | zero matches.** Original REC8 status unchanged: six individual PASS, K04/K08 MISSING, combined INCOMPLETE.

## New hypothesis

The original 4 October print-fleet retirement docket maps selected north 0417 to L-29/N service tickets and preserved south RECOVER ACK 0448 to L-29/S. A previously checked **unknown shared XOR pad U** hypothesis modeled coupon_lane = U XOR F(ticket_set, metadata). That experiment generated 2,209,194 complete original north candidates, all rejected. The present class instead uses a **shared additive pad U**, where carries and cyclic machine-word boundaries produce distinct coupon values. It is a new 128-bit group law over the same source-paired identifiers, not a repeat of the earlier XOR outputs:

    C_S = U + F(S)  [group modulus]
    C_N = U + F(N)  [same group]
    C_N = C_S - F(S) + F(N) [group modulus]

It permits an *unknown pad* shared between north and south, so Agent10's earlier direct south-F(S) source-negative does not refute it. The source has **no attested common shared pad, additive coupon writer or ticket-to-printer cryptographic relation**. The return docket was reconciled **4 October 09:18 UTC**, after the 3 October target print events, so the service-ticket **recording date cannot itself authenticate pre-print use of those ticket numbers**. The south spool source is likewise a retained buffer, not independently proven physical media. These are explicit limitations of a speculative but mathematically complete selected-coupon mechanism.

## Source-frozen candidate family

Use the exact same **2,106 source-labeled paired north/south ticket metadata encodings** and **25 digest/HMAC16 masks plus four CPython Random seed representations at phases 0..255** from the earlier [cancellable-XOR experiment](h17-k04-cassette-unknown-shared-pad-20261104.md). Independently evaluate five standard additive groups:

| Group | Arithmetic unit / endian | Complete original K04 component checks | SHA256 original hits | Planted whole-source positives |
| --- | --- | ---: | ---: | ---: |
| G128-BE | one unsigned 128-bit big-endian integer mod 2^128 | 2,209,194 | **0** | 2 |
| G128-LE | one unsigned 128-bit little-endian integer mod 2^128 | 2,209,194 | **0** | 2 |
| G32-BE | four separate big-endian 32-bit words mod 2^32 | 2,209,194 | **0** | 2 |
| G32-LE | four separate little-endian 32-bit words mod 2^32 | 2,209,194 | **0** | 2 |
| G8 | sixteen independent byte sums mod 256 | 2,209,194 | **0** | 2 |
| **TOTAL** | 5 algebraically different group structures | **11,045,970** | **0** | **10** |

Every tested full 16-byte derived north physical coupon is reduced with unchanged original route XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C`, then SHA256 hashed against original K04 full commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. Original south source payload `234BE186E97EE05830909790E336109E` at 18:24 UTC and both five-ticket sets are SHA-pinned. Source-selected disputed north ACK2 copy never enters model fitting.

Two positive controls per group plant a nonzero unknown shared U in each exact group, generate independent synthetic south from U plus F(S), and prove reconstruction equals complete U+F(N): one digest role, one genuine CPython stream at phase73. All ten recovered **exact complete** synthetic north objects. They verify sign direction, carry behavior, byte-endian interpretation and group cancellation. They are implementation controls, not independent evidence of original writer behavior.

## Execution and reproducibility

Read-only [portable single-file SFT](../agents/agent41/k04_cassette_common_additive_sft.py) checks source digests for original fleet return register, spool, route and acceptance. It can run all five group families, or each independently with a second argument `add128be`, `add128le`, `add32be`, `add32le` or `add8` for short bounded runs. All five were **actually executed against the unmodified attached original 46-member archive extraction**. Per-group logs each returned:

    PAIRED_SOURCE_FORMS 2106
    COMPLETE_ADDITIVE_K04_COMPARISONS 2209194
    PLANTED_FULL_COUPON_POSITIVES 1 digest, 1 python
    ORIGINAL_K04_HITS 0 []

The checked *assignment* count includes possible duplicate final component values across source masks/groups; it is not an independently unique 11-million-coupon guarantee. This result rules out the five specifically defined common-additive-pad families if north/south share U and the south copy is faithful. Unknown lane-specific secrets, cryptographic multi-block AES modes, independent source generation and physical copier faults remain outside. Zero authenticated physical K04 bits or literal final K08 words were obtained. Do not repeat these exact source-paired additive group tests as new mathematics; target the missing selected physical media or author-final transcription, or a true pre-print source relation.
