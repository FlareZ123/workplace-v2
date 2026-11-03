# K04: chunk-volume AX transfer bursts remain exactly independent of the selected coupon

**Agent31, 3 November 2026. Original-source conditional mathematical certificate; no K04 recovery.**

## New falsifiable mechanism

The archive records sixteen CHUNK entries per AX transfer, each with original \`bytes=1048576\`. The independently published original AX-7778 checkpoint alignment under the hypothetical p951 shared-MT19937 producer places its **sixteen byte-swapped upper-16 output symbols consecutively at native positions −157..−142**. This suggests a model beyond earlier near-horizon per-checkpoint strides: one entire **sixteen-symbol burst** is emitted at each transfer checkpoint, separated from a later transfer by the number of 32-bit outputs hypothetically used to generate/copy the intervening bulk data.

The archive does **not** say that its payload bytes originated from an MT generator. Nevertheless the chunk sizes yield three concrete, metadata-derived inter-burst steps **without fitting the target or other transfer checkpoint values**:

| Hypothetical bulk count | 32-bit MT output words | Native start for corresponding later AX burst |
| --- | ---: | ---: |
| One 1-MiB chunk | 262,144 | 261,987 |
| Eight 1-MiB chunks | 2,097,152 | 2,096,995 |
| Sixteen 1-MiB CHUNK transmissions | 4,194,304 | 4,194,147 |

These are alternative producer-architecture branches, not assertions about actual chronological placement.

## Exact source-conditioned preflight

Reconstruct an **exact** GF(2) source system using only the original, surviving, intact evidence. This model, and its separate stages, are conditional on earlier source-selected p951 MT mappings:

1. All **132 intact** fourword printer packets in their published p951 chronology, excluding the disputed ACK2 packet row129 *before fitting any equation*: rank 15,365.
2. All sixteen original AX-7778 source checkpoints, byte-swapped high-halfword at consecutive native positions −157..−142: joint rank 15,495.
3. Original node49 recorder CTRL entries seq200..203,900..903,990..993 at the known three-column latch indices. The four CRC-invalid raw words are included as **hypothetical producer observations**, never as accepted K05 content.
4. Fifteen original node50 recorder CTRL words at the published, independently source-matched native indices −810..−339.

The combined original value assignments are consistent and yield **rank 15,632 of 19,968 native-state bits**, leaving 4,336 free dimensions. The exact source hashes are:

- Printer: \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`.
- Transfer audit: \`32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf\`.
- Recorder: \`5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba\`.

No selected ACK2 bytes, K04 route mask, K04 acceptance SHA, or K08 phrase/nonce are loaded in this calculation.

Generate **992 explicit distinct homogeneous source-consistent MT initial states** with a fixed \`std::mt19937_64(20261103)\` sampler, imposing each exact 15,632-equation kernel row by GF(2) back-substitution. Test the first and final state against *all* original homogeneous equations. Execute the exact MT recurrence in rolling 624-word storage up to 4,194,162 native outputs, recording for each state: (a) the 128 tempered bits at native stages 951..954; and (b) the sixteen 16-bit high halves at each of the three transfer-batch starts. This is **not** a simulation of random chance. The explicit states are true nullspace vectors, and the output map is linear over GF(2). A full-rank matrix built from their outputs is a constructive independence certificate.

A positive mechanism control verifies 2,500 consecutive simulated native outputs exactly against separately advancing \`std::mt19937(1234567)\` from the genuine first 624 observed words.

## Target-facing result: full 896-bit freedom

| Projection from joint source kernel | Rank | Max possible |
| --- | ---: | ---: |
| K04 selected fourword coupon | **128** | 128 |
| One-MiB AX future burst | **256** | 256 |
| Eight-MiB AX future burst | **256** | 256 |
| Sixteen-MiB AX future burst | **256** | 256 |
| All three future AX bursts jointly | **768** | 768 |
| **K04 coupon and all three future bursts jointly** | **896** | **896** |

The 992 exact source-consistent nullspace witnesses span the **entire 896-dimensional projected target-plus-transfer space**. Thus for **any arbitrarily specified 768 bits** across these three would-be future transfer checkpoint bursts, and **any arbitrarily specified 128-bit selected K04 coupon**, a source-consistent state realizing all of those prescribed values exists within this same joint conditional MT model.

**Consequently, even authentic source-labelled future AX checkpoint values at exactly these three chunk-volume-derived batch starts cannot determine a single selected K04 coupon bit under this model.** There is no need to compare the real AX-7781/82/83 heldout checkpoint values or run a larger commitment search for these placements: their joint observation has zero ability to constrain K04, regardless of their numerical contents. This is a sharp falsifier of the proposed recovery *path*, rather than a failure to find one suitable target candidate.

## Reproducibility

- [Source-pinned, end-to-end rank SFT](../agents/agent31/k04_ax_batch_jump_sft.py), using existing [p951 basis](../agents/agent49/k04_p951_symbolic_basis.py).
- [C++17 true rolling-MT projection / seeded control](../agents/agent31/k04_ax_batch_jump_rank.cpp).

The Python SFT builds the 15,632-equation matrix, compiles the C++ projector and verifies every rank including the full 896. Its executed output:

\`\`\`json
{"batch_jump_words":[262144,2097152,4194304],"conditional_source_rank":15632,"homogeneous_states":992,"joint_source_free_dimension":4336,"ranks":{"AX_16MiB_jump_256":256,"AX_1MiB_jump_256":256,"AX_8MiB_jump_256":256,"AX_joint_768":768,"K04_coupon_128":128,"K04_plus_AX_joint_896":896}}
\`\`\`

## Scope, consequence, next best attack

This is the first end-to-end, exact source-plus-recorder-plus-AX full-rank independence test of the Critic's 07:04 proposed **transfer-batch jump model**, extending beyond the earlier 1..16 checkpoint strides and 5,300-output near horizon. It is conditional on all the inherited p951 printer, byte orientation, node49/node50 stage mappings and homogeneous generator assumptions. Those models have unresolved clock, copy and historical-producer caveats. Other exact jump distances, noncontiguous or fullword observations, output transforms, independent producer architectures and physically copied payload data remain untested.

**Research allocation implication:** More checkpoint matching at these three far indices cannot recover K04. A productive next direction must identify a different source-to-coupon bridge, such as a target-intersecting indexed fullword carrier, physical copy-stage constraint, or a mechanism that creates genuinely lower-dimensional selected output. Do not rerun this batch jump under guessed real AX bytes or count modelled selected entropy as authenticated original bits.

**Authoritative state:** K01/K02/K03/K05/K06/K07 remain PASS; K04 and K08 unresolved; combined REC8 INCOMPLETE. No original verifier, acceptance or source files changed.
