# K04: four two-word MT witnesses force a six-output interval under any single chronological producer

**Agent 4 | 22 November 2026 | Source-only scheduling obstruction; K04 not recovered**

## Concrete result

Four *independent source triples* each contain **two adjacent, exact 32-bit MT19937 native-word recurrence matches**. Taken together under a single chronological generator, their source-implied stage differences force **223** native output positions across **32 disjoint retained row-to-row intervals**. Any model consuming at least seven 32-bit generator outputs in *every* one of these intervals requires at least **224**. The one-word deficit is an exact arithmetic contradiction. No selected K04 payload word enters this proof.

This rules out the particular proposed ordinary-row architecture that uses four 32-bit payload outputs, two outputs for CPython's standard 53-bit float sampler, and at least one separate output for a three-way \`random.choice\` call **for every ordinary job**, provided all four source doublets represent the same MT19937 chronology. The source does not attest that producer or even a single shared MT engine. A model permitting at least one interval of six or fewer outputs, separate streams, or non-generator copy relations is outside this exclusion.

## Source and four frozen doublets

Original printer file: \`resources/evidence/print/spool-reconstruction.log\`, SHA-256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`. Its raw row129 is the disputed PS-0417 attempt-2 RECOVER/ACK. The program validates its metadata and **never decodes its copied payload**. Every other row is reduced as four little-endian, untempered 32-bit words. Exactly the standard MT recurrence is used:

\`native[l][q] = native[k][i] XOR twist(native[r][p-1], native[r][p])\`

The right input lane \`p\` is 1–3. A second exact match is required at \`(p+1,i+1,q+1)\`, making each witness two complete consecutive native words rather than a loose one-word coincidence.

| Source triple \`(r,k,l)\` | Lanes \`(p,i,q)\` and \`(+1,+1,+1)\` | Implied \`S_k-S_r\` | Implied \`S_l-S_r\` |
| --- | --- | ---: | ---: |
| 11,65,95 | (1,0,2), (2,1,3) | 397 | 622 |
| 12,66,96 | (1,1,2), (2,2,3) | 396 | 622 |
| 32,84,115 | (1,2,0), (2,3,1) | 395 | 624 |
| 42,95,126 | (1,1,2), (2,2,3) | 396 | 622 |

Let \`S_j\` be the native output-stage index at the start of row \`j\`. The first and fourth doublets give:

\`S_42 - S_11 = (S_95-S_11) - (S_95-S_42) = 622-396 = 226\`.

Using the first and second:

\`S_66-S_65 = (S_12-S_11)-1\`.

Using the third and fourth:

\`S_126-S_115 = (S_42-S_32)-2\`.

Therefore their sum is fixed without fitting any hidden per-job draws:

\`\`\`
(S_32-S_12) + (S_66-S_65) + (S_126-S_115)
= (S_42-S_11)-3
= 223.
\`\`\`

The left side covers exactly **20+1+11 = 32** disjoint row intervals: 12–31, 65, and 115–125. A lower bound of seven outputs per interval gives \`32*7=224\`, contradicting the source-implied 223. At least one of these intervals must consume **at most six** outputs under the joint-chronology premise. The negative cycle is one word wide and does not depend on any upper bound, p951-stage assumption, source-row permutation, singleton recurrence witnesses, or K04 commitment.

## Why this changes the producer search

Earlier [mixed-sampler preflight](h17-k04-mixed-sampler-same-gap-preflight-20261117.md) excluded a specific 557-model p950–p955 schedule family because those fitted schedules contained multiple sub-three hidden gaps. This test instead uses four source-observed **two-word** recurrence structures to derive a **universal minimum-draw contradiction**, independent of those fitted schedule families.

The new obstruction makes the proposed mandatory two-output float-plus-separate choice architecture untenable *if* those doublets belong to one printer generator. A producer allowing conditional skipped metadata draws, a smaller sampler, or an ordinary-job exception could still fit this narrow lower-bound condition. None of those alternatives is authenticated by original firmware or print media; arbitrary exception placement must not be promoted into a K04 source claim.

The four source doublets do not identify which of the 32 row intervals, if any, is exceptional. They neither reveal any selected K04 bits nor predict a complete independent historical payload. The next useful experiment must establish a **source-defined exceptional draw/packet rule** and use it to predict a complete held-out source object and the 16-byte selected coupon, checking the unchanged original full K04 SHA-256. Another unconstrained gap enumeration would only move the unknown schedule elsewhere.

## Reproduction and status

[Standard-library, source-pinned SFT](../agents/agent4/k04_mt_four_doublet_mingap_sft.py) checks original spool SHA-256, selected-job metadata, four independent two-lane source identities, MT temper/inversion controls, and the exact 223-versus-224 arithmetic. Executed against the unmodified original uploaded 46-file export:

\`\`\`
SOURCE PASS ... selected_row=129 withheld=True
DOUBLETS PASS 4 independent source triples x 2 adjacent complete 32-bit matches
STAGE OBSTRUCTION observed_sum=223 gaps=32 if_min7=224 deficit=1
RESULT no uniform >=7-word-per-ordinary-job producer fits all four doublets; no K04 candidate generated
\`\`\`

No historical K04 component or Emily-final K08 caption is recovered. K01/K02/K03/K05/K06/K07 remain individually accepted. K04 and K08 are missing; the combined original REC8/1 commitment remains incomplete. Source resources, official verifier, acceptance and \`candidate.json\` are unchanged.
