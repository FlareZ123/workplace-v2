# K08: relative AES transport from authentic note HMACs to aligned printer jobs

**Agent 5 | 9 November 2026 | Original-source whole-caption holdout rejection**

The recently documented [note-to-spool alignment](h17-k08-note-spool-metadata-bytechannel-holdouts-20261109.md) places N02/N06/N13/N17/N18 under PS-0302/0306/0313/0317/0318 and N23 (the unquoted keeper final-margin locator) under PS-0323. This chronology+metadata alignment remains a **hypothesis about historical text-to-print transport**, not an authenticated queue-to-envelope map.

## New invertible transport construction

A source-invertible alternative to the existing raw-hash, byte-affine and GF128 note transport mechanisms is **one-source AES-128** with a common unknown copy-stage XOR mask. For any normalized original note `N`, form the official `H = HMAC_SHA256(original_desk_nonce,N)[:16]`. Model printer payload `P` as either `AES_K(H) XOR pad` or `AES_K(H XOR pad)`, or the same two laws using AES decryption. No original evidence asserts this AES producer; the fixed 16-byte pad is learned from the complete original **N02 ↔ PS-0302** control only.

Eight known keys: six individually accepted components, original route mask, and original desk nonce. Apply four whole-block/word-byte views independently to HMAC and printer data. This creates exactly **8 × 2 cipher directions × 4 HMAC views × 4 spool views × 2 pad positions = 512 complete issuer models**. Each predicts four *genuine complete withheld original HMAC16s*: Emily N06, N13, N17 and N18. The original N02 HMAC control matches the independent published value `BF889359B0303F2B2B2FD96AE841210B`. N13 is scene prose, not explicitly a printed label, which limits the assumed carrier family.

For every model, **invert the source transport** on the original PS-0323 16-byte payload to recover a complete hypothetical K08 HMAC16 component **without guessing a single word of Emily's missing final caption**, then compare the untouched full SHA256 K08 commitment. This is a direct component attack conditional on the independent note-to-printer association.

## Executed original result

The read-only [standalone SFT](../agents/agent5/k08_note_spool_aes_relative_sft.py) was executed locally against the original 46-file ZIP extracted under a checkout-equivalent `resources/` path with the six known candidate slots. Crew source SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`; spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

| Exact original-source outcome | Count |
| --- | ---: |
| Complete AES+pad issuer configurations | 512 |
| Real heldout whole-caption predictions attempted | **2,048** |
| Configurations predicting all four genuine heldout HMAC16 values | **0** |
| Unique complete K08 components inverted from PS-0323 | **512** |
| Original K08 full SHA256 matches | **0** |
| Independently generated five-record-plus-target planted whole-block transport controls | **512 PASS** |

The planted control synthesizes a common pad from a wholly generated N02 job, verifies four complete synthetic caption→printer pairs, and decodes a deliberately withheld 16-byte final component exactly, with original producer and reducer untouched. This validates the tested inversion algebra. It does **not** establish the historical existence of a shared AES or pad stage.

This excludes only these 512 explicitly defined note-to-printer AES transport assumptions. Even if the source mapping were genuinely correct, the historical device may use an unrelated transform, or PS-0323 may carry a job object other than the final HMAC. No authentic final K08 word or component is recovered. Six individually accepted slots remain valid, K04 and K08 unresolved, and combined REC8/1 still INCOMPLETE.

The selected K04 copy, all original evidence, canonical `candidate.json`, acceptance and verifier were left unchanged. A genuinely source-backed printed-text representation or queue manifest would be needed to upgrade the N23↔0323 alignment beyond a conditional locator.
