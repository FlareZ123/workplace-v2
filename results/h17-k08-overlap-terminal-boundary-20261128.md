# K08: AT -> MT -> ET/PT overlap chain reconstructs the complete N20 motif payload

**Agent 45 | 28 November 2026 | source-only finite overlap decoder; final author wording still unresolved**

## Question

The earlier Agent45 checkpoint showed that the source-emitted literal address `AT` and the independently constructed `MT` address select two uniquely strong common spans with N20. Can the already-emitted operator vocabulary continue that chain *without* consulting the K08 commitment and recover the remaining social motif with a source-visible stop?

## Frozen continuation

This extension reads only the pinned 24-note crew source. It never reads the K08 desk nonce, HMAC target, `acceptance.json`, or `candidate.json`.

1. Reproduce the existing `AT -> N01/N20` and `MT -> N13/N20` unique maximal common spans.
2. Apply the already-emitted **LEN** operator to the `MT` common span. Its word length is **5**, hence ordinary A1Z26 gives **E**. Preserve the existing N20 pivot `T`, yielding address **ET**.
3. `ET -> N05/N20` has one unique maximal common span of **2** normalized words. In N20 it begins **immediately after** the five-word `MT` span.
4. From the end of that `ET` span, scan forward in N20 for the earliest normalized contiguous span of length >=2 that is also present in any other numbered note. The earliest such downstream boundary is unique and is address **PT -> N16/N20**.
5. Apply the already source-emitted **BETWEEN** operator to the two boundaries: the words strictly between the end of the ET span and the start of the PT span form one four-word segment.
6. The PT common span is the first two normalized tokens of N20's second sentence. Thus PT is a source-visible stop boundary for the first-sentence payload rather than a stop chosen after reading the target.

Raw recovered source wording is omitted under the repository output boundary. The SFT asserts word counts, exact source positions, and SHA-256 fingerprints.

## Results

- AT span: 2 words, N20 start index 6 (zero-based), SHA-256 `556713372501bc1d2a113beaf1fe4fe921267d5cd0c9655b2386ec536a6bffa0`.
- MT span: 5 words, N20 start index 8, SHA-256 `a9bb20e02706cf2079ed0a11b3fededd1c9325edeea5925734f7592ca7c943c9`.
- ET span: 2 words, N20 start index 13, SHA-256 `44359e21492d788147966d8c0bc5beb2f4f4d0d05dd36f3ff36a0cd36a349907`.
- PT stop span: 2 words, N20 start index 19, SHA-256 `9ad80878ed715fd6a1b1bf2b353e344a3dda762a4f3f5c713ccb2dad3d01d88f`.
- BETWEEN(ET,PT): 4 words, SHA-256 `1c142a3af93b7bf154aa022daf9431d6d38599c9e880e043a7b5185ca5142401`.
- Complete reconstructed first-sentence motif payload from AT through the word immediately before PT: **13 normalized words**, SHA-256 `4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c`.

The ET span is exactly adjacent to the MT span. PT is the unique earliest downstream repeated >=2-word boundary after ET. The BETWEEN segment therefore has no free lexical or placement choices.

## Meaning

This materially upgrades the source-local K08 path from two isolated motif coincidences to a finite overlap decoder that reconstructs **all three N20 motif regions and stops at the source's second-sentence prohibition**. It uses only already-emitted operations: A1Z26 addressing, LEN, and BETWEEN.

It still does **not** recover the keeper's author-final caption. N20 is explicitly a semantic brief and the literal reconstructed motif payload has already been checked elsewhere as a complete K08 negative. The next useful step is therefore an exact source-visible edit/version operation from this now-deterministic N20 payload (or its selected N09/N13 antecedents) to the missing N23 margin wording. Do not widen this result into another paraphrase grammar.

## Reproducer

`agents/agent45/k08_overlap_terminal_boundary_sft.py` pins the original crew-note SHA, reproduces the four address spans, verifies ET adjacency, enumerates every downstream repeated >=2-word N20 span to prove PT is the first eligible stop, extracts BETWEEN(ET,PT), and emits only aggregate positions/lengths/fingerprints.
