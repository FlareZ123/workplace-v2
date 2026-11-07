# PTW-417 REMOVED seal serials: source-separated K04 negative test

**Question.** Does the distinct signed CLOSED REMOVED four-bay set from PTW-417 provide a K04 component or pre-mask payload under the two direct 16-byte interpretations?

## Source-defined selection

PTW-417 is the four-bay seal-rack inventory/as-left witness. MAIL-04 says the receipt export has the right seal serials, a stores picking ticket is not the as-left record, signed closed fitment should be used, REMOVED entries should be kept separate, and the signed witness walk is **B,D,A,C**. The work-order page says a reopened item does not invalidate an earlier signed as-left record unless a later signed closeout replaces it.

For context, the latest signed CLOSED AS_LEFT rows (revision 2, with asset and inspector) in B,D,A,C order are:

```text
D7DAD6BC9714519B7DAD0AD4BE8E87FD
```

This sequence is already established prior art as the **K03 prehash input**: its SHA256-first16 matches the accepted K03 component. Agent38's PTW417 serial-label digest SFT and Agent12's PTW bay-transition/p951 SFT already tested the AS_LEFT sequence as a direct K04 interpretation and across broader order/serialization families. The direct K04 hashes below are included only as a reproducibility cross-check, not as a new investigation or new K04 evidence.

MAIL-04 explicitly says to keep REMOVED entries separate. The latest signed CLOSED REMOVED rows are revision 4. In the same witness order B,D,A,C they yield:

| Bay | Revision | State / fitment | Serial |
|---|---:|---|---|
| B | 4 | CLOSED / REMOVED, signed | `SG-531FFABE` |
| D | 4 | CLOSED / REMOVED, signed | `SG-99AE58D8` |
| A | 4 | CLOSED / REMOVED, signed | `SG-885464E5` |
| C | 4 | CLOSED / REMOVED, signed | `SG-9BB5A10C` |

The separate REMOVED sequence is exactly 16 raw bytes:

```text
531FFABE99AE58D8885464E59BB5A10C
```

## Acceptance tests

The unchanged K04 commitment is:

```text
930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0
```

The unchanged route mask is:

```text
8556C8CB6140A7F9A5123AC7571BEE1C
```

### Prior-art cross-check: AS_LEFT set

- Direct SHA256 of `D7DAD6BC9714519B7DAD0AD4BE8E87FD`: `F45288D8D1984A285FAD2FB145F840B51EC343BFC62CED6ED476BC5B59299175` (does not match K04).
- XOR with the route mask: `528C1E77F654F662D8BF3013E99569E1`; SHA256: `BA03876DD482CA591AFEF534A32BA7547ECCD7947FFB8B076B8FDF0C3A02327B` (does not match K04).

These two checks reproduce a small subset of prior work. They are not claimed as novel. The raw AS_LEFT sequence is a K03 prehash input, not K04.

### New narrow test: separate REMOVED set

- Direct SHA256 of the REMOVED serial bytes: `E07215CECC96DD5D2D9A110E518C5A611BB5F84273FCFFEDCD3B092A4E619B4` — **NO MATCH**.
- XOR with the unchanged route mask: `D6493275F8EEFF212D465E22CCAE4F10`; SHA256: `0541AD136C883EB52A43C962DABC0912901B115449F60F8E9BE0239454579C33` — **NO MATCH**.

This is a bounded negative for the separate REMOVED set under direct-component and pre-mask-payload interpretations. It does not test arbitrary transforms, and none should be invented without the original commissioning note.

## Conclusion and next use

The PTW-417 receipt export contains two semantically distinct four-bay sets. The signed AS_LEFT set is already the accepted K03 prehash source. The separate signed REMOVED set does not satisfy K04's commitment as either the raw component or the pre-mask payload. Neither set should be promoted to K04.

Keep AS_LEFT, OPEN and REMOVED artifacts separate. Retrieve the complete PTW-417 signed closeout, all revisions, field sketch, original coupon, requested photograph/caption and supplier commissioning note. Ask the original commissioning note whether the REMOVED serials select, validate or otherwise relate to the ESC-N coupon; do not infer a transform.

**Confidence:** High in the local receipt-row selection and the exact REMOVED-set negative tests. The AS_LEFT K03 identification is established prior art. No K04 bits or component were recovered.

**Reproducibility:** `evidence/maintenance/seal-receipts.jsonl`, `evidence/maintenance/work-order-417.html`, `evidence/mail/04.eml`, `evidence/mail/16.eml`, `evidence/recovery-routing.json`, and `acceptance.json`.
