# H-17 ticket-to-spool complement index: acquisition hypothesis (2026-11-07)

## Question

Does the supplier/Risk reference suffix identify an earlier printer job by complementing the K04-selected job number, i.e. does

`PS job suffix = 417 - ticket suffix`

provide a real cross-record index? If so, the inferred job numbers may identify missing original spool objects and possibly records outside the supplied N01–N24 note export.

This is an **unverified acquisition hypothesis**, not a recovered K04/K08 value and not a source-authenticated mapping.

## Source basis

- `resources/evidence/recovery-routing.json` selects `PS-261003-0417` for K04.
- `resources/evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv` contains 18 distinct ST/RN references, including the five L-29/N FA-17 tabs, two L-28/A2 FA-17 controls, three RISK folios, and other-account controls.
- `resources/evidence/print/spool-reconstruction.log` contains a contiguous ordinary job sequence beginning at PS-0300 and running through PS-0427, plus late records.
- The existing `results/h17-k08-note-spool-sequence-crosswalk-20261107.md` establishes the note/job alignment only for supplied notes N01–N24: Nn ↔ PS-(0300+n).
- `resources/evidence/h17-supplemental-office-files/retired-office-bookmarks.html` preserves the missing historic index locators `R:/Stores/returns/SEP26/index.htm`, `R:/Records/INDEX/IR-261003-H17.txt`, and `R:/Risk/Transfers/BX25/transfer-index.htm`.

## Candidate mapping

For each ticket/reference suffix (t), calculate (j=417-t). Since the supplied note/job sequence uses PS-0300 as its base, a further *index-like* value is (i=j-300=117-t). This second value is **not** asserted to be a note ID outside the N01–N24 range.

| Reference | Source / account / folio | (417-t) | Spool row | (117-t) (index hypothesis) |
|---|---|---:|---|---:|
| RN-047 | RISK / ST-09 / BX25/03 | PS-0370 | ACK, LABEL, desk | 70 |
| RN-052 | RISK / FA-17 / BX25/08 | PS-0365 | ACK, RECOVER, bench | 65 |
| RN-053 | RISK / LV-42 / BX25/12 | PS-0364 | ACK, STORES, desk | 64 |
| ST-081 | L-29 / FA-17 / H17-POL-17/A3 | PS-0336 | ACK, LABEL, bench | 36 |
| ST-087 | L-28 / FA-17 / H17-POL-17/A2 | PS-0330 | ACK, STORES, desk | 30 |
| ST-094 | L-29 / FA-17 / H17-POL-17/A3 | PS-0323 | ACK, RECOVER, store | 23 |
| ST-098 | L-28 / FA-17 / H17-POL-17/A2 | PS-0319 | ACK, RECOVER, desk | 19 |
| ST-099 | L-29 / FA-17 / H17-POL-17/A3 (R3 POSTED; R2 VOID is superseded) | PS-0318 | ACK, RECOVER, store | 18 |
| ST-106 | L-29 / FA-17 / H17-POL-17/A3 | PS-0311 | ACK, STORES, desk | 11 |
| ST-112 | L-29 / FA-17 / H17-POL-17/A3 (R3 POSTED; R4 HELD is not the posted row) | PS-0305 | ACK, LABEL, store | 5 |

The remaining eight distinct references have suffixes greater than 117 and therefore map below PS-0300 under this formula: ST-121→0296, ST-130→0287, ST-135→0282, ST-142→0275, ST-151→0266, ST-157→0260, ST-164→0253, and ST-176→0241. None is present in the supplied spool sequence.

## Why this is worth checking

1. The five L-29/N binder tabs map to five extant jobs: ST-094→PS-0323, ST-081→PS-0336, ST-106→PS-0311, ST-099→PS-0318, ST-112→PS-0305.
2. The two L-28/A2 FA-17 records act as a small historical holdout: ST-098→PS-0319 and ST-087→PS-0330.
3. The three RISK folios also map to extant jobs. RN-052 is particularly notable: its folio is BX25/08, and PS-0365 is a 12:25Z RECOVER/bench ACK, the same class/destination as the selected PS-0417 attempt-2 ACK at 18:02Z.
4. The derived index values 5, 11, 18, 19 and 23 fall within the supplied N01–N24 sequence; 30, 36, 64, 65 and 70 do not. The latter five are only candidate sequence positions. They are **not evidence that notes N30/N36/N64/N65/N70 exist**.

## Important caveat

The apparent range separation is not independent validation. The anchor 417 is the K04 job suffix and the base 300 is the first spool-job range / note-job base. Therefore (417-t) necessarily lands at or above 300 whenever (t\le117); the ten low-suffix references then fall inside a spool log that covers that range. This can be a numerical coincidence. No supplied source explicitly states that ticket suffix plus spool-job suffix equals 417, and no original ticket-to-job pair has yet authenticated the rule.

The inferred index values beyond 24 must not be promoted to note IDs. The existing N01–N24 crosswalk does not, by itself, license extrapolation to PS-0330, PS-0336, PS-0364, PS-0365 or PS-0370.

## Bounded payload checks

- For all ten mapped jobs, neither the raw 16-byte spool payload nor payload XOR the published K04 mask matched the K04 or K08 slot commitment.
- For the five L-29/N payloads and seven FA-17 payloads, tested direct payloads, subset XOR/sum folds, SHA-256/MD5/BLAKE2s and HMAC folds keyed by the K04 mask or K08 desk nonce; no K04/K08 commitment matched.
- Tested contiguous 16-byte windows in the mapped-payload concatenations, raw and mask-XOR; no commitment matched.
- For the RN-052 / BX25-08 connection, the PS-0365 payload did not directly match the unencrypted PDF trailer IDs or common whole-file digest truncations. This does not test or authorize any PDF password route.

These checks only close the listed simple constructions. They do not disprove an explicit index or source-side producer/copy relationship.

## Highest-value next evidence

1. Obtain the original `R:/Stores/returns/SEP26/index.htm` and `R:/Records/INDEX/IR-261003-H17.txt`; check for an explicit ST/RN↔PS job cross-reference.
2. Obtain the original `R:/Risk/Transfers/BX25/transfer-index.htm` and the RN-047/RN-052/RN-053 folio records. RN-052 / BX25/08 and PS-0365 are the highest-value same-role comparison.
3. If the original index supports the mapping, obtain native spool objects and queue manifests for PS-0330, PS-0336, PS-0364, PS-0365 and PS-0370, plus the five L-29/N jobs.
4. Only if the index confirms an extended note series, seek the corresponding native records at inferred positions 30, 36, 64, 65 and 70. Do not assume these are note IDs before source confirmation.

Agent 12 sent the hypothesis and caveats for adversarial review to Agents 6, 10, 36 and 44 in separate communications. No independent confirmation is claimed here.

## Conclusion

The complement mapping is a **specific, testable acquisition lead** that points to a small set of original index and spool objects. It has not recovered any component. Official acceptance remains K01/K02/K03/K05/K06/K07 PASS; K04 and K08 remain missing, so the combined recovery key is incomplete.
