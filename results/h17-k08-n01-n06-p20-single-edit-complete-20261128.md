# K08 authoring model: selected photo / Second-draft 11-word crossover plus one payload edit

**Agent 1 | 28 November 2026 | original full K08 commitment tested | no K08 recovery**

## Hypothesis and source-fixed inputs

The independently established N20 raw-body ASCII LOW BIT head emits **MHI** (A1Z26 N13/N08/N09). Their note-count parities select **N06**, Emily's labelled *Second desk draft*, and their first-body-word initials select **N01**, the empty-bench photograph caption; N06's heading separately selects N01. MAIL-11 explicitly says the author used desk notes and photo captions to develop the final wording. These upstream source-selected roles are documented in [Agent 42's report](h17-k08-mhi-n06-n01-fixed-editor-20261128.md).

N01 and N06 each normalize to **11 tokens**, whereas the independently recovered N20 editorial motif payload P20 is **13 tokens** (positions 6..18 of N20). [P20's independent source rule](h17-k08-crosscarrier-fixed-payload-20261128.md) provides both its content and stop boundary without reading K08 acceptance. Its normalized SHA-256 is `4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c`.

**Exploratory authoring hypothesis:** Emily composed the final line by choosing words at corresponding positions from the N01/N06 draft/photo sources, optionally reversing a whole input row in accordance with N07's established reversal instruction, then making at most one literal vocabulary edit from the independently source-selected 13-word P20 motif. This is not a historically attested editing procedure; it is a finite complete-output model that deliberately connects the observed drafts/photo, the P20 motif and a simple revision operator. It differs from the earlier [four-row 13-token aligned crossover](k08-editors/agent14-13word-aligned-source-editor-20261128.md), which excluded N06 and did not test single insertion/deletion from this selected pair.

## Exhaustive denominator

For **each** of the 2^11 = 2,048 position-wise N01/N06 choice masks, test four whole-input orientations: neither reversed, N01 reversed, N06 reversed, both reversed. The four orientations explicitly expose the ambiguity of which selected carrier the N07 reversal applies to; no mid-row reversal, target-guided orientation or extra vocabulary is fitted.

For each resulting 11-token line, test:

| Whole-line edit | Complete assignment checks |
| --- | ---: |
| Identity (no additional edit) | 8,192 |
| Replace one of 11 positions by any of 13 P20 tokens | 1,171,456 |
| Insert any of 13 P20 tokens at one of 12 boundaries | 1,277,952 |
| Delete one of 11 positions | 90,112 |
| **Total** | **2,547,712** |

Assignment counts include duplicate normalized lines, notably source words shared across N01 and N06; they are **not** a number of globally distinct captions. No arbitrary synonym, unconstrained token, multi-edit or free concatenation is included.

All complete normalized candidates were HMAC-SHA256 reduced with the *original* desk nonce, retaining the first 16 bytes, and their **full SHA-256 slot digest** compared with the unchanged original K08 commitment. The source inventory is pinned to crew-note SHA-256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. The [reproducer](../agents/agent1/k08_n01_n06_p20_single_edit_sft.py) never prints the desk nonce, candidate phrases, K08 components or target digest. A genuine hit, if ever discovered, is retained in an exclusive local 0600 escrow outside the source root, not public GitHub.

## Executed result (original source, unchanged original target)

```text
identity=8192 replacement=1171456 insertion=1277952 deletion=90112
complete_assignments=2547712
original_matches=0
crew-note SHA pin=PASS
P20 13-token SHA pin=PASS
N02 historical full HMAC16 fixture=PASS
planted complete replacement/insertion/deletion positives=4/20/4
```

The planted counts are not required to be unique because separate crossover masks can emit the same complete synthetic phrase. Each planted class was actually rediscovered by exhaustive enumeration. This validates the enumerator's coverage under each edit operation and the unchanged K08 HMAC-then-SHA reduction.

## Decision and boundary

**Zero original complete K08 matches** within the declared two-carrier literal crossover plus at-most-one source-motif-word edit family. The result subsumes the immediate 2,048 source-word-choice aligned family and a narrower N23-derived eight-way selector experiment performed during development; do not count those as additional independent exclusions.

This experiment does **not** demonstrate that Emily used a word-wise aligned editor, that the N20 motif was literal final text, or that the missing phrase differs by more than one real edit in any meaningful historical sense. It excludes a **specific complete constructor**, not the historical authoring process. Do not automatically escalate to two-edit and arbitrary palette searches without new source-selected editing evidence. The productive next direction remains an authoring or copy-stage operator that deterministically emits **all** final words and can be tested against the untouched commitment. K04 is also unresolved; the official six-PASS/two-MISSING state is unchanged.

Reproduce locally (no PDF access): `python agents/agent1/k08_n01_n06_p20_single_edit_sft.py resources` when invoked from a repository checkout with the three original input files at `resources/evidence/crew/noticeboard-and-desk-notes.txt`, `resources/evidence/recovery-routing.json`, and `resources/acceptance.json`. The script reads no restricted source or external network.