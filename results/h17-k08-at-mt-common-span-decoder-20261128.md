# K08: emitted AT -> MT addresses recover the first two N20 motif spans

**Agent 45 | 28 November 2026 | target-blind source-local decoder refinement; K08 remains unresolved**

## Decision question

Agent5's source-selected `TAILBIT`/`LEN` construction emits the literal two-character token `AT` without reading the K08 target or nonce. Separately, the established `ATEALBIT` LOW-BIT channel emits column `M`, and the existing source-local step of seven advances that column to `T`. Do these outputs act as the same A1Z26 note addresses already used by the STOW/SEAT branch, and if so do they recover source text with a finite corpus control rather than a prose grammar?

## Frozen construction

The reproducer reads only the pinned 24-note crew source and never reads `acceptance.json`, the K08 target, desk nonce, or `candidate.json`.

1. Reproduce the source-selected seven-note `TAILBIT` run from the K05-K07 sender-union note set.
2. Apply the already-derived `TAILBIT` and complete-body `LEN` operators in source order; the two seven-bit outputs reproduce `AT`.
3. Read `AT` by the already-established A1Z26 note-address convention. Compute the **unique longest exact contiguous normalized-word span** common to those two addressed notes.
4. Apply LOW BIT to the tail token of that recovered span. It yields the already-established step value 7.
5. Reproduce `M` from LOW BIT of the frozen `ATEALBIT` sequence. Advance `M` by the source-derived step 7, reproducing the existing `M+7=T` checksum and therefore the second address `MT`.
6. Read `MT` by the same A1Z26 convention and compute its unique longest exact common contiguous span.

Raw span text is deliberately omitted from this public report under the current output boundary. The reproducer records only their word lengths and SHA-256 fingerprints.

## Result and finite controls

The two addressed spans are exactly the first two motif spans in N20 and occur there in source order.

- `AT -> N01/N20`: unique longest common span length **2** words; SHA-256 `556713372501bc1d2a113beaf1fe4fe921267d5cd0c9655b2386ec536a6bffa0`.
- `MT -> N13/N20`: unique longest common span length **5** words; SHA-256 `a9bb20e02706cf2079ed0a11b3fededd1c9325edeea5925734f7592ca7c943c9`.

Across all **276** unordered pairs of N01-N24:

- only **12** pairs share any exact contiguous run of two or more normalized words;
- `N01/N20` is the **only** pair whose maximal common run has the first span fingerprint;
- `N13/N20` is the **only** pair with a shared contiguous run of **five or more words**.

This converts the new literal `AT` emitter into a deterministic note-pair text selector and composes it with the pre-existing M/T construction. The second address is not selected from the desired wording: its `T` is generated from the first recovered span's tail LOW BIT plus the independently existing `M` channel.

## What changes

This is stronger than another N20-themed phrase check. Two source-generated address tokens now recover, by one fixed overlap rule, the first two N20 motif spans with explicit whole-corpus denominators. The first recovered span also supplies the numeric step that constructs the second address, so the two stages are chained rather than independently post-selected.

It still does **not** emit a terminating complete author-final phrase. N20's remaining social motif is not produced by the same two-note overlap rule, and prior complete phrase/edit grammars already cover broad ways of combining the known motifs. The next useful test is therefore a source-generated third address or a source-visible stop/editor that consumes these two recovered spans and deterministically emits the remaining normalized wording; do not widen this result into a new paraphrase grid.

## Reproducer

`agents/agent45/k08_at_mt_common_span_sft.py`

It pins the crew-note SHA-256, reproduces the `AT` emitter, performs A1Z26 addressing and maximal-common-run extraction, derives the step 7 from the first span without embedding its wording, reproduces the `M -> T` transition, checks the second address, enumerates all 276 pair controls, and emits only aggregate/hash results.
