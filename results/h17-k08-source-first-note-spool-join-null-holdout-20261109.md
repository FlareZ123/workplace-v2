# K08: note-to-printer source-first role holdouts overturn an apparent unique metadata offset

**Agent 11 | 9 November 2026 | source-pinned original experiment; K08 still unrecovered.**

## The potential recovery mechanism

A proposed direct recovery of K08 maps N23, Emily's unquoted final-margin reference, to printer PS-0323, then inverts an assumed cipher from its 16-byte packet to obtain a full unknown K08 HMAC. This requires a genuine note-to-packet connection before cipher inversion. The prior [Agent17 retrospective role screen](h17-k08-note-spool-metadata-bytechannel-holdouts-20261109.md) found offset zero uniquely among 105 note-window offsets by assigning five role expectations after inspecting the printer CLASS/DEST values.

To test that assumption, I independently froze seven plausible document-form roles from the note wording, without consulting their hypothetical matched printer fields. The source does not authenticate any note-to-printer submission. Four of these notes, N09/N12/N16/N21, were excluded from the earlier five-role offset selection. Drafts, narrative passages, N20, and the unquoted N23 abstain from source-first role predictions.

| Note's original description | Source-text predicted CLASS / DEST | Hypothetical offset-zero printer CLASS / DEST | Match |
|---|---|---|---|
| N09 galley board caption | LABEL / store | STORES / store | No |
| N12 workshop card | LABEL / bench | STORES / store | No |
| N16 canteen notice | LABEL / store | STORES / desk | No |
| N17 standby envelope label | LABEL / store | LABEL / store | Yes |
| N18 commissioning envelope label | LABEL / store | RECOVER / store | No |
| N21 freezer door writing | STORES / store | LABEL / bench | No |
| N24 departure board text | LABEL / store | LABEL / store | Yes |

**Four independent role holdouts: zero of four complete CLASS+DEST matches.** The seven roles score **2/7 at offset zero**, which ranks **26th of 105 offsets including ties**. Offset +24 scores 3/7. An alternate *purpose-aware* reading of N18 as RECOVER/store raises offset zero to 3/7, but then it **ties offset +88**; the four independent holdouts remain 0/4.

An exact multiset-preserving permutation of the seven role labels among the same seven note positions has **42 unique arrangements**. **26/42** reach at least the actual 2/7 score at offset zero. Another null with 100,000 seeded draws (20261109) shuffles those role labels and reassigns their positions among N01..N24, preserving role frequency and the original printer distribution; **34,777/100,000** score at least 2/7. These are descriptive checks for this one plausible source-first mapping, not universal p-values for historical printing.

The five retrospectively selected roles reproduce the earlier 5/5 unique offset-zero maximum. Leaving any single one out retains a 4/4 unique winner. That redundancy cannot validate roles chosen after inspection, nor predict the four newly withheld complete category pairs.

## Tested artifact and control

The [portable Python single-file reproducer](../agents/agent11/k08_note_spool_role_join_sft.py) checks exact SHA256 pins for the original crew notes (13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb) and spool reconstruction (7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083). The original-source experiment ran against the unchanged uploaded ZIP. It covers all 24 notes, all 128 ordinary printer packets, all 105 legal offsets, all 42 unique role permutations, and 100,000 frozen random position nulls.

For a synthetic positive, a complete seven-role alignment was planted at hidden offset +37. Six training pairs uniquely recover +37, and the seventh originally withheld CLASS+DEST pair is predicted exactly. This tests the implementation; it supplies no historical K08 wording or paper-queue attribution.

## Recovery conclusion and uncertainty

The genre-to-print-class mapping remains interpretive. A workshop card could be dispatched through a stores printer class; some captions may never have been printed. Therefore these mismatches **do not disprove** every possible N23-to-PS0323 relationship. They demonstrate that the allegedly privileged offset-zero association is **not robust to extra source-text-derived role controls**. Continuing to invert speculative AES, PRF, or bit-wire transports on that unverified pairing is a poor use of recovery effort.

A source-authentic final editorial quotation or independent queue-to-caption link would be needed to turn this into a complete K08 value. K04, K08, and the combined key remain unresolved; six verified REC8/1 slots remain PASS. Original evidence, route, verifier, acceptance commitments and canonical candidate were left unchanged.


## Independent source-first corroboration (Agent40, 9 November)

After this test was committed, Agent40 independently froze **11 literal printable-role cues** from the original notes (photographs, captions, heading, notice, envelope labels and departure board) and predicted only the printer CLASS=LABEL field, without using this report's discretionary DEST assumptions. This orthogonal source-only experiment gets **5/11 LABEL matches** at offset zero, with **48 of 105 offsets at least as good**. Eight N01..N16 out-of-anchor cues get **3/8**, with **78 of 105 offsets as good or better**. The explicit N17 and N18 envelope labels map to different observed CLASS values, LABEL and RECOVER. A planted whole-role alignment is detected uniquely. See [Agent40 source-only CLASS report](h17-k08-sourceonly-role-offset-discriminator-20261109.md) and [SFT](../agents/agent40/k08_note_spool_sourceclass_sft.py).

Agent17, author of the earlier selected-role alignment, acknowledged in [direct correspondence](../communications/agent11/20261109T0426Z_agent17-concede-k08-role-holdout.md) that the original five-role unique offset-zero fit is **not independently predictive** and no longer justifies PS-0323 transport inversion. Both external corroborations preserve the distinction between an interpretive textual role and an **authenticated physical print submission**; neither recovers K08.
