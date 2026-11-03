# Agent33: two unexplored K04 recovery models, 3 November 2026

**No recovered component.** The original six accepted slots remain unchanged; K04/K08 remain missing, combined REC8 incomplete. These source-conditioned models are exploratory. Original evidence, commitments and verifier were not altered.

## Shared printer/route-mask byte serialization fault

The selected copied payload and route mask might have undergone a *common* physical lane serializer, in which both 16byte operands are permuted identically, instead of either operand independently as tested by other workers. The derived 16byte coupon is therefore the same permutation applied to the observed XOR result `2CFF149C50E54557228E7DE60B3EB7C9`. Freeze four 4byte lanes; permute lanes in 24 orders and independently permute bytes inside each lane in 24 orders, for **24^5 = 7,962,624** complete candidate assignments. All 16 XOR-result bytes are unique, so the candidate coupons are distinct.

A locally executed C/OpenSSL SHA256 solver hashed all 7,962,624 coupons against the **unaltered** original K04 SHA256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. **Zero original commitment hits.** A deliberately nonidentity lane-and-byte permuted synthetic coupon was independently hashed and recovered **exactly once** within the complete enumeration. This specifically differs from payload-only permutations, mask-only permutations, and the earlier dual 32bit-lane (384×384) cross-product. It cannot exclude a more general 16byte permutation, changed original bytes, different mask transcription or a different producer.

## Source-derived string-seeded printer generator

A distinct CPython `random.Random(str)` producer hypothesis was tested against **132 intact original printer packets**, withholding the disputed selected ACK. Seed lexemes were derived from the original **nonprinter** records only, excluding random hex payloads and original acceptance values. **2,167** lexemes yielded **2,660** archival-name/identifier/textual combined seeds. Each was tested at stream offsets 0..16,383 against all intact original 128bit packets in the two word-endian and two word-order representations: **five firstword coincidences; zero complete source packet matches**. A separate 14-format per-job textual-seed family tested all 132 intact rows at 1,024 offsets per form and produced **zero complete 128bit matches**. Synthetic deterministic seeded word-offset controls passed.

This eliminates those precise source-conditioned string-seed constructions, not arbitrary CPython secrets or unrelated printer generators. It provides no selected coupon bit.

The stronger source-model target-observability finding is separately preserved in [the recorder ceiling report](h17-k04-idealized-recorder-target-observability-20261103.md), which demonstrates substantial residual K04 degrees of freedom even after optimistic fixed-index original recorder/transfer stages.

**Next work:** prioritize obtaining a source-authenticated *selected physical* coupon/copy witness or an indexed future-stage donor. For K08, the original final margin/envelope wording remains absent, and another undirected paraphrase lottery has little evidence value.
