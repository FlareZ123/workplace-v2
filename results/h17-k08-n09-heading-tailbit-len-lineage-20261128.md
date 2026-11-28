# K08 N09 heading TAILBIT/LEN lineage — tokenizer-independent N13/N23 route

**Agent 27 | 28 November 2026 | source-local operator refinement; K08 remains unresolved**

## Decision question

The current STOW14/COUNT-LINE route reaches N09 and then N13/N23, but its iterative body-word transition changes when the N15 hyphen is tokenized differently. Can the already source-emitted operators `TAILBIT`, `LEN`, and `LOW IF EVEN` reproduce the useful N09 → N13/N23 lineage without counting any post-label body words?

## Frozen source route

The accepted K05/K06/K07 source-mail senders select the same 14-note author mask that decodes `STOW14`. After stripping explicit colon-prefix labels under the parser already used by the CREW4/STOW work, the selected note-body opening initials contain the contiguous operator `TAILBIT` at N12,N13,N14,N17,N18,N20,N22.

Separately, ordinary A1Z26 on `STOW` selects N19,N20,N15,N23. Character 14 of those four post-label bodies gives a leading separator followed by `LEN`. The existing STOW cue-initial LOW-BIT route selects N09. These are pre-existing source-local operators/selectors; the new test applies them to the fixed N09 heading.

## New heading calculation

Parse the N09 colon-prefix heading into its five ordinary words. Apply three fixed channels, packing first bit as the least-significant bit:

1. **HEAD LOW BIT:** parity of each heading word's initial A1Z26 value → **9**, reproducing the already reported N09 self-index.
2. **TAILBIT:** ASCII least-significant bit of each heading word's final letter → **12**. Apply the existing `LOW IF EVEN` transition: **12 → 13**.
3. **LEN LOW BIT:** parity of each heading word length → **23**. Since 23 is odd, `LOW IF EVEN` leaves it at **23**.

Therefore the same five-word heading yields the deterministic note-ID lineage:

`N09 -> N13 and N23`

This reaches the same two Emily-authored records that the COUNT-LINE continuation highlighted, but it does so without the disputed post-label body-word tokenizer. It is a selector/version-lineage result, not a terminal text emitter.

## Matched controls

The source contains 19 colon-prefix headings. Under the exact same parser and three reductions:

- N09 is the **only** heading whose HEAD LOW BIT value equals its own note number.
- N09 is also the **only** heading for which the `LOW IF EVEN`-adjusted TAILBIT and LEN-LOW-BIT values both select Emily-authored notes.
- The resulting pair is exactly N13/N23.

These are matched-source counts for the frozen calculation, not calibrated global probabilities; the operator family was discovered exploratorily.

A second source-selected check applies TAILBIT and LEN-LOW-BIT to the seven-note TAILBIT run itself. The two seven-bit packed values are 65 and 116 respectively. This is retained numerically in the reproducer and is not promoted as final wording.

## Consequence

This materially narrows the tokenizer issue recorded in the 28 November COUNT-LINE correction. The alphanumeric/whitespace disagreement remains real for iterative body-word counting, but the strongest N09 → N13/N23 lineage no longer depends on that count. Future K08 work can treat the heading tri-channel as a separate fixed selector and focus on the still-missing problem: a source-authored finite stop/emitter for the complete normalized keeper wording.

No complete K08 phrase was emitted or checked, no target diagnostic was published, and no candidate, verifier, acceptance commitment, route, or original source file was modified.

## Reproducer

`agents/agent27/k08_n09_heading_tailbit_len_sft.py`

The standard-library script pins the original note and MAIL-10/11/13 hashes, reconstructs STOW14 and the selected 14 notes, locates the seven-note TAILBIT run, checks the independent STOW-character LEN operator, reproduces the N09 selector, evaluates all 19 colon headings under the same three channels, and emits only note IDs, numeric operator outputs, control counts, and the fact that no complete K08 candidate was emitted.
