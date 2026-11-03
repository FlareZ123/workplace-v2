# K08 source-indexed N-record and MAIL-word extraction pilot: chronology-shuffle falsifier

**Agent24, 3 November 2026.** Explored the Critic's 19:04 proposed *structured record-to-text channel* as a distinct alternative to editorial caption edits. The original label-masked record IDs do not exhibit source-selective output under the tested finite extraction: 16/16 shuffled-ID placebo contexts produce an equal or higher maximum source-bigram-coherence score than the authentic IDs. **0 original K08 hits in 78,480 complete indexed-word assignments.** This result does not recover the author-final caption and is only a sharply bounded negative for the specified selector.

## Source, intended causal clue and independent controls

The original source identifies an ordered N01–N24 crew-note series and MAIL01–MAIL20 correspondence, with the separate standby inscription at N17, commissioning inscription at N18, and keeper wording only *referenced* in N23. A hypothetical indexing code might select a word from each numbered record using its ID, original source order and the envelope's note number as a key. This differs from Agent8's earlier full-note simple `(a*N+b)%length` sampler by adding a **specific envelope-number term, source-to-envelope temporal filtering, mail-order groups, and independently shuffled record-ID controls**. No historical document claims such an indexer exists.

Read official 24 crew-note entries, source SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, and 20 original mail text bodies. Erase the **two N17/N18 exact inscription lines** as candidate sources, and remove the exact duplicated inscriptions from MAIL11, before any vocabulary extraction. The original exact labels are retained *only as heldout test answers*. The resulting 42 original text documents contain `lights` but no exact singular `light`, as in Agent14's earlier source-masking observation. No lexical morphology or semantic synonym expansion is assumed.

Four preselected indexed input groups: preceding note IDs, preceding Emily-only note IDs, complete mail IDs in original order, and all other source notes, each in its original internal ordering. For each envelope anchor **N17, N18, or N23**, choose the last `L=5..16` eligible records. Extract exactly one word per record at `position=(a*record_id + b*envelope_note_id + c) mod number_of_words`, using `a∈{-2,-1,0,1,2}`, `b∈{-1,0,1}`, `c∈{0..23}`, and either normal or reversed within-document indexing. Join the extracted words in fixed record order. This defines a finite, completely specified original-source selector; no K08 commitment or control label dictates a selected index.

## Complete results

| Envelope anchor | Complete assignments | Distinct complete texts | Exact known inscription | Original K08 SHA256-of-HMAC slot matches |
|---|---:|---:|---:|---:|
| N17 standby | 25,920 | 14,760 | 0 | 0 |
| N18 commissioning | 25,920 | 15,120 | 0 | 0 |
| N23 keeper | 26,640 | 17,390 | Unknown | 0 |
| **Total** | **78,480** | Not globally deduplicated | **0/2 known labels** | **0** |

The original first-draft N02 HMAC control reproduced its exact independent 16-byte value `BF889359B0303F2B2B2FD96AE841210B`. A planted complete N23 indexed text was recovered by the same enumeration and commitment reduction, proving the extraction-to-acceptance path is operational.

**Source-selectivity adversary:** Define the preselected coherence metric as the *maximum number of adjacent extracted word pairs that occur as an intact bigram within any surviving individual source document*, across the N23 extractor's complete candidate family. The authentic original record IDs achieve a maximum of **5**. Independently shuffle ID-to-content assignments in the N series and MAIL series, preserving each entire document, source-type membership and all source words; repeat for 16 seeded shuffles. Shuffled maxima are `[6,6,6,7,6,6,6,5,6,5,6,6,6,6,6,5]`: all **16 of 16 match or exceed** the original source's best score. This coarse language metric cannot discover an exotic non-linguistic code, but it gives **no favorable original-ID evidence for this word-level source indexer**.

## Decision and limits

The specified source-indexed selector neither reconstructs the known inscriptions nor produces a K08 accepted value, and its best text coherence is weak compared with shuffled record IDs. Under this finite mechanism there is no detectable reason to privilege the original record-ID mapping. A source-specific steganographic encoding with a different operation might still exist; the source has no attested literal final-margin words and the method cannot infer a word not expressible from the selected source words (such as singular `light` in the fully masked source).

This is an executed source-channel discrimination with honest heldout/shuffle controls. It should **not** motivate a broader combinatorial catalog of ID/shift formulas without a newly observed source feature that selects an actual producer. Original source, verifier, acceptance and six known components were unchanged; K04 and K08 missing, REC8/1 combined incomplete.

Local read-only SFT `/mnt/data/k08_structured_record_index_sft.py`, SHA256 `3d335dc6be2d819677e91f652ed0d9d6b72c111a83b6a00153ba91acdc83d987`. A portable repository copy is retained under Agent24 for continuation.
