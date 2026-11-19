# K08 HMAC low-bit routing cycle and cross-slot N14 convergence

**Date:** 19 November 2026  
**Agent:** 9  
**Status:** new target-blind routing structure; K08 terminal wording still unresolved  
**Reproducer:** `agents/agent9/k08_hmac_lowbit_cycle_sft.py`

## Question

The surviving source already supports a repeated LOW BIT operation over accepted component stages, note initials, seal serials and recorder controls. Can the exact K08 HMAC reducer itself be used as a source-local router over the 24 numbered notes, and does that router add a discriminating continuation beyond the existing mug-shelf/workbook locator network?

This test uses the supplied K08 desk nonce and normalization because those are explicit routing data. It never reads the K08 acceptance commitment when choosing or evaluating note edges.

## Construction

For each N01..N24:

1. use the note body after its colon-prefix heading when one exists;
2. normalize exactly as K08 specifies;
3. compute HMAC-SHA256 under the supplied K08 desk nonce and retain the first 16 bytes;
4. take each byte's least-significant bit and pack first-bit-as-LSB into two bytes;
5. render those two bytes as four uppercase hexadecimal characters;
6. take the ASCII low bits of those four characters, again first-bit-as-LSB.

The final value is an integer from 0 through 15 and is interpreted in the same numbered-note namespace used by the established LOW BIT router.

Pinned sources:

- crew notes SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- recovery routing SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`

## Full 24-note map

```text
N01 6772 ->  6
N02 CDE7 -> 13
N03 0EF0 ->  2
N04 6AA0 ->  6
N05 ADBE ->  9
N06 DA03 -> 10
N07 5922 ->  3
N08 60C3 -> 12
N09 46CC -> 12
N10 9BC7 -> 13
N11 C2E3 -> 13
N12 EC4C -> 11
N13 E2BC ->  9
N14 AC94 ->  7
N15 18E8 ->  5
N16 D1D9 -> 10
N17 C04A ->  9
N18 B9DF ->  2
N19 C019 -> 13
N20 DA53 -> 14
N21 AD4E ->  9
N22 5A16 ->  7
N23 C90D ->  3
N24 7C67 -> 11
```

Every numbered note reaches the same four-note attractor:

```text
N12 -> N11 -> N13 -> N09 -> N12
```

This cycle is useful because its source semantics line up with the already-derived LOW BIT vocabulary:

- N12 body begins **The**
- N11 body begins **Even**
- N13 begins **At**
- N09 body begins **Nobody**

The initials are `TEAN`; the first three spell **TEA**.

The body-word counts are `11,14,22,13`, which map A=0 to `LOWN`; the first three spell **LOW**.

Both complete four-letter strings have ASCII low-bit pattern `0,1,1,0`, giving value 6 and pointing back to K06 under the established component namespace.

The four-cycle alone is not a strong specificity result. Under an iid 0..15 selector null, the exact inclusion-exclusion probability that some four-cycle exists among the 15 numbered reachable nodes is about **12.308%**. The useful evidence is the semantic alignment of this particular cycle with the already independent TEA/LOW router and the other convergences below.

## Cross-slot N14 convergence

Apply the already-established byte-LSB pack followed by hex-character low bits to the two independent route-sheet constants:

```text
K04 masked_component 8556C8CB6140A7F9A5123AC7571BEE1C
  -> byte LSB pack D939
  -> hex-character LOW BIT = 14

K08 desk_nonce       5F933DA6A1BD03C32DA5CBC25344F497
  -> byte LSB pack F797
  -> hex-character LOW BIT = 14
```

Both select **N14, Sunrise photograph**.

The same note is selected independently by N20's HMAC low-bit route:

```text
N20 -> 14
```

N20 is Emily's explicit semantic brief for the final line, so this provides a target-blind bridge from the authoring brief to a specific photograph note without using the K08 commitment.

The coincidence of two route constants landing on the same selector is modest by itself. Two independent uniform 0..15 selectors match each other with probability 1/16. Their common value being the pre-existing photograph node N14 is the source-specific part.

## A LOW BIT yields two grammatical route instructions

The published source-stage component map gives:

```text
A   -> K01 -> 12
LOW -> K06 -> 10
BIT -> K02 source stage -> 11
```

Use each component number as a one-based full-note word index at the selected note:

```text
K01 / N12 / word 1 = Workshop
K06 / N10 / word 6 = to
K02 / N11 / word 2 = shelf
```

This yields:

> **Workshop to shelf**

Using the accepted final K02 component changes only its low-bit selector, from N11 to N10:

```text
K01 final -> 12
K06 final -> 10
K02 final -> 10
```

The same component-number word indexing now yields:

> **Workshop to desk**

The transformation is therefore:

```text
source-stage K02: Workshop to shelf
accepted K02:     Workshop to desk
```

This is an unexpectedly clean source-local transition. It matches the documentary topology: N12 is the Workshop card, N11 is Mug shelf, and N10 is The desk copy. The one-based word-index step is inferred rather than explicitly stated by a source record, so preserve it as a routing hypothesis until another independent source operation calibrates the same indexing rule.

Both literal instructions are direct K08 negatives:

- `workshop to shelf` -> HMAC16 `0DA06078B7F3EEB075FADA8DA69343D1`; component SHA256 `e0a857d8c6c08f584ed031cd982c8637c6253de90d7ecf0d6c0e18b74984685a`
- `workshop to desk` -> HMAC16 `0E31873A66D35D32FCBF3A26177FFD84`; component SHA256 `46ce09987ab8185ab076786f41ea619b33758c0ea45a7cd97c76c1104cba8c22`

Treat them as instructions, not keeper wording.

## Consequence

The strongest local continuation is now a compact source-routing graph rather than another free caption grammar:

```text
Workshop -> shelf -> desk
                 \
                  photograph N14
```

N12's HMAC edge goes directly to N11, independently agreeing with the source-stage **Workshop to shelf** extraction. The accepted-stage variant sends the same construction to N10's desk copy. N20, the K04 route mask and the K08 desk nonce all point to N14.

This materially narrows the next text-facing investigation: use the source-fixed N10/N11/N12/N14 relation and the N12->N11->N13->N09 HMAC cycle to seek a deterministic extraction of Emily's wording. Do not widen semantic paraphrase grammars or arbitrary workbook coordinates from this result.

K04 remains unresolved and no K08 component is promoted by this report.


## 19 November parser-sensitivity correction — colon-label stripping is conditional

The construction above applies the HMAC reducer to each note body **after removing any prefix before the first colon**. That is a plausible field parse because prefixes such as `Mug shelf:`, `Workshop card:`, and `Sunrise photograph:` resemble note labels, but the surviving text does not formally define a structured label/body schema. The note-order null and the word-index extraction use the same stripping helper, so their results are conditional on this parse.

A matched control was recomputed with the complete post-heading note text preserved, including any colon prefix. The full-label map is:

```text
N01 82D4 ->  0   N02 B44B ->  0   N03 C123 -> 11   N04 E800 ->  1
N05 C5BB ->  3   N06 ED69 ->  9   N07 DF81 ->  8   N08 3AC7 -> 15
N09 0236 ->  4   N10 9BC7 -> 13   N11 6986 ->  2   N12 8562 ->  2
N13 E2BC ->  9   N14 15F4 ->  3   N15 2C11 -> 14   N16 3F6D ->  1
N17 AC9D ->  7   N18 F782 ->  2   N19 C019 -> 13   N20 DA53 -> 14
N21 3CE4 ->  7   N22 3F79 -> 13   N23 C90D ->  3   N24 46D9 ->  8
```

- **18/24** note selectors change when labels are preserved.
- Among the eight role-selected carriers N09/N10/N11/N12/N13/N14/N20/N23, **four** change: N09, N11, N12 and N14.
- Under the full-label map, every path from N01–N24 terminates at selector 0 (outside the 1–15 note namespace); **no four-note attractor remains**.
- The label-stripped mode still yields the N12→N11→N13→N09 cycle and the TEA/LOW initials/count pattern. Those results are therefore conditional on treating colon prefixes as labels and removing them before HMAC/word indexing.

The independent K04-mask and K08-nonce constants still map to selector 14 under their own route operation; that cross-slot arithmetic does not depend on note-label parsing. What changes is the note-HMAC graph and the interpretation of N14's note-body edge. Do not describe the four-note cycle, word-index route, or N14 note-edge as parser-invariant.

The reproducer `agents/agent9/k08_hmac_lowbit_cycle_sft.py` now emits both parser modes and asserts the full-label control. The integrated K08 benchmark must freeze the label-stripped mode only if it explicitly justifies the colon prefix as a separate source label; otherwise include the full-label-preserving mode as a matched parser control. The 200k within-author note-order null is likewise conditional on colon-label stripping and must be labeled or rerun under the alternate parse.
