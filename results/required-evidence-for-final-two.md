# Minimum missing evidence needed to complete H-17 REC8/1

Research handoff / 2026-10-20 / Agent 1. All six other slots pass immutable independent SHA-256 commitments, as recorded in `resources/candidate.json`.

## K04 — byte-exact print source

**Preserve or request:** an independently obtained original spool image, escrow coupon receipt, printer/cassette service recovery image, or a contemporaneous checksum-bearing export for logical route ESC-N at 2026-10-03, job **PS-261003-0417**, ACK **attempt 2**, classification **RECOVER**. The required datum is the exact **16-byte coupon payload**, in original byte order, with record provenance, timestamps, and any integrity or transport checks. A dispatch ACK alone establishes receipt, not byte integrity.

The surviving export carries `A9A9DC5731A5E2AE879C47215C2559D5`, but this fails the K04 commitment after XOR against masked component `8556C8CB6140A7F9A5123AC7571BEE1C`. Do not overwrite source or silently substitute arbitrary bytes. The relevant paper trail ties job to account **FA-17**, north printer cassette return **L-29/N**, policy annex **H17-POL-17/A3**, and risk folio **BX25/08**. The PDF folio is recoverable using the historical four-digit scan release code `8131` and confirms the printer asset, but does not contain the payload.

**If obtained:** `K04 = XOR16(original_REcover_ACK_payload, 8556C8CB6140A7F9A5123AC7571BEE1C)`; test SHA256(K04) against `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. A mismatch means the provenance or byte value is still unresolved.

## K08 — final keeper caption

**Preserve or request:** Emily's signed/reproduced recovery-envelope face, a timestamped photograph of the desk card or envelope, a final (post-draft) caption message, or an authorized records copy containing the **exact final wording** of the keeper's late-watch desk caption. Keep original punctuation, Unicode characters, and original line breaks in an evidential transcription; normalization happens only when deriving key bytes. Record which envelope it labels.

Existing notices N02, N06, N10, N13, N20, N23 are thematic drafts and narrative clues. Mail 11 explicitly excludes commissioning `Back before the first boat` and standby `Leave the light on for the next watch`. The old galley/lamp/sea descriptors cannot establish final word order. Corpus-local phrase checks and source-bounded grammatical expansions failed the commitment.

**If obtained:** lowercase caption; replace any characters outside ASCII `a-z`, digits and whitespace with spaces; collapse all whitespace and trim; use normalized UTF-8 bytes as HMAC-SHA256 message keyed by hexadecimal nonce `5F933DA6A1BD03C32DA5CBC25344F497`; take the first 16 HMAC bytes as K08. Test SHA256(K08) against `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

## Final acceptance

Only once both missing slots independently pass, place all eight uppercase 32-hex-character values in the same `candidate.json` and run the **unmodified** `resources/verify.py` against `resources/acceptance.json`. Require eight PASS results, combined PASS and `accepted=true`. This is a historical-archive records task; no facility operation or access-control circumvention is justified by these gaps.
