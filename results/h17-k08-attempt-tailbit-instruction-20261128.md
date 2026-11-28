# K08: source-schema completion yields ATTEMPT TAILBIT LOW IF EVEN

**Agent 2 | 28 November 2026 | target-blind source-program interlock; K08 still unresolved**

## Result

The source-selected K05/K06/K07 mail senders are Simon, Emily and Gabriel. Selecting their crew notes in N01..N24 order gives the already observed body-head stream:

`ATTPTTAILBITTE`

The literal operator `TAILBIT` begins after the five-character prefix `ATTPT`. Prior work could only call that prefix “plausibly attempt” because the letters `E` and `M` were absent.

The newer overlap decoder removes that ambiguity enough to make a finite source-schema test possible. Across all note pairs, **N13/N20 is the only pair with a maximal common run of at least five words**; its unique run is `the end of the night`. Its length gives **E** under the established LEN/A1Z26 convention, while the non-N20 address note N13 gives **M**. Therefore the only two new symbols admitted here are E and M.

Enumerate every insertion boundary in `ATTPT` and both orders `EM` / `ME`: 12 total completions. Compare them only against literal field names already present in the surviving spool / transfer schemas. There is exactly one match:

`ATT + EM + PT = ATTEMPT`

`ATTEMPT` is not selected from an English dictionary; it is the exact `ATTEMPT` field used by the original printer log and the exact `attempt` key in the transfer audit.

Composing that schema token with the literal run and the already established count continuation gives:

**ATTEMPT TAILBIT LOW IF EVEN**

This directly describes the previously conditional AX-7782 construction: for even-numbered chunks choose the lower attempt number (attempt 1), otherwise attempt 2, concatenate the selected checkpoints, then take each selected byte's tail/low bit and pack first-bit-as-LSB.

MAIL-13 independently selects AX-7782 as the final custodian handoff, states that all eight chunks are numbered from zero, and says each chunk was retried once. Applying the instruction gives:

`6224 CEDC F3B8 73BA 1888 7BE6 3DB0 C5C9`

Tail bits pack to:

`50 D4` = ASCII **P** followed by unsigned **212** = **P212**.

The same exact mixed-attempt/tail-bit operation on the other complete transfers gives controls:

| transfer | packed tail bits |
|---|---|
| AX-7778 | `694A` |
| AX-7781 | `C28A` |
| **AX-7782** | **`50D4` = P212** |
| AX-7783 | `CF59` |

## Specificity and what changed

Among all 20 possible three-author masks, the independently source-selected Simon/Emily/Gabriel mask is the only one whose body-head stream contains `TAILBIT`. The smaller Emily/Gabriel mask also contains TAILBIT when author-set cardinality is allowed to vary, so this is not claimed as a globally calibrated probability.

The substantive advance is narrower: the formerly hand-read `ATTPT` fragment now has a **finite, source-vocabulary completion** to the exact schema field `ATTEMPT`, using only the E/M symbols supplied by the independent N13/N20 overlap structure. This makes the semantics of the P212 transform substantially less arbitrary: both **ATTEMPT** and **TAILBIT** are now emitted/source-matched instructions rather than analyst glosses.

The remaining conditional step is the established reading of **LOW IF EVEN** as “use the lower attempt on even chunk numbers.” P212 remains a locator/checksum output, not Emily's final keeper-envelope wording and not a recovered K08 component. No acceptance target, nonce, candidate phrase or commitment was read by the reproducer.

## Reproducer

`agents/agent2/k08_attempt_tailbit_instruction_sft.py`

The SFT pins the original crew notes, MAIL-10/11/13, transfer audit and spool reconstruction; reproduces the sender-selected head stream; exhausts all 20 three-author TAILBIT masks; proves the unique N13/N20 >=5-word overlap; exhausts the 12 E/M insertion completions against source schema fields; reproduces the full instruction and all four transfer controls; and reads no K08 target data.
