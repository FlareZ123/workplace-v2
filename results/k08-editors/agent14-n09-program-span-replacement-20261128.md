# K08: replace the N09 AES/SHA/AES program span with the emitted table fragment — one-output MISS

**Agent 14 | 28 November 2026 | deterministic authoring-operator test | no recovered K08 component**

## Question

Two independent 27–28 November source-local results now land on the same selected N09 caption:

1. the STOW/CLBM and heading lineage mechanically emits the four-word fragment beginning with N09's first word and ending at N20's selected table token; and
2. N09 body words **2 through 8** are exactly the contiguous region covered by the unique overlapping source program **AES / SHA / AES** (triplet starts 2, 4 and 6).

Can those two source-selected structures define the missing final edit without a free phrase grammar?

## Frozen editor

The rule is fixed before consulting acceptance:

- keep N09's first word through the independently emitted four-word lineage fragment;
- remove N09 body words 2..8, exactly the span occupied by the unique AES/SHA/AES encoding;
- replace that span with the independently emitted lineage fragment's remaining words;
- preserve N09 body words 9..13 verbatim as the tail;
- apply the official K08 normalization/reduction once.

This emits **one complete nine-word normalized candidate**. No synonyms, row choices, optional connectors, deletion masks, rotations, or target-selected lexical decisions exist.

The exact candidate wording is deliberately not reproduced here. The source-pinned SFT reconstructs it directly from the preserved notes.

## Source-vs-free decision ledger

| Decision | Source-fixed or free? |
| --- | --- |
| Base record N09 | source-selected by the independent STOW/CLBM and heading routes |
| Program span boundary | source-fixed: the unique AES/SHA/AES windows start at N09 words 2/4/6 and jointly cover words 2..8 |
| Replacement fragment | source-emitted by the N09 -> N13/N23 lineage plus the N20 indexed token |
| Tail after program span | fixed: preserve N09 words 9..13 |
| Lexical choices / joiners / positions | none |
| “Program span should be replaced by the emitted fragment” | **the single unverified authoring-edge hypothesis** |
| Complete authored same-operation holdout | none survives |
| Operator/source controls | unique AES/SHA/AES span, independently emitted fragment, historical N02 K08 reducer fixture |

The missing historical attestation is therefore explicit and singular: the records do not state that Emily replaced the encoded N09 span this way.

## Original result

Local execution against the unchanged original archive:

```text
source_pin=PASS
aes_sha_aes_span=PASS
emitted_fragment=PASS
candidate_word_count=9
complete_candidates=1
historical_n02_control=PASS
original_k08_hits=0
```

**The one deterministic complete output misses the original K08 commitment.**

## Relation to prior work

Agent18 previously tested a natural complete edit that inserts the emitted table fragment after N09's first word while retaining the rest of N09. That candidate also misses K08.

This experiment is different: the newly discovered AES/SHA/AES structure supplies an exact **replacement boundary**, so N09 words 2..8 are removed rather than retained. Repository search for the joint AES/SHA/AES + emitted-table replacement found no earlier equivalent result.

The same-day Agent14 aligned editors are also separate: they expose per-position palette choices. This editor has **one** complete output and therefore satisfies the newer selected-operator gate.

## Consequence

The most literal composition of the two strongest N09 source-local structures is false: the encoded program span is not replaced by the mechanically emitted table fragment while preserving the N09 tail.

That is useful because it removes a complete source-selected authoring rule without opening another combinatorial family. Future work should change the authoring edge or obtain a final carrier; it should not vary the replacement boundary, tail length, or fragment synonyms unless another retained record selects those decisions.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing; REC8/1 remains incomplete.

## Reproducer

`agents/agent14/k08_n09_program_span_replacement_sft.py`

The script pins the crew-note source, reconstructs the AES/SHA/AES span and lineage fragment from source text, checks the historical N02 HMAC fixture, emits exactly one candidate internally, and reports only the candidate count/word count and commitment hit count.
