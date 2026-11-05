# K08 whole-source nonce replacement (5 Nov 2026)

**Agent 9.** Complete original-target test. **310,224 SHA256-of-HMAC16 comparisons, zero original K08 matches.** Six individually accepted slots remain PASS. K04 and K08 remain missing, combined REC8/1 incomplete.

## Distinct source-cued model

The original K08 routing rule identifies the complete 16-byte nonce `5F933DA6A1BD03C32DA5CBC25344F497`. A hypothetical **whole-field transcription substitution** might replace that nonce by another intact sixteen-byte field actually in the retained archive. Prior Agent12 investigated only one/two-byte nonce corruption and shared word reordering over nine quoted captions. This new family replaces the key *entirely* using full original source fields and considers many more exact literal texts. There is no historical claim that the route nonce was altered.

Read the 46 unmodified original ZIP files, extract all exactly bounded 32-hex-character fields; add complete file SHA256 first16/last16 and MD5 digests, the six official accepted components and original K08 nonce. Deduplicate to **276 original/source-derived 16-byte keys**. Test four whole-key layouts: natural, reversed 16-byte order, reversed bytes within each 32-bit word, reversed order of four whole 32-bit words.

Build complete text candidates from the 24 crew-note bodies and caption-after-colon phrases, and from all 20 surviving mail bodies, paragraphs, and individual sentences. The official ASCII alphanumeric/whitespace normalization yields **281 different complete source texts**.

For every key/text, HMAC-SHA256 with the candidate key and normalized UTF-8 text, truncate to sixteen bytes and check all 256 bits of SHA256 against the untouched original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

## Original executable outcome

```text
source 16byte key fields       276
normalized source texts       281
complete key layouts            4
full original K08 checks   310224
genuine original K08 matches    0
synthetic full-source positive  1
```

Source SHA256 controls: spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; notes `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`; route `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`.

The real N02 original caption control generates exact HMAC first16 `BF889359B0303F2B2B2FD96AE841210B`. A separate full synthetic target planted under the *different original K04 route mask as key* and authentic N17 standby caption was recovered exactly once. Synthetic hashes are separate from the original untouched K08 target.

The read-only [source-pinned SFT](../agents/agent9/k08_whole_source_nonce_replacement_sft.py) reproduces the source cardinalities, all full comparisons and controls.

## Boundary

This excludes **only** the named whole-key substitution, layout and complete source-text families. There is no evidence the original HMAC nonce was corrupted or that Emily's final chosen margin line is one of the surviving quotes. The true final wording remains absent, no original K04 coupon bit was authenticated, and combined acceptance remains INCOMPLETE.
