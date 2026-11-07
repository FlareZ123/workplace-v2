# K08 exact N01 photo-caption literal test

**Agent 36 · 7 November 2026**

## Question

Does the exact surviving N01 caption, attributed to Jason, equal the K08 keeper's caption after the route sheet's specified normalization?

Source text in `resources/evidence/crew/noticeboard-and-desk-notes.txt`:

> The sea looks different when you have finally finished your tea.

The source is N01, described as the caption for the empty-bench photograph. Agent49's photo-caption acquisition result links N01 contextually to Emily's later N10 reference to “the photograph after the last cup”, while explicitly withholding proof that the two notes refer to the same image or that Emily adopted Jason's caption.

## Reproducible commitment check

The original `evidence/recovery-routing.json` K08 rule specifies:
1. lowercase the phrase;
2. replace every character other than ASCII a-z, digits and whitespace with a space;
3. collapse whitespace and trim;
4. compute HMAC-SHA256 using the decoded K08 desk_nonce as key;
5. retain the first 16 bytes;
6. SHA256 those 16 bytes and compare with the K08 acceptance commitment.

Inputs:
- Raw N01 literal: `The sea looks different when you have finally finished your tea.`
- Normalized message: `the sea looks different when you have finally finished your tea`
- K08 desk nonce: `5F933DA6A1BD03C32DA5CBC25344F497`
- Expected K08 SHA256 commitment: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`

Computed:
- HMAC-SHA256 first 16 bytes: `4D9BAD0C7C773568B09DD8C80795096C`
- SHA256 of those 16 bytes: `d3a899102cfd1598245d91f0ced97a0a111da547b439082a086e297acfa00dbb`

<badge color="red" label="NO MATCH" />

## Interpretation and limits

The exact N01 caption literal is **not** the K08 phrase under the original route normalization and acceptance commitment. This is one source-motivated exact-string falsification, not a phrase-generation sweep.

It does not exclude the possibility that Emily adapted the photograph's subject, wording or a later caption into her own final envelope margin. It does not establish that N01 and N10 refer to the same physical image. The final K08 words remain unrecovered.

Reproduction uses only the supplied N01 line, K08 nonce, normalization rule and acceptance digest. No original candidate, verifier, route sheet or acceptance file was modified.
