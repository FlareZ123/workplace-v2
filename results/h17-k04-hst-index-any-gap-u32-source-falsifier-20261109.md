# K04/HST: original one-word 32-bit uniform PV mechanism contradicts historian within print gaps

**Agent 32 | 9 November 2026 | Source-only necessary-condition test | K04/K08 still unresolved.**

## New model, distinct from the earlier two-word float test

The 112 original HST-4 historian `PV` records seq100..211 have an arithmetic job-index correspondence to printer jobs PS-0300..0411. The proposed source relation is that each value is generated from **one 32-bit native MT19937 output word** as `round(12 + 76 * (word / 2**32), 3)`. This is distinct from the preceding Python `random.random()` 53-bit/two-word model, and it allows *each* historian row to choose **any individual output position** in its corresponding inter-packet gap, with no common stride or fixed phase.

All original source use is target-free: the selected PS-0417 ACK2 row129 is omitted completely, the original printer source SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, and the historian export SHA256 is `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`. The 132 intact printer 16byte packets furnish rank15,365 fixed native MT constraints under the hypothetical p951 chronology.

For a millivalue `m=1000*PV`, the rounded-reading requirement is the exact integer interval

```
ceil((2*m-24001)*2^32/152000) <= word <
ceil((2*m-23999)*2^32/152000)
```

The common high-bit prefix of this interval is compared only where the withheld-row-independent printer basis already determines those bits at a candidate stage. A historian record contradicts the model only if **every** one-word stage in its corresponding gap has a source-fixed mismatching prefix.

## Original result and true positive

**GitHub Actions [run 42602218853](https://github.com/FlareZ123/workplace-v2/actions/runs/42602218853) completed success**, executing original source assertions and the planted-source positive control. Follow-up **[run 42602647005](https://github.com/FlareZ123/workplace-v2/actions/runs/42602647005) also succeeded**, checking four source-global byte views with genuine planted positives.

| Result | Count |
| --- | ---: |
| Original HST PV records | 112 |
| Historian rows with at least one fixed stage bit among candidate positions | 72 |
| Original rows contradicting **every** valid gap position | **16/112** |
| Contradicted rows marked GOOD | **9** |
| Contradictions in seq100..179 | **9/80** |
| Contradictions in seq180..211 | **7/32** |
| True MT synthetic source values whose correct position passes | **112/112** |
| Informative planted positive values | 42 |

One particularly concrete original source contradiction is GOOD PV102=59.877. Other contradicted GOOD rows include PV123=13.532, PV133=25.557, PV179=79.377 and late block PV180=65.433, PV182=71.986, PV183=63.807, PV193=80.237, PV208=51.265. These are retained source values, **not** reconstructed or fitted target bytes. All original conflicts are printed by the source SFT.

The synthetic positive generates a genuine single CPython MT stream, uses the original 133 printer packet stage positions and excludes selected row129 from source fitting; it places the **synthetic** historian sample at the first valid postpacket 32bit position. All 112 genuine synthetic PV values pass, including 42 informative tests. This detects bit-order, quantization, common-prefix or stage-index implementation mistakes.

Reproducer: [Agent32's 32-bit HST gap single-file SFT](../agents/agent32/k04_hst_gap_uint32_sft.py); manual [CI workflow](../.github/workflows/agent32-k04-hst-gap-u32-manual.yml).

## Physical byte-order alternative

The [source-only byte-order SFT](../agents/agent32/k04_hst_gap_byteorder_sft.py) additionally tested the four canonical whole-byte layouts of each native 32bit output interpreted as a fixed producer word: original order, four-byte reversal, two-16bit-word swap, and swap within each 16bit half. Each model allows independent per-record gap positions but fixes the selected byte order **globally** and tests 112 genuine historical values without the K04 target. **All four have exactly 16 all-stage contradictions, 9 GOOD, 7 among late seq180..211**, with 72 original rows informative; a genuine seeded MT positive passes 112/112 for **each** layout (42 informative per layout). Thus conventional 16/32bit endian transformations do not rescue this specified single-u32 source model. These are necessary-condition exclusions, not a claim about arbitrary nonlinear renderers.

## Consequence

The original historian contradicts the exact **one-word MT u32/2^32, 12..88 quantizer, job-indexed, arbitrary within-gap stage** hypothesis. This conclusion is independent of the earlier two-word Python float model's 29/112 incompatibilities and does not assume a common global placement or treat uncertainty as a contradiction. It does not disprove alternative byte/bit orders, other quantizers, clocks, other source producers or printer/HST noncorrespondence. The paired HST source data do not reduce selected K04 q951..954 unknown bits under this rejected model.

**No original selected K04 byte or Emily author-final K08 caption word is recovered.** Six original slots still PASS and combined REC8/1 is INCOMPLETE.
