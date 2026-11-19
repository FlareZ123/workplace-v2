# K08 complete-email direct-adoption control (20 messages)

**Date:** 2026-11-19  
**Status:** Completed, source-pinned negative control  
**Owner:** Agent 9

## Question

Does the K08 keeper's final caption occur verbatim as a complete text unit in any of the 20 surviving email records, after applying the exact K08 normalization and HMAC commitment procedure?

This is a narrow direct-adoption test. It does not attempt arbitrary phrase assembly from email fragments.

## Method

The reproducer `agents/agent9/k08_email_complete_text_control.py`:

1. Verifies the SHA-256 commitments for `resources/acceptance.json`, `resources/evidence/recovery-routing.json`, and each of `mail/01.eml` through `mail/20.eml`.
2. Reads the K08 desk nonce from `recovery-routing.json` and the K08 slot commitment from `acceptance.json`.
3. Extracts six complete-text forms from each message: full message, subject, body, paragraphs, non-empty lines, and sentences.
4. Normalizes each candidate exactly as K08 specifies: lowercase; replace characters outside ASCII a–z, digits, and whitespace with spaces; collapse whitespace; trim.
5. Deduplicates normalized candidates, computes HMAC-SHA256 with the decoded desk nonce as key, retains the first 16 bytes, and compares SHA-256 of those bytes with the K08 commitment.

No arbitrary substring windows, word permutations, or cross-message assembly are used.

## Results

<badge color="success">Source checks passed</badge>

| Candidate form | Raw candidates |
|---|---:|
| Full message | 20 |
| Subject | 20 |
| Body | 20 |
| Paragraph | 87 |
| Non-empty line | 231 |
| Sentence | 182 |
| **Total raw** | **560** |

<badge color="danger">0 HMAC matches</badge>

The 560 raw candidates reduce to **482 unique normalized strings**. None reproduces the K08 commitment.

## Interpretation

The exact K08 phrase is not a direct complete-text adoption from the surviving email subjects, full messages, bodies, paragraphs, lines, or sentences under the prescribed normalization.

This does **not** exclude:
- wording reconstructed from multiple email fragments;
- a transformation or selector applied to email text;
- a phrase preserved in the missing mug-stock workbook, desk image, envelope, or original margin;
- an email attachment or native source not present in the surviving export.

The negative result is high-confidence for the defined direct-adoption domain only. It should be retained as a matched carrier control in the full-chain benchmark, not treated as evidence that email-related source paths are irrelevant.

## Reproduction

Run from the repository root:

```bash
python agents/agent9/k08_email_complete_text_control.py
```

The script prints the exact source hashes, raw candidate counts, unique normalized candidate count, and any hits. Expected summary: `560 raw / 482 unique / 0 hits`.
