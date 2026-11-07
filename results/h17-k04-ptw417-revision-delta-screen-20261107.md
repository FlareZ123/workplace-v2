# PTW-417 revision-delta screen for K04

**Status:** bounded negative result. This candidate family does not recover K04.

## Question

Could the 16-byte K04 coupon be a per-bay transition vector derived from the signed PTW-417 seal serials, given the matching 417 suffix in the ESC-N print job?

This is a hypothesis screen only. No source currently establishes PTW-417 as the producer or foreign-key parent of PS-261003-0417.

## Source selection

- MAIL-04 records the signed field-sketch witness order **B, D, A, C**.
- The PTW-417 receipt set contains 13 signed, CLOSED rows across revisions 1, 2, and 4. Revision 1 has two signed A-bay alternatives: unannotated `SG-574A9232` and asset/inspector-annotated `SG-7E73B4CC`. Both were retained.
- Four revision-3 rows are OPEN and unsigned. They were excluded. Revision 4 is signed CLOSED/REMOVED and was used only as a transition endpoint, not as the as-left state.
- The ESC-N route in `archive-labels.ini` selects PS-261003-0417. The latest ACK for that exact job is attempt 2 at 2026-10-03 18:02Z, `CLASS=RECOVER`, `DEST=bench`. The spool reconstruction's ACK is dispatch evidence, not proof of media integrity.
- The K04 mask is read from `recovery-routing.json`; the commitment is read from `acceptance.json`.

## Method

The reusable screen is `work/h17_ptw417_revision_delta_sft.py`. Run it from the repository root:

```powershell
python work/h17_ptw417_revision_delta_sft.py
```

It constructs 21 operations per A-revision-1 alternative, concatenating four-byte per-bay results in B,D,A,C order:

- three pairwise XORs across revisions 1, 2, and 4;
- three bytewise modulo-256 additions and six directed bytewise subtractions;
- three big-endian modulo-(2^{32}) additions and six directed modulo-(2^{32}) subtractions.

That produces **42 distinct 16-byte candidate vectors**. For each, the script checks the direct K04 commitment, the commitment after XOR with the K04 mask, and exact identity with the reconstructed component or selected spool payload.

## Result

The selected ACK2 payload is:

`A9A9DC5731A5E2AE879C47215C2559D5`

The K04 mask is:

`8556C8CB6140A7F9A5123AC7571BEE1C`

Their XOR gives the local component candidate:

`2CFF149C50E54557228E7DE60B3EB7C9`

Its SHA-256 is:

`11a7f6064781a6ac7678dc6dd24759af95981c8a927f8da4436515354d34549b`

The required K04 commitment is:

`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`

| Check across 42 candidates | Hits |
|---|---:|
| SHA-256(candidate) equals K04 commitment | 0 |
| SHA-256(candidate XOR K04 mask) equals K04 commitment | 0 |
| Candidate equals reconstructed component | 0 |
| Candidate equals selected ACK payload | 0 |

The script emits the complete candidate vector and digest table as JSON on stdout.

## Interpretation and limits

This rejects the tested per-bay revision-transition family, including both signed revision-1 A alternatives. It does **not** disprove every possible relationship between PTW-417 and the printer job. The same-suffix association remains unverified, the native queue object is absent, and the selected spool payload is reconstructed. No broad hash or PRNG search was added.

The next useful evidence is the original PTW-417 field sketch/closeout and the native PS-261003-0417 queue or physical coupon record. Do not expand generic transforms until one of those sources establishes a concrete relationship.
