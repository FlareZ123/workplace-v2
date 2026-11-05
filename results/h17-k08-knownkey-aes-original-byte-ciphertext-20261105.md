# K08: source-wide AES-CTR offsets as an incremental carrier exclusion; ECB/CBC prior-art overlap

**Agent 48, 5 November 2026.** The original six accepted REC8 components remain valid. K04's physical 16-byte coupon and K08's author-final caption remain missing, so original combined acceptance remains incomplete. This report records an exploratory alternative to further natural-language caption guessing.

## Target-reaching mechanism

Hypothesis: surviving evidence copied the final keeper caption as one or more encrypted binary blocks, with an AES-128 key reused from one of six already authenticated REC8 components or the two recorded 16-byte K04/K08 nonce/mask fields. An exact decrypted caption would be normalized and fed to the unchanged K08 HMAC16 + SHA256 commitment. This is a **conditional archival-transport hypothesis**. No original note attests encryption, AES, or use of any of those keys to encode the keeper final. **Prior-art correction:** Agent33's [earlier source-wide AES full-object report](h17-agent33-aes-wholeobject-source-negative-20261105.md) already exhausts the core **ECB and CBC** carrier hypothesis over a larger original corpus, with zero readable K08 plaintext. Therefore the ECB/CBC observations here are reproduction/controls, **not new cracking**. The incremental mechanism is explicitly **CTR keystream positions 0..3** under those eight keys and three original IVs, which Agent33 did not report. The changed scanner's 61,695 unique whole-block windows likewise is no claim to broader corpus coverage. It also differs from `agents/agent42/k08_aes_oldcaption_witness_sft.py`, which encrypted/decrypted **known old caption HMAC outputs** and compared them to raw archive carriers.

Extract every 16-byte contiguous raw window and 16-byte decoded ASCII-hex window from the original `evidence/` sources, excluding the selected disputed 18:02 0417 ACK2 copied row before scanning. The exact 61,695 unique windows are searched without assuming the final caption's location. Try eight keys: K01/K02/K03/K05/K06/K07, the K08 desk nonce and K04 route mask. All six components first reproduce their unchanged `acceptance.json` SHA256 digests.

For each key, evaluate 16 genuinely different modes/counter positions: one AES-ECB block decryption; CBC first-block decryption under each of nonce, mask, and zero IVs; and four consecutive first-block CTR keystream offsets under each of those three IVs. Keep every block consisting entirely of 16 printable ASCII bytes for the exact K08 reducer. A stricter English diagnostic requires at least nine alphabetic letters and one space, but the actual K08 acceptance pathway would admit **any** fully printable candidate. Total **61,695 × 8 × 16 = 7,896,960** original full-block decryptions.

A separate multi-block contiguous-packet trial uses the 128 authentic ordinary sequential printer ACKs as two-block binary donors. For each of 127 pairs and all eight keys, evaluate two-block ECB, CBC second-block `D(C2) XOR C1` (independent of IV), and CTR/IV configurations with the same three IVs; the printed source rows are genuine intact controls but are not proven to be ciphertext.

## Executed results

Original source SHA256 pins: printer `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; original notes `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`; route `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`; acceptance `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

Exact local execution on the unchanged 46-file user export:

```text
ORIGINAL carriers 61695 keys 8 views_per_key 16 block_decryptions 7896960
ORIGINAL all_printable 0 readable_phrase_blocks 0 K08_hits 0
ORIGINAL 128packet_pairs 7112 CBC_follow_readable 0 two_block_phrases 0
PLANTED_AES CBC_and_CTR_two_block_controls PASS
```

The CBC synthetic test encrypts a real complete two-block English/zero payload under an accepted key and checks its recovered first block exactly. The CTR synthetic test independently encrypts and recovers the same two-block plaintext. Source checksums and old-key acceptance controls catch archive or key drift. **Zero all-printable original 16-byte plaintexts** were observed, hence zero complete K08 acceptance matches in the tested class. The **5,922,720** CTR decryptions (61,695 windows × 8 keys × 12 CTR views) are the incremental original comparisons, so the overall reported 7,896,960 must never be marketed as a disjoint new search count. The entire read-only [SFT](../agents/agent48/k08_aes_ciphertext_carrier_sft.py) requires NumPy and `cryptography` and reproduces the fixed source/candidate counts.

## Limit

This rules out only the identified AES key/IV/mode/alignment families and a *literal contiguous 16-printable-character plaintext* at the tested block boundary. A shorter text with nonprintable padding, longer text with a mixed partial block, a different key or encryption algorithm, non-AES packing, or a final version never copied into the surviving export remains untested. The experiment adds **no** actual K08 normalized author-final word or K04 physical bit. The sample ciphertext mechanism is conjectural; this result should not be interpreted as historical evidence of encryption. Further trials need a source-supported encoding cue or a true independent original cipher/carrier relation.