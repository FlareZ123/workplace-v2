# K04: bounded CCITT T.6 Group-4 first-line test (negative)

**Date:** 2026-11-13  
**Owner:** Agent 20  
**Status:** No strict parse; no candidate; no K04 recovery.

## Question

Does the selected North printer ACK/RECOVER payload decode as one 128-pixel, one-row CCITT T.6 Group-4 strip using the standard all-white initial reference row? If so, does packing the decoded raster into 16 bytes and XORing the unchanged K04 mask produce a component matching the acceptance commitment?

The only source cue motivating this codec hypothesis is noticeboard item N22: “The label printer has spent another morning thinking it is a fax machine.” This is anecdotal, not an explicit statement that the printer emitted CCITT data.

## Pinned inputs

The script verifies these exact source hashes before testing:

| Source | SHA-256 |
|---|---|
| \`evidence/print/spool-reconstruction.log\` | \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\` |
| \`evidence/recovery-routing.json\` | \`f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5\` |
| \`acceptance.json\` | \`681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f\` |
| \`evidence/crew/noticeboard-and-desk-notes.txt\` | \`13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb\` |

The selected record is exactly:

- Job: \`PS-261003-0417\`
- Attempt: \`2\`
- State/class: \`ACK / RECOVER\`
- Payload: \`A9A9DC5731A5E2AE879C47215C2559D5\`

The unchanged K04 mask is \`8556C8CB6140A7F9A5123AC7571BEE1C\`. The required K04 SHA-256 commitment is \`930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0\`.

## Frozen decoder and candidate space

The reproducible implementation is \`agents/agent20/k04_t6_group4_first_line_sft.py\`.

It implements the standard T.6 2D mode codes for pass, horizontal, and vertical offsets 0/±1/±2/±3, followed by the standard Modified-Huffman white/black run tables. The extension mode is excluded. The row width is fixed at 128 pixels; the reference row is the standard all-white first-line reference. The decoder uses an explicit coordinate convention (\`a0=-1\`, \`b1=b2=127\)) and requires every pixel to be assigned and every encoded bit to be consumed.

The only target framing interpretations are FillOrder 1 or 2, with either no EOFB or the standard 24-bit EOFB, and 0–7 zero pad bits. For any strict parse, the decoded row is packed into 16 bytes under both photometric polarities and both output bit-packing orders, XORed with the unchanged K04 mask, and checked against the unchanged commitment.

No byte reversal, leading fill bits, arbitrary bit shifts, alternate widths, multi-line reference donors, uncompressed extensions, arbitrary code tables, or ad hoc predictor/permutation families were introduced.

## Decoder controls

Two independent Pillow/libtiff Group-4 fixtures supplied by Agent 43 pass:

1. A 17-byte 128×1 strip, \`3314CC53314CC53314CC53314CC5001001\`, with byte-aligned EOFB. It decodes to \`00FF00FF00FF00FF00FF00FF00FF00FF\`.
2. An exact-16-byte 128×1 strip, \`26A3290183832E060CCCF07050010010\`, with EOFB beginning at bit offset 100 and four trailing zero pad bits. It decodes to \`FE0000003FFFE0FE7FFFFFC03E07FF87\`.

Both fixtures also pass when each compressed byte is bit-reversed and decoded as FillOrder 2. In the execution environment, 100 deterministic random 128×1 Group-4 rows generated independently through Pillow/libtiff 12.3.0 also pass under FillOrder 1 and the equivalent bit-reversed FillOrder 2.

These controls validate the bounded decoder and packing path; they do not establish that the H-17 payload is a fax strip.

## Result

For the selected 16-byte H-17 payload:

- Only two framing suffixes matched: the empty/no-EOFB/no-padding interpretation under FillOrder 1 and FillOrder 2.
- Strict 128-pixel T.6 parses: **0**.
- Unique decoded 16-byte coupon candidates: **0**.
- K04 commitment hits: **0**.

No K04 component was produced. This model is rejected for the selected payload.

## Prior-art distinction and scope

This is distinct from the earlier generic fax-named searches:

- \`results/h17-k04-fax-2d-predictive-copy-20261105.md\` tested 2D neighbor-predictive XOR families.
- \`results/h17-k04-fax-bitplane-global-bit-order-20261105.md\` tested global bitplane/bitposition layouts.

Those searches are not being reopened. This result covers only the standards-conforming, single-row, 128-pixel, all-white-reference T.6 Group-4 hypothesis. It does **not** rule out every printer or fax encoding, multi-line stream, or other copy-stage mechanism. There is no basis to widen this branch without new source evidence.
