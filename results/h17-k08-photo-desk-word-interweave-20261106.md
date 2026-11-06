# K08 source-role word interweaving, 6 Nov 2026

**Agent 21.** Original K08 component **not recovered**. This is a bounded original-source, fully normalized HMAC16 + SHA256 test of a new *editorial merge* operation. The original verifier, acceptance commitments and supplied ZIP were read only.

## Hypothesis and why this is different

MAIL11 says Emily worked out final wording from desk notes and photograph captions, while N20 names the sea, the end of the night and voices at the table. An interleaving of **two source strands** is one exact alternative to previously exhausted contiguous snippet concatenation, source-bigram walks and the assumption that N13's entire prefatory clause must survive.

Choose a single contiguous **3–9 word span** from each of two independent source roles:

- A photograph caption from N01, N08, N09, or N14, containing at least one of `sea water night boat tea cup rain horizon daylight window colors morning first last`.
- An Emily-authored desk/draft/recollection entry from N02, N06, N10, N13, or N20, containing at least one of `room watch hands lamp window night mugs voices table sea cup people morning tea corridor`.

For each pair, require the *combined* spans to contain at least one literal token from each set `{sea,water}`, `{night,watch,morning}`, and `{room,voices,table,people}`. This ensures direct contact with all three source-stated themes before a candidate is generated. Exclude older, explicitly wrong-purpose standby and commissioning inscriptions N17/N18.

Emit every order-preserving two-strand interleaving. In addition to taking the next token from either source, when both next tokens are *identical*, allow consuming both and writing that token just once. This coalescence is a common-supersequence editorial merge and produces full strings that fragment concatenation alone cannot generate. Both spans retain their internal word order, but there is **no forced initial N13 prefix** and no requirement to keep all of N13. Lowercase ASCII alphanumeric tokenization and joining words with one space already implements the original normalization for these emitted strings.

This is a *speculative authoring/copy operation*. No surviving source authenticates an interleaved physical caption, or the exact final line. Its usefulness is as a bounded complete-candidate generator with a different structural bias.

## Full original-source outcome

The original crew source is SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. Source extraction yields 172 photograph spans and 297 Emily spans. Exactly **1,607 source-role span pairs** satisfy all three literal motif groups.

Every complete emitted candidate is reduced using original desk nonce `5F933DA6A1BD03C32DA5CBC25344F497` to `SHA256(HMAC_SHA256(nonce, caption)[:16])`, and compared to the **unchanged** original full K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

| Photograph source | Qualified span pairs | Complete construction assignments | Original K08 matches | Synthetic planted positives |
| --- | ---: | ---: | ---: | ---: |
| N01 | 511 | 3,267,571 | **0** | 1 |
| N08 | 994 | 7,490,106 | **0** | 1 |
| N09 | 43 | 526,475 | **0** | 1 |
| N14 | 59 | 833,280 | **0** | 1 |
| **Total** | **1,607** | **12,117,432** | **0** | **4** |

The counts are complete **assignments**, not necessarily distinct normalized texts, because different interleavings can produce identical words. The Python SFT includes a SHA-pinned 24-note parser, the historically known N02 draft HMAC16 fixture (`BF889359B0303F2B2B2FD96AE841210B`) and an independently planted, complete motif-qualified interleaved caption whose constructed digest is detected in each source shard. Every original source shard completed locally against the attached 46-file ZIP with all assertions passing.

The portable source is [Agent 21's word-interweave SFT](../agents/agent21/k08_photo_desk_word_interweave_sft.py), supporting a photograph N-ID argument for deterministic, bounded shard runs. All four executed source shards are disjoint by photograph-note ID, so their exact assignment counts add without duplicate model assignments.

## Interpretation and next different attack

The true final caption is absent from this precisely defined two-strand 3–9-word source-anchored editorial-merge family. This does **not** prove that Emily did not combine photographs and desk recollections, because prose could be newly authored, use a different edit operation, or retain unseen words. Source selection and final-caption version are still unauthenticated.

Do **not** multiply fragment length bounds or add unconstrained synonym permutations as an automatic sequel. This experiment probes a distinct interleaving mechanism and it fails. New source-stage evidence, a genuine final text carrier, or a demonstrably source-selected author-final operation would warrant a different attack. K04's physical coupon remains unverified, and six prior REC8/1 slots PASS, K04/K08 MISSING, combined INCOMPLETE.
