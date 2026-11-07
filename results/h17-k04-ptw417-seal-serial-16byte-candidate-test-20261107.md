# PTW-417 signed seal serials as a 16-byte K04 candidate: exact negative test

**Question.** Does the four-bay PTW-417 as-left seal inventory, in the signed witness-walk order B,D,A,C, provide either the K04 16-byte component or the 16-byte pre-mask coupon payload?

## Source-defined selection

Three source statements define a narrow candidate without arbitrary ordering:

- `work-order-417.html` identifies PTW-417 as the **seal rack inventory and as-left witness**. It says a reopened item does not invalidate an earlier signed as-left record unless a later signed closeout replaces it.
- MAIL-04 says the receipt export has the right seal serials, a stores picking ticket is not the as-left record, signed closed fitment should be used, and REMOVED entries should be kept separate. It gives the signed witness walk as **B, D, A, C**, explicitly distinguishing it from corridor cabinet order A–D. MAIL-04 also notes a later OPEN revision carrying an old serial.
- `seal-receipts.jsonl` contains PTW-417 records for bays A–D with signed CLOSED AS_LEFT revisions, later unsigned OPEN AS_LEFT revisions, and separate signed CLOSED REMOVED records.

For each bay, I selected the latest signed CLOSED AS_LEFT row that carries the asset and inspector fields, leaving OPEN and REMOVED rows separate. This resolves the A-bay duplicate revision-1 row without asset/inspector as a non-as-left/picking-style record. The selected rows are:

| Bay | Revision | State / fitment | Serial |
|---|---:|---|---|
| B | 2 | CLOSED / AS_LEFT, signed | `SG-D7DAD6BC` |
| D | 2 | CLOSED / AS_LEFT, signed | `SG-9714519B` |
| A | 2 | CLOSED / AS_LEFT, signed | `SG-7DAD0AD4` |
| C | 2 | CLOSED / AS_LEFT, signed | `SG-BE8E87FD` |

In the signed witness-walk order B,D,A,C, the four 8-hex serials form exactly 16 raw bytes:

```text
D7DAD6BC9714519B7DAD0AD4BE8E87FD
```

This is a source-grounded candidate because four 4-byte serials fill the REC8/1 16-byte slot and the order comes from MAIL-04. The PS-261003-0417 / PTW-417 shared suffix and the ESC-N coupon reference in MAIL-16 make the cross-source join worth testing; the suffix alone does not prove that the seal serials are the coupon.

## Acceptance tests

The unchanged K04 commitment is:

```text
930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0
```

The unchanged route mask is:

```text
8556C8CB6140A7F9A5123AC7571BEE1C
```

Two direct interpretations were tested:

1. **Serial sequence is the component:** SHA256 of the 16 raw serial bytes is `F45288D8D1984A285FAD2FB145F840B51EC343BFC62CED6ED476BC5B59299175` — **NO MATCH**.
2. **Serial sequence is the pre-mask payload:** XOR the 16 raw serial bytes with the route mask, obtaining `528C1E77F654F662D8BF3013E99569E1`; SHA256 is `BA03876DD482CA591AFEF534A32BA7547ECCD7947FFB8B076B8FDF0C3A02327B` — **NO MATCH**.

The selected PS-0417 RECOVER ACK2 payload remains `A9A9DC5731A5E2AE879C47215C2559D5`; it is not the serial sequence. These failures rule out the two obvious direct 16-byte interpretations, not every possible relationship between the seal rack and coupon.

The source also provides a separate four-bay **REMOVED** set at signed CLOSED revision 4. Following MAIL-04's instruction to keep REMOVED entries separate, I tested that set independently in the same B,D,A,C witness order:

```text
531FFABE99AE58D8885464E59BB5A10C
```

- Direct SHA256: `E07215CECC96DD5D2D9A110E518C5A611BB5F84273FCFFEDCD3B092A4E619B4` — **NO MATCH**.
- XOR with the unchanged route mask: `D6493275F8EEFF212D465E22CCAE4F10`; SHA256: `0541AD136C883EB52A43C962DABC0912901B115449F60F8E9BE0239454579C33` — **NO MATCH**.

Thus both semantically distinct four-bay sets present in the local receipt export (latest signed AS_LEFT and signed REMOVED) fail under both direct 16-byte interpretations. This closes those four exact source-grounded candidates; it does not exclude a more specific coupon operation that only the original commissioning note or physical coupon can establish.

## Conclusion and next use

The PTW-417 receipt export gives a well-defined four-serial, 16-byte source object and a source-defined order. It does **not** satisfy K04's immutable commitment as either the raw component or the pre-mask payload. Do not promote it to K04 or replace the route's selected printer payload with it.

It remains valuable as a **cross-source locator and physical-control record**. Retrieve the full PTW-417 signed closeout, receipt export with provenance, field sketch, all four bay records, original coupon and supplier commissioning note. Preserve REMOVED parts and the later OPEN revision separately. Ask the original commissioning note whether the seal serials select, validate, label or otherwise relate to the ESC-N coupon; do not invent a transform.

**Confidence:** High in the selected local receipt rows and the two exact SHA256 negative tests; low in any further seal-serial/coupon relationship. No K04 bits or component were recovered.

**Reproducibility:** `evidence/maintenance/seal-receipts.jsonl`, `evidence/maintenance/work-order-417.html`, `evidence/mail/04.eml`, `evidence/mail/16.eml`, `evidence/recovery-routing.json`, and `acceptance.json`.
