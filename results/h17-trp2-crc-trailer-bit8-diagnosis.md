> **PRIOR-ART CORRECTION (2 November 2026, Agent23): This entire one-bit CRC diagnosis is an independent replication, NOT new H-17 cracking.** [Workplace-v1 Agent12's 19 October CRC-syndrome report](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-recorder-crc-syndrome.md) already established the identical four invalid indices, syndrome `0x00000100`, unique CRC-trailer bit8 single-bit repair, **and the stronger complete two-bit repair exclusion** (18,336 assignments per record). It also independently found the row72/printer predecessor match and no new target words. The result below is redundant and must not be cited as a new source insight, new K04 constraint, or research advance. The original prior-art report supersedes this narrower replication.

# H-17 TRP2 corruption: four bad records have the same CRC-trailer one-bit explanation

**Agent23, 2 November 2026. Independent original-source checksum replication (superseded by v1 Agent12, 19 October); no recovered K04/K08 slot.** Executable [source-pinned CRC32 single-bit diagnostic](../agents/agent23/k04_trp_crc_trailer_singlebit_sft.py). Original recorder SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`; 88 records of 24 bytes follow a 16byte header. No source bytes, commitments, or verifier were changed.

## Precise question and original data

Four TRP2 records are marked invalid by comparing the stored little-endian uint32 CRC32 at byte offset20 to IEEE/zlib CRC32 of the preceding20 bytes. These are record indices **14, 41, 72, 77** (zero-based). In every case, the checksum difference is exactly **`stored_crc XOR calculated_crc = 0x00000100`**, corresponding to bit8 in the stored CRC trailer.

This common, *identical* single-bit discrepancy is an original-source observation rather than a fabricated expected value.

## Complete one-bit error diagnosis

For a fixed 20byte input length, CRC32 is affine over GF(2), so the XOR syndrome of changing any one data bit is independent of the other 159 data bits. Compute all **160** possible single-data-bit syndromes using the exact `zlib.crc32` variant specified by the TRP2 format note. **None equals `0x00000100`.**

Flipping precisely **bit8 of the stored 4byte CRC trailer** does yield `0x00000100` for a genuinely valid original packet (record28), used as a synthetic corruption positive. Therefore, under the specific model of **exactly one bit corrupted anywhere in the 24byte record**, each of the four invalid records is explained by a CRC-trailer bit8 error, and **no one-bit corruption in the 20byte data region** can explain its checksum discrepancy. The intact four-byte control fields at offset12 would survive that minimum-error mechanism.

This is **conditional fault localization**. Two or more data-bit errors can have the same CRC XOR syndrome, and these results alone cannot certify the four original control words, identify a shared equipment fault, or establish an original printer producer.

## Existing MT bridge and target implication

[The older TRP2-to-printer MT fingerprint analysis](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-trp2-printer-hidden-word-bridge.md) had already found **record72's control word** as a low31 predecessor match for printer row10 word2 → row41 word2, explicitly flagging its bad CRC; this match is *prior art*, not a newly recovered source link. A newly executed all-88-record inverse-twist source sweep independently reproduced the same record72 match and the six known CRC-valid positive matches. The other three invalid CRC records had **no** new printer inverse-twist pair matches (both 32bit byte orders), and none of the seven original cross-carrier matches touches the separate row43/44 or row96/97 K04 target-side windows. No authentic selected K04 bit is obtained.

The checksum diagnosis strengthens a **parsimonious explanation** of why the previously correlated record72 may have retained its native control bytes despite its rejected CRC. It does not modify **K05's mandatory rejection of bad CRC records** under the original route rule. No K04 coupon or K08 phrase is generated and the official six PASS / K04,K08 MISSING / combined INCOMPLETE state is unchanged.

## Reproduction and research decision

Run the linked single-file standard-library SFT at repo root. It pins the unmodified raw recorder SHA256, asserts exactly the four original bad record IDs and identical syndromes, enumerates all 160 data-bit faults, then confirms trailer bit8 on a valid original control. The associated *source-only* MT sweep used [the previous exact inverse-twist identity](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-cross-source-rc17-recorder-bridge.md), held out the selected printer row129, and never consulted the K04 target digest.

The next relevant event-level insight would be independent evidence that the **same trailer-only damage mechanism affected the selected printer's retained payload**, or a new indexed donor inside both missing target gaps. No such link exists in the surviving source. Repeating generic CRC-bit corrections on the 16byte copier value, which has no recorded checksum, is unsupported.
