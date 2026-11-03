# K04: 14 early-source donors, eight residual bits, and two original quartet-family tests

**Agent 32 | 3 November 2026 | A new complete-coupon, conditional p951 inverse-source mechanism, original commitment NO_MATCH.**

## Distinct mechanism: 14 early MT outputs collapse target to 256 complete values

The [22-stage early donor construction](h17-k04-ptw-early-fullword-observability-horizon-20261103.md) recovers a complete selected K04 coupon from 22 hypothetically authentic fullword outputs, using the existing original p951 printer/MT source and without a fabricated original selected ACK. Remove eight selected stages from that set, leaving three **fourword source runs** plus one **two-word source run**:

| Hypothetical four/twoword donor site | Original output native stages | Source carrier class tested |
| --- | --- | --- |
| A (four words) | -1087,-1086,-1085,-1084 | First source quartet |
| B (two words) | -1027,-1026 | Two ordered words of second quartet |
| C (four words) | -918,-917,-916,-915 | Third source quartet |
| D (four words) | -860,-859,-858,-857 | Fourth source quartet |

The original p951 printer source basis has rank **15,365**, built solely from its 132 intact logged packets (selected r129 excluded). The 14 hypothesized complete donor words add **445 independent equations** (source+donor rank **15,810**), with exactly **three independent source-syndrome constraints** on their 448 supplied bits. If a set of source-carrier values satisfies those syndromes, the native selected fourword packet at stages 951..954 has exactly **eight unresolved bits**. Thus enumerate the **256 exact complete coupons**, temper them, serialize four little-endian words, XOR the *unaltered* original K04 mask and compare the *unaltered* original full SHA256 commitment.

This is a different target-facing transform from Agent19's 2×fourword **future** paired donors at 1347/1574 (127 bits and two completions). These are **early** donor positions and a four-source, 14-word geometry. The source does not authenticate the hypothetical emitter or these native stage placements.

**End-to-end planted positive:** Back-substitute all original printer equations to obtain a full genuine source-consistent MT state; withhold its native K04 packet; generate its true early 14 donor outputs; solve the donor-augmented source and enumerate exactly 256 candidate packets. The actual hidden packet \`054AD23723EAFB47DDF71A422DD941CB\` is recovered by the 256-way enumerator. The implanted packet is a reproducibility control, **not** the historical selected printer coupon and not an accepted K04.

## Two original-source assignments

For both families, freeze four physically named, complete historical fourword groups before consulting the K04 acceptance hash. Test all 24 assignments of four distinct groups to A/B/C/D, independently four serializer views per group (natural/reversed word order × little/big within-word byte orientation), and either first or last two words of the B group. This is **24 × 4⁴ × 2 = 12,288 complete source assignments** per fixed quartet set. Each is first checked against all 448 native MT source equations and the three real source syndromes; only compatible assignments undergo 256 original K04 SHA checks.

| Original historical quartet family | Complete assignments | Source-compatible assignments | Complete K04 hash checks | Original matches |
| --- | ---: | ---: | ---: | ---: |
| TRP2 node49/event82 four seq cohorts 200..203, 300..303, 900..903, 990..993 | 12,288 | **1,560** | **399,360** | **0** |
| PTW-417 four revision groups × four bays, A/B/C/D. Two alternative original A/rev1 receipts, both tested | 24,576 | **3,216** | **823,296** | **0** |
| **Total** | **36,864** | **4,776** | **1,222,656** | **0** |

The original recorder group 900..903 carries bad recorded CRC and is **hypothetical raw source input only**, never a valid replacement for K05. Original PTW-417 revision3 is OPEN/unsigned and revision4 is REMOVED; they are considered recorded generator *candidate words* only, never authorized K03 as-left receipts. Two different original PTW-417 bay-A/rev1 receipts exist; both are explicitly included as independent assignments, with no silent preference. The historical K03 rule remains highest signed CLOSED AS_LEFT per bay, unchanged.

Counts are source assignments and full coupon SHA checks, **not globally unique candidate coupons**. Some different source encoder assignments can map to the same 16-byte candidate.

## Evidence pins and reproducibility

- Original printer source: \`resources/evidence/print/spool-reconstruction.log\`, SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`; conditional source builder [Agent49 original symbolic basis](../agents/agent49/k04_p951_symbolic_basis.py). No selected row129 source used.
- Original recorder: \`resources/evidence/recorder/trip-recorder.raw\`, SHA256 \`5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba\`. Four 4-word candidate controls use recorded bytes exactly and CRC status only as a provenance warning.
- Original maintenance: \`resources/evidence/maintenance/seal-receipts.jsonl\`, SHA256 \`c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32\`.
- K04 original mask \`8556C8CB6140A7F9A5123AC7571BEE1C\`, original target \`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0\`, unchanged.
- [Original-source SFT](../agents/agent32/k04_p951_early_14cohort_coupon_sft.py) builds the exact source-only quotient, the two original quartet families and serializer views, validates the planted synthetic coupon, then prints and asserts the counts above. Completed source-equivalent local executions: TRP2 12,288 assignments and 399,360 original SHA checks in 16.1s; PTW417 24,576 assignments and 823,296 hashes in 33.43s.

**Result:** This eliminates only the two explicitly assigned original quartet families under the stated 14-stage oracle and four orientations. Nothing supports actual chronology between these historically unrelated groups or authentic values at the 14 hypothetical native indices. The general 14/22-stage early-donor reconstruction remains algebraically valid, and it may matter if an independently indexed source packet appears. No historically authenticated selected K04 bit has been recovered. K08's author-final wording is still absent; K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING and combined REC8 INCOMPLETE.
