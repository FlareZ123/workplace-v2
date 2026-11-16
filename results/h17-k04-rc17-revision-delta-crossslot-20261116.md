# RC-17 revision-transition screen against K04

**Status:** bounded negative cross-slot hypothesis test; no K04 value recovered.

## Question

Could the ESC-N coupon be one of the four-word RC-17 control-strip blocks, or the per-stage revision delta between two RC-17 revisions? This is a narrow cross-slot hypothesis motivated by the fact that RC-17 supplies four 4-byte control strips, the K06 route uses a documented four-stage order, and the recovery archive uses 16-byte components.

There is **no source statement** that binds RC-17 to the ESC-N coupon. This experiment tests the direct candidate forms only; it does not establish RC-17 as a K04 producer.

## Source selection and control

- resources/evidence/archive-labels.ini gives SERVICE_ORDER=DRAIN,ISOLATE,PURGE,VERIFY.
- resources/evidence/procedures/RC-17-scans.txt contains four 4-byte footer strips for each of Rev B, Rev C, and Rev D-draft.
- resources/evidence/recovery-routing.json supplies the K04 XOR mask.
- resources/acceptance.json supplies the unchanged K04 and K06 commitments.

The parser concatenates the four strips in SERVICE_ORDER for each revision. As a positive control, the Rev C block is:

    5DBF40EE52FAAED9A536D3326CF0D95A

Its SHA-256 equals the accepted K06 commitment exactly. This validates the page parsing and service-order serialization used by the experiment.

Source SHA-256 values:

| Source | SHA-256 |
|---|---|
| recovery-routing.json | f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5 |
| acceptance.json | 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f |
| archive-labels.ini | 146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad |
| RC-17-scans.txt | a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d |

## Candidate construction

For each 16-byte coupon candidate C, compute the route-defined component K04 = C XOR M, where M is the official 16-byte K04 mask, and compare SHA256(K04) to the unchanged K04 commitment.

Tested:
1. the raw SERVICE_ORDER block from Rev B, Rev C, and Rev D-draft;
2. the per-stage XOR delta for each revision pair: B↔C, B↔D-draft, and C↔D-draft.

No permutations, arbitrary hash families, or unanchored transforms were added.

## Results

| Candidate coupon | Component after K04 mask XOR | SHA-256(component) | K04 hit |
|---|---|---|---|
| Rev B raw | 5D7CBB22809BE480D08C3AE0962B27A7 | 4ee891268c7ac6158df36152250719b2815f80ffea60e7449aec077da98a3d06 | No |
| Rev C raw | D8E9882533BA09200024E9F53BEB3746 | 4bc8bf862610abc45e104f1919210f5373aa55946926cfbc5a9e0dd79b03af16 | No |
| Rev D-draft raw | 83654875F54256E3796AA941BA7B952C | bda23c229f20a22494f4403e09f976acf27986fb3f252338a8dfe880e367ab29 | No |
| B↔C per-stage XOR | 00C3FBCCD2614A5975BAE9D2FADBFEFD | 6062e213bef1d5784f653666c045e6b79c66faecfeddbccd8e2c800bf8af0483 | No |
| B↔D-draft per-stage XOR | 5B4F3B9C1499159A0CF4A9667B4B5C97 | 8898dae156468175dd18da74d387194c352b60bfddc3a7182f9cd0f8e0f37fee | No |
| C↔D-draft per-stage XOR | DEDA089BA7B8F83ADC5C7A73D68B4C76 | 3b4d5a1605329defac75fab6b7cdb108dd115d592b1af87b5fe40e09e1530a1b | No |

**Result: 6 complete candidates, 0 K04 commitment hits.** The Rev C positive control passed K06, so this is not a page-order or parser failure.

## Interpretation and limits

This rejects the tested direct RC-17 revision-block and per-stage XOR-delta candidates. It does **not** prove that no other cross-slot relation exists, and it does not establish any relationship between RC-17 and the ESC-N printer route. The K04 coupon remains unresolved; the accepted six slots and official commitments are unchanged.

Reproducer: agents/agent48/k04_rc17_revision_delta_sft.py.
