# K08: N02→N06 scene-revision operator and final-stage transfer test

**Agent 2 | 12 November 2026 | Source-pinned whole-caption control.** K08 remains unrecovered. This result tests one concrete authoring operation; it does not claim that a semantic paraphrase is the final envelope inscription.

## Result

A retrospective, cross-source **abstract-handoff → concrete-domestic-scene** reconstruction reproduces the complete N06 second-desk-draft wording from N02 plus retained crew context. The repeated “little lamp” is in N13 (Emily) and MAIL-12 (Zoey); MAIL-12 also supplies “corridor” and the dimmed-corridor cue:

> The little lamp stays on until the corridor has gone quiet.

The script constructs the candidate before it reads N06, then compares the entire N06 inscription. The match is exact. The underlying MAIL-12 cross-author scene-donor relation is not new: Agent 24 already documented its N06/N13 rare-token overlap and a 777,600-phrase NO_MATCH family in results/h17-k08-mail12-crossauthor-scene-lineage-and-paraphrase.md. The incremental contribution here is the explicit N02→N06 semantic template and the strict pre-MAIL-12 chronology control, not rediscovery of MAIL-12. **It is not, however, a historically authenticated version prediction:** MAIL-12 is by Zoey and dated 2 October 2026 06:33Z; N06 has no timestamp. The source does not establish that MAIL-12 was available when N06 was drafted.

## Frozen operator

1. **Preserve the proposition in N02:** a good watch leaves a shared space ready for the next people.
2. **Replace the abstract subject with the repeated concrete object:** “little lamp” appears in N13 (Emily) and MAIL-12 (Zoey).
3. **Recast the retained action statively:** N13 says somebody remembered to leave the little lamp on; N17's standby label says to leave the light on for the next watch. The scene form is “stays on.”
4. **Replace the generic room with the evidenced place:** MAIL-12 names the corridor and says its lights are dimmed.
5. **Turn the handover duration into an end condition:** “for the next watch” plus N13's end-of-night setting becomes an “until” clause.

The final lexical completion **“quiet” is an inference**, not a token in the unwithheld inputs. It is semantically supported by the dimmed corridor and end-of-night context, but it is not mechanically determined by those words. In addition, the only retained source supplying the exact place “corridor” is MAIL-12, dated 2 October and written by Zoey. N02, N06, N13 and N17 have no timestamps, so the chronology cannot establish that this cue preceded N06. Without MAIL-12, the closest source-anchored place is N02's “room,” yielding “The little lamp stays on until the room has gone quiet,” not N06. Thus the exact match is a retrospective cross-source fit, not a deterministic or chronologically authenticated authoring operator.

## Chronology test

- MAIL-11 is Emily's message dated 1 October 2026 18:14Z. MAIL-12 is Zoey's message dated 2 October 2026 06:33Z.
- N02, N06, N13 and N17 are undated note extracts. No timestamp establishes where N06 falls relative to MAIL-12.
- The exact N06 match uses the corridor cue from MAIL-12. The strict pre-MAIL-12 control uses N02's “room” instead and does not reproduce N06; its HMAC16 is 2C2797D6632EBD7E7BE34AE7FD78910E and its commitment hash is 0d649e720cfea58f70381b9a22d7cb7d58ff11122a29fe68cf0a7ef895052899 (NO_MATCH).
- Consequently, the N06 match is a useful retrospective semantic reconstruction, but it does not establish a time-valid version chain.

## Final-stage transfer

MAIL-11 describes the intended relationship as people making room for each other after a long watch, with water outside and the night almost finished. N20 explicitly names the sea, end of night and voices at the table. Applying the same scene-rewrite idea gives complete, source-grounded candidates, but none passes the original K08 commitment:

| Complete candidate | HMAC-SHA256 first 16 bytes | SHA256 of those 16 bytes | K08 |
|---|---|---|---|
| “At the end of the night, the sea is quiet beyond the window and the voices at the table make room for one another.” | 32CD1CB2F47E8422820E9FAF7A2DBEEB | 0da40ac6e6ebacb3bc2debb971d025e623f1a6d549535d3b81687b9edb4e93e3 | NO_MATCH |
| “The sea is quiet beyond the window, and the voices at the table make room for one another.” | CC0638517D0CD42801B367EFA96E0246 | b0272fb1abae9662b4d64259c18bc11f5d9b352829d26316a69f9860b12c6c2c | NO_MATCH |
| “The sea stays quiet until the voices at the table have made room for one another.” | 77D60D12462E2E94E09F5E5675D424D6 | daaa19d18584cb5ee12adc94084874361f4b4a028ca56c0f52cee3cb1ae413cc | NO_MATCH |

The N06 control itself normalizes to “the little lamp stays on until the corridor has gone quiet”; its HMAC16 is 0C3B326D0324BF93F55D4A3EEAB26CDE, whose SHA256 is 61ab8eb46d2ec91b1accf14e87cdd85149a88201147d4165f8c2d6cbe3041018, also not K08.

## Interpretation

- **Supported:** N06 can be reconstructed as a concrete scene rewrite when the N02 handoff proposition is combined with N13/N17 and the cross-author lamp/corridor context in MAIL-12.
- **Not supported:** that the reconstruction is historically prospective, that Emily had MAIL-12 available when she wrote N06, or that this operation uniquely determines the author-final margin. N06 is a second draft, not a final-stage exemplar; N20 is a semantic brief, not a quotation; MAIL-11 gives intent, not the final words.
- **Practical consequence:** retain this operator as a useful authoring control, but do not promote any of its three final-stage candidates. A complete author-final source or an independently eligible final-version example is still needed to determine exact wording. More unconstrained phrase expansion is not justified by this result. Treat this as a control/falsifier for later author-version work, not a new source discovery.

## Reproduction

The standard-library SFT is agents/agent2/k08_n02_n06_revision_operator_sft.py. From the repository root, run:

    python agents/agent2/k08_n02_n06_revision_operator_sft.py --root resources

Optionally pass --archive /path/to/h17-archive-dump.zip to assert the original ZIP SHA256 as well. The script pins the four source-file SHA256 values, validates the N02/N13/N17/MAIL-12 anchors, generates before reading N06, checks the entire N06 caption, records the date-order limitation and strict pre-MAIL-12 control, and evaluates the three complete final-transfer candidates against the unchanged K08 commitment. The supplied ZIP SHA256 is e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7.

No official evidence, route, acceptance commitment, verifier, or canonical candidate was modified. Six original slots remain PASS; K04 and K08 remain missing; REC8/1 remains INCOMPLETE.
