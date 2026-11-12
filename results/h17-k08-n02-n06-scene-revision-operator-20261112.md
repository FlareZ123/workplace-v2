# K08: N02→N06 scene-revision operator and final-stage transfer test

**Agent 2 | 12 November 2026 | Source-pinned whole-caption control.** K08 remains unrecovered. This result tests one concrete authoring operation; it does not claim that a semantic paraphrase is the final envelope inscription.

## Result

A source-conditioned **abstract-handoff → concrete-domestic-scene** rewrite reproduces the complete N06 second-desk-draft wording from N02 plus Emily's other retained context:

> The little lamp stays on until the corridor has gone quiet.

The prediction stage uses N02, N13, N17 and MAIL-12. The script constructs the candidate before it reads N06, then compares the entire N06 inscription. The match is exact. This is a materially different operation from the earlier cross-crew word/bigram graph grammars: it uses an author-specific semantic revision and recurring image anchors, not a free word expansion.

## Frozen operator

1. **Preserve the proposition in N02:** a good watch leaves a shared space ready for the next people.
2. **Replace the abstract subject with the repeated concrete object:** “little lamp” appears in both Emily's N13 note and MAIL-12.
3. **Recast the retained action statively:** N13 says somebody remembered to leave the little lamp on; N17's standby label says to leave the light on for the next watch. The scene form is “stays on.”
4. **Replace the generic room with the evidenced place:** MAIL-12 names the corridor and says its lights are dimmed.
5. **Turn the handover duration into an end condition:** “for the next watch” plus N13's end-of-night setting becomes an “until” clause.

The final lexical completion **“quiet” is an inference**, not a token in the unwithheld inputs. It is semantically supported by the dimmed corridor and end-of-night context, but it is not mechanically determined by those words. The result is therefore a plausible human-editor operation with a successful whole-caption reconstruction, not a deterministic source-only transducer. It has one genuine draft-to-draft control, not a calibrated population of final-stage examples.

## Final-stage transfer

MAIL-11 describes the intended relationship as people making room for each other after a long watch, with water outside and the night almost finished. N20 explicitly names the sea, end of night and voices at the table. Applying the same scene-rewrite idea gives complete, source-grounded candidates, but none passes the original K08 commitment:

| Complete candidate | HMAC-SHA256 first 16 bytes | SHA256 of those 16 bytes | K08 |
|---|---|---|---|
| “At the end of the night, the sea is quiet beyond the window and the voices at the table make room for one another.” | 32CD1CB2F47E8422820E9FAF7A2DBEEB | 0da40ac6e6ebacb3bc2debb971d025e623f1a6d549535d3b81687b9edb4e93e3 | NO_MATCH |
| “The sea is quiet beyond the window, and the voices at the table make room for one another.” | CC0638517D0CD42801B367EFA96E0246 | b0272fb1abae9662b4d64259c18bc11f5d9b352829d26316a69f9860b12c6c2c | NO_MATCH |
| “The sea stays quiet until the voices at the table have made room for one another.” | 77D60D12462E2E94E09F5E5675D424D6 | daaa19d18584cb5ee12adc94084874361f4b4a028ca56c0f52cee3cb1ae413cc | NO_MATCH |

The N06 control itself normalizes to “the little lamp stays on until the corridor has gone quiet”; its HMAC16 is 0C3B326D0324BF93F55D4A3EEAB26CDE, whose SHA256 is 61ab8eb46d2ec91b1accf14e87cdd85149a88201147d4165f8c2d6cbe3041018, also not K08.

## Interpretation

- **Supported:** Emily's second draft can be reconstructed as a concrete scene rewrite of the first draft when her repeated lamp/corridor context and earlier light-on label are used.
- **Not supported:** that this operation uniquely determines the author-final margin. N06 is a second draft, not a final-stage exemplar; N20 is a semantic brief, not a quotation; MAIL-11 gives intent, not the final words.
- **Practical consequence:** retain this operator as a useful authoring control, but do not promote any of its three final-stage candidates. A complete author-final source or an independently eligible final-version example is still needed to determine exact wording. More unconstrained phrase expansion is not justified by this result.

## Reproduction

The standard-library SFT is agents/agent2/k08_n02_n06_revision_operator_sft.py. From the repository root, run:

    python agents/agent2/k08_n02_n06_revision_operator_sft.py --root resources

Optionally pass --archive /path/to/h17-archive-dump.zip to assert the original ZIP SHA256 as well. The script pins the four source-file SHA256 values, validates the N02/N13/N17/MAIL-12 anchors, generates before reading N06, checks the entire N06 caption, and evaluates the three complete final-transfer candidates against the unchanged K08 commitment. The supplied ZIP SHA256 is e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7.

No official evidence, route, acceptance commitment, verifier, or canonical candidate was modified. Six original slots remain PASS; K04 and K08 remain missing; REC8/1 remains INCOMPLETE.
