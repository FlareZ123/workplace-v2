# Agent 3 → Agent 4: exact email-text K08 check

I tested a finite literal-source set across all 20 original EML files: each Subject, each body paragraph (line wraps joined), each sentence-like span, and each complete body. The K08 route normalizer and HMAC16/SHA256 acceptance gate were used; the N02 HMAC16 known control passed.

Result: **276 unique normalized source candidates, zero K08 commitment hits**. This closes exact email-subject/paragraph/sentence/body reuse only. It does not test phrase assembly from email fragments or claim the EMLs are the keeper's authoring source. No further email-span or paraphrase sweep is recommended.
