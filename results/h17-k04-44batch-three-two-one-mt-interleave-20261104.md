# K04: 44-batch 3:2:1 source interleave and 44 independent MT source controls

**Agent39 | 4 November 2026.** Fresh structural hypothesis based on an exact original-source cardinality relation. The preserved export contains **132 other printer rows**, **88 recorder records**, and **44 seal-receipt records**. The proportions are precisely **3 printer packets : 2 recorder records : 1 seal receipt, repeated 44 times**, with one disputed selected printer packet omitted. This potentially offers a more realistic source construction than concatenating entire file streams into a 624-word MT19937 state. The finite targeted source tests are negative, with independently planted positive MT controls. This is not new accepted K04 evidence.

## Case A: 624-word state from 44 printer/recorder batches

The 132 other 16-byte printer packets furnish 528 four-byte words, while all 88 recorder controls supply 88 more, and previously accepted signed K01 ink strips plus issued K06 procedure strips supply eight. Thus **528+88+8=624** known 32-bit source words. The disputed original selected K04 printed packet remains entirely excluded.

To test whether the 44-source relation reflects historical *interleaved* RNG generation, construct each of 44 batches from 3 printer packets (12 words) and 2 recorder words (2 words), or each of 88 sub-batches from 6 printer words and 1 recorder word. Six fixed arrangements were used: (i) all three printer packets then two recorder words, (ii) alternating one printer packet and recorder word before the third printer packet, (iii) recorder first then printer, (iv) 6 printer words then one recorder, (v) recorder then six printer words, and (vi) two recorder then three printer packets. The eight K01/K06 source words are inserted in one of eight predeclared arrangements at the beginning, middle, end, or bookends.

For each group independently choose big/little-endian and forward/reverse record order, and for printer also reverse within-packet word order. Apply correct MT19937 untemper/twist/temper to the 624 known source words to predict four additional 32-bit words as **the complete missing K04 physical coupon**. For each generated four-word future value, test the eight combinations of native/tempered, byte endianness and word reversal, XOR with unchanged route mask, compare SHA256 to the untouched original K04 slot commitment.

**Original result:** 196,608 complete candidate assignments; 29,248 distinct K04 16-byte values; **zero original K04 acceptance hits**. The 44-batch/administrative-register reshaping predicts all four held-out future MT words on a seeded synthetic Python MT19937 trace.

## Case B: include the 44 original seal-serial words for a genuine source-only holdout

The 44 JSONL seal receipts each carry one eight-hex-digit serial word. Include exactly one corresponding 32-bit serial in each 44-batch alongside the 12 printer words and two recorder words; now each batch has **15 words**, yielding **44×15=660 original source words**, plus 8 K01/K06 administrative words = **668 observed** words.

This creates **44 independently observable source-to-source MT19937 next-state recurrences** for any hypothetical contiguous 668-word output chronology. Six fixed 15-word per-batch interleavings, eight administrative-register placements, and independent group endian/record-reversal options produce **98,304** finite fully specified source layouts. For each layout, evaluate exact native 32-bit recurrence equations at indices i=0..43, comparing the model-predicted output i+624 with the actual intact source word. The disputed selected K04 packet and the K04 target digest are **excluded entirely from this source-only control**.

**Original result:**

| Exact 32-bit matches among 44 original source equations | Source layouts |
| ---: | ---: |
| 0 | **98,304** |
| 1 or more | **0** |

The exact same code path on a seeded 672-output Python MT trace reshaped to the proposed 44-batch source convention passes **44/44 original-source predictions** and reproduces **all four additional future outputs**; it therefore distinguishes correctly modeled sequences in a synthetic positive.

## Interpretation

These are new finite **complete-candidate** and **source-selectivity** tests of a coherent 44-batch architecture suggested by the original record counts. They genuinely extend the [block-concatenated 624-state work](h17-k04-mt624-complete-before-after-coupon-20261104.md): the stronger 668-word experiment has 44 intact observed outputs that can refute the proposed generator independently of K04.

The result rejects only the specified interleaving patterns and serializer choices under an actual contiguous MT19937 producer and faithful sampled source bytes. The exact record counts can arise because the export was assembled in convenient groups; in particular, all 88 recorder records include some CRC-invalid/irrelevant samples and the 44 seal serials include unselected PTWs. Those are **not independently authenticated as one hardware generator stream**. Different historical source ordering, seed resets, intentional omissions or a completely different producer remain open. The 98,304 zero-MT-equality result should prevent further scaling of these exact 44-batch patterns absent a newly discovered causal serializer.

The read-only local scripts created for the research are /mnt/data/h17_mt44_interleave_sft.py and /mnt/data/h17_mt44_with_seals_sft.py. The common source SHA pin/extractors and correct MT inverse were previously committed in [Agent39's initial SFT](../agents/agent39/k04_mt624_mosaic_sft.py). Full source and original commitment were unmodified. No newly authenticated K04 physical coupon bits or verbatim K08 final words have been obtained; REC8 remains six PASS, K04/K08 missing, combined incomplete.
