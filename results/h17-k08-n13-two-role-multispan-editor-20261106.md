# K08: N13 two-role, multiword scene revision under the historical author-purpose notes

**Agent 49 | 6 November 2026 | original-source local execution.** Exactly **2,859,120 complete candidate assignments**, **2,215,036 distinct normalized caption strings**, **zero authentic K08 commitments**. A complete synthetic positive was recovered exactly once. This is a bounded new author-version hypothesis, not a recovery of Emily's final caption.

## Proposed version operation

The original N13 recollection begins `at the end of the night` and continues with a mugs/window image and a somebody/lamp image. N20 and Emily MAIL11 separately describe the final keeper-envelope purpose in terms of sea/water outside and people/voices at the table. Instead of using N13 as a fixed whole caption with one- or two-*word* substitutions, hypothesize a **two-role paragraph edit**: preserve the N13 opening and unmodified residual wording but replace the middle environmental scene and the later human scene with separately extracted complete multiword phrases from N20/MAIL11.

This specifically tests a *version-production* mechanism and retains source-supported continuity in the original N13 scene. It differs from previously tested independent three-fragment collages, one-word-per-note selections, bigram walks and N13's prior radius-two single-token edits. The source does not authenticate this operation or any terminal words.

Tokenize lowercased ASCII alphanumerics. Original N13 has 22 words; its first six are `at the end of the night`. Derive exact contiguous **2..9-word** source spans from N20's first 19 words and MAIL11's actual `For this envelope I wanted...` paragraph only:
- **95 distinct environmental replacement spans**, each containing at least one of `sea, water, outside`.
- **114 distinct human replacement spans**, each containing at least one of `voices, table, people, room, each, other`.

A role-constrained, small boundary-jitter operator picks original N13 indices `a=6..8`, `b=10..14`, `c=12..16`, `d=19..22` under `a<b<=c<d`, totaling **264 distinct cut quadruples**. The whole normalized caption is:

```text
join(N13[:a] + environment_span + N13[b:c] + people_span + N13[d:])
```

All original words outside the two replaced passages remain in their original order. Exhaustively test **264×95×114 = 2,859,120 complete assignments**; many assignments merge to the same normalized sentence. The 2,215,036 unique outputs have sorted-newline-set SHA256 `42f32d94a966fe623fbf0df897d585cff3f8c177372915f1cec5eff678769105`.

## Original-source execution and controls

- Crew notes SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`; MAIL11 SHA256 `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`; both independently asserted before generating candidates.
- K08 original desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`. For each fully normalized caption, compute `SHA256(HMAC_SHA256(nonce, UTF8(caption))[:16])` and compare the **complete original** target `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.
- The original historical Emily N02 known first-draft HMAC16 control equals `BF889359B0303F2B2B2FD96AE841210B`, as required.
- An independently planted candidate from the exact two-role edit grammar was recovered **once** by the same full HMAC-and-SHA loop.
- Actual unmodified local ZIP experiment: `assignments=2859120 unique_normalized=2215036 original_hits=0 synthetic_hits=1` (15.43s). No official source, original verifier or canonical six-pass candidate was changed.

**Reproducible single-file source-pinned Python SFT:** [agents/agent49/k08_two_role_multispan_editor_sft.py](../agents/agent49/k08_two_role_multispan_editor_sft.py). It reads the original resources and pins the distinct set fingerprint.

## Consequence and research direction

The final literal is **not** any normalized output of this precisely defined two-role multispan editor. This negative does not refute a substantially different revision operation, independently authored final wording, missing printed/inked margin, or another medium. It offers no authenticated final K08 word, and no K04 physical selected coupon bit. Six original K01/K02/K03/K05/K06/K07 checks remain accepted, K04 and K08 unresolved, combined REC8/1 INCOMPLETE.

The next useful experiment should be a different author-final version producer, a specific literal source witness, or an independently held-out selected K04 physical/capture transformation. More boundary jitter on this same family has little expected discriminating value.
