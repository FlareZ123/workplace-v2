# K04 original printer/recorder 624-word striped state, all 384 complete output serializers

**Agent 17, 9 November 2026. Source-preserving complete K04 original commitment experiment.** Original six accepted components remain unchanged. K04/K08 and combined acceptance remain unresolved.

## Hypothesis and distinct arrangement

Withhold the event-selected 18:02 ESC-N job PS-261003-0417 attempt-2 reconstructed ACK bytes completely. The 132 other preserved spool packets each contain 16 bytes, supplying 528 original 32-bit words. The 88 retained TRP2 recorder CONTROL fields yield 88 more words. The accepted signed WN-14 K01 and issued RC17 K06 eight source words finish an exact 624-word MT19937 state window.

Earlier source-group MT work (Agent 30 and Agent 39, 4 November) concatenated these four groups in entire blocks. This experiment instead tests a **6 printer + 1 recorder word stripe** repeated exactly 88 times, inserting one of the eight original trusted words into every 11 stripes, with the relative stripe phase and word ordering inferred only from the finite specified layouts. The producer hypothesis and cross-record temporal join are speculative and are not supported by original firmware or producer documentation. It is a direct whole-coupon reconstruction, rather than a brute-force alteration of selected copied ACK2.

## Source and finite complete-value search

Original pinned source:
- Printed payload log SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- Original recorder dump SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`
- Original routing JSON SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- Original K01/K06 hash accepted under unmodified `resources/acceptance.json`.
- K04 mask `8556C8CB6140A7F9A5123AC7571BEE1C`
- Original full K04 slot SHA256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Test 7 recorder positions inside each seven-word stripe, 8 insertion positions for the eighth accepted word, 11 stripe phases, 8 spool row/word/byte orientations, 4 recorder row/byte orientations, and 16 grouped-accepted-word orders/endian views, yielding **315,392 complete 624-word source states**. Invert standard MT19937 temper on the four first state words, their index1 successors and their index397–400 partners; twist to obtain the next four complete 32-bit outputs.

For each complete output, enumerate all 24 permutations of its four words and every combination of big/little endian within each word (16 arrangements). Reduce the whole 16-byte hypothetical physical coupon with the unchanged official XOR mask and check the **complete 256-bit** original SHA256 commitment. Exactly **384 serializers** per model.

| Full original-source search | Results |
| --- | ---: |
| 6+1 record-striped source states | **315,392** |
| Canonical four-output serialization tests | **1,261,568** |
| All word permutations, both uniform word endians | **15,138,816** |
| Mixed individual word-byte endians, excluding uniform | **105,971,712** |
| **All complete original K04 checks** | **121,110,528** |
| Original K04 commitment matches | **0** |
| Synthetic seeded MT next-four-word control | **4/4 PASS** |

The original source-matched local Python scripts executed independently over unchanged user-supplied ZIP extraction: `k04_braided_mt_sft.py`, `k04_braided_mt_perm48_sft.py`, and `k04_braided_mt_mixed336_sft.py`. The 48 uniform-layout run finished with zero original matches; the remaining 336 mixed-endian layouts completed their **105,971,712** full SHA256 original checks in **261.214 seconds**, zero original matches. The genuine seeded `random.Random` 628-output positive correctly regenerated four withheld MT words from the preceding 624 source words, and independently checked temper/untemper inversion. Source checks verify selected 18:02 ACK event header but exclude its copied disputed payload.

## Interpretation

This directly rejects the specified **six-printer-one-recorder interleaving architecture** when the 624 observed words are assumed to be an adjacent full native MT19937 output window and the selected coupon is the next four outputs. The numerical 624-word coincidence is insufficient to establish real historical co-generation. Other stream chronology, source-generated time-indexed issuer, paper/copy-stage transformation, independent physical original or author-final K08 wording remain open. **Actual independently authenticated original K04 bits remain 0/128; exact K08 final words remain unquoted; six PASS and combined INCOMPLETE.**

Do not rerun the same 6:1 braid with another arbitrary output byte-order menu. A materially different mechanism must explain an independent historical whole-output control and supply the selected physical/copy-stage value, or directly recover a source-authenticated author-final caption.
