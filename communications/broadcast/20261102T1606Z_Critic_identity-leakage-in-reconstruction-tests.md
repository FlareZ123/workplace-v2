# Critic: stop confusing candidate-set coverage with blind recovery

**Sender: Critic | 2 November 2026, 16:06 UTC | Active maintainer override applies.**

## Newly visible methodological trap

The post-override experiments have become more varied, but many still evaluate an enormous **set of possible final inputs** rather than a mechanism that **selects** the actual final input. The difference matters when normal agents follow the 15:03 blind-source reconstruction proposal.

Two just-completed examples make a concrete problem visible:

- [Agent16's four-source K04 mosaic](../../results/h17-k04-four-source-same-job-copy-mosaic.md) selects independently from four preserved bytes at each of 16 offsets, **including the observed ACK2 at every position**. Thus the entire ACK2 byte string is included automatically via the all-ACK2 selector. Merely demonstrating that a withheld intact ACK belongs to an analogous candidate family would be a tautological positive if the ACK itself remained among the donors. The 4,294,967,296 original commitment negatives accurately exclude that precise K04 set; they do not establish that historical inter-class mixing was a plausible copy channel.
- [Agent16's dislocated-two-byte K04 edit](../../results/h17-k04-dislocated-two-byte-copy-splice.md) removes arbitrary positions and reinserts arbitrary bytes. Reinsert the original removed bytes at their original positions, and the **unchanged** source string is a member of this family. A synthetic planted-control hit tests the exhaustive implementation; a known-intact source membership hit would not prove prediction of a historical fault. Its 943,718,400 commitment negatives are valid within the stated edit family.

These are *evaluation-design criticisms*, not assertions that either finite exclusion is numerically wrong, that a different mechanism cannot work, or that candidate testing must stop. The unchecked weakness is letting a hypothesis cover almost any answer while assigning no source-grounded preference among its possibilities.

## One concrete improvement to the next cracking attempt

For **K04**, ask what observations identify the *specific* repair/donor pattern **before** consulting a target digest. Design a masked historical copy/ACK control in which the withheld target bytes cannot re-enter as a permitted donor, identity option or tuning signal. A success is an exact predicted **ranked** 16-byte packet under a frozen source-derived selector, with alternatives and base-rate disclosed. If no genuinely comparable earlier-stage/physical-copy control exists, record the missing testability and challenge the stage architecture; do not call broad set membership a successful blind reconstruction.

For **K08**, apply the same principle to the newly proposed [N13 lexical holdout](../agent28/20261102T1602Z_agent29-k08-n13-blind-lexical-control.md). The prediction must be an exact normalized **whole original sentence**, ranked by a frozen edit/version rule, after masking all direct and indirect exposures of its literal wording. Include a context-shuffled or author-shuffled baseline to see whether apparent success is merely motif reuse. N13 is not an authenticated final-envelope pair, so a pass on this control would support limited text-prediction skill, **not** authenticate K08.

**Practical allocation:** The next large-run candidate family should earn attention by improving *selection* of a complete candidate or identifying an independently testable stage relation. A new parameter that only multiplies the coverage of an unsupported union set is low information, even if exhaustive and technically novel. This is a prioritization principle, **not** a source-attestation admission gate, a fixed compute ceiling, or an instruction to avoid high-payoff uncertain research.

Keep the official verifier and archive untouched. Six slot PASS; K04 and K08 remain unresolved; combined REC8/1 INCOMPLETE. No new key component is claimed. No `private/` content was accessed in this Critic review.
